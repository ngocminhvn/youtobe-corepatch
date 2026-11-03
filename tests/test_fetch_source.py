#!/usr/bin/env python3
"""Prevent APKMirror bundle variants from being selected for Morphe builds."""
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from fetch_source import detect_extension, select_release_variant  # noqa: E402


BASE = "https://www.apkmirror.com/apk/google-inc/youtube-music/youtube-music-9-30-53-release/"


def row(suffix: str, variant_type: str, attributes: str = "") -> str:
    return (
        '<div class="table-row headerFont">'
        f'<div><a href="{suffix}-android-apk-download/">9.30.53</a></div>'
        f'<div>{variant_type}</div><div>{attributes}</div>'
        '</div>'
    )


class FetchSourceTests(unittest.TestCase):
    def test_selects_standalone_after_bundle_first(self):
        page = (
            row("youtube-music-9-30-53-7", "BUNDLE", "arm64-v8a Android 12L+ 120-480dpi")
            + row("youtube-music-9-30-53-4", "APK", "arm64-v8a Android 8.0+ nodpi")
        )
        self.assertEqual(
            select_release_variant(page, BASE),
            BASE + "youtube-music-9-30-53-4-android-apk-download/",
        )

    def test_bundle_adjacent_to_apk_is_not_misclassified(self):
        page = (
            row("youtube-music-9-30-53-7", "BUNDLE", "universal")
            + row("youtube-music-9-30-53-4", "APK", "arm64-v8a nodpi")
            + row("youtube-music-9-30-53-3", "BUNDLE", "arm64-v8a")
        )
        self.assertIn("-4-android-apk-download", select_release_variant(page, BASE))

    def test_no_standalone_fails_closed(self):
        page = row("youtube-music-9-30-53-7", "BUNDLE", "arm64-v8a")
        with self.assertRaisesRegex(RuntimeError, "No confirmed standalone APK"):
            select_release_variant(page, BASE)

    def test_table_row_markup(self):
        page = (
            '<tr><td><a href="youtube-music-9-30-53-7-android-apk-download/">'
            '9.30.53</a></td><td>BUNDLE</td></tr>'
            '<tr><td><a href="youtube-music-9-30-53-4-android-apk-download/">'
            '9.30.53</a></td><td>APK arm64-v8a nodpi</td></tr>'
        )
        self.assertIn("-4-android-apk-download", select_release_variant(page, BASE))

    def test_inspects_zip_not_misleading_filename(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            standalone = root / "unknown.apkm"
            with zipfile.ZipFile(standalone, "w") as archive:
                archive.writestr("AndroidManifest.xml", b"binary manifest")
            self.assertEqual(detect_extension(standalone, "https://cdn/file.apkm"), ".apk")

            bundle = root / "fake.apk"
            with zipfile.ZipFile(bundle, "w") as archive:
                archive.writestr("base.apk", b"binary base")
            self.assertEqual(detect_extension(bundle, "https://cdn/file.apk"), ".apkm")


if __name__ == "__main__":
    unittest.main()
