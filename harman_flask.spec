# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['harman_flask.py'],
    pathex=[],
    binaries=[],
    datas=[('templates/cal.html', 'templates'), ('static/js/script.js', 'static/js'), ('static/css/style.css', 'static/css')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='harman_flask',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
