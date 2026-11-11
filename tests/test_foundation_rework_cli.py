"""New process reads approved rework and causal refusal without internal edits."""
import unittest
import test_foundation_cli as cli_fixture

class ReworkCLITests(unittest.TestCase):
    setUp=cli_fixture.CLITests.setUp
    tearDown=cli_fixture.CLITests.tearDown
    call=cli_fixture.CLITests.call
    plan=cli_fixture.CLITests.plan

    def setup_rework(self):
        for work in ('report','other'):
            plan=self.plan(work)
            self.call('ordinary','approve',work,'--receipt',plan['receipt'],'--statement','진행')
            self.call('ordinary','start',work);(self.root/(work+'.md')).write_text(work+' first')
            review=self.call('ordinary','submit',work,'--summary','초안','--passed','원본 보존::대조','--passed','집계 대조::대조')
            if work=='report':first=review
        self.call('ordinary','revise','report','--receipt',first['receipt'],'--statement','확인 날짜 한 줄 추가해줘. 제출까지 진행해.')
        (self.root/'report.md').write_text('report first\n확인 날짜: 회의에서 결정')

    def test_process_resume_refusal_and_corrected_submit_single_acceptance(self):
        self.setup_rework();(self.root/'unknown.md').write_text('outside')
        result=self.call('ordinary','view','report')
        self.assertEqual('active',result['state']);self.assertEqual(['원본 보존','집계 대조'],result['checks'])
        self.assertIn('확인 날짜',result['rework']['approved_request'])
        options=('ordinary','submit','report','--summary','확인 날짜 추가','--passed','원본 보존::대조','--passed','집계 대조::대조')
        refusal=self.call(*options,code=2);self.assertEqual('outside-scope-change',refusal['error'])
        self.assertEqual('unknown.md',refusal['details']['items'][0]['path'])
        human=self.call(*options,code=2,machine=False)
        self.assertIn('unknown.md',human);self.assertIn('추가',human);self.assertIn('보존',human)
        for private in ('sha256','receipt','SKILL.md',str(self.home),'baseline'):self.assertNotIn(private,human)
        (self.root/'unknown.md').unlink()
        review=self.call(*options);self.assertEqual('review',review['state'])
        self.assertEqual(['report.md'],review['files']);self.assertEqual('other.md',review['attribution']['items'][0]['path'])
        final=self.call('ordinary','accept','report','--receipt',review['receipt'],'--statement','마무리해',machine=False)
        self.assertIn('마무리했습니다',final);self.assertLess(len(final.splitlines()),4)
        self.assertEqual('other first',(self.root/'other.md').read_text())

if __name__=='__main__':unittest.main()
