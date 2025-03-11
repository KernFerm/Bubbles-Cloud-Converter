import os
import uuid
import json
import logging
from logging.handlers import RotatingFileHandler
import werkzeug.utils
import magic  # Requires python-magic
from flask import Flask, render_template, request, send_from_directory, redirect, url_for, flash, jsonify
from converter import convert_file, async_convert

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
    # Sanitizes the filename to avoid path traversal
    return werkzeug.utils.secure_filename(filename)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    if 'file' not in request.files:
        flash('No file part')
        logging.error("No file part in the request")
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        logging.error("No file selected")
        return redirect(request.url)
    
    # Sanitize filename
    original_filename = secure_filename(file.filename)
    
    # Enhanced file type validation using python-magic
    file.seek(0)
    detected_type = magic.from_buffer(file.read(1024), mime=True)
    file.seek(0)  # Reset file pointer
    ext = os.path.splitext(original_filename)[1].lower()
    allowed = False
    if ext in ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff']:
        allowed = detected_type.startswith("image/")
    elif ext in ['.mp3', '.wav', '.flac', '.ogg', '.aac']:
        allowed = detected_type.startswith("audio/")
    elif ext in ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.mpeg', '.mpg']:
        allowed = detected_type.startswith("video/")
    elif ext in ['.doc', '.docx', '.odt', '.txt', '.html', '.md', '.pdf', '.xls', '.xlsx', '.ppt', '.pptx', '.csv']:
        allowed = True  # Accept various document types
    if not allowed:
        flash("File type does not match its extension. Please upload a valid file.")
        logging.error("File type validation failed: extension %s but detected mime type %s", ext, detected_type)
        return redirect(url_for('index'))
    
    # Get parameters from the form
    output_filename = request.form.get('output_filename', '').strip()
    compress = request.form.get('compress', 'n') == 'y'
    advanced = request.form.get('advanced', 'n') == 'y'
    
    # Advanced options
    options = {}
    target_size = request.form.get('target_size', None)
    target_bitrate = request.form.get('target_bitrate', None)
    target_resolution = request.form.get('target_resolution', None)
    if target_size:
        try:
            options['target_size'] = int(float(target_size) * 1024)  # Convert KB to bytes
        except Exception as e:
            logging.error("Error converting target_size: %s", e)
    if target_bitrate:
        options['target_bitrate'] = target_bitrate
    if target_resolution:
        parts = target_resolution.lower().split('x')
        if len(parts) == 2:
            try:
                options['target_resolution'] = (int(parts[0]), int(parts[1]))
            except Exception as e:
                logging.error("Error converting target_resolution: %s", e)
    
    # Generate a unique prefix for file naming
    unique_prefix = uuid.uuid4().hex
    input_filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_prefix + "_" + original_filename)
    file.save(input_filepath)
    logging.info("File saved to %s", input_filepath)
    
    if not output_filename:
        output_filename = 'converted_' + original_filename
    else:
        output_filename = secure_filename(output_filename)
    output_filepath = os.path.join(app.config['CONVERTED_FOLDER'], unique_prefix + "_" + output_filename)
    
    # Queue the conversion task asynchronously via Celery and wait for result
    task = async_convert.delay(input_filepath, output_filepath, compress, advanced, options)
    result = task.get(timeout=300)  # Wait up to 5 minutes for conversion
    
    if not result[0]:
        flash("Conversion error: " + result[1])
        logging.error("Conversion error for %s: %s", input_filepath, result[1])
        return redirect(url_for('index'))
    
    logging.info("Conversion successful: %s", output_filepath)
    return send_from_directory(directory=app.config['CONVERTED_FOLDER'],
                               path=os.path.basename(output_filepath),
                               as_attachment=True)

# REST API Endpoint
@app.route('/api/convert', methods=['POST'])
def api_convert():
    try:
        if 'file' not in request.files:
            logging.error("API conversion: No file provided")
            return jsonify(success=False, message="No file provided"), 400
        file = request.files['file']
        if file.filename == '':
            logging.error("API conversion: No file selected")
            return jsonify(success=False, message="No file selected"), 400
        
        original_filename = secure_filename(file.filename)
        output_filename = request.form.get('output_filename', '').strip()
        compress = request.form.get('compress', 'n') == 'y'
        advanced = request.form.get('advanced', 'n') == 'y'
        
        options = {}
        target_size = request.form.get('target_size', None)
        target_bitrate = request.form.get('target_bitrate', None)
        target_resolution = request.form.get('target_resolution', None)
        if target_size:
            try:
                options['target_size'] = int(float(target_size) * 1024)
            except Exception as e:
                logging.error("API conversion: error with target_size: %s", e)
        if target_bitrate:
            options['target_bitrate'] = target_bitrate
        if target_resolution:
            parts = target_resolution.lower().split('x')
            if len(parts) == 2:
                try:
                    options['target_resolution'] = (int(parts[0]), int(parts[1]))
                except Exception as e:
                    logging.error("API conversion: error with target_resolution: %s", e)
        
        unique_prefix = uuid.uuid4().hex
        input_filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_prefix + "_" + original_filename)
        file.save(input_filepath)
        
        if not output_filename:
            output_filename = 'converted_' + original_filename
        else:
            output_filename = secure_filename(output_filename)
        output_filepath = os.path.join(app.config['CONVERTED_FOLDER'], unique_prefix + "_" + output_filename)
        
        task = async_convert.delay(input_filepath, output_filepath, compress, advanced, options)
        result = task.get(timeout=300)
        if not result[0]:
            logging.error("API conversion error for %s: %s", input_filepath, result[1])
            return jsonify(success=False, message=result[1]), 500
        
        download_url = url_for('download_file', filename=os.path.basename(output_filepath), _external=True)
        logging.info("API conversion successful: %s", output_filepath)
        return jsonify(success=True, message=result[1], download_url=download_url)
    except Exception as e:
        logging.exception("Unexpected error in API conversion")
        return jsonify(success=False, message=str(e)), 500

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['CONVERTED_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=False)
