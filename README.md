# 🔐 Biometric Data Uploader

Modern application for uploading driver biometric data to api-condutores. Available in both **GUI** and **CLI** versions.

---

## 🚀 Quick Start

### GUI Version (Recommended)

**For End Users - No Python Required:**

1. Download `BiometricUploader.exe` from releases
2. Double-click to run
3. Select your CSV file
4. Enter API URL
5. Click "Start Upload"

**For Developers:**

```bash
# Install dependencies
pip install -r requirements.txt

# Run GUI
python biometric_gui.py

# Build executable
python build.py
```

### CLI Version (Advanced Users)

```bash
# Install dependencies
pip install -r requirements.txt

# Upload data
python csv_api_sender.py data.csv http://127.0.0.1:5000

# With options
python csv_api_sender.py data.csv http://127.0.0.1:5000 --output report.json
```

---

## CSV Formats

The application supports **two CSV formats**:

### Format 1: Tipo_Biometria (File Paths)

**Columns:**
- `Numero_Carta` - Driver's license number (required)
- `Caminho_Completo` - Full path to biometric file
- `Tipo_Biometria` - Type code: 1=Face, 2=Signature, 3=Fingerprint1, 4=Fingerprint2
- `Is_Active` - 1=Active, 0=Inactive (optional, defaults to 1)
- `ID`, `Nome_Ficheiro` - Optional metadata

**Features:**
- Automatically reads files and converts to base64
- Groups multiple rows by `Numero_Carta`
- Sends all biometric data for each driver in one API call

**Sample CSV:**
```csv
ID,Numero_Carta,Nome_Ficheiro,Caminho_Completo,Is_Active,Tipo_Biometria
1,10028588,FOTO_10028588.bmp,/path/to/FOTO_10028588.bmp,1,1
2,10028588,ASSINATURA_10028588.bmp,/path/to/ASSINATURA_10028588.bmp,1,2
3,10028588,IMPRESSAO_DIGITAL_1_10028588.bmp,/path/to/FP1.bmp,1,3
4,10028588,IMPRESSAO_DIGITAL_2_10028588.bmp,/path/to/FP2.bmp,1,4
```

### Format 2: Direct Base64 (Legacy)

**Columns:**
- `numero_carta` (or `Numero_Carta`, `license_number`) - Required
- `fileFace` - Base64 encoded face image
- `fileSign` - Base64 encoded signature
- `filesFinger1` - Base64 encoded fingerprint 1
- `filesFinger2` - Base64 encoded fingerprint 2

**Sample CSV:**
```csv
numero_carta,fileFace,fileSign,filesFinger1,filesFinger2
1234567,<base64_face>,<base64_sign>,<base64_fp1>,<base64_fp2>
```

## 📊 Features

### GUI Application

- ✅ **User-Friendly Interface** - No command-line knowledge required
- 📁 **File Browser** - Easy CSV file selection
- 🔄 **Real-Time Progress** - Visual progress bar and live status updates
- 🎨 **Color-Coded Results** - Green (success), Red (failed), Yellow (skipped)
- 📈 **Live Summary** - Running totals of success/failed/skipped uploads
- 💾 **Export Reports** - Save detailed JSON reports with one click
- 🔒 **Secure** - Optional authentication token support (masked input)
- ⚡ **Non-Blocking** - UI stays responsive during uploads

### CLI Application

- 🚀 **Fast Processing** - Command-line for batch operations
- 📊 **Detailed Console Output** - Color-coded real-time status
- 📄 **JSON Reports** - Machine-readable output for automation
- 🔧 **Flexible** - Custom headers and authentication options

---

## 📸 Screenshot Examples

### GUI Interface

```
┌─────────────────────────────────────────────────────────┐
│  🔐 Biometric Data Uploader                             │
│  Upload driver biometric data to api-condutores         │
├─────────────────────────────────────────────────────────┤
│  Configuration                                          │
│  CSV File: [/path/to/data.csv]          [Browse...]    │
│  API URL:  [http://127.0.0.1:5000]                     │
│  Auth:     [**********] (Optional)                     │
├─────────────────────────────────────────────────────────┤
│  Progress                                               │
│  ████████████████████░░░░░░░░ 65%                      │
│                                                         │
│  ✓ [1/3] SUCCESS 10028588: Created: 4 files            │
│  ✓ [2/3] SUCCESS 10029445: Created: 2 files            │
│  ⏳ Processing 10030122...                              │
├─────────────────────────────────────────────────────────┤
│  Total: 3  ✓ Success: 2  ✗ Failed: 0  ⊘ Skipped: 0   │
├─────────────────────────────────────────────────────────┤
│          [▶ Start Upload]  [💾 Save Report]             │
└─────────────────────────────────────────────────────────┘
```

### CLI Output

```
Starting processing of 7 CSV rows → 3 unique drivers
────────────────────────────────────────────────────────────
[1/3] 10028588 [✓ OK] New driver | Created: fileFace, fileSign, filesFinger1, filesFinger2
[2/3] 10029445 [✓ OK] Updated | Created: fileFace | Warning: Missing filesFinger1
[3/3] 10030122 [⊘ SKIPPED] No biometric data available

SUMMARY
────────────────────────────────────────────────────────────
Total CSV rows:        7
Total unique drivers:  3
Successful:            2
Failed:                0
Skipped:               1
Files not found:       1
```

---

## 📄 Reports

### Beautiful HTML Reports (GUI)

When you save a report in the GUI, you get **both** JSON and HTML:

- **📄 JSON Report** - Machine-readable data for automation
- **🌐 HTML Report** - Beautiful, interactive web page

The HTML report features:
- ✨ Modern, professional design
- 🎨 Color-coded status (green/red/yellow)
- 🔍 Filter by status (All/Success/Failed/Skipped)
- 📊 Visual summary cards
- 📱 Responsive (works on mobile)
- 🖨️ Print-friendly

**Example HTML Report:**
![Report Screenshot]
- Summary cards showing totals at a glance
- Filterable list of all uploads
- Detailed file information (created/updated/missing)
- Error messages for failed uploads
- One-click to open in browser

### JSON Report Format

```json
{
  "total_csv_rows": 7,
  "total_drivers": 3,
  "success": 2,
  "failed": 0,
  "skipped": 1,
  "details": [
    {
      "driver": 1,
      "numero_carta": "10028588",
      "status": "success",
      "files_created": ["fileFace", "fileSign", "filesFinger1", "filesFinger2"],
      "files_updated": [],
      "files_missing": [],
      "driver_created": true,
      "csv_rows": 4
    }
  ]
}
```

### Generate HTML Report from JSON (CLI)

```bash
# Convert existing JSON report to HTML
python report_viewer.py upload_report.json

# Output: upload_report_report.html
```

---

## 🔌 API Integration

**Endpoint:** `POST http://<api_url>/biometric-data/{numero_carta}`

**Request Body:**
```json
{
  "fileFace": "<base64_encoded_image>",
  "fileSign": "<base64_encoded_signature>",
  "filesFinger1": "<base64_encoded_fingerprint>",
  "filesFinger2": "<base64_encoded_fingerprint>"
}
```

**Response Codes:**
- ✅ **201** - Success (files_created, files_updated, files_missing)
- ⚠️ **400** - Skipped (no valid biometric data)
- ❌ **404** - Config error (wrong API endpoint)
- ⚡ **500** - Server error (contact administrator)

---

## 🛠️ Building from Source

See [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) for detailed build instructions.

**Quick build:**
```bash
pip install -r requirements.txt
python build.py
```

Executable will be in `dist/BiometricUploader.exe`

---

## 📞 Support

For issues or questions, please contact your system administrator or refer to the API documentation.
