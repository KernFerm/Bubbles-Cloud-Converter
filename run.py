import os
import uuid
import json
import logging
from logging.handlers import RotatingFileHandler
import werkzeug.utils
import magic
from flask import Flask, render_template, request, send_from_directory, abort
from converter import convert_file

# Configure logging securely
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
handler = RotatingFileHandler('app.log', maxBytes=1000000, backupCount=5)
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logging.getLogger('').addHandler(handler)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.abspath(os.path.join(os.getcwd(), 'uploads'))
app.config['CONVERTED_FOLDER'] = os.path.abspath(os.path.join(os.getcwd(), 'converted'))
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB

# Load secret key securely
config_file = os.path.join(os.getcwd(), 'config.json')
if os.path.exists(config_file):
    with open(config_file, 'r') as f:
        config = json.load(f)
    app.secret_key = config.get("SECRET_KEY", os.urandom(24))
else:
    app.secret_key = os.urandom(24)
    logging.warning("config.json not found; using random secret key.")

# Ensure directories exist
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
        logging.warning("Missing file part in request")
        return "Missing file", 400

    file = request.files['file']
    if not file or file.filename == '':
        logging.warning("No file selected")
        return "No file selected", 400

    original_filename = secure_filename(file.filename)
    file.seek(0)
    detected_type = magic.from_buffer(file.read(2048), mime=True)
    file.seek(0)
    ext = os.path.splitext(original_filename)[1].lower()

    # Allowlist validation
    valid_exts = {
        'image': ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff'],
        'audio': ['.mp3', '.wav', '.flac', '.ogg', '.aac'],
        'video': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.mpeg', '.mpg'],
        'doc': ['.doc', '.docx', '.odt', '.txt', '.html', '.md', '.pdf', '.xls', '.xlsx', '.ppt', '.pptx', '.csv']
    }

    category = None
    for key, exts in valid_exts.items():
        if ext in exts:
            category = key
            break

    if not category or not detected_type.startswith(category + '/'):
        logging.warning(f"Blocked: mismatched MIME type {detected_type} for extension {ext}")
        return "File type not allowed or mismatched", 400

    compress = request.form.get('compress', 'n') == 'y'
    advanced = request.form.get('advanced', 'n') == 'y'
    output_filename = secure_filename(request.form.get('output_filename', 'converted_' + original_filename))

    options = {
        'target_size': int(float(request.form.get('target_size', 0)) * 1024) if request.form.get('target_size') else None,
        'target_bitrate': request.form.get('target_bitrate'),
        'target_resolution': tuple(map(int, request.form.get('target_resolution', '0x0').split('x'))) if 'x' in request.form.get('target_resolution', '') else None,
        'gpu': request.form.get('gpu', '').lower() if request.form.get('gpu') in ['nvidia', 'amd'] else None
    }

    # Construct file paths safely
    unique_prefix = uuid.uuid4().hex
    input_filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{unique_prefix}_{original_filename}")
    output_filepath = os.path.join(app.config['CONVERTED_FOLDER'], f"{unique_prefix}_{output_filename}")

    try:
        file.save(input_filepath)
    except Exception as e:
        logging.exception("Failed to save uploaded file")
        return "Internal error saving file", 500

    success, message = convert_file(input_filepath, output_filepath, compress, advanced, options)
    if not success:
        logging.error(f"Conversion failed: {message}")
        return f"Conversion failed: {message}", 500

    return send_from_directory(app.config['CONVERTED_FOLDER'], os.path.basename(output_filepath), as_attachment=True)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
