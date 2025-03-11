import os
from flask import Flask, render_template, request, send_from_directory, redirect, url_for, flash, jsonify
from converter import convert_file

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
app.config['CONVERTED_FOLDER'] = os.path.join(os.getcwd(), 'converted')
app.secret_key = 'your-secret-key'  # Replace with a secure secret key

# Ensure required directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['CONVERTED_FOLDER'], exist_ok=True)

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
    
    # Get parameters from form
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
            options['target_size'] = int(float(target_size) * 1024)  # KB to bytes
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
    
    # Save the uploaded file
    input_filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(input_filepath)
    
    if not output_filename:
        output_filename = 'converted_' + file.filename
    output_filepath = os.path.join(app.config['CONVERTED_FOLDER'], output_filename)
    
    # Convert the file
    success, message = convert_file(input_filepath, output_filepath, compress=compress, advanced=advanced, options=options)
    if not success:
        flash("Conversion error: " + message)
        return redirect(url_for('index'))
    
    return send_from_directory(directory=app.config['CONVERTED_FOLDER'],
                               path=output_filename,
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
        
        input_filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(input_filepath)
        
        if not output_filename:
            output_filename = 'converted_' + file.filename
        output_filepath = os.path.join(app.config['CONVERTED_FOLDER'], output_filename)
        
        success, message = convert_file(input_filepath, output_filepath, compress=compress, advanced=advanced, options=options)
        if not success:
            return jsonify(success=False, message=message), 500
        
        download_url = url_for('download_file', filename=output_filename, _external=True)
        return jsonify(success=True, message=message, download_url=download_url)
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['CONVERTED_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
