"""Source-only assets and linked resource checks; no installation or app launch."""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from tests.platform_fixtures import require_archived_agent_entries

ROOT = Path(__file__).resolve().parents[1]
BRAND = ROOT / "assets/brand"

def module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

class BrandPackagingTests(unittest.TestCase):
    def test_manifest_and_outlined_assets(self):
        manifest = json.loads((BRAND / "manifest.json").read_text())
        for name, expected in manifest["files"].items():
            raw = (BRAND / name).read_bytes()
            self.assertEqual(expected, {"sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}, name)
        for p in BRAND.glob("*.svg"):
            text = p.read_text()
            for forbidden in ("<text", "font-family", "@font-face", "/Users/", "Avenir"):
                self.assertNotIn(forbidden, text, p.name)
        for name in manifest["inputs"]:
            self.assertEqual(manifest["inputs"][name], hashlib.sha256((BRAND / "source" / name).read_bytes()).hexdigest())

    def test_native_icon_containers_and_regeneration(self):
        builder = module("brand_coff", "scripts/build-windows-icon.py")
        ico = (BRAND / "colvia.ico").read_bytes()
        self.assertEqual(len(builder.icon_images(ico)), 8)
        recorded = json.loads((ROOT / "distribution/windows/icon-resources.json").read_text())
        self.assertEqual(recorded["icon_sha256"], hashlib.sha256(ico).hexdigest())
        self.assertEqual(recorded["png_256_sha256"], hashlib.sha256((BRAND / "png/icon-256.png").read_bytes()).hexdigest())
        for name, expected in recorded["objects"].items():
            self.assertEqual(expected, hashlib.sha256((ROOT / "distribution/windows" / name).read_bytes()).hexdigest())
        for arch in builder.MACHINES:
            self.assertEqual(builder.resource_object(ico, arch), (ROOT / f"distribution/windows/rsrc_windows_{arch}.syso").read_bytes())
        bad = bytearray(ico); bad[6] = 15
        with self.assertRaises(ValueError): builder.icon_images(bad)
        with self.assertRaises(ValueError): builder.icon_images(ico + b"extra")
        raw = (BRAND / "colvia.icns").read_bytes()
        self.assertEqual(raw[:4], b"icns"); self.assertEqual(struct.unpack_from(">I",raw,4)[0], len(raw))
        pos=8; types=set()
        while pos < len(raw):
            kind=raw[pos:pos+4]; size=struct.unpack_from(">I",raw,pos+4)[0]
            self.assertNotIn(kind, types); types.add(kind); self.assertGreater(size, 8)
            self.assertEqual(raw[pos+8:pos+16], b"\x89PNG\r\n\x1a\n"); pos+=size
        self.assertEqual(pos,len(raw)); self.assertIn(b"ic10",types)

    def test_exact_managed_inventory_excludes_build_assets(self):
        require_archived_agent_entries(ROOT)
        from hv2ref import product
        expected = set(product.CONTINUATION_MANAGED_PATHS)
        from distribution.source_layout import read_checkout
        payload = read_checkout(ROOT)["payload"]
        self.assertNotEqual(payload["README.md"], (ROOT / "README.md").read_bytes())
        self.assertEqual(set(payload), expected)
        self.assertEqual(len(expected), 30)
        self.assertFalse(any(n.startswith(("assets/", "scripts/", "distribution/")) for n in payload))
        for name, raw in payload.items():
            self.assertNotIn(b"assets/brand", raw, name)

    @unittest.skipUnless(shutil.which("go"), "source cross-compilation requires Go")
    def test_linked_icons_in_both_windows_architectures(self):
        builder = module("brand_windows_builder", "scripts/build-windows-basic.py")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); archive = root / "python.zip"
            import zipfile
            with zipfile.ZipFile(archive, "w") as z: z.writestr("python.exe", b"synthetic compile-only input")
            raw = archive.read_bytes()
            targets = {arch: builder.PythonTarget(row.machine, len(raw), builder.digest(raw)) for arch,row in builder.TARGETS.items()}
            candidate = {"release_ref": {"inventory_id":"windows-2", "id":"compile-only"}, "payload":{"README.md":b"synthetic"}}
            env = {**os.environ, "GOTOOLCHAIN":"local", "GOENV":"off", "GOWORK":"off", "GOFLAGS":"", "GO111MODULE":"off", "GOPROXY":"off", "GOSUMDB":"off", "GOTELEMETRY":"off", "CGO_ENABLED":"0", "GOCACHE":str(root/"host-cache"), "GOTMPDIR":str(root/"host-temp")}
            for n in ("host-cache", "host-temp"): (root/n).mkdir()
            env.pop("GOOS",None);env.pop("GOARCH",None)
            inspect = root / "inspect"
            subprocess.run([shutil.which("go"),"build","-trimpath","-o",str(inspect),str(ROOT/"tests/fixtures/inspect_icon_pe.go")],env=env,check=True,capture_output=True,timeout=90)
            for arch in targets:
                with patch.object(builder,"TARGETS",targets),patch.object(builder,"workspace_candidate",return_value=candidate),contextlib.redirect_stdout(io.StringIO()):
                    builder.build(root/"unused",archive,root/arch,None,arch)
                catalog=json.loads((root/arch/"build/src/colvia.local/windows-bootstrap/catalog.json").read_text())
                with zipfile.ZipFile(root/arch/"build/src/colvia.local/windows-bootstrap/core.zip") as packaged:
                    png=packaged.read("notice-icon.png")
                    self.assertEqual(png,(BRAND/"png/icon-256.png").read_bytes())
                    digest=hashlib.sha256(png).hexdigest()
                    self.assertEqual(catalog["payload"]["notice-icon.png"],digest)
                    self.assertIn(('ICON_SHA256 = "'+digest+'"').encode(),packaged.read("notices.py"))
                    self.assertEqual(json.loads((root/arch/"build.json").read_text())["notice_icon_sha256"],digest)
                executable=(root/arch/"colvia-manage.exe").read_bytes()
                for private_root in (root, root.resolve(), Path(os.environ.get("HOME", str(root)))):
                    self.assertNotIn(str(private_root).encode(), executable)
                self.assertIn(b"path\tcolvia.local/windows-bootstrap\n", executable)
                build_info=(root/arch/"build/build-info.txt").read_text()
                self.assertNotIn("path\t_/", build_info)
                self.assertIn("-trimpath=true", build_info)
                self.assertIn("GOARCH="+arch, build_info)
                result=subprocess.run([str(inspect),str(root/arch/"colvia-manage.exe"),str(BRAND/"colvia.ico"),arch],capture_output=True,text=True,timeout=10)
                self.assertEqual(result.returncode,0,result.stderr)
