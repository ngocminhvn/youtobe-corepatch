#!/usr/bin/env python3
"""Regression tests for release asset cleanup (YouTube vs YouTube Music)."""
import hashlib
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PUBLISH = REPO / "scripts" / "publish_release.sh"

MOCK_GH = """#!/usr/bin/env python3
import json
import os
import sys

args = sys.argv[1:]
with open(os.environ["MOCK_GH_LOG"], "a", encoding="utf-8") as f:
    f.write(json.dumps(args) + "\\n")
if args[:2] == ["release", "view"] and "--json" in args:
    print("\\n".join(json.loads(os.environ["MOCK_ASSETS"])))
"""


class PublishReleaseTests(unittest.TestCase):
    def run_publish(self, app: str):
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            package_dir = work / "artifacts" / "verified"
            package_dir.mkdir(parents=True)
            bindir = work / "bin"
            bindir.mkdir()
            gh = bindir / "gh"
            gh.write_text(MOCK_GH, encoding="utf-8")
            gh.chmod(0o755)

            versions = {"youtube": "21.30.216", "youtube-music": "9.30.53"}
            prefixes = {
                "youtube": "YouTube",
                "youtube-music": "YouTube-Music",
            }
            other = "youtube-music" if app == "youtube" else "youtube"
            filename = f"{prefixes[app]}-{versions[app]}-patch-2.3.0-191126.apk"
            stale = f"{prefixes[app]}-{versions[app]}-patch-2.3.0-181126.apk"
            untouched = f"{prefixes[other]}-{versions[other]}-patch-2.3.0-181126.apk"

            content = b"verified test APK"
            (package_dir / filename).write_bytes(content)
            info = (
                f"APP_KEY={app}\n"
                f"APP_VERSION={versions[app]}\n"
                "MORPHE_PATCHES_TAG=v2.3.0\n"
                f"OUTPUT_APK={filename}\n"
                f"APK_SHA256={hashlib.sha256(content).hexdigest()}\n"
            )
            (package_dir / "build-info.env").write_text(info, encoding="utf-8")
            log = work / "gh_calls.jsonl"
            env = os.environ.copy()
            env.update({
                "PATH": f"{bindir}{os.pathsep}{env.get('PATH', '')}",
                "GH_TOKEN": "test",
                "GITHUB_REPOSITORY": "example/repo",
                "EXPECTED_APPS_JSON": json.dumps([app]),
                "EXPECTED_TARGETS_JSON": json.dumps(versions),
                "EXPECTED_PATCHES_TAG": "v2.3.0",
                "EXPECTED_RELEASE_TAG": "morphe-2.3.0",
                "RELEASE_MODE": "update_existing",
                "GITHUB_STEP_SUMMARY": str(work / "summary.md"),
                "MOCK_GH_LOG": str(log),
                "MOCK_ASSETS": json.dumps([filename, stale, untouched, "notes.txt"]),
            })
            completed = subprocess.run(
                ["bash", str(PUBLISH)], cwd=work, env=env,
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            calls = [json.loads(line) for line in log.read_text().splitlines()]
            deleted = [call[3] for call in calls if call[:2] == ["release", "delete-asset"]]
            uploaded = [call for call in calls if call[:2] == ["release", "upload"]]
            self.assertEqual(len(uploaded), 1)
            return deleted, stale, untouched

    def test_updating_youtube_does_not_delete_music(self):
        deleted, stale, untouched = self.run_publish("youtube")
        self.assertEqual(deleted, [stale])
        self.assertNotIn(untouched, deleted)

    def test_updating_music_does_not_delete_youtube(self):
        deleted, stale, untouched = self.run_publish("youtube-music")
        self.assertEqual(deleted, [stale])
        self.assertNotIn(untouched, deleted)


if __name__ == "__main__":
    unittest.main()
