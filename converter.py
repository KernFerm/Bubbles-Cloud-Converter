import os
import shutil
from io import BytesIO
from PIL import Image
from pydub import AudioSegment

def convert_image(input_path, output_path, compress=False, advanced=False, options=None):
    """
    Convert an image to the desired format.
    Supports basic compression (JPEG quality) and advanced compression via iterative quality reduction
    to meet a target file size.
    """
    if options is None:
        options = {}
    try:
        img = Image.open(input_path)
        ext = os.path.splitext(output_path)[1].lower()
        
        # Advanced compression for JPEG images with target size
        if advanced and 'target_size' in options and ext in ['.jpg', '.jpeg']:
            target_size = options.get('target_size')
            quality = 95
            quality_step = 5
            min_quality = 20
            best_data = None
            while quality >= min_quality:
                temp_io = BytesIO()
                img.save(temp_io, format='JPEG', quality=quality)
                size = temp_io.tell()
                if size <= target_size:
                    best_data = temp_io.getvalue()
                    break
                quality -= quality_step
            if best_data:
                with open(output_path, 'wb') as f:
                    f.write(best_data)
                return True, f"Image converted with advanced compression (quality={quality})"
            else:
                img.save(output_path, quality=min_quality)
                return True, f"Image converted with advanced compression (min quality={min_quality})"
        # Basic compression for JPEG images
        elif compress and ext in ['.jpg', '.jpeg']:
            quality = options.get('quality', 85)
            img.save(output_path, quality=quality)
        else:
            img.save(output_path)
        return True, "Image conversion successful"
    except Exception as e:
        return False, str(e)

def convert_audio(input_path, output_path, advanced=False, options=None):
    """
    Convert an audio file.
    Allows specifying a target bitrate if advanced compression is enabled.
    If a target file size is provided, iteratively reduce bitrate.
    """
    if options is None:
        options = {}
    try:
        audio = AudioSegment.from_file(input_path)
        fmt = os.path.splitext(output_path)[1].replace('.', '')
        # Advanced iterative compression for audio if target_size is provided
        if advanced and 'target_size' in options:
            target_size = options.get('target_size')
            candidate_bitrates = ["320k", "256k", "192k", "128k", "96k"]
            best_data = None
            chosen_bitrate = None
            for br in candidate_bitrates:
                temp_io = BytesIO()
                audio.export(temp_io, format=fmt, bitrate=br)
                size = temp_io.tell()
                if size <= target_size:
                    best_data = temp_io.getvalue()
                    chosen_bitrate = br
                    break
            if best_data:
                with open(output_path, 'wb') as f:
                    f.write(best_data)
                return True, f"Audio converted with advanced compression (bitrate={chosen_bitrate})"
            # If not below target, use the lowest bitrate candidate
            audio.export(output_path, format=fmt, bitrate=candidate_bitrates[-1])
            return True, f"Audio converted with advanced compression (minimum bitrate={candidate_bitrates[-1]})"
        else:
            # Use target_bitrate if provided (basic advanced option)
            export_args = {}
            if 'target_bitrate' in options:
                export_args['bitrate'] = options['target_bitrate']
            audio.export(output_path, format=fmt, **export_args)
            return True, "Audio conversion successful"
    except Exception as e:
        return False, str(e)

def convert_video(input_path, output_path, advanced=False, options=None):
    """
    Convert a video file using MoviePy.
    Supports additional formats and, if advanced options are provided,
    target resolution, bitrate, and iterative bitrate reduction if target file size is provided.
    """
    if options is None:
        options = {}
    try:
        from moviepy.editor import VideoFileClip
        clip = VideoFileClip(input_path)
        ext = os.path.splitext(output_path)[1].replace('.', '').lower()
        codec = 'libx264' if ext == 'mp4' else None
        
        # Prepare write parameters
        write_kwargs = {}
        if advanced:
            if 'target_resolution' in options:
                write_kwargs['target_resolution'] = options['target_resolution']
            if 'target_bitrate' in options:
                write_kwargs['bitrate'] = options['target_bitrate']
        
        # If target file size is specified, try iterative bitrate reduction
        if advanced and 'target_size' in options:
            target_size = options.get('target_size')
            candidate_bitrates = ["2500k", "2000k", "1500k", "1000k", "500k"]
            chosen_bitrate = None
            best_success = False
            for br in candidate_bitrates:
                temp_out = output_path + ".temp"
                write_kwargs['bitrate'] = br
                clip.write_videofile(temp_out, codec=codec, audio_codec='aac', **write_kwargs, verbose=False, logger=None)
                if os.path.exists(temp_out):
                    size = os.path.getsize(temp_out)
                    if size <= target_size:
                        chosen_bitrate = br
                        os.rename(temp_out, output_path)
                        best_success = True
                        break
                    else:
                        os.remove(temp_out)
            if best_success:
                clip.close()
                return True, f"Video converted with advanced compression (bitrate={chosen_bitrate})"
            else:
                # Use the lowest candidate if none met target size
                clip.write_videofile(output_path, codec=codec, audio_codec='aac', bitrate=candidate_bitrates[-1], **write_kwargs)
                clip.close()
                return True, f"Video converted with advanced compression (minimum bitrate={candidate_bitrates[-1]})"
        else:
            clip.write_videofile(output_path, codec=codec, audio_codec='aac', **write_kwargs)
            clip.close()
            return True, "Video conversion successful"
    except Exception as e:
        return False, str(e)

def convert_document(input_path, output_path, advanced=False, options=None):
    """
    Convert a document using pypandoc.
    Advanced compression options are not applicable for document conversion.
    """
    try:
        import pypandoc
        ext = os.path.splitext(output_path)[1].replace('.', '')
        output = pypandoc.convert_file(input_path, to=ext)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output)
        return True, "Document conversion successful"
    except Exception as e:
        return False, str(e)

def fallback_convert(input_path, output_path, advanced=False, options=None):
    """
    Fallback conversion: simply copy the file if no conversion is supported.
    """
    try:
        shutil.copy(input_path, output_path)
        return True, "File copied without conversion (unsupported file type)"
    except Exception as e:
        return False, str(e)

def convert_file(input_path, output_path, compress=False, advanced=False, options=None):
    """
    Determine file type and perform conversion.
    Supports images, audio, video, documents (including spreadsheets and presentations),
    and falls back to a copy if conversion is unsupported.
    """
    if options is None:
        options = {}
    ext = os.path.splitext(input_path)[1].lower()
    if ext in ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff']:
        return convert_image(input_path, output_path, compress=compress, advanced=advanced, options=options)
    elif ext in ['.mp3', '.wav', '.flac', '.ogg', '.aac']:
        return convert_audio(input_path, output_path, advanced=advanced, options=options)
    elif ext in ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.mpeg', '.mpg']:
        return convert_video(input_path, output_path, advanced=advanced, options=options)
    elif ext in ['.doc', '.docx', '.odt', '.txt', '.html', '.md', '.pdf', '.xls', '.xlsx', '.ppt', '.pptx', '.csv']:
        return convert_document(input_path, output_path, advanced=advanced, options=options)
    else:
        return fallback_convert(input_path, output_path, advanced=advanced, options=options)
