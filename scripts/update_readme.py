#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def stable_target(app: dict):
    versions = app.get("versions") or []
    stable = [v for v in versions if not v.get("experimental")]
    return stable[0] if stable else (versions[0] if versions else None)


def build_readme(data: dict) -> str:
    patches_tag = data.get("patchesTag", "unknown")
    release_url = data.get("releaseUrl", "https://github.com/MorpheApp/morphe-patches/releases")
    apps = data.get("apps") or {}

    rows = []
    for key in ("youtube", "youtube-music"):
        app = apps.get(key) or {}
        target = stable_target(app)
        if not target:
            continue
        rows.append(
            f"| {app.get('appName', key)} | **{target.get('version', '-')}** | "
            f"{target.get('minSdk') if target.get('minSdk') is not None else '-'} | "
            f"{target.get('defaultPatches', 0)}/{app.get('defaultPatches', 0)} |"
        )

    lines = [
        "# Youtobe Patched",
        "",
        "Youtobe Patched builds **YouTube** and **YouTube Music** for CorePatch ROMs using the upstream Morphe patch engine.",
        "",
        "## Current stable targets",
        "",
        f"- Morphe patches: **{patches_tag}**",
        "",
        "| App | Stable / recommended | minSdk | Default patches |",
        "|---|---:|---:|---:|",
        *rows,
        "",
        "See **[SUPPORTED.md](SUPPORTED.md)** for the complete stable + experimental compatibility matrix.",
        "",
        "## Build behavior",
        "",
        "- Original package name is preserved.",
        "- Original signing certificate identity is preserved for CorePatch ROMs.",
        "- Original launcher icon is preserved.",
        "- GmsCore support is disabled.",
        "- Clone app is disabled.",
        "- Spoof signature is disabled.",
        "- Custom branding and app icon patches are disabled.",
        "",
        "For YouTube and YouTube Music, this keeps the stock Google Play Services sign-in path instead of redirecting to GmsCore.",
        "",
        "## Release output",
        "",
        "Each upstream Morphe patches version has one Youtobe Patched Release for YouTube and YouTube Music.",
        "New upstream patches trigger both Stable builds. Successful APKs are published independently, and missing apps retry later. Older releases are preserved.",
        "",
        "APK filenames use Vietnam build date in `DDMMYY` format, with no `NeedCorePatch` suffix:",
        "",
        "- `Youtobe-Patched-YouTube-<version>-patch-<patch>-DDMMYY.apk`",
        "- `Youtobe-Patched-YouTube-Music-<version>-patch-<patch>-DDMMYY.apk`",
        "",
        "For example: `Youtobe-Patched-YouTube-21.30.216-patch-2.0.0-031126.apk`.",
        "",
        "The workflow checks Morphe's supported Stable targets once per day (09:13 Vietnam time).",
        "A new Morphe patch version publishes successfully built Stable APKs. A newer supported",
        "Stable app version updates only that app in the current release. Otherwise, it stops after the check.",
        "",
        "## Status legend",
        "",
        "- 🟢 **Stable** — recommended target.",
        "- 🧪 **Experimental** — supported upstream, but not the recommended stable target.",
        "",
        f"[Morphe patches release]({release_url}) · [GitHub Releases](../../releases)",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", required=True)
    ap.add_argument("--output", default="README.md")
    args = ap.parse_args()

    data = json.loads(Path(args.json).read_text(encoding="utf-8"))
    Path(args.output).write_text(build_readme(data), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
