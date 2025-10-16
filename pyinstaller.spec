# PyInstaller spec for packaging
# Run: pyinstaller pyinstaller.spec
block_cipher = None
a = Analysis(['main.py'], pathex=['.'], binaries=[], datas=[('resources', 'resources')], hiddenimports=['models'], hookspath=[])
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(pyz, a.scripts, exclude_binaries=True, name='leave_manager', debug=False)
coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas, strip=False, upx=True)
