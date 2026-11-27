import io
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

from colvia.codec import RecordError
from colvia import group_owner_console as ui
from colvia.cli import command_readonly, main, parser


class LocalDecisionTests(unittest.TestCase):
    def test_cancel_and_separate_challenges(self):
        console = Mock()
        record = dict(head='first')
        reply = 'START-' + ui.digest(record)[:8]
        console.ask.return_value = ''
        self.assertFalse(ui.confirmed(console, 'START', record))
        console.ask.return_value = reply
        self.assertTrue(ui.confirmed(console, 'START', record))
        self.assertFalse(ui.confirmed(console, 'APPLY', record))
        self.assertFalse(ui.confirmed(console, 'START', dict(head='changed')))

    def test_untrusted_display_cannot_introduce_control_sequences(self):
        value = '한글\x1b[2J\r\n\u202e\u2066\x85\ud800'
        output = ui.rendered(value)
        self.assertIn('한글', output)
        for character in ('\x1b', '\r', '\u202e', '\u2066', '\x85', '\ud800'):
            self.assertNotIn(character, output)

    def test_select_uses_current_local_page(self):
        store, console = Mock(), Mock()
        console.ask.side_effect = ['N', '1']
        row = dict(kind='work-group', destination='here', member_count=2,
                   work_group='expected', title='Known locally', state='planned')
        with patch.object(ui, 'project_status', side_effect=[
            dict(items=[row | dict(destination='other')], next='cursor'),
            dict(items=[row], next=None),
        ]) as pages:
            self.assertEqual(ui.select_group(store, 'here', console), 'expected')
            self.assertEqual(pages.call_args.kwargs, dict(cursor='cursor'))

    def test_title_follows_registered_work_id(self):
        grouped = Mock()
        grouped.view.return_value = dict(head='h', state='planned', required_checks=['check'], members=[
            dict(work='a', title='Alpha'), dict(work='b', title='Beta')])
        plan = dict(group_head='h', target='dest', dispatch_receipt='receipt',
                    members=[dict(work=w, goal=w, source_path=w, scope=[w], plan=w) for w in ('b', 'a')])
        with patch.object(ui, 'dispatch_plan', return_value=plan):
            _, record = ui.prepare_plan(grouped, 'pair', {}, 'journal')
            console = Mock()
            ui.confirmed(console, 'START', record)
            console.show.assert_any_call('Work  "b"  "Beta"')
            console.show.assert_any_call('Work  "a"  "Alpha"')
            plan['members'][0]['work'] = 'other'
            with self.assertRaisesRegex(RecordError, 'group-worker-members-changed'):
                ui.prepare_plan(grouped, 'pair', {}, 'journal')

    def test_managed_cli_opens_the_workspace_and_exits_on_no_selection(self):
        import sys
        entry = Mock()
        entry.workspace.return_value = (Mock(), Mock(), Mock())
        with patch.object(sys, 'platform', 'win32'), patch('colvia.platforms.windows_owner_console.OwnerConsole'), patch.object(ui,'select_group',return_value=None):
            self.assertFalse(command_readonly(parser(managed=True).parse_args(['parallel'])))
            self.assertEqual(main(['parallel'], entry=entry), 0)
            self.assertEqual(entry.workspace.call_args.kwargs, {'readonly': False})

    def test_incomplete_group_reopen_only_displays(self):
        entry, group, console = Mock(), Mock(), Mock()
        group.view.return_value = dict(state='approved', member_count=2, accepted=0,
                                       members=[dict(work='a', state='review'), dict(work='b',state='active')])
        with patch.object(ui,'journal_location',return_value=Path('local')), patch.object(ui,'Dispatch') as dispatch:
            self.assertEqual(ui.inspect_or_run(entry,group,'pair',console)['accepted'], 0)
            dispatch.return_value.run.assert_not_called()
            dispatch.return_value.resume.assert_not_called()
            console.ask.assert_not_called()

    def test_final_review_rejects_replaced_submission(self):
        group = Mock()
        member = dict(work='one', submission={'sha256':'fixed'}, revision=2, files=[{'path':'f'}])
        view = dict(state='review',stale=False,checks=[dict(status='passed')],members=[member])
        with patch.object(ui,'content',return_value=dict(submission={'sha256':'changed'},revision=2)):
            with self.assertRaisesRegex(RecordError,'group-submission-changed'):
                ui.finish(group,'group',view,Mock())
        group.execute.assert_not_called()

    def test_final_decline_cannot_publish(self):
        group, console = Mock(), Mock()
        console.ask.return_value = ''
        with patch.object(ui,'review_record',return_value=dict(head='fixed')):
            self.assertEqual(ui.finish(group,'g',{},console),dict(state='review',accepted=0))
        group.execute.assert_not_called()

    def test_only_windows_managed_parser_offers_entry(self):
        import sys
        from contextlib import redirect_stderr
        with patch.object(sys, 'platform', 'win32'):
            self.assertEqual(parser(managed=True).parse_args(['parallel']).group, 'parallel')
            with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                parser(managed=True).parse_args(['parallel','--approve'])
        with patch.object(sys,'platform','darwin'), redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            parser(managed=True).parse_args(['parallel'])

