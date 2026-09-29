"""Generate Windows VERSIONINFO from the installer/application version source."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
version = (ROOT / 'desktop/packaging/version.txt').read_text().strip()
if not re.fullmatch(r'\d+\.\d+\.\d+', version):
    raise ValueError('Version must be major.minor.patch')
numbers = tuple(int(part) for part in version.split('.')) + (0,)
output = ROOT / 'build/desktop/version-info.txt'
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(f'''VSVersionInfo(
 ffi=FixedFileInfo(filevers={numbers!r}, prodvers={numbers!r}, mask=0x3f,
 flags=0x0, OS=0x40004, fileType=0x1, subtype=0x0, date=(0, 0)),
 kids=[StringFileInfo([StringTable('040904B0', [
 StringStruct('CompanyName', 'AutoTransAI'),
 StringStruct('FileDescription', 'AutoTransAI Desktop'),
 StringStruct('FileVersion', '{version}'),
 StringStruct('ProductName', 'AutoTransAI'),
 StringStruct('ProductVersion', '{version}'),
 StringStruct('OriginalFilename', 'AutoTransAI.exe')])]),
 VarFileInfo([VarStruct('Translation', [1033, 1200])])])
''', encoding='utf-8')
