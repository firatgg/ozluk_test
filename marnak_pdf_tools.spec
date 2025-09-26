# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path

# Proje dizinini belirle
import os
project_dir = os.path.dirname(os.path.abspath(SPEC))
marnak_dir = os.path.join(project_dir, 'marnak_pdf_tools')

# Gerekli dosya ve klasörleri topla
datas = [
    (os.path.join(marnak_dir, 'icons'), 'marnak_pdf_tools/icons'),
    (os.path.join(marnak_dir, 'ui', 'styles.py'), 'marnak_pdf_tools/ui'),
    (os.path.join(marnak_dir, 'translations'), 'marnak_pdf_tools/translations'),
    (os.path.join(project_dir, 'tests', 'assets'), 'tests/assets'),
]

# Gizli import'ları belirle
hiddenimports = [
    'PyQt6.QtCore',
    'PyQt6.QtGui', 
    'PyQt6.QtWidgets',
    'PyPDF2',
    'fitz',  # PyMuPDF
    'logging',
    'pathlib',
    'tempfile',
    'marnak_pdf_tools.core.converter',
    'marnak_pdf_tools.core.extractor',
    'marnak_pdf_tools.core.merger',
    'marnak_pdf_tools.core.renamer',
    'marnak_pdf_tools.core.splitter',
    'marnak_pdf_tools.services.pdf_service',
    'marnak_pdf_tools.ui.windows.main_window',
    'marnak_pdf_tools.ui.windows.pdf_extract_window',
    'marnak_pdf_tools.ui.windows.pdf_merge_window',
    'marnak_pdf_tools.ui.windows.pdf_rename_window',
    'marnak_pdf_tools.ui.windows.pdf_split_window',
    'marnak_pdf_tools.ui.components.buttons',
    'marnak_pdf_tools.ui.components.drag_drop',
    'marnak_pdf_tools.ui.components.inputs',
    'marnak_pdf_tools.ui.components.labels',
    'marnak_pdf_tools.ui.components.list_widget',
    'marnak_pdf_tools.ui.components.modern_button',
    'marnak_pdf_tools.ui.components.progress',
    'marnak_pdf_tools.ui.components.pdf_viewer',
    'marnak_pdf_tools.utils.file_utils',
    'marnak_pdf_tools.utils.settings',
]

a = Analysis(
    ['marnak_pdf_tools/app.py'],
    pathex=[str(project_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MarnakPDFAraclari',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI uygulaması için console=False
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(marnak_dir, 'icons', 'favicon.ico'),
    version='version_info.txt'
)
