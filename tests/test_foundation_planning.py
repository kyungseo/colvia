import unittest
from colvia.codec import RecordError
from colvia.planning import Planning,candidate_key,followup_key
from test_foundation_work import WorkFixture


class PlanningTests(WorkFixture,unittest.TestCase):
    def test_candidate_and_followup_do_not_start_work_or_accept_result(self):
        self.start();(self.root/'report.md').write_text('report');review=self.submit()
        planning=Planning(self.store)
        planning.save_candidate(operation='candidate',candidate='next',title='다음 보고서',reason='추가 자료를 비교한다')
        self.assertEqual('review',self.service.view('report')['state'])
        self.assertIsNone(planning.candidate('next')['linked_work'])
        self.assertFalse(planning.followup('report')['recorded'])
        planning.choose_followup(operation='choose',work='report',choice='candidate',target='next',statement='다음 후보로 남겨줘')
        self.assertEqual('review',self.service.view('report')['state'])
        self.assertEqual('candidate',planning.followup('report')['choice'])
        self.service.accept(operation='accept',work='report',receipt=review['receipt'],statement='수락')
        self.assertEqual('open',planning.candidate('next')['state'])

    def test_candidate_completion_is_derived_only_from_existing_exact_work_link(self):
        self.start();(self.root/'report.md').write_text('report');review=self.submit()
        planning=Planning(self.store)
        planning.save_candidate(operation='candidate',candidate='report-candidate',title='보고서 후보',reason='범위가 정해짐',work='report')
        self.assertEqual('review',planning.candidate('report-candidate')['linked_state'])
        self.service.accept(operation='accept',work='report',receipt=review['receipt'],statement='수락')
        self.assertEqual('completed',planning.candidate('report-candidate')['linked_state'])

    def test_explicit_none_and_undecided_stay_distinct_and_cas_protected(self):
        self.start();planning=Planning(self.store)
        self.assertFalse(planning.followup('report')['recorded'])
        planning.choose_followup(operation='none',work='report',choice='none',statement='후속 작업 없음')
        self.assertEqual('none',planning.followup('report')['choice'])
        with self.assertRaisesRegex(RecordError,'followup-changed'):
            planning.choose_followup(operation='stale',work='report',choice='undecided',statement='나중에 결정')
        planning.choose_followup(operation='undecided',work='report',choice='undecided',statement='나중에 결정',expected=self.store.head(followup_key('report')))
        self.assertTrue(planning.followup('report')['recorded']);self.assertEqual('undecided',planning.followup('report')['choice'])

    def test_paged_candidates_preserve_all_and_refuse_stale_cursor(self):
        planning=Planning(self.store)
        for n in range(5):planning.save_candidate(operation=f'op-{n}',candidate=f'c-{n}',title=f'후보 {n}',reason='검토 후보')
        first=planning.candidates(limit=2);second=planning.candidates(limit=2,cursor=first['next']);third=planning.candidates(limit=2,cursor=second['next'])
        self.assertEqual(5,len({v['candidate'] for page in (first,second,third) for v in page['items']}))
        self.assertIsNone(third['next'])
        planning.save_candidate(operation='new',candidate='new',title='새 후보',reason='추가')
        with self.assertRaisesRegex(RecordError,'list-changed-or-invalid-cursor'):planning.candidates(cursor=first['next'])

if __name__=='__main__':unittest.main()
