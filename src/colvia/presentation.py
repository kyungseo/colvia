"""Concise human output; machine receipts and source paths require explicit JSON."""
import json


def _diagnostic_item(item):
    label={'addition':'추가','modification':'수정','deletion':'삭제','proof-mismatch':'대조 근거 불일치'}.get(item['change'],'변경 확인 필요')
    line=item['path']+' — '+label
    if item.get('peer_title'):line+=' — '+item['peer_title']
    requirement={'match-peer-submission':'대조한 제출본과 다시 일치해야 함','unchanged-from-original':'원래 작업 기준과 일치해야 함','separate-scope-decision':'별도 범위 확인 필요'}.get(item.get('requirement'))
    return line+(' — '+requirement if requirement else '')


def human(value):
    if 'error' in value:
        lines=[value['message']];details=value.get('details')
        if details:
            lines.append(details['reason'])
            lines.extend(_diagnostic_item(i) for i in details.get('items',[]))
            if details.get('omitted'):lines.append('그 밖에 '+str(details['omitted'])+'개가 더 있습니다.')
            lines.append(details['next_action'])
        return '\n'.join(lines)
    state=value.get('state');title=value.get('title') or '작업'
    if value.get('kind')=='execution-readiness':
        if state=='prepared-dispatch-unavailable':return '문서 실행에 필요한 파일은 준비됐지만, 이 설치본에서는 아직 실행할 수 없습니다. 일반 작업과 결과 검토는 계속할 수 있습니다.'
        return '이 설치본에는 문서 실행 구성이 준비되지 않았습니다. 일반 작업과 결과 검토는 계속할 수 있습니다.'
    if 'original' in value and 'click_accepts' in value:
        original=value['original'];current=value['current']
        if original['kind']=='executed':lines=['맡긴 실행의 결과입니다. 보고서 제출이나 수락은 별도로 남아 있습니다.']
        else:lines=[original['title']+' — 당시 전달한 결과입니다.',original.get('summary') or '작업 현황을 기록했습니다.']
        if not value['workspace_connected']:lines.append('프로젝트를 다시 연결한 뒤 현재 상태를 확인해 주세요.')
        elif current.get('state')=='completed':lines.append('현재 이 작업은 마무리됐습니다.')
        else:lines.append('프로젝트 대화에서 현재 결과를 확인하고 다음 결정을 내려 주세요.')
        return '\n'.join(lines)
    if 'integration' in value:
        if state=='completed':return '선택한 변경을 Git에 기록했습니다. 작업 결과의 수락 기록과 다른 staging 내용은 보존했습니다.'
        if state=='not-applied':return 'Git에 반영되지 않은 것을 확인했습니다. 현재 변경은 그대로 남아 있습니다.'
        if state=='prepared':
            import base64
            raw=base64.b64decode(value['diff_base64']);patch=raw.decode('utf-8','backslashreplace')
            patch=''.join(c if c in '\n\t' or c.isprintable() else repr(c)[1:-1] for c in patch)
            return '\n'.join(['Git에 기록할 변경: '+', '.join(value['files']),'대상 브랜치: '+value['branch'],
                '메시지: '+value['message'],patch,value['question']])
        return 'Git 반영이 중간 상태로 남아 있습니다. 현재 Git 상태를 확인한 뒤 복구 여부를 결정해 주세요.'
    if 'delivery' in value:
        if 'notification' in value:return {'emitted':'결과 알림을 보냈습니다.','failed':'결과는 보존돼 있지만 알림을 보내지 못했습니다.','unknown':'결과는 보존돼 있습니다. 알림 전송 여부는 확인이 필요합니다.'}[value['notification']]
        if state=='prepared':
            from datetime import datetime
            lines=[title+' — '+{'submit':'준비된 결과를 검토용으로 제출합니다.','inspect':'작업 현황을 정리합니다.','execute':'승인한 문서 작업을 실행합니다.'}[value['action']]]
            if 'deadline_ns' in value:lines.append('기한: '+datetime.fromtimestamp(value['deadline_ns']/1e9).astimezone().isoformat(timespec='seconds'))
            if value.get('receiver'):lines.append('결과 알림 요청도 함께 기록합니다.')
            lines.append('이 범위로 진행할까요?');return '\n'.join(lines)
        if state=='finished':return {'submit':'검토할 결과를 제출했습니다. 내용을 확인한 뒤 마무리 여부를 결정해 주세요.','inspect':'작업 현황을 기록했습니다.','execute':'맡긴 실행의 결과를 기록했습니다. 결과 내용을 확인해 주세요.'}[value['action']]
        if state=='cancelled':return '실행하지 않은 요청을 취소했습니다. 작업 파일과 수락 기록은 그대로입니다.'
        if value.get('cancel_requested'):return '중단 요청을 기록했습니다. 이미 시작한 처리가 끝났는지 확인 중입니다.'
        return '요청한 단계를 '+('시작할 준비가 됐습니다.' if state=='queued' else '처리 중입니다.')
    if 'run' in value and ('document_write_effect' in value or 'cancel_requested' in value):
        if value.get('cancel_requested'):return '중단 요청을 기록했습니다. 실행이 종료됐는지는 별도로 확인해야 합니다.'
        return '맡긴 문서 실행 상태: '+{'completed':'실행 완료','interrupted':'중단됨','incomplete':'처리 중 또는 확인 필요','unknown':'확인 필요','revoked-before-launch':'시작 전 중단','operator-resolved-unknown':'불명 상태 확인 기록됨'}.get(value.get('status'),'확인 필요')+' — 작업 결과의 수락과는 별개입니다.'
    if value.get('delegation'):return '이 격리 작업의 적용·수락 위임을 '+('철회했습니다.' if state=='revoked' else '기록했습니다. 아직 파일을 적용하지 않았습니다.')
    if 'application' in value:
        if state=='completed':
            lines=['대상 작업 폴더에 결과를 적용하고 수락 기록까지 마무리했습니다.']
            if value.get('retained_original_modified'):lines.append('보존한 원본에 추가 편집이 있습니다: '+', '.join(value['retained_original_modified'])+' — 별도로 보존합니다.')
            if value.get('blocked'):lines.append('현재 파일 상태는 다시 확인해야 합니다: '+failure(value['blocked']['reason']))
            return '\n'.join(lines)
        if state=='cancelled':return '현재 파일이 적용 전 내용과 같음을 확인하고 요청을 취소했습니다. 원래 결과의 수락 상태는 그대로입니다.'
        if state=='pending':
            labels={'pre':'아직 적용 전','post':'적용됨','evacuated':'원본을 보존한 뒤 중단됨','unknown':'확인 필요'}
            lines=['파일 적용을 마무리하기 전입니다. 현재 파일과 중단 기록을 확인한 뒤 이어가야 합니다.']
            lines.extend(item['path']+' — '+labels[item['state']] for item in value.get('paths',[]))
            if value.get('blocked'):lines.append(failure(value['blocked']['reason']))
            if value.get('retained_original_modified'):lines.append('보존한 원본에 추가 편집이 있습니다: '+', '.join(value['retained_original_modified'])+' — 별도로 보존합니다.')
            return '\n'.join(lines)
        return '\n'.join([title+' — '+value.get('destination_label','대상 작업 폴더')+'에 적용할 결과입니다.',value.get('summary',''),
            ('적용이 끝나면 이 결과의 수락도 기록합니다.' if value.get('accepts_result') else '기존 수락 기록은 그대로 유지합니다.'),
            '바뀔 파일: '+', '.join(value.get('files',[])),value.get('question','내용을 확인한 뒤 적용 여부를 결정해 주세요.')])
    if 'children' in value:
        lines=['통합 작업에 연결할 하위 결과입니다.']
        lines.extend(child['title']+' — '+('수락됨' if child['ready'] else '결과 수락 전') for child in value['children'])
        if value.get('removed'):lines.append('이번 구성에서 뺄 작업: '+', '.join(child['title'] for child in value['removed'])+' — 기존 결과와 수락 이력은 보존합니다.')
        lines.append(value['question']);return '\n'.join(lines)
    if state=='planned':
        return '\n'.join([title,value.get('goal',''),'대상: '+', '.join(value.get('scope',[])),
            '확인할 것: '+', '.join(value.get('checks',[])),
            *(['제외: '+', '.join(value['excludes'])] if value.get('excludes') else []),
            value.get('question','이 범위로 진행할까요?')])
    if state=='approved':return '이 범위로 진행하겠습니다. 검사가 끝나면 검토할 결과를 보여드리겠습니다.'
    if state=='active':
        context=value.get('rework')
        if not context:return '작업을 진행할 수 있습니다. 수정과 검사가 끝나면 결과를 제출해 주세요.'
        lines=[title+' — 수정 중입니다.','승인한 수정: '+context['approved_request']]
        differences=context.get('differences',{})
        if differences.get('items'):lines.append('마지막 제출 뒤 바뀐 파일: '+', '.join(i['path'] for i in differences['items']))
        diagnostic=context.get('submission_check',{})
        if diagnostic.get('status')=='blocked':
            lines.append(diagnostic['reason'])
            lines.extend(_diagnostic_item(i) for i in diagnostic.get('items',[]))
            if diagnostic.get('omitted'):lines.append('그 밖에 '+str(diagnostic['omitted'])+'개가 더 있습니다.')
        elif diagnostic.get('status')=='unavailable':lines.append('현재 변경 대조를 완료하지 못했습니다.')
        lines.append(context['next_action']);return '\n'.join(lines)
    if state=='review':
        lines=[title+' — 검토할 결과가 준비됐습니다.']
        if value.get('summary'):lines.append(value['summary'])
        if value.get('files'):lines.append('확인할 파일: '+', '.join(value['files']))
        unresolved=[c['name'] for c in value.get('checks',[]) if c['status']!='passed']
        if unresolved:lines.append('확인이 남은 항목: '+', '.join(unresolved))
        if value.get('current_matches') is False:lines.append('검토 후 파일이 바뀌었습니다. 바뀐 내용을 먼저 확인해 주세요.')
        elif value.get('current_matches') is None:lines.append('현재 파일을 확인하지 못했습니다. 기록된 결과와 파일 상태를 대조한 뒤 결정해 주세요.')
        else:lines.append(value.get('question','이대로 마무리할까요, 아니면 고칠 부분이 있을까요?'))
        return '\n'.join(lines)
    if state=='completed':
        lines=[title+' 작업을 수락한 내용으로 마무리했습니다.']
        if value.get('current_matches') is False:lines.append('그 뒤 파일이 바뀌었습니다. 수락한 내용은 기록에서 다시 볼 수 있습니다.')
        elif value.get('current_matches') is None:lines.append('수락 기록은 보존돼 있습니다. 현재 파일은 확인하지 못했습니다.')
        return '\n'.join(lines)
    if 'operation' in value and 'recorded' in value:return value['message']
    if 'before' in value and 'after' in value:
        lines=[value['title']+' — '+value['path']]
        for key,label in (('before','작업 전'),('after','제출한 내용')):
            body=value[key];lines.append(label+':')
            lines.append('파일 없음' if not body['exists'] else body['text'] if body['text'] is not None else '본문을 보존했습니다. 이 화면에서는 크기 또는 파일 형식 때문에 표시하지 않습니다.')
        return '\n'.join(lines)
    if 'items' in value:
        lines=[item.get('title',item.get('work',item.get('candidate','항목')))+' — '+item.get('state','') for item in value['items']]
        if value.get('next') is not None:lines.append('더 있습니다. 다음 목록을 요청해 주세요.')
        return '\n'.join(lines) or '등록된 항목이 없습니다.'
    if 'choice' in value:
        return {'none':'후속 작업은 없는 것으로 기록했습니다.','undecided':'후속 작업은 아직 정하지 않았습니다.',
                'candidate':'후속 후보를 기록했습니다. 아직 시작하지 않았습니다.','work':'이어갈 작업을 기록했습니다. 실행 승인을 대신하지 않습니다.'}[value['choice']]
    if 'candidate' in value:return value['title']+' 후보를 기록했습니다. 아직 시작하지 않았습니다.'
    if 'enabled' in value:
        names={'official-execution':'문서 작업 실행'}
        selected=', '.join(names.get(name,name) for name in value['enabled'])
        message='선택 기능: '+selected if selected else '선택 실행 기능이 꺼져 있습니다.'
        return message+'\n'+(value['question'] if 'question' in value else '기존 작업 기록과 결과는 계속 확인할 수 있습니다.')
    if value.get('published') is True and 'manifest' in value:
        return '백업 파일을 저장하고 다시 읽어 확인했습니다.\n파일: '+value['destination']+('' if value['receipt_saved'] else '\n백업은 저장됐지만 마지막 백업 정보는 기록하지 못했습니다.')
    if 'verified_export_recorded' in value:
        if not value['verified_export_recorded']:return '아직 확인된 백업 기록이 없습니다.'
        return '마지막으로 확인한 백업 기록이 있습니다.'+(' 그 뒤 기록이 바뀌었습니다.' if value.get('different_root') else '')+'\n백업 파일이 지금도 보관돼 있는지는 별도로 확인해 주세요.'
    return json.dumps(value,ensure_ascii=False,indent=2)


MESSAGES={
 'attribution-limit':'다른 작업의 추가 파일을 한 번에 대조할 수 있는 한도를 넘었습니다. 수정본과 기록은 보존돼 있습니다. 파일을 무시하거나 기록을 지우지 말고 작업 범위를 점검해 주세요.',
 'attribution-policy-changed':'파일을 포함하거나 제외하는 정책이 달라 추가 파일을 안전하게 구분하지 못했습니다. 정책 변경과 수정본을 보존한 채 변경 이유를 확인해 주세요.',
 'attribution-peer-changed':'대조 중에 다른 작업의 상태가 바뀌어 제출하지 않았습니다. 현재 작업과 해당 작업의 최신 상태부터 확인해 주세요.',
 'attribution-heads-changed':'다른 작업의 제출 근거를 읽는 중 작업 상태가 바뀌었습니다. 현재 상태부터 다시 확인해 주세요.',

 'check-report-mismatch':'계획과 검사 결과의 항목 이름 또는 개수가 맞지 않습니다. 제출 중이라면 작업 계획과 누락·추가·중복 항목을 대조하고, 실패·미실행 검사도 그대로 남겨 주세요. 제출이 아닌 조회·수락 등에서 발생했다면 기록을 수정하지 말고 진단을 요청해 주세요.',
 'document-assets-inspection-failed':'문서 실행 파일을 확인하지 못했습니다. 설치본 진단이 필요합니다. 실행이나 기록 변경은 하지 않았습니다.',
 'document-assets-invalid':'문서 실행 파일 구성이 올바르지 않습니다. 설치본 점검이 필요합니다. 실행이나 기록 변경은 하지 않았습니다.',
 'document-assets-changed':'문서 실행 파일이 없어졌거나 바뀌었습니다. 설치본 점검이 필요합니다. 실행이나 기록 변경은 하지 않았습니다.',
 'document-assets-platform':'문서 실행 파일이 이 플랫폼과 맞지 않습니다. 실행이나 기록 변경은 하지 않았습니다.',
 'result-not-awaiting-review':'이 작업은 지금 결과 검토를 기다리는 상태가 아닙니다. 작업 현황에서 진행 중인지 이미 마무리됐는지 확인해 주세요.',
 'selected-partial-staging-conflict':'같은 파일에 별도로 staging한 내용이 있습니다. 그 내용을 보존하려고 멈췄습니다. 어느 변경을 Git에 기록할지 먼저 정해 주세요.',
 'git-hooks-require-manual-integration':'이 저장소는 Git hook을 사용합니다. hook을 건너뛰지 않고 직접 커밋하는 경로로 이어가겠습니다. 현재 staging 내용을 먼저 확인해 주세요.',
 'git-child-outcome-unknown':'Git 처리의 종료를 확인하지 못했습니다. 같은 명령을 반복하지 말고 중단 기록과 현재 Git 상태를 확인해 주세요.',
 'git-integration-context-changed':'검토 후 Git 상태나 파일이 바뀌었습니다. 기존 변경을 보존하고 현재 차이부터 확인해 주세요.',
 'wsl-native-interop-unqualified':'이 경로는 아직 검증되지 않았습니다. Windows PowerShell이나 Windows 데스크톱 앱에서 같은 프로젝트를 열어 주세요.',
 'git-integration-platform-unavailable':'이 플랫폼의 Git 자동 반영은 아직 연결되지 않았습니다. 수락한 결과는 보존되며 Git 반영은 별도로 진행할 수 있습니다.',
 'git-index-lock-unrecorded':'중단 당시 Git 잠금의 소유 정보를 확정하지 못했습니다. index.lock을 지우거나 commit하지 말고, 보존한 중단 기록과 Git 상태의 점검을 요청해 주세요.',
 'git-index-lock-not-owned':'다른 실행이 사용하는지 확인할 수 없는 Git 잠금이 있습니다. index.lock을 지우거나 commit하지 말고 중단 기록을 먼저 점검해 주세요.',
 'feature-not-enabled':'이 프로젝트에서는 문서 실행 기능이 꺼져 있습니다. 필요한 경우 기능 설정을 먼저 확인해 주세요.',
 'configuration-preview-changed':'기능 설정이 그 뒤 바뀌었습니다. 현재 설정을 확인한 뒤 다시 결정해 주세요.',
 'runtime-entry-selection-changed':'실행환경이 갱신됐습니다. 같은 Colvia 실행기로 새 명령을 시작해 주세요.',
 'runtime-selection-changed':'실행환경이 갱신됐습니다. 진행 상태를 새 명령에서 확인해 주세요.',
 'dedicated-runtime-mismatch':'Colvia 전용 실행환경과 현재 실행기가 맞지 않습니다. Python 설정 대신 설치된 Colvia 실행기를 사용해 주세요.',
 'workspace-registration-required':'같은 프로젝트의 새 작업 폴더입니다. 첫 작업을 시작하면 이 폴더의 기록을 연결합니다. 아직 다른 폴더의 상태를 이곳의 상태로 판단하지 않습니다.',
 'managed-git-changed':'등록된 Git 도구가 바뀌었습니다. 관리 도구에서 실행 경로를 다시 확인해 주세요.',
 'runtime-feature-unavailable':'이 실행환경에서는 해당 선택 기능을 사용할 수 없습니다.',
 'backup-destination-exists':'같은 이름의 파일이 있습니다. 기존 백업은 보존하고 다른 저장 위치를 지정해 주세요.',
 'update-trust-verification-failed':'배포 파일의 서명이나 무결성을 확인하지 못해 중단했습니다. 기록은 지우지 않았습니다. 배포 안내를 확인해 주세요.',
 'update-download-failed':'배포 파일을 받지 못했습니다. 네트워크와 배포 주소를 확인해 주세요.',
 'update-trust-repair-required':'갱신을 확인할 정보가 없습니다. 기존 기록을 보존한 채 관리 도구 복구가 필요합니다.',
 'runtime-repair-required':'선택된 실행환경을 확인할 수 없습니다. Python 설정을 바꾸기보다 관리 도구 복구를 진행해 주세요.',

 'effect-busy':'다른 처리가 파일 적용 상태를 확인하고 있습니다. 잠시 뒤 현황을 확인해 주세요.',
 'external-effect-pending':'중단되거나 진행 중인 파일 적용을 먼저 확인해야 합니다. 기록과 파일은 보존돼 있으며, 상태 조회로 이어갈 수 있습니다.',
 'effect-outcome-unknown':'파일 적용의 완료 여부를 확정하지 못했습니다. 원본과 준비한 결과를 보존하고 중단 상태를 유지합니다. 상태를 먼저 확인해 주세요.',
 'effect-path-unknown':'적용 중 확인했던 파일과 현재 내용이 다릅니다. 양쪽 파일을 보존한 채 차이를 확인해 주세요. 자동으로 덮어쓰거나 되돌리지 않습니다.',
 'worker-outside-scope-change':'적용 범위 밖 파일도 바뀌었습니다. 원래 적용 조건을 다시 확인할 때까지 중단 상태를 유지합니다.',
 'effect-destination-occupied':'적용할 위치에 다른 파일이 생겼습니다. 기존 파일과 준비한 결과를 모두 보존했습니다. 어느 내용을 남길지 먼저 확인해 주세요.',
 'effect-staging-already-exists':'이 적용 요청의 준비 파일이 이미 있습니다. 기존 자료는 보존합니다. 적용 현황을 확인하고, 시작되지 않은 요청이면 새 적용 요청을 준비해 주세요.',
 'worker-policy-edit-unsupported':'파일 관측 규칙을 바꾸는 .gitignore 수정은 이 자동 적용 경로에서 지원하지 않습니다. 규칙 변경을 별도로 검토한 뒤 나머지 결과를 준비해 주세요.',
 'worker-source-files-changed':'수락 전 원본 결과가 바뀌어 적용을 멈췄습니다. 적용 현황에서 바뀐 부분을 확인해 주세요.',
 'effect-ancestor-changed':'대상 파일의 상위 폴더가 바뀌었습니다. 현재 파일과 보존 원본을 유지한 채 적용 현황을 확인해 주세요.',
 'effect-staged-file-missing':'적용할 사본이 없어 이어갈 수 없습니다. 원본이 그대로라면 적용 요청을 취소할 수 있습니다.',
 'effect-evacuated-file-changed':'보존한 원본에 추가 편집이 확인됐습니다. 추가 내용을 잃지 않도록 적용을 멈추고 파일을 보존했습니다.',
 'effect-evacuated-file-missing':'중단 복구에 필요한 원본 파일을 찾지 못했습니다. 자동으로 재생성하거나 적용을 완료하지 않습니다.',
 'worker-destination-baseline-changed':'대상 폴더의 시작 내용이 이 결과의 기준과 다릅니다. 현재 파일을 보존하고 두 작업의 기준부터 맞춰야 합니다.',
 'worker-destination-has-active-work':'대상 폴더에서 다른 작업이 진행 중이거나 검토를 기다리고 있습니다. 그 작업을 먼저 확인해 주세요.',
 'worker-source-selection-changed':'적용 대상으로 확인했던 결과의 상태가 바뀌었습니다. 최신 결과를 다시 확인해 주세요.',
 'worker-policy-context-mismatch':'두 작업 폴더의 파일 관측 규칙이 다릅니다. 설정을 확인하기 전에는 결과를 자동 적용할 수 없습니다.',
 'worker-cancel-requires-all-pre':'이미 적용된 부분이 있어 단순 취소할 수 없습니다. 현재 파일을 보존하고 중단된 적용의 상태부터 확인해 주세요.',
 'effect-writer-unavailable':'이 환경에는 검증된 파일 적용 경로가 없습니다. 결과 검토는 가능하지만 자동 적용은 진행하지 않습니다.',
 'effect-filesystem-unqualified':'이 파일시스템의 안전한 적용 동작은 아직 확인되지 않았습니다. 자동 적용을 시작하거나 이어가지 않습니다.',
 'effect-staging-volume-mismatch':'원본을 안전하게 보존할 공간이 대상 폴더와 같은 볼륨에 필요합니다. 현재 구성에서는 자동 적용하지 않습니다.',
 'composition-required-child-missing':'아직 수락되지 않았거나 다시 연결해야 할 하위 결과가 있습니다. 하위 작업 현황을 먼저 확인해 주세요.',
 'composition-child-changed':'연결한 하위 결과가 바뀌었습니다. 통합 결과를 수락하기 전에 변경된 하위 결과를 다시 확인해 주세요.',
 'composition-rebind-required':'통합 관계가 있는 계획입니다. 하위 결과를 명시적으로 다시 연결하고 새 계획을 확인해 주세요.',
 'composition-report-required':'통합 결과를 설명할 문서가 아직 없습니다. 합의한 문서를 작성해 함께 제출해 주세요.',
 'composition-integration-check-failed':'통합 검사 중 통과하지 못한 항목이 있습니다. 해당 결과를 확인한 뒤 제출해 주세요.',
 'stale-composition-rebind-receipt':'하위 작업 현황이 바뀌었습니다. 현재 결과를 다시 확인한 뒤 연결해 주세요.',
 'delivery-prepared-files-changed':'제출을 준비한 뒤 파일이 바뀌었습니다. 현재 변경을 확인한 뒤 새 제출 요청을 준비해 주세요.',
 'delivery-dependency-changed':'맡긴 작업의 기준이 바뀌었습니다. 현재 작업 상태를 확인해 주세요.',
 'delivery-deadline':'요청한 기한이 지났습니다. 남은 작업 상태를 확인한 뒤 다시 범위를 정해 주세요.',
 'delivery-cancelled':'중단 요청이 있어 다음 단계를 시작하지 않았습니다.',
 'notice-emission-already-attempted':'이미 알림을 시도한 결과입니다. 다시 보내지 않고 기존 결과를 확인합니다.',
 'execution-qualified-runtime-required':'이 소스 경로에는 검증된 실행환경이 아직 연결되지 않았습니다. 설치본 검증 후 사용할 수 있습니다.',
 'invalid-command-input':'입력한 경로나 옵션 형식을 확인해 주세요. 작업 상태는 상태 조회로 확인할 수 있습니다.',
 'invalid-git-tree':'Git 파일 목록을 해석할 수 없습니다. Git 상태를 확인한 뒤 이어가 주세요.',
 'invalid-scope':'수정할 파일을 중복 없이 한 번씩 지정해 주세요.',
 'boundary-swallows-protected':'다른 작업 폴더나 관리 영역 안의 파일은 이 작업에서 수정할 수 없습니다. 해당 작업 폴더에서 시작해 주세요.',
 'work-not-found':'이 작업을 찾지 못했습니다. 작업 목록에서 제목을 확인해 주세요.',
 'access-denied':'파일 또는 폴더 접근이 차단돼 진행을 멈췄습니다. 차단된 경로와 필요한 접근 권한(읽기·쓰기·실행)을 확인해 주세요. 변경 요청 중이었다면 다시 실행하기 전에 현재 상태를 확인해 주세요.',
 'list-changed-or-invalid-cursor':'목록이 바뀌었거나 이어보기 정보가 맞지 않습니다. 목록을 다시 열어 주세요.',
 'list-changed':'목록을 읽는 동안 상태가 바뀌었습니다. 목록을 다시 열어 주세요.',
 'stale-plan-receipt':'계획이 바뀌었습니다. 현재 계획을 확인한 뒤 진행해 주세요.',
 'stale-result-receipt':'검토 대상이 바뀌었습니다. 현재 결과를 확인한 뒤 결정해 주세요.',
 'reviewed-files-changed':'검토 후 파일이 바뀌었습니다. 바뀐 부분을 확인한 뒤 수락해 주세요.',
 'attributed-result-not-supported':'이 수정본의 다른 작업 추가 파일 근거는 현재 다른 폴더 적용에서 지원하지 않습니다. 같은 폴더의 검토·수락·본문 조회는 가능합니다.',
 'attribution-checks-required':'다른 작업의 추가 파일을 대조한 수정본은 계획한 검사를 모두 통과해야 제출할 수 있습니다. 실패하거나 확인하지 못한 검사를 통과로 적지 마세요. 수정본은 보존하고 남은 검사나 범위 결정을 확인해 주세요.',
 'plan-not-awaiting-approval':'이미 계획 승인 단계를 지난 작업입니다. 작업 현황에서 승인한 범위와 검사 항목을 확인해 주세요.',
 'attribution-discovery-limit':'다른 작업의 추가 파일을 자동 대조하는 고정 한도를 넘었습니다. 수정본과 기록은 보존됩니다. 이번 예외로는 계속 제출할 수 없으며, 일반 외부 변경 복구는 아직 지원하지 않습니다.',
 'outside-scope-change':'맡긴 범위 밖 파일도 바뀌었습니다. 다른 작업의 변경인지 먼저 확인해 주세요. 현재 결과를 보존하고 새 기준의 작업으로 이어갈 수 있습니다.',
 'plan-baseline-changed':'계획을 확인한 뒤 프로젝트 내용이 바뀌었습니다. 변경 내용을 반영한 계획이 필요합니다.',
 'opaque-edit-not-supported':'이 작업에는 링크나 submodule 내부 편집을 포함할 수 없습니다. 일반 파일로 범위를 정해 주세요.',
 'wrong-workspace':'이 결과는 다른 작업 폴더에서 만들어졌습니다. 해당 작업 폴더에서 이어가 주세요.',
 'update-space-insufficient':'갱신에 필요한 공간이 부족합니다. 대상 볼륨의 공간을 확보해 주세요.',
 'package-space-unavailable':'배포 파일을 풀 공간이 부족합니다. 대상 볼륨의 공간을 확보해 주세요.',
 'update-space-query-unavailable':'대상 볼륨의 남은 공간을 확인하지 못했습니다. 볼륨과 접근 권한을 확인해 주세요.',
 'update-disk-full':'파일을 저장하던 중 대상 볼륨의 공간이 부족해 중단했습니다. 실행 상태를 먼저 확인해 주세요.',
 'git-prerequisite-required':'Git 저장소를 연결하려면 Colvia 관리 도구에 Git을 등록해 주세요. Git이 설치되어 있다면 사용하려는 실행 파일의 절대 경로로 git-register-preview를 먼저 실행하세요.',
 'managed-git-changed':'등록한 Git 실행 파일이나 버전이 바뀌었습니다. 새 실행 파일을 확인하고 Colvia 관리 도구에서 다시 등록해 주세요.',
 'git-registration-review-changed':'Git 등록을 미리 본 뒤 실행 파일이나 설치 상태가 달라졌거나 확인 시간이 지났습니다. 현재 상태에서 새 미리보기를 확인해 주세요.',
 'git-registration-outcome-unknown':'Git 등록을 저장한 결과를 확정하지 못했습니다. 같은 적용을 반복하기 전에 현재 등록과 새 미리보기를 확인해 주세요.',
 'git-registration-replacement-required':'이미 등록된 Git이 있습니다. 이전 등록을 교체할지 확인하고 git-register의 --replace 옵션으로 적용해 주세요.',
 'store-busy':'다른 기록 처리가 진행 중입니다. 잠시 뒤 상태를 확인해 주세요.',
 'store-outcome-unknown':'처리 결과를 확정하지 못했습니다. 같은 요청을 반복하기 전에 실행 기록을 확인해 주세요.',
 'recovery-required':'중단된 기록 저장을 복구해야 합니다. 복구 안내를 확인해 주세요.',
}


def failure(code):
    recovery={
        'connect-project-overlap':'기존 Colvia 연결과 작업 영역 또는 Git 저장소가 겹칩니다. 기존 연결을 사용하거나 다른 폴더를 선택해 주세요.',
        'rebind-project-overlap':'복원 대상의 작업 영역 또는 Git 저장소에 기존 Colvia 연결이 있습니다. 겹치지 않는 폴더에서 새 복원 연결 미리보기를 확인해 주세요.',
        'connect-resume-project-overlap':'중단된 연결이 다른 Colvia 연결과 충돌합니다. 기존 연결을 확인하고 충돌을 해소한 뒤 이 연결을 재개해 주세요.',
        'connect-ancestor-marker':'상위 폴더에 Colvia 연결 정보가 있습니다. 상위 연결 상태를 확인하거나 겹치지 않는 폴더를 선택해 주세요.',
        'connect-boundary-unavailable':'기존 연결의 폴더 범위를 확인하지 못했습니다. 연결 상태와 폴더 접근을 확인한 뒤 다시 진행해 주세요.',
        'connect-reservation-changed':'중단된 연결의 대상이 기존 기록과 일치하지 않습니다. 현재 연결 상태를 확인해 주세요.',
        'store-io-unavailable':'기록 저장소를 읽거나 쓰는 중 오류가 발생했습니다. 원인은 아직 확정되지 않았습니다. 같은 작업을 반복하기 전에 현재 Work 상태와 진단 코드를 확인해 주세요.',
        'initial-publication-extra-path':'이 설치가 만든 것으로 확인할 수 없는 파일이 있습니다. 파일은 보존했으니 설치 상태와 현재 폴더를 확인해 주세요.',
        'initial-quarantine-unknown':'격리 중인 파일의 위치를 확정하지 못했습니다. 파일을 보존했으니 진단 후 같은 작업을 재개해 주세요.',
        'initial-quarantine-file-changed':'격리 대상이나 보존한 파일이 바뀌었습니다. 자동으로 덮거나 삭제하지 않았습니다.',
        'initial-quarantine-started':'이 설치의 파일 격리가 진행 중입니다. 설치 상태를 확인하고 같은 격리 작업을 재개해 주세요. 다른 설치는 시작하지 않았습니다.',
        'initial-quarantine-extra-path':'설치가 만들었다고 확인할 수 없는 파일이 있습니다. 파일을 보존했으니 격리 대상과 현재 폴더를 확인해 주세요.',
        'initial-quarantine-foreign-state':'이 첫 설치에 속하지 않는 실행기 또는 알림 등록 기록이 있습니다. 자동으로 정리하지 않았습니다.',
        'initial-publication-unknown':'설치 파일의 게시 상태를 확정하지 못했습니다. 기존 파일을 보존한 채 설치 상태를 확인해 주세요.',
        'initial-quarantine-review-changed':'확인한 격리 대상과 현재 파일이 달라졌습니다. 새 미리보기를 확인해 주세요.',
        'initial-install-recovery-required':'이전 설치가 중단됐습니다. 설치 상태 조회로 최근 시도와 준비 상태를 확인한 뒤 재시도 또는 재개해 주세요. 기존 파일은 보존했습니다.',
        'installation-attempt-superseded':'이 설치 시도는 이미 다른 시도로 이어졌습니다. 설치 상태 조회에서 최근 시도를 확인해 주세요.',
        'initial-attempt-not-current':'이 설치 시도는 이미 다른 시도로 이어졌습니다. 가장 최근 시도의 상태를 확인해 주세요.',
        'initial-retry-use-resume':'설치 파일 준비가 끝난 상태입니다. 새로 받지 말고 준비된 설치를 재개해 주세요.',
        'initial-retry-live-effects':'이미 일부 설치 파일이 있습니다. 같은 설치를 재개하거나, 원래 배포본을 사용할 수 없다면 격리 미리보기를 확인해 주세요.',
        'update-preparation-expired':'배포 정보의 유효기간이 지났습니다. 같은 파일을 다시 인증한 뒤 재개하거나, 중단된 갱신 파일을 이전 상태로 복구할 수 있습니다.',
        'renewal-target-changed':'새 배포 정보가 원래 준비한 파일과 다릅니다. 기존 준비본과 실패 기록을 보존하고 중단했습니다.',
        'release-rollback-started':'이 갱신은 이전 파일로 복구 중이거나 복구됐습니다. 기존 갱신 요청은 재사용하지 않습니다.',
        'rollback-runtime-selection-changed':'실행기 선택이 바뀌어 이 복구를 진행할 수 없습니다. 현재 실행기의 상태를 먼저 확인해 주세요.',
        'lifecycle-directory-publication-unconfirmed':'설치 폴더의 게시 결과를 확정하지 못했습니다. 남아 있는 폴더를 삭제하지 말고 상태를 확인해 주세요.'}
    if code in recovery:return recovery[code]
    if code.startswith(('gitlink-','uninitialized-gitlink-','nested-gitlink-')):
        return 'submodule의 상태가 바뀌었거나 이 방식으로 확인할 수 없습니다. 현재 변경은 보존하고 submodule 상태를 먼저 확인해 주세요.'
    return MESSAGES.get(code,'현재 상태를 확인하지 못해 진행을 멈췄습니다. 진단 정보에서 원인과 다음 조치를 확인해 주세요.')
