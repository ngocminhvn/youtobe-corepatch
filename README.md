# Youtobe Patched

**Youtobe Patched** builds **YouTube** and **YouTube Music** for CorePatch ROMs using upstream Morphe patches.

## Latest verified Stable targets (3 November 2026)

- Upstream Morphe patches: **v2.0.0**

| App | Stable / recommended | minSdk | Default patches |
|---|---:|---:|---:|
| YouTube | **21.30.216** | — | — |
| YouTube Music | **9.30.53** | — | — |

See **[SUPPORTED.md](SUPPORTED.md)** for the complete stable + experimental compatibility matrix.

## Build behavior

- Original package name is preserved.
- Original signing certificate identity is preserved for CorePatch ROMs.
- Original launcher icon is preserved.
- GmsCore support is disabled.
- Clone app is disabled.
- Spoof signature is disabled.
- Custom branding and app icon patches are disabled.
- **Disable Play Store updates** is explicitly enabled for both apps.
- The APK manifest `versionCode` is set to `2147483647`; Morphe patches app-side `PackageInfo` version reads to use the original code.
- Build validation fails if the update-blocking patch is not present in Morphe's applied-patches report.

For YouTube and YouTube Music, this keeps the stock Google Play Services sign-in path instead of redirecting to GmsCore.
The Play Store update-blocking patch is not effective when the app is installed using root mounting; it can also cause app-specific issues. Existing release APKs are unchanged until rebuilt.

## Release output

Each upstream Morphe patches version has one **Youtobe Patched Release** for YouTube and YouTube Music.
New patch versions trigger both Stable builds. Successful APKs are published independently, failed apps are retried later, and older releases are preserved.

APK filenames use Vietnam build date in `DDMMYY` format, with no `NeedCorePatch` suffix:

- `Youtobe-Patched-YouTube-<version>-patch-<patch>-DDMMYY.apk`
- `Youtobe-Patched-YouTube-Music-<version>-patch-<patch>-DDMMYY.apk`

For example: `Youtobe-Patched-YouTube-21.30.216-patch-2.0.0-031126.apk`.

The workflow checks Morphe's supported Stable targets once per day (09:13 Vietnam time).
A new Morphe patch version publishes successfully built Stable APKs. A newer supported
Stable app version updates only that app in the current release. Otherwise, it stops after the check.

## Status legend

- 🟢 **Stable** — recommended target.
- 🧪 **Experimental** — supported upstream, but not the recommended stable target.

[Morphe patches (upstream)](https://github.com/MorpheApp/morphe-patches/releases/tag/v2.0.0) · [GitHub Releases](../../releases)

> **Branding:** Youtobe Patched is the project/release name. Original package names, signing identity and launcher icons remain unchanged for CorePatch compatibility. Release tags `morphe-*` are preserved for version-history compatibility.
