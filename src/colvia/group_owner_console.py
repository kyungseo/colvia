"""Two independent local decisions for two registered native Codex Works."""
from pathlib import Path
import json
from uuid import uuid4

from .codec import require
from .group_records import digest
from .group_view import content
from .group_worker_dispatch import Dispatch, dispatch_plan
from .project_status import project_status


def rendered(value):
    raw = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False)
    return ''.join(c if c.isprintable() or c == '\n' else ascii(c)[1:-1] for c in raw)


def confirmed(console, action, record):
    code = action + '-' + digest(record)[:8]
    if action == 'START' and 'members' in record:
        console.show('Approve two Work scopes and start two Codex sessions')
        console.show('Group  ' + rendered(record['group']) + '\nDestination  ' + rendered(record['target']))
        for member in record['members']:
            title = record['titles'][member['work']]
            console.show('Work  ' + rendered(member['work']) + '  ' + rendered(title))
            console.show('Goal  ' + rendered(member['goal']) + '\nFolder  ' + rendered(member['source_path']))
            console.show('Allowed files  ' + rendered(member['scope']))
            console.show('Plan  ' + rendered(member['plan']))
        console.show('Workers  ' + rendered(record['executables']) + '\n' + record['profile'])
        console.show('Account  ' + record['subscription'])
        console.show('Required integration checks  ' + rendered(record['required_checks']))
    elif action == 'APPLY' and 'members' in record:
        console.show('Review both submissions before applying them together')
        console.show('Group  ' + rendered(record['group']) + '\nDestination  ' + rendered(record['target']))
        for member in record['members']:
            console.show('Work  ' + rendered(member['work']) + '  revision ' + str(member['revision']))
            console.show('Submission  ' + rendered(member['submission']))
            for item in member['files']:
                console.show('File  ' + rendered(item['change']['path']))
                for side in ('before', 'after'):
                    console.show(side + '  ' + rendered(item['change'][side]))
                    body = item['content'][side]
                    if body is not None and 'text' in body:
                        console.show(rendered({key: value for key, value in body.items() if key != 'text'}))
                        for line in body['text'].split('\n'):
                            console.show('  | ' + rendered(line))
                    else:
                        console.show(rendered(body))
            console.show('Work checks  ' + rendered(member['reported_checks']))
        console.show('Check definitions  ' + rendered(record['definitions']))
        console.show('Required integration checks  ' + rendered(record['checks']))
    else:
        console.show(rendered(record))
    return console.ask('Type ' + code + ' to confirm. Enter alone leaves the decision open.') == code


def select_group(store, workspace, console):
    cursor = None
    while True:
        page = project_status(store, workspace, cursor=cursor)
        groups = [row for row in page['items'] if row.get('kind') == 'work-group'
                  and row.get('destination') == workspace and row.get('member_count') == 2]
        for index, row in enumerate(groups, 1):
            console.show(str(index) + '. ' + rendered([row['work_group'], row['title'], row['state']]))
        if not groups and not page['next']:
            console.show('No eligible pair on this page. Prepare two registered Works and a group plan in this project.')
            return None
        reply = console.ask('Choose a number on this page, N for the next page, or Enter to close.')
        if reply.upper() == 'N':
            if page['next']:
                cursor = page['next']
            else:
                console.show('This is the last page.')
            continue
        if not reply:
            return None
        require(reply.isascii() and reply.isdigit() and len(reply) <= 2
                and 1 <= int(reply) <= len(groups), 'parallel-selection-unavailable')
        return groups[int(reply) - 1]['work_group']


def journal_location(home, project):
    from .platforms.windows_paths import local_appdata
    return Path(local_appdata()) / ('ColviaWorkerState-' + digest(dict(home=str(home), project=project))[:24])


def review_record(grouped, name, view):
    require(view['state'] == 'review' and not view['stale'] and view['checks']
            and all(check['status'] == 'passed' for check in view['checks']), 'group-tested-review-required')
    root = grouped.store.root().ref
    members = []
    for member in view['members']:
        inspected = []
        for item in member['files']:
            result = content(grouped, name, member['work'], item['path'])
            require(result['submission'] == member['submission']
                    and result['revision'] == member['revision'], 'group-submission-changed')
            inspected.append(dict(change=item, content=result))
        require(len(inspected) == member['submitted_file_count'], 'group-submission-changed')
        members.append(dict(work=member['work'], revision=member['revision'], submission=member['submission'],
                            scope=member['scope'], files=inspected, reported_checks=member['reported_checks']))
    require(grouped.store.root().ref == root and grouped._selected(name).ref.sha256 == view['head'],
            'group-view-changed')
    return dict(action='Accept both submissions and apply them to the destination', group=name,
                target=view['destination_path'], head=view['head'], receipt=view['receipt'], members=members,
                checks=view['checks'], definitions=view['required_checks'])


def finish(grouped, name, view, console):
    record = review_record(grouped, name, view)
    if not confirmed(console, 'APPLY', record):
        return dict(state='review', accepted=0)
    # execute verifies the receipt and source state again under the application lock.
    key = digest(dict(group=name, review=view['receipt']))[:32]
    return grouped.execute(operation='op-'+uuid4().hex, group=name, application='group-local-'+key,
                           request='local-'+key, receipt=view['receipt'],
                           statement='Accept both displayed revisions and apply them to the displayed destination.')


def prepare_plan(grouped, name, paths, journal):
    view = grouped.view(name)
    require(view['state'] == 'planned' and len(view['members']) == 2, 'group-workers-require-windows-plan')
    plan = dispatch_plan(grouped, name, 'codex', {m['work']:'codex' for m in view['members']}, paths, journal)
    require(view['head'] == plan['group_head'], 'group-view-changed')
    titles = {member['work']: member['title'] for member in view['members']}
    require(len(titles) == 2 and len(plan['members']) == 2
            and titles.keys() == {member['work'] for member in plan['members']}, 'group-worker-members-changed')
    record = dict(action='Approve both scopes, start both Codex workers, collect and check their submissions',
                  subscription='Current local Codex CLI login', profile='Windows MXC / colvia_worker; tool approvals disabled; web search and MCP disabled',
                  group=name, target=plan['target'], executables=paths, members=plan['members'],
                  titles=titles, required_checks=view['required_checks'],
                  dispatch_receipt=plan['dispatch_receipt'])
    return plan, record


def check_results(grouped, name, expected_checks, console, *, build):
    if build:
        grouped.candidate(operation='op-'+uuid4().hex, group=name)
    view = grouped.check(operation='op-'+uuid4().hex, group=name)
    require(view['required_checks'] == expected_checks, 'group-view-changed')
    if view['state'] != 'review':
        console.show(rendered(view['checks']))
        return dict(state=view['state'], accepted=0)
    return finish(grouped, name, view, console)


def inspect_or_run(entry, grouped, name, console):
    from .platforms.windows_group_workers import NativeWorkers, check_instruction_inputs
    from .platforms.windows_owner_console import pinned_codex
    observed_root = grouped.store.root().ref
    view = grouped.view(name)
    require(view['member_count'] == 2, 'group-worker-members-changed')
    state = view['state']
    if state == 'review':
        return finish(grouped, name, view, console)
    journal = journal_location(entry.home.root, grouped.store.project)
    dispatch = Dispatch(grouped, name, journal, files=entry.home.files)
    if state != 'planned' or dispatch.path.exists():
        # Merely opening a partial group must not collect, check, rerun or publish.
        console.show(rendered(dict(group=name, state=state, accepted=view['accepted'],
                                   members=[(m['work'],m['state']) for m in view['members']])))
        resumable = (state == 'approved' and all(m['state'] == 'review' for m in view['members'])
                     or state == 'checks-required' and not view['checks'] and not view['stale'])
        if resumable:
            record = dict(action='Prepare and check the two submitted revisions', group=name,
                          target=view['destination_path'], head=view['head'], checks=view['required_checks'],
                          members=[dict(work=m['work'], submission=m['submission']) for m in view['members']])
            if confirmed(console, 'CHECK', record):
                require(grouped.store.root().ref == observed_root and grouped.view(name) == view, 'group-view-changed')
                return check_results(grouped, name, view['required_checks'], console, build=state == 'approved')
        console.show('Existing group state retained. Inspect its recorded operation before explicit recovery.')
        return dict(state=state, accepted=view['accepted'])
    with pinned_codex(entry.home.files) as paths:
        plan, proposal = prepare_plan(grouped, name, paths, journal)
        if not confirmed(console, 'START', proposal):
            return dict(state='planned', accepted=0)
        try:
            entry.home.files.create_directory(journal)
        except FileExistsError:
            pass
        entry.home.files.private_directory(journal)

        def validate():
            current, displayed = prepare_plan(grouped, name, paths, journal)
            require(current == plan and displayed == proposal, 'group-worker-dispatch-stale')
            check_instruction_inputs(current['members'])

        result = dispatch.run(plan, receipt=plan['dispatch_receipt'],
                              statement='Approve both displayed Work scopes and launch their Codex workers.',
                              native=NativeWorkers(paths), first_dispatch_check=validate)
    if not result['ready_for_group_candidate']:
        console.show(rendered({key:w['phase'] for key,w in result['workers'].items()}))
        return dict(state='incomplete', submitted=result['submitted'], accepted=0)
    require(result['submitted'] == 2, 'group-worker-members-changed')
    return check_results(grouped, name, proposal['required_checks'], console, build=True)
