"""
Empacota sevenzip_gui.py em um app .app usando py2app.

Uso local (em um Mac):
    pip3 install -r requirements.txt
    python3 setup.py py2app

O workflow do GitHub Actions (.github/workflows/build-dmg.yml) faz isso
automaticamente em um runner macOS Intel e gera o .dmg final.
"""

import os
from setuptools import setup

APP = ["sevenzip_gui.py"]
DATA_FILES = []

# Deployment target: define a versão mínima de macOS suportada pelo app.
# Pode ser ajustado via variável de ambiente no workflow do GitHub Actions.
os.environ.setdefault("MACOSX_DEPLOYMENT_TARGET", "10.13")

OPTIONS = {
    "argv_emulation": False,
    "iconfile": "AppIcon.icns" if os.path.exists("AppIcon.icns") else None,
    # 'py7zr' e suas dependências (compressão) precisam ser embutidas
    # explicitamente, pois py2app nem sempre detecta importações dinâmicas.
    "packages": ["py7zr"],
    "includes": [
        "py7zr",
        "texttable",
        "pyzstd",
        "pyppmd",
        "pybcj",
        "inflate64",
        "multivolumefile",
        "Cryptodome",
    ],
    # Proteção extra: caso alguma dependência puxe futuramente o pacote
    # "backports" (namespace package sem __init__.py), impedir que o
    # py2app tente processá-lo — é isso que causa o erro
    # "ImportError: No module named 'backports'" durante o build.
    "excludes": ["backports"],
    "plist": {
        "CFBundleName": "7-Zip GUI",
        "CFBundleDisplayName": "7-Zip GUI",
        "CFBundleIdentifier": "com.example.sevenzipgui",
        "CFBundleShortVersionString": "1.0.0",
        "CFBundleVersion": "1.0.0",
        "LSMinimumSystemVersion": os.environ["MACOSX_DEPLOYMENT_TARGET"],
        "NSHumanReadableCopyright": "Baseado em software de código aberto (py7zr, licença LGPL/BSD).",
        "NSHighResolutionCapable": True,
    },
}

setup(
    app=APP,
    name="7ZipGUI",
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
