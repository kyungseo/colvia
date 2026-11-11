"""Clock and process API doubles only: no OS child, signal, or installation."""
import signal,unittest
from types import SimpleNamespace
from unittest.mock import patch,Mock
from colvia.codec import RecordError
from colvia.platforms.darwin_processes import DarwinProcesses
from test_foundation_execution_history import BIRTH

class StopBudgetTests(unittest.TestCase):
    def test_term_has_absolute_half_budget_leaving_kill_phase(self):
        port=object.__new__(DarwinProcesses);now=[0.0];signals=[];budgets=[]
        process=SimpleNamespace(pid=9100,returncode=None,poll=lambda:process.returncode)
        known={9100:dict(birth=BIRTH)}
        def observe(p,k,*,seconds):
            budgets.append(seconds);now[0]+=min(3,seconds)
            if signals and signals[-1]==signal.SIGKILL:process.returncode=-9;return {}
            return {9100:dict(pgid=9100,ppid=1,birth=BIRTH)}
        with patch.object(port,'observe',side_effect=observe),patch('colvia.platforms.darwin_processes.time.monotonic',side_effect=lambda:now[0]),patch('colvia.platforms.darwin_processes.time.sleep',side_effect=lambda s:now.__setitem__(0,now[0]+s)),patch('colvia.platforms.darwin_processes.os.killpg',side_effect=lambda pid,sig:signals.append(sig)),patch('colvia.platforms.darwin_processes.group_absent',return_value=True):
            result=port.stop(process,known,seconds=8)
        self.assertEqual([signal.SIGTERM,signal.SIGKILL],signals);self.assertTrue(result['final_scan_confirmed']);self.assertLessEqual(now[0],8)
        self.assertLessEqual(budgets[0],2)
    def test_owned_abort_uses_only_live_handle_not_group_number(self):
        process=Mock();port=object.__new__(DarwinProcesses)
        with patch('colvia.platforms.darwin_processes.os.killpg') as group:port.abort_owned(process,seconds=2)
        process.kill.assert_called_once_with();process.wait.assert_called_once_with(timeout=2);group.assert_not_called()
    def test_invalid_argv_proves_no_child(self):
        port=object.__new__(DarwinProcesses)
        with patch('colvia.platforms.darwin_processes.subprocess.Popen') as popen,self.assertRaises(OSError):port.launch([],cwd='/',env={})
        popen.assert_not_called()

    def test_fixed_latency_scan_never_receives_a_term_tail_budget(self):
        port=object.__new__(DarwinProcesses);now=[0.0];signals=[];budgets=[]
        process=SimpleNamespace(pid=9100,returncode=None,poll=lambda:process.returncode);known={9100:dict(birth=BIRTH)}
        def observe(p,k,*,seconds):
            budgets.append(seconds)
            if seconds<.05:raise RecordError('process-timeout')
            now[0]+=.05
            if signals and signals[-1]==signal.SIGKILL:process.returncode=-9;return {}
            return {9100:dict(pgid=9100,ppid=1,birth=BIRTH)}
        with patch.object(port,'observe',side_effect=observe),patch('colvia.platforms.darwin_processes.time.monotonic',side_effect=lambda:now[0]),patch('colvia.platforms.darwin_processes.time.sleep',side_effect=lambda s:now.__setitem__(0,now[0]+s)),patch('colvia.platforms.darwin_processes.os.killpg',side_effect=lambda pid,sig:signals.append(sig)),patch('colvia.platforms.darwin_processes.group_absent',return_value=True):result=port.stop(process,known,seconds=1)
        self.assertEqual([signal.SIGTERM,signal.SIGKILL],signals);self.assertTrue(result['final_scan_confirmed']);self.assertGreaterEqual(min(budgets),.25)
