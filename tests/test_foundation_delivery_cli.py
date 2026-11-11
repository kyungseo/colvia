"""Source process entry and actual local lock, no installed app or OS notice."""
import sys,unittest
from colvia.presentation import human
from test_foundation_cli import CLITests

@unittest.skipUnless(sys.platform=='darwin','native source lock')
class DeliveryCLITests(unittest.TestCase):
    setUp=CLITests.setUp;tearDown=CLITests.tearDown;call=CLITests.call;plan=CLITests.plan
    def test_fresh_process_delivery_and_original_result_view(self):
        plan=self.plan();self.call('ordinary','approve','report','--receipt',plan['receipt'],'--statement','진행해')
        self.call('ordinary','start','report');(self.root/'report.md').write_text('# 보고서\n문의 비교\n')
        prepared=self.call('delivery','prepare','report-ready','--work','report','--step','submit','--seconds','600',
            '--summary','회의용 보고서','--passed','원본 보존::변경 없음','--passed','집계 대조::5건 대조',
            '--receiver','synthetic-receiver','--receiver-version','1')
        shown=self.call('delivery','preview','report-ready',machine=False)
        for internal in ('receipt','sha256','SKILL.md',str(self.home)):self.assertNotIn(internal,shown)
        self.assertIn('회의 보고서',shown)
        self.call('delivery','start','report-ready','--receipt',prepared['receipt'],'--statement','제출과 알림 요청까지 진행')
        done=self.call('delivery','run','report-ready');self.assertEqual('finished',done['state'])
        self.assertEqual('review',self.call('ordinary','view','report')['state'])
        repeated=self.call('delivery','run','report-ready');self.assertEqual(done,repeated)
        details=self.call('delivery','details','report-ready');self.assertEqual('submitted',details['original']['kind'])
        self.assertFalse(details['click_accepts'])
        short=self.call('delivery','view','report-ready',machine=False);self.assertLess(len(short.splitlines()),3)
        self.assertIn('검토',short)
    def test_queued_cancellation_never_starts_submission(self):
        self.plan();prepared=self.call('delivery','prepare','status','--work','report','--step','inspect','--seconds','60')
        self.call('delivery','start','status','--receipt',prepared['receipt'],'--statement','현황 정리')
        cancelled=self.call('delivery','cancel','status','--statement','진행하지 마')
        self.assertEqual('cancelled',cancelled['state']);self.assertTrue(cancelled['cancel_requested'])
        self.assertEqual('planned',self.call('ordinary','view','report')['state'])
