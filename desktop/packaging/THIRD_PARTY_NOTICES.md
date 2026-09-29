# AutoTransAI desktop third-party components

This payload includes independently licensed software. Actual file hashes are in
`payload-sha256.json`; pinned download provenance is in `vendor-lock.json`;
`vendor-binaries.json` records extracted tool hashes. Python and npm inventories
record installed versions, project metadata and license files. Retain all notices
when redistributing. Build tooling is listed separately in the Python inventory;
being installed in the build environment does not imply inclusion in the app.

- FFmpeg/FFprobe: Gyan essentials Windows static build, GPL-3.0-or-later;
  accompanying LICENSE and README provide build information. Upstream source:
  https://ffmpeg.org/ and build distribution https://www.gyan.dev/ffmpeg/builds/ .
  This GPL-enabled build requires corresponding source/license obligations on
  redistribution; a download link alone is not a written source offer. A release
  owner must prepare the corresponding source/build material or another valid
  compliance arrangement before public distribution.
- yt-dlp: official Windows executable, main project Unlicense, third-party code
  under the terms in `yt-dlp-THIRD_PARTY_LICENSES.txt`. Official frozen executable
  includes EJS; no remote EJS component download is configured by this package.
  https://github.com/yt-dlp/yt-dlp
- Deno: private Windows executable, MIT with third-party terms. Build records the
  executable's `deno --license` output alongside its source LICENSE.
  https://github.com/denoland/deno
- CPython: PSF License; license copied from build interpreter. Python dependency
  metadata/licenses are exported from the isolated, hash-locked environment.
- pywebview/pythonnet/WebView2: component license files are retained in the Python
  license export. Microsoft WebView2 Runtime is a separately licensed prerequisite,
  not an app-owned browser runtime; the installer uses its official distribution.
- React, React DOM and axios: frontend production dependency tree and licenses are
  exported from the committed npm lockfile installation.

Optional Chromaprint/fpcalc is not bundled. Features requiring it remain optional.
Node/npm, PyInstaller and package build tools are not end-user prerequisites.
Unsigned developer artifacts are not a signed or approved public release.
