import os
import uuid
import json
import logging
from logging.handlers import RotatingFileHandler
import werkzeug.utils
from urllib.parse import urlparse
import magic  # Requires python-magic
from flask import Flask, render_template, request, send_from_directory, abort, jsonify, url_for
from converter import convert_file  # Make sure to adjust the converter.py as previously discussed

# Configure logging with RotatingFileHandler
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')
handler = RotatingFileHandler('app.log', maxBytes=1000000, backupCount=5)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logging.getLogger('').addHandler(handler)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
app.config['CONVERTED_FOLDER'] = os.path.join(os.getcwd(), 'converted')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # Limit file uploads to 50 MB

# Load configuration from config.json for sensitive info (like secret key)
config_file = os.path.join(os.getcwd(), 'config.json')
if os.path.exists(config_file):
    with open(config_file, 'r') as f:
        config = json.load(f)
    app.secret_key = config.get("SECRET_KEY", "default-secret-key")
else:
    app.secret_key = "default-secret-key"
    logging.warning("config.json not found; using default secret key.")

# Ensure required directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['CONVERTED_FOLDER'], exist_ok=True)

def secure_filename(filename):
    return werkzeug.utils.secure_filename(filename)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    if 'file' not in request.files:
        logging.error("No file part in the request")
        return "Error: No file part in the request", 400
    file = request.files['file']
    if file.filename == '':
        logging.error("No file selected")
        return "Error: No file selected", 400
    
    original_filename = secure_filename(file.filename)
    file.seek(0)
    detected_type = magic.from_buffer(file.read(1024), mime=True)
    file.seek(0)  # Reset file pointer
    ext = os.path.splitext(original_filename)[1].lower()
    allowed = (detected_type.startswith("image/") and ext in ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff']) or \
              (detected_type.startswith("audio/") and ext in ['.mp3', '.wav', '.flac', '.ogg', '.aac']) or \
              (detected_type.startswith("video/") and ext in ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.mpeg', '.mpg']) or \
              ext in ['.doc', '.docx', '.odt', '.txt', '.html', '.md', '.pdf', '.xls', '.xlsx', '.ppt', '.pptx', '.csv']
    if not allowed:
        logging.error("File type validation failed: extension %s but detected mime type %s", ext, detected_type)
        return "Error: File type does not match its extension", 400

    output_filename = request.form.get('output_filename', '').strip()
    compress = request.form.get('compress', 'n') == 'y'
    advanced = request.form.get('advanced', 'n') == 'y'
    
    options = {
        'target_size': int(float(request.form.get('target_size', 0)) * 1024) if request.form.get('target_size') else None,
        'target_bitrate': request.form.get('target_bitrate'),
        'target_resolution': tuple(map(int, request.form.get('target_resolution', '0x0').split('x'))) if 'x' in request.form.get('target_resolution', '') else None
    }

    unique_prefix = uuid.uuid4().hex
    input_filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_prefix + "_" + original_filename)
    file.save(input_filepath)
    
    output_filename = output_filename if output_filename else 'converted_' + original_filename
    output_filepath = os.path.join(app.config['CONVERTED_FOLDER'], unique_prefix + "_" + output_filename)

    # Perform the conversion
    success, message = convert_file(input_filepath, output_filepath, compress, advanced, options)
    if not success:
        logging.error("Conversion error: %s", message)
        return "Error: Conversion failed", 500

    return send_from_directory(directory=app.config['CONVERTED_FOLDER'],
                               path=os.path.basename(output_filepath),
                               as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
