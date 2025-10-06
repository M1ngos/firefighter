# 📘 Biometric Data Uploader - User Guide

## For End Users (Non-Technical)

### What Does This Do?

This application uploads driver biometric data (photos, signatures, fingerprints) from CSV files to the api-condutores system. It makes the process easy and shows you exactly what's happening.

---

## 🚀 Getting Started

### 1. Open the Application

- **Windows**: Double-click `BiometricUploader.exe`
- The window will open automatically

### 2. Select Your CSV File

- Click the **"Browse..."** button
- Find your CSV file (should have driver biometric data)
- Select it and click Open

### 3. Enter API Settings

**API URL**: Enter the server address (example: `http://192.168.1.100:5000`)

**Auth Token** (Optional): If required, enter your authentication token here
- Leave blank if not needed
- The text will be hidden for security

### 4. Start Upload

- Click **"▶ Start Upload"**
- Watch the progress bar fill up
- See real-time status for each driver:
  - ✓ Green = Success
  - ✗ Red = Failed
  - ⊘ Yellow = Skipped

### 5. View Results

The summary at the bottom shows:
- **Total**: How many drivers were processed
- **✓ Success**: Successful uploads
- **✗ Failed**: Failed uploads (with error messages)
- **⊘ Skipped**: Skipped (usually missing data)

### 6. Save Report

- Click **"💾 Save Report"** when finished
- Choose where to save
- You'll get TWO files:
  1. **JSON file** - Technical data
  2. **HTML file** - Beautiful report you can open in your web browser

- Click "Yes" to automatically open the HTML report
- Share the HTML report with your team (it's a single file)

---

## 📋 Understanding Your CSV File

Your CSV file should look like this:

```csv
ID,Numero_Carta,Nome_Ficheiro,Caminho_Completo,Is_Active,Tipo_Biometria
1,10028588,FOTO_10028588.jpg,/path/to/photo.jpg,1,1
2,10028588,ASSINATURA_10028588.png,/path/to/signature.png,1,2
3,10028588,IMPRESSAO_DIGITAL_1.bmp,/path/to/fingerprint1.bmp,1,3
4,10028588,IMPRESSAO_DIGITAL_2.bmp,/path/to/fingerprint2.bmp,1,4
```

**Important Columns:**
- `Numero_Carta` - Driver's license number (required)
- `Caminho_Completo` - Full path to the image file
- `Tipo_Biometria` - Type of biometric data:
  - 1 = Face photo
  - 2 = Signature
  - 3 = First fingerprint
  - 4 = Second fingerprint
- `Is_Active` - Set to 1 for active records

**Note**: Multiple rows can have the same `Numero_Carta` (one driver can have multiple biometric files)

---

## 🎨 Understanding the HTML Report

When you open the HTML report in your browser, you'll see:

### Summary Cards (Top)
- **Total Drivers** - How many unique drivers
- **Successful** - Green number (uploads that worked)
- **Failed** - Red number (uploads that didn't work)
- **Skipped** - Yellow number (no data to upload)

### Filter Buttons
Click to show only:
- **All** - Show everything
- **✓ Success** - Only successful uploads
- **✗ Failed** - Only failed uploads
- **⊘ Skipped** - Only skipped records

### Detailed Records
Each driver shows:
- **License Number** (big, bold)
- **Status Badge** (colored: Success/Failed/Skipped)
- **What Happened**:
  - ✓ Created files (new files uploaded)
  - ↻ Updated files (replaced existing files)
  - ⚠ Missing files (files not provided)
- **Error Messages** (if something went wrong)

---

## ❓ Common Questions

### Q: What if some files are missing?

**A**: The app will:
- Upload the files it can find
- Mark the upload as "Success" if at least one file was uploaded
- Show a warning for missing files
- Continue with the next driver

### Q: What does "Skipped" mean?

**A**: A driver is skipped when:
- No biometric files could be found
- All file paths are invalid
- The license number is missing

### Q: Can I run multiple uploads at once?

**A**: No, wait for one to finish before starting another. The button will be disabled during upload.

### Q: How do I share the report with my manager?

**A**:
1. Click "💾 Save Report"
2. Find the HTML file (ends with `_report.html`)
3. Send it via email or copy it to a shared folder
4. Anyone can open it in any web browser (Chrome, Firefox, Edge, etc.)

### Q: What if the upload fails?

**A**: Check:
1. Is the API URL correct?
2. Is the server running?
3. Do you need an Auth Token?
4. Are the file paths in your CSV correct?
5. Look at the error message for details

---

## 🆘 Getting Help

If you encounter problems:

1. **Check the Status Log** - Read the messages in the app, they often explain the problem
2. **Save the Report** - Include it when asking for help
3. **Note the Error** - Write down any error messages
4. **Contact Support** - Reach out to your IT team or system administrator

---

## 📞 Technical Support

For technical issues, provide:
- ✅ Screenshot of the error
- ✅ The HTML/JSON report
- ✅ Sample CSV file (first few lines)
- ✅ API URL being used
- ✅ What you were doing when it failed

---

**Version**: 1.0
**Last Updated**: 2025-10-06
**Created with**: ❤️ and Python
