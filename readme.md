# Bubbles Cloud Converter 🫧☁️

**Bubbles Cloud Converter** is a robust, web-based file conversion platform built to provide local, secure, and GPU-accelerated file conversion services. This tool processes various file types quickly and efficiently through a modern Flask-based interface.

---


## 🌟 Features

- **Convert a wide range of file types:**  
  Supports images (`PNG`, `JPEG`, `BMP`, `GIF`, `TIFF`), audio (`MP3`, `WAV`, `FLAC`, `OGG`, `AAC`), video (`MP4`, `AVI`, `MKV`, `MOV`, `WMV`, `MPEG/MPG`), and documents (`DOC`, `DOCX`, `ODT`, `TXT`, `HTML`, `MD`, `PDF`, `XLS`, `XLSX`, `PPT`, `PPTX`, `CSV`).

- **Custom output filenames:**  
  Rename your converted files to whatever you like.

- **Compression Options:**  
  Includes standard and advanced compression for images, audio, and video.

- **MIME Type Verification:**  
  Ensures uploaded file content matches its extension using `python-magic`.

- **GPU Acceleration Support:**  
  Utilizes **NVIDIA (CUDA)** and **AMD (DirectML)** for faster video conversions.

- **Secure Web Interface:**  
  Simple drag-and-drop UI built with Bootstrap, secured with a user-defined secret key.

---

## 📋 Requirements

- **Python 3.11.9**
- **FFmpeg** (required by pydub/moviepy – installed via Chocolatey or manually)
- Python packages:
  - Flask
  - Pillow
  - pydub
  - moviepy
  - pypandoc
  - python-magic
  - werkzeug
  - torch==2.8.0
  - torch-directml==0.2.5.dev240914 *(required for AMD GPU support)*

---

## 🛠 Installation (Windows)

## 📥 How to Download the Repo (First-Time Users)

Click the link to read [**Instructions**](https://www.gitprojects.fnbubbles420.org/how-to-download-repos) 📄.

### Download ZIP:
1. 📥 Click the green `"Code"` button at the top right of the repository page.
2. 📂 Choose `"Download ZIP"` from the dropdown menu.
3. 📁 This will download a `ZIP file` with the entire repository.
### Extract the ZIP File:
1. 🗂 Find the downloaded `ZIP file` on your computer.
2. 🔧 `Extract` it using your computer's built-in extraction tool or a third-party tool like `WinRAR` or `7-Zip`.

2. Create a Virtual Environment & Install Dependencies:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

3. Install FFmpeg (Required):
- 🥇 Recommended (Chocolatey):
- use powershell
```bash
choco install ffmpeg -y
```

- 🧰 Manual Install: Download from: `https://www.gyan.dev/ffmpeg/builds/`
Extract and add the `bin/` folder to your `system PATH`.

## 🔐 Secure the App
Generate a Secure Secret Key:

```bash
import secrets
print(secrets.token_hex(32))  # 64-character hex string
```

## Create a config.json file in the project root:

```json
{
    "SECRET_KEY": "your-secure-64-character-key"
}
```

## 🚀 Run the Application
```bash
python run.py
```
- Then visit 👉 http://localhost:5000

## 📡 Usage
- Drag and drop your file into the web app.
- Choose a custom output name and compression settings.
- Select advanced GPU settings (NVIDIA/AMD) if applicable.
- Download your converted file instantly.

## 🔒 Security Notes

- Debug mode is disabled in production (`debug=False`)
- MIME validation and path sanitation ensure safe conversion
- All temporary and converted files stay local (no cloud storage)
---
# ❤️ From the Dev
This tool is built with love to help others convert files easily and securely—especially for those needing GPU power on local machines. 
Have fun converting and customizing your media!
---

