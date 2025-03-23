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
  - torch==2.6.0
  - torch-directml==2.6.0 *(required for AMD GPU support)*

---

## 🛠 Installation (Windows)

1. **Clone the Repository:**

```bash
git clone https://github.com/yourgithub/Bubbles-Cloud-Converter
cd Bubbles-Cloud-Converter
```

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
