"""Windows publication protocol double; native filesystem qualification pending."""
from contextlib import contextmanager
from pathlib import Path
import unittest
from colvia.codec import RecordError
from colvia.storage.windows import WindowsFiles,local_path

class API:
    def __init__(self):
        self.nodes={local_path('C:/user/stage'):[1,'directory',1]};self.moves=[];self.opened_count=0
    @contextmanager
    def ancestors(self,path):yield
    @contextmanager
    def opened(self,path,**kwargs):
        path=local_path(path)
        if path not in self.nodes:raise FileNotFoundError(path)
        self.opened_count+=1
        try:yield path
        finally:self.opened_count-=1
    def state(self,handle,path):return dict(directory=True,identity=tuple(self.nodes[handle]))
    def private(self,handle,**kwargs):pass
    def ok(self,value):return value
    def MoveFileExW(self,source,target,flags):
        assert self.opened_count==0 # All staging handles closed before publication.
        self.moves.append((source,target,flags))
        if target in self.nodes:raise FileExistsError(target)
        self.nodes[target]=self.nodes.pop(source);return True

class DirectoryPublicationTests(unittest.TestCase):
    def test_windows_no_replace_move_without_copy_and_closed_handles(self):
        api=API();files=WindowsFiles(api=api);sync=[];files.sync_directory=lambda path:sync.append(path)
        files.publish_directory(Path('C:/user/stage'),Path('C:/user/home'),[1,'directory',1])
        self.assertEqual([(local_path('C:/user/stage'),local_path('C:/user/home'),8)],api.moves)
        self.assertEqual([Path('C:/user')],sync)
    def test_windows_foreign_destination_and_changed_identity_refuse(self):
        api=API();files=WindowsFiles(api=api);files.sync_directory=lambda path:None
        with self.assertRaisesRegex(RecordError,'directory-changed'):
            files.publish_directory(Path('C:/user/stage'),Path('C:/user/home'),[1,'other',1])
        self.assertEqual([],api.moves)
        api.nodes[local_path('C:/user/home')]=[1,'foreign',1]
        with self.assertRaisesRegex(RecordError,'publication-unconfirmed'):
            files.publish_directory(Path('C:/user/stage'),Path('C:/user/home'),[1,'directory',1])
        self.assertEqual([1,'foreign',1],api.nodes[local_path('C:/user/home')])
        self.assertIn(local_path('C:/user/stage'),api.nodes)


class OwnedNodeWindowsProtocolTests(unittest.TestCase):
    def test_file_move_keeps_original_identity_without_replace_or_copy(self):
        from colvia.platforms import owned_install_files as nodes
        from unittest.mock import patch
        api=API();api.nodes[local_path('C:/user')]=[1,'parent',1]
        files=WindowsFiles(api=api);files.sync_directory=lambda p:None
        expected=dict(kind='file',identity=[1,'directory',1],mode='100644',size=3,sha256='synthetic')
        def capture(f,path):
            value=dict(expected);value['identity']=api.nodes[local_path(path)];return value
        with patch.object(nodes,'capture',side_effect=capture):
            nodes.move(files,Path('C:/user/stage'),Path('C:/user/retained'),expected)
        self.assertEqual(8,api.moves[0][2]);self.assertEqual([1,'directory',1],api.nodes[local_path('C:/user/retained')])
    def test_file_move_sharing_error_never_retries(self):
        from colvia.platforms import owned_install_files as nodes
        from unittest.mock import patch
        api=API();api.nodes[local_path('C:/user')]=[1,'parent',1]
        files=WindowsFiles(api=api);expected=dict(kind='file',identity=[1,'directory',1])
        with patch.object(nodes,'capture',return_value=expected),patch.object(api,'MoveFileExW',side_effect=PermissionError('sharing')) as move:
            with self.assertRaises(PermissionError):nodes.move(files,Path('C:/user/stage'),Path('C:/user/saved'),expected)
        self.assertEqual(1,move.call_count);self.assertIn(local_path('C:/user/stage'),api.nodes)
