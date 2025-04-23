import os
import uuid
import json
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, render_template, request, send_from_directory, abort
from werkzeug.utils import secure_filename, safe_join
import magic
import bleach

from converter import convert_file

# --- Logging setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
handler = RotatingFileHandler('app.log', maxBytes=1_000_000, backupCount=5)
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logging.getLogger('').addHandler(handler)

# --- Flask config ---
app = Flask(__name__)
app.config['UPLOAD_FOLDER']    = os.path.abspath(os.path.join(os.getcwd(), 'uploads'))
app.config['CONVERTED_FOLDER'] = os.path.abspath(os.path.join(os.getcwd(), 'converted'))
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB

# load secret key
config_path = os.path.join(os.getcwd(), 'config.json')
if os.path.exists(config_path):
    with open(config_path, 'r') as f:
        cfg = json.load(f)
    app.secret_key = cfg.get("SECRET_KEY") or os.urandom(24)
else:
    app.secret_key = os.urandom(24)
    logging.warning("config.json not found; using random secret key.")

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['CONVERTED_FOLDER'], exist_ok=True)


def sanitize_str(s: str, max_length: int = 255) -> str:
    """Strip anything but plain text, then truncate."""
    cleaned = bleach.clean(s or '', tags=[], attributes={}, strip=True)
    return cleaned[:max_length]


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/convert', methods=['POST'])
def convert():
    # 1) check file part
    if 'file' not in request.files:
        logging.warning("Missing file part")
        return "Missing file", 400

    file = request.files['file']
    if not file or file.filename == '':
        logging.warning("No file selected")
        return "No file selected", 400

    # 2) sanitize & secure original filename
    orig_name = secure_filename(sanitize_str(file.filename))

    # 3) detect MIME from content
    file.seek(0)
    detected_mime = magic.from_buffer(file.read(2048), mime=True)
    file.seek(0)

    # 4) extension allowlist
    ext = os.path.splitext(orig_name)[1].lower()
    valid_exts = {
        'image': ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff'],
        'audio': ['.mp3', '.wav', '.flac', '.ogg', '.aac'],
        'video': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.mpeg', '.mpg'],
        'doc':   ['.doc', '.docx', '.odt', '.txt', '.html', '.md', '.pdf', '.xls', '.xlsx', '.ppt', '.pptx', '.csv']
    }
    category = next((cat for cat, exts in valid_exts.items() if ext in exts), None)
    if not category or not detected_mime.startswith(f"{category}/"):
        logging.warning(f"Blocked upload: {detected_mime} vs {ext}")
        return "File type not allowed or mismatched", 400

    # 5) sanitize form inputs
    compress = request.form.get('compress', 'n').lower() == 'y'
    advanced = request.form.get('advanced', 'n').lower() == 'y'

    raw_out = request.form.get('output_filename', f"converted_{orig_name}")
    clean_out = secure_filename(sanitize_str(raw_out))
    # ensure extension matches original
    if not clean_out.lower().endswith(ext):
        clean_out = os.path.splitext(clean_out)[0] + ext

    # 6) parse & validate options
    def parse_int(val, default=None):
        try:
            return int(float(val))
        except:
            return default

    target_size    = parse_int(request.form.get('target_size'), None)
    target_bitrate = sanitize_str(request.form.get('target_bitrate', '')).lower()
    # only allow digits + k/m suffix
    import re
    if target_bitrate and not re.fullmatch(r'\d+[km]?b', target_bitrate):
        target_bitrate = None

    res = request.form.get('target_resolution', '')
    if 'x' in res:
        w, h = res.split('x', 1)
        w_i = parse_int(w); h_i = parse_int(h)
        target_resolution = (w_i, h_i) if w_i and h_i else None
    else:
        target_resolution = None

    gpu_opt = request.form.get('gpu', '').lower()
    gpu = gpu_opt if gpu_opt in ['nvidia', 'amd'] else None

    options = {
        'target_size': target_size and target_size * 1024,
        'target_bitrate': target_bitrate,
        'target_resolution': target_resolution,
        'gpu': gpu
    }

    # 7) build safe paths
    prefix = uuid.uuid4().hex
    try:
        inp_path = safe_join(app.config['UPLOAD_FOLDER'], f"{prefix}_{orig_name}")
        out_path = safe_join(app.config['CONVERTED_FOLDER'], f"{prefix}_{clean_out}")
    except Exception as e:
        logging.exception("Path traversal attempt")
        return "Invalid filename", 400

    # 8) save file
    try:
        file.save(inp_path)
    except Exception:
        logging.exception("Failed saving uploaded file")
        return "Internal error saving file", 500

    # 9) convert
    success, message = convert_file(inp_path, out_path, compress, advanced, options)
    if not success:
        logging.error("Conversion failed: %s", message)
        return "Conversion error", 500

    # 10) return
    return send_from_directory(
        app.config['CONVERTED_FOLDER'],
        os.path.basename(out_path),
        as_attachment=True
    )


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
