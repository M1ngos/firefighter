# Build Instructions for Biometric Uploader

## Prerequisites

Install dependencies:
```bash
pip install -r requirements.txt
```

## Building the Executable

### Option 1: Using build script (Recommended)

```bash
python build.py
```

### Option 2: Manual PyInstaller command

```bash
pyinstaller biometric_gui.py \
  --name=BiometricUploader \
  --onefile \
  --windowed \
  --add-data="csv_api_sender.py:." \
  --clean \
  --noconfirm
```

## Output

The executable will be created in the `dist/` directory:
- **Windows**: `dist/BiometricUploader.exe`
- **Linux**: `dist/BiometricUploader`
- **macOS**: `dist/BiometricUploader`

## Distribution

Simply copy the executable file from `dist/` folder to the target machine. No Python installation required!

## Running the Application

### GUI Version
Double-click the executable or run:
```bash
./BiometricUploader
```

### CLI Version (if needed)
```bash
python csv_api_sender.py your_data.csv http://api-url:5000
```

## File Structure for End Users

The application expects CSV files with the following structure:
```
ID,Numero_Carta,Nome_Ficheiro,Caminho_Completo,Is_Active,Tipo_Biometria
1,10028588,FOTO.jpg,/path/to/foto.jpg,1,1
```

Where Tipo_Biometria codes are:
- 1 = Face photo
- 2 = Signature
- 3 = Fingerprint 1
- 4 = Fingerprint 2

## Troubleshooting

If the build fails:
1. Make sure all dependencies are installed: `pip install -r requirements.txt`
2. Check Python version (3.8+ recommended)
3. On Windows, you may need to run as Administrator
4. Check antivirus isn't blocking PyInstaller
