import os
import uuid
from flask import Flask, render_template, request, send_from_directory, redirect, url_for, flash, jsonify
from converter import convert_file
import werkzeug.utils

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
app.config['CONVERTED_FOLDER'] = os.path.join(os.getcwd(), 'converted')
app.secret_key = 'your-secret-key'  # Replace with a secure secret key
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # Limit file uploads to 50 MB

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
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    # Sanitize filename
    original_filename = secure_filename(file.filename)
    
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
        except Exception:
            pass
    if target_bitrate:
        options['target_bitrate'] = target_bitrate
    if target_resolution:
        parts = target_resolution.lower().split('x')
        if len(parts) == 2:
            try:
                options['target_resolution'] = (int(parts[0]), int(parts[1]))
            except Exception:
                pass
    
    # Generate a unique prefix for file naming
    unique_prefix = uuid.uuid4().hex
    input_filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_prefix + "_" + original_filename)
    file.save(input_filepath)
    
    if not output_filename:
        output_filename = 'converted_' + original_filename
    else:
        output_filename = secure_filename(output_filename)
    output_filepath = os.path.join(app.config['CONVERTED_FOLDER'], unique_prefix + "_" + output_filename)
    
    # Convert the file based on its type and options
    success, message = convert_file(input_filepath, output_filepath, compress=compress, advanced=advanced, options=options)
    if not success:
        flash("Conversion error: " + message)
        return redirect(url_for('index'))
    
    return send_from_directory(directory=app.config['CONVERTED_FOLDER'],
                               path=os.path.basename(output_filepath),
                               as_attachment=True)

# REST API Endpoint
@app.route('/api/convert', methods=['POST'])
def api_convert():
    try:
        if 'file' not in request.files:
            return jsonify(success=False, message="No file provided"), 400
        file = request.files['file']
        if file.filename == '':
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
            except Exception:
                pass
        if target_bitrate:
            options['target_bitrate'] = target_bitrate
        if target_resolution:
            parts = target_resolution.lower().split('x')
            if len(parts) == 2:
                try:
                    options['target_resolution'] = (int(parts[0]), int(parts[1]))
                except Exception:
                    pass
        
        unique_prefix = uuid.uuid4().hex
        input_filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_prefix + "_" + original_filename)
        file.save(input_filepath)
        
        if not output_filename:
            output_filename = 'converted_' + original_filename
        else:
            output_filename = secure_filename(output_filename)
        output_filepath = os.path.join(app.config['CONVERTED_FOLDER'], unique_prefix + "_" + output_filename)
        
        success, message = convert_file(input_filepath, output_filepath, compress=compress, advanced=advanced, options=options)
        if not success:
            return jsonify(success=False, message=message), 500
        
        download_url = url_for('download_file', filename=os.path.basename(output_filepath), _external=True)
        return jsonify(success=True, message=message, download_url=download_url)
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['CONVERTED_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=False)
