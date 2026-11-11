"""Harmless native detail-reader children only; no app/registration/notification."""
import subprocess,sys,tempfile,unittest
from pathlib import Path

@unittest.skipUnless(sys.platform=='darwin','Darwin native reader')
class ReceiverReaderTests(unittest.TestCase):
    def test_stdout_eof_does_not_remove_deadline_and_success_is_preserved(self):
        with tempfile.TemporaryDirectory(prefix='receiver-reader-') as temporary:
            root=Path(temporary);source=Path(__file__).resolve().parents[1]/'distribution/notification/WorkWindow.m'
            harness=root/'reader.m'
            harness.write_text('#define main receiver_unused_main\n#include '+repr(str(source)).replace("'",'"')+'\n#undef main\n'+r'''
int main(int argc,const char **argv) {
 @autoreleasepool {
  NSTask *good=[NSTask new];good.executableURL=[NSURL fileURLWithPath:@"/bin/echo"];good.arguments=@[@"synthetic detail"];
  NSString *value=readDetailTask(good,2);
  if (![value isEqualToString:@"synthetic detail\n"]) return 1;
  NSTask *slow=[NSTask new];slow.executableURL=[NSURL fileURLWithPath:[NSString stringWithUTF8String:argv[1]]];
  slow.arguments=@[@"-I",@"-B",@"-c",@"import os,time;os.close(1);time.sleep(10)"];
  NSTimeInterval start=NSProcessInfo.processInfo.systemUptime;
  value=readDetailTask(slow,0.2);
  if (![value isEqualToString:missing] || NSProcessInfo.processInfo.systemUptime-start>2) return 2;
  NSTimeInterval end=NSProcessInfo.processInfo.systemUptime+2;
  while (slow.running && NSProcessInfo.processInfo.systemUptime<end) [NSThread sleepForTimeInterval:0.01];
  return slow.running ? 3 : 0;
 }
}
''')
            binary=root/'reader'
            built=subprocess.run(['/usr/bin/clang','-fobjc-arc','-framework','AppKit','-framework','UserNotifications',
                '-framework','CoreServices',str(harness),'-o',str(binary)],capture_output=True,timeout=30)
            self.assertEqual(0,built.returncode,built.stderr.decode())
            result=subprocess.run([str(binary),sys.executable],capture_output=True,timeout=8)
            self.assertEqual(0,result.returncode,result.stderr.decode())
