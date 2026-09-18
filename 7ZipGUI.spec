# -*- mode: python ; coding: utf-8 -*-
"""
Arquivo de especificação do PyInstaller para o 7-Zip GUI.

Gera dist/7ZipGUI.app — o nome é definido explicitamente aqui, então
não há ambiguidade como acontecia com o py2app.

Uso local (em um Mac):
    pip3 install -r requirements.txt
    pyinstaller 7ZipGUI.spec --noconfirm
"""

from PyInstaller.utils.hooks import collect_submodules

# py7zr importa alguns módulos de compressão dinamicamente; coletamos
# todos os submódulos para garantir que nada fique de fora do bundle.
hidden = collect_submodules("py7zr")
hidden += [
    "pyzstd",
    "pyppmd",
    "pybcj",
    "inflate64",
    "multivolumefile",
    "texttable",
    "brotli",
    "Cryptodome",
    "Cryptodome.Cipher.AES",
    "Cryptodome.Random",
]

a = Analysis(
    ["sevenzip_gui.py"],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["backports"],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="7ZipGUI",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,  # app de janela, sem terminal
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="7ZipGUI",
)

app = BUNDLE(
    coll,
    name="7ZipGUI.app",
    icon=None,
    bundle_identifier="com.example.sevenzipgui",
    info_plist={
        "CFBundleName": "7-Zip GUI",
        "CFBundleDisplayName": "7-Zip GUI",
        "CFBundleShortVersionString": "1.0.0",
        "CFBundleVersion": "1.0.0",
        "LSMinimumSystemVersion": "10.13",
        "NSHighResolutionCapable": True,
        "NSHumanReadableCopyright": "Baseado em software de codigo aberto (py7zr, LGPL).",
    },
)
