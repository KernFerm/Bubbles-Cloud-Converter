# Bubbles Cloud Converter 🫧☁️

Bubbles Cloud Converter is a robust, web-based file conversion platform built to provide local, synchronous file conversion services. This tool allows for the direct processing of various file types, ensuring quick and efficient handling directly within the application.

## Features ✨

- **Upload and convert a wide range of file types:**  
  Convert images (`PNG`, `JPEG`, `BMP`, `GIF`, `TIFF`), audio (`MP3`, `WAV`, `FLAC`, `OGG`, `AAC`), video (`MP4`, `AVI`, `MKV`, `MOV`, `WMV`, `MPEG/MPG`), and documents (`DOC`, `DOCX`, `ODT`, `TXT`, `HTML`, `MD`, `PDF`, `XLS`, `XLSX`, `PPT`, `PPTX`, `CSV`).

- **Customize output file names:**  
  Save your converted files with any name and extension you choose.

- **Apply compression options:**  
  Utilize settings to adjust the quality and size of the output, including basic and advanced compression options.

- **File Type Validation:**  
  Uses `python-magic` to validate the MIME type of uploaded files, ensuring accurate processing.

- **User-Friendly Web Interface:**  
  A simple drag-and-drop interface for file uploads with an option to toggle advanced settings.

## Requirements 📋

- **Python 3.x**
- **Flask**: For running the web server.
- **Pillow**: For image processing.
- **pydub**: For audio processing.
- **moviepy**: For video processing.
- **pypandoc**: For document conversion.
- **python-magic**: For file type validation.
- **werkzeug**: Utility library for Flask.

## Installation 🛠️

1. **Clone the Repository:**
```bash
git clone https://github.com/yourgithub/Bubbles-Cloud-Converter
cd Bubbles-Cloud-Converter
```

2. Create a Virtual Environment and Install Dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Unix/macOS
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
```

3. Configure the Application: Create a config.json in the root directory with your configuration, such as:

```bash
{
    "SECRET_KEY": "your-secret-key"
}
```

Run the Application:

```bash
python run.py
```
- Access the web interface by navigating to `http://localhost:5000` in your web browser.

## Usage 📡

To convert a file, simply drag and drop your file into the web interface and select the desired output format and any compression options. The file will be processed, and a download link will be provided upon completion.





