import os
import shutil
import uuid
from io import BytesIO
from PIL import Image
from pydub import AudioSegment
import logging
from moviepy.editor import VideoFileClip
import pypandoc

logger = logging.getLogger(__name__)

# Define allowed base directories
SAFE_UPLOAD_DIR = os.path.abspath(os.path.join(os.getcwd(), 'uploads'))
SAFE_OUTPUT_DIR = os.path.abspath(os.path.join(os.getcwd(), 'converted'))


def is_safe_path(base_dir, path):
    try:
        return os.path.commonpath([os.path.abspath(path), base_dir]) == base_dir
    except Exception as e:
        logger.warning(f"Path safety check failed: {e}")
        return False


def sanitize_path(path):
    return os.path.normpath(os.path.abspath(path))


def convert_image(input_path, output_path, compress=False, advanced=False, options=None):
    if options is None:
        options = {}
    try:
        input_path = sanitize_path(input_path)
        output_path = sanitize_path(output_path)
        # ensure both paths are under their safe dirs
        if not (is_safe_path(SAFE_UPLOAD_DIR, input_path) and is_safe_path(SAFE_OUTPUT_DIR, output_path)):
            raise ValueError("Invalid input or output path")

        img = Image.open(input_path)
        ext = os.path.splitext(output_path)[1].lower()

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
                logger.info(f"Image converted with advanced compression at quality {quality}")
                return True, f"Image converted with advanced compression (quality={quality})"
            else:
                img.save(output_path, quality=min_quality)
                logger.info(f"Image converted with advanced compression at minimum quality {min_quality}")
                return True, f"Image converted with advanced compression (min quality={min_quality})"
        elif compress and ext in ['.jpg', '.jpeg']:
            quality = options.get('quality', 85)
            img.save(output_path, quality=quality)
        else:
            img.save(output_path)
        logger.info(f"Image conversion successful for {output_path}")
        return True, "Image conversion successful"
    except Exception as e:
        logger.exception("Error converting image")
        return False, str(e)


def convert_audio(input_path, output_path, advanced=False, options=None):
    if options is None:
        options = {}
    try:
        input_path = sanitize_path(input_path)
        output_path = sanitize_path(output_path)
        # ensure safe paths
        if not (is_safe_path(SAFE_UPLOAD_DIR, input_path) and is_safe_path(SAFE_OUTPUT_DIR, output_path)):
            raise ValueError("Invalid input or output path")

        audio = AudioSegment.from_file(input_path)
        fmt = os.path.splitext(output_path)[1].replace('.', '')
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
                logger.info(f"Audio converted with advanced compression at bitrate {chosen_bitrate}")
                return True, f"Audio converted with advanced compression (bitrate={chosen_bitrate})"
            audio.export(output_path, format=fmt, bitrate=candidate_bitrates[-1])
            logger.info(f"Audio converted with advanced compression at minimum bitrate {candidate_bitrates[-1]}")
            return True, f"Audio converted with advanced compression (minimum bitrate={candidate_bitrates[-1]})"
        else:
            export_args = {}
            if 'target_bitrate' in options:
                export_args['bitrate'] = options['target_bitrate']
            audio.export(output_path, format=fmt, **export_args)
            logger.info(f"Audio conversion successful for {output_path}")
            return True, "Audio conversion successful"
    except Exception as e:
        logger.exception("Error converting audio")
        return False, str(e)


def convert_video(input_path, output_path, advanced=False, options=None):
    if options is None:
        options = {}
    try:
        input_path = sanitize_path(input_path)
        output_path = sanitize_path(output_path)
        # ensure safe paths
        if not (is_safe_path(SAFE_UPLOAD_DIR, input_path) and is_safe_path(SAFE_OUTPUT_DIR, output_path)):
            raise ValueError("Invalid input or output path")

        clip = VideoFileClip(input_path)
        ext = os.path.splitext(output_path)[1].replace('.', '').lower()
        codec = 'libx264'
        write_kwargs = {}

        if advanced:
            if 'target_resolution' in options:
                write_kwargs['resolution'] = options['target_resolution']
            if 'target_bitrate' in options:
                write_kwargs['bitrate'] = options['target_bitrate']
            if 'gpu' in options:
                if options['gpu'] == 'nvidia':
                    codec = 'h264_nvenc'
                elif options['gpu'] == 'amd':
                    codec = 'h264_vaapi'
                    write_kwargs['ffmpeg_params'] = ['-vaapi_device', '/dev/dri/renderD128', '-vf', 'format=nv12|vaapi,hwupload']

        clip.write_videofile(output_path, codec=codec, audio_codec='aac', **write_kwargs)
        clip.close()
        logger.info(f"Video conversion successful for {output_path}")
        return True, "Video conversion successful"
    except Exception as e:
        logger.exception("Error converting video")
        return False, str(e)


def convert_document(input_path, output_path, advanced=False, options=None):
    try:
        input_path = sanitize_path(input_path)
        output_path = sanitize_path(output_path)
        # ensure safe paths
        if not (is_safe_path(SAFE_UPLOAD_DIR, input_path) and is_safe_path(SAFE_OUTPUT_DIR, output_path)):
            raise ValueError("Invalid input or output path")

        ext = os.path.splitext(output_path)[1].replace('.', '')
        output = pypandoc.convert_file(input_path, to=ext)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output)
        logger.info(f"Document conversion successful for {output_path}")
        return True, "Document conversion successful"
    except Exception as e:
        logger.exception("Error converting document")
        return False, str(e)


def fallback_convert(input_path, output_path, advanced=False, options=None):
    try:
        input_path = sanitize_path(input_path)
        output_path = sanitize_path(output_path)
        # ensure safe paths
        if not (is_safe_path(SAFE_UPLOAD_DIR, input_path) and is_safe_path(SAFE_OUTPUT_DIR, output_path)):
            raise ValueError("Invalid input or output path")

        shutil.copy(input_path, output_path)
        logger.info(f"Fallback conversion: file copied to {output_path}")
        return True, "File copied without conversion (unsupported file type)"
    except Exception as e:
        logger.exception("Error in fallback conversion")
        return False, str(e)


def convert_file(input_path, output_path, compress=False, advanced=False, options=None):
    input_path = sanitize_path(input_path)
    output_path = sanitize_path(output_path)
    # ensure safe paths
    if not (is_safe_path(SAFE_UPLOAD_DIR, input_path) and is_safe_path(SAFE_OUTPUT_DIR, output_path)):
        raise ValueError("Invalid input or output path")

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
