# Bubbles Cloud Converter

Bubbles Cloud Converter is a robust, asynchronous, web-based file conversion platform built to mimic CloudConvert’s functionality. With this tool, you can:

- **Upload and convert a wide range of file types:**  
  Convert images (`PNG`, `JPEG`, `BMP`, `GIF`, `TIFF`), audio (`MP3`, `WAV`, `FLAC`, `OGG`, `AAC`), video (`MP4`, `AVI`, `MKV`, `MOV`, `WMV`, `MPEG/MPG`), documents (`DOC`, `DOCX`, `ODT`, `TXT`, `HTML`, `MD`, `PDF`, `XLS`, `XLSX`, `PPT`, `PPTX`, `CSV`), and **more**.

- **Customize output file names:**  
  Save your converted file with any name and extension you choose.

- **Apply compression options:**  
  Use basic compression (e.g. JPEG quality) or enable advanced compression. Advanced options include:
  - Iterative quality reduction for images to meet a target file size.
  - Iterative bitrate reduction for audio and video if a target file size is specified.
  - Specifying target resolutions for video.

- **Asynchronous Processing:**  
  Heavy conversion tasks are processed asynchronously using Celery (with Redis as the message broker), keeping the web interface responsive.

- **Enhanced File Type Validation:**  
  Utilizes `python-magic` to validate the MIME type of uploaded files against their extension.

- **Robust Logging:**  
  Logs are managed with a Rotating File Handler, ensuring persistent log management and easier debugging.

- **REST API Endpoints:**  
  Convert files programmatically via a JSON-based API at `/api/convert`.

- **User-Friendly Web Interface:**  
  An intuitive drag-and-drop file upload system with advanced options toggling.

## Features ✨

- **Multi-Format Conversion:**  
  Robust handling for images, audio, video, and document file formats (including spreadsheets and presentations).

- **Advanced Compression Options:**  
  Iterative adjustments of quality or bitrate to meet target file sizes.

- **Asynchronous Conversion:**  
  Conversion tasks are offloaded to a Celery worker, preventing blocking of web requests.

- **Enhanced Validation & Logging:**  
  Validates file types using `python-magic` and logs events using a RotatingFileHandler.

- **REST API:**  
  Easily integrate conversion functionality into your own applications with JSON responses and download URLs.

## Requirements 📋

- **Python 3.11.9**
- **ffmpeg:**  
  Required by [pydub](https://github.com/jiaaro/pydub) and [moviepy](https://zulko.github.io/moviepy/) for audio and video conversion.  
  [Download ffmpeg](https://ffmpeg.org/download.html) and add it to your system PATH.
- **pandoc:**  
  Required by [pypandoc](https://pypi.org/project/pypandoc/) for document conversion.
- **Redis:**  
  Required as the Celery message broker.
- Python packages listed in `requirements.txt`.

## Installation 🛠️

1. **Clone the Repository:**

```bash
git clone https://github.com/kernferm/Bubbles-Cloud-Converter
cd Bubbles-Cloud-Converter
```

2. **Create a Virtual Environment and Install Dependencies**:

```bash
python -m venv venv
# Activate the virtual environment:
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
pip install -r requirements.txt
```

3. **Configure the Application**:

Create a `config.json` file in the root directory with your configuration, for example:

```json
{
  "SECRET_KEY": "your-secret-key"
}
```

4. **Run Redis**:

- Ensure a Redis server is running locally (or update the Celery broker URL in the code accordingly).

- **Start the Celery Worker**:
### In a separate terminal window, run:

```
celery -A run.celery worker --loglevel=info
```

6. **Run the Application**:

```
python run.py
```

- **Access the Web Interface**:

Open your browser and navigate to http://localhost:5000.


## REST API Usage 📡

Send a POST request to `/api/convert` with the following form-data parameters:

- `file`: (required) the file to convert.
- `output_filename`: (optional) desired output file name with extension.
- `compress`: (required) `"y"` for basic compression or `"n"` otherwise.
- `advanced`: (optional) `"y"` to enable advanced compression options.
- `target_size`: (optional) for images, audio, or video, target file size in KB.
- `target_bitrate`: (optional) target bitrate for `audio/video` (e.g., `192k`).
- `target_resolution`: (optional) for video, target resolution in the format `widthxheight` (e.g., `1280x720`).

- The API returns a JSON response with a `download_url` for the converted file.

## Extending the Utility 🚀

- **Additional File Formats**:
Extend `converter.py` to support more specialized file formats if needed.

- **Enhanced Compression**:
Tune the advanced compression loops further to meet specific quality or size targets.

- **API Enhancements**:
Extend or secure the REST API for additional functionalities, such as authentication or rate limiting.

- **Scalability**:
Consider integrating additional asynchronous processing or job queue systems for high load.

---
# Happy converting with Bubbles Cloud Converter! 🎉
---
