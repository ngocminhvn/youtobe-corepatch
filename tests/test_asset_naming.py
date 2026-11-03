#!/usr/bin/env python3
"""Youtobe Patched naming regression tests."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from asset_naming import asset_name, current_asset


class AssetNamingTests(unittest.TestCase):
    def test_youtube(self):
        name = asset_name("youtube", "21.30.216", "2.0.0", "031126")
        self.assertEqual(name, "Youtobe-Patched-YouTube-21.30.216-patch-2.0.0-031126.apk")
        self.assertTrue(current_asset(name, "youtube", "21.30.216", "2.0.0"))

    def test_music(self):
        name = asset_name("youtube-music", "9.30.53", "2.0.0", "031126")
        self.assertEqual(name, "Youtobe-Patched-YouTube-Music-9.30.53-patch-2.0.0-031126.apk")
        self.assertTrue(current_asset(name, "youtube-music", "9.30.53", "2.0.0"))
        self.assertFalse(current_asset(name, "youtube", "9.30.53", "2.0.0"))

    def test_previous_brand_no_longer_current(self):
        self.assertFalse(current_asset(
            "YoutubeMusic-9.30.53-morphe-2.0.0-031126.apk",
            "youtube-music", "9.30.53", "2.0.0",
        ))

    def test_date_does_not_matter(self):
        self.assertTrue(current_asset(
            asset_name("youtube", "21.30.216", "2.0.0", "041126"),
            "youtube", "21.30.216", "2.0.0",
        ))

    def test_bad_date(self):
        with self.assertRaises(ValueError):
            asset_name("youtube", "21.30.216", "2.0.0", "0311")


if __name__ == "__main__":
    unittest.main()
