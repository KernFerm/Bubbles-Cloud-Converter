# Bubbles Cloud Converter

Bubbles Cloud Converter is a robust, web-based file conversion platform built to mimic CloudConvert’s functionality. With this tool, users can:

- **Upload and convert a wide range of file types:**  
  Convert images (`PNG`, `JPEG`, `BMP`, `GIF`, `TIFF`), audio (`MP3`, `WAV`, `FLAC`, `OGG`, `AAC`), video (`MP4`, `AVI`, `MKV`, `MOV`, `WMV`, `MPEG/MPG`), documents (`DOC`, `DOCX`, `ODT`, `TXT`, `HTML`, `MD`, `PDF`, `XLS`, `XLSX`, `PPT`, `PPTX`, `CSV`), and **more**.

- **Customize output file names:**  
  Save your converted file with any name and extension you choose.

- **Apply compression options:**  
  Use basic compression (e.g. JPEG quality) or enable advanced compression. Advanced options include:
  - Iterative quality reduction for images to meet a target file size.
  - Iterative bitrate reduction for audio and video if a target file size is specified.
  - Specifying target resolutions for video.

- **REST API Endpoints:**  
  Convert files programmatically via a JSON-based API at `/api/convert`.

- **User-Friendly Web Interface:**  
  An intuitive drag-and-drop file upload system with advanced options toggling.

## Features ✨

- **Multi-Format Conversion:**  
  Robust handling for images, audio, video, and document file formats (including spreadsheets and presentations).

- **Enhanced Compression Options:**  
  Advanced compression logic that iteratively adjusts quality or bitrate to meet target file sizes.

- **REST API:**  
  Easily integrate conversion into your own applications with JSON responses and download URLs.

## Requirements 📋

- **Python 3.11.9**
- **ffmpeg:**  
  Required by [pydub](https://github.com/jiaaro/pydub) and [moviepy](https://zulko.github.io/moviepy/) for audio and video conversion.  
  [Download ffmpeg](https://ffmpeg.org/download.html) and add it to your system PATH.
- **pandoc:**  
  Required by [pypandoc](https://pypi.org/project/pypandoc/) for document conversion.
- Python packages listed in `requirements.txt`.

## Installation 🛠️

1. **Clone the Repository:**

```bash
git clone https://github.com/yourusername/Bubbles-Cloud-Converter
git
cd BubblesCloudConverter
```

2. Create a Virtual Environment and Install Dependencies:

```bash
python -m venv venv
# Activate the virtual environment:
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
pip install -r requirements.txt
```

3. Run the Application:

```bash
python run.py
```

4. Access the Web Interface:

Open your browser and navigate to http://localhost:5000.

## REST API Usage 📡

Send a POST request to `/api/convert` with the following form-data parameters:

- `file`: (required) the file to convert.
- `output_filename`: (optional) desired output file name with extension.
- `compress`: (required) `"y"` for basic compression or "n" otherwise.
- `advanced`: (optional) `"y"` to enable advanced compression options.
- `target_size`: (optional) for images, audio, or video, target file size in KB.
- `target_bitrate`: (optional) target bitrate for audio/video (e.g., `192k`).
- `target_resolution`: (optional) for video, target resolution in the format `widthxheight` (e.g., `1280x720`)

The API returns a JSON response with a `download_url` for the converted file.

## Extending the Utility 🚀

- **Additional File Formats**:
The converter now supports further document formats (including spreadsheets and presentations). Extend `converter.py` for more specialized conversion if needed.
- **Enhanced Compression**:
The advanced compression loops can be tuned further to meet your specific requirements.
- **API Endpoints**:
Extend or secure the REST API for additional functionalities, authentication, or logging.

---
# Happy converting with Bubbles Cloud Converter! 🎉
---