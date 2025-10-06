#!/usr/bin/env python3
"""Build script for creating executable with PyInstaller."""

import PyInstaller.__main__
import os

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# PyInstaller arguments
PyInstaller.__main__.run([
    'biometric_gui.py',
    '--name=BiometricUploader',
    '--onefile',
    '--windowed',
    '--icon=NONE',
    '--add-data=csv_api_sender.py:.',
    '--clean',
    '--noconfirm',
    f'--distpath={os.path.join(current_dir, "dist")}',
    f'--workpath={os.path.join(current_dir, "build")}',
    f'--specpath={os.path.join(current_dir, "build")}',
])

print("\n" + "="*60)
print("Build complete!")
print("="*60)
print(f"\nExecutable location: {os.path.join(current_dir, 'dist', 'BiometricUploader.exe')}")
print("\nYou can now distribute the single .exe file")
