import os
import subprocess
import sys
import urllib.request
import zipfile
import shutil

def run(command):
    print(f"🔧 Running: {command}")
    subprocess.check_call(command, shell=True)

def install_python_packages():
    packages = [
        "torch==2.7.0",
        "torch-directml==2.6.0",
        "Flask",
        "Pillow",
        "pydub",
        "moviepy",
        "pypandoc",
        "python-magic",
        "werkzeug"
    ]
    print("\n📦 Installing Python packages...\n")
    run(f"{sys.executable} -m pip install --upgrade pip")
    run(f"{sys.executable} -m pip install " + " ".join(packages))

def install_ffmpeg_choco():
    try:
        print("🧪 Checking for Chocolatey...")
        subprocess.check_call("choco -v", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("🍫 Chocolatey detected. Installing FFmpeg...")
        run("choco install ffmpeg -y")
        return True
    except subprocess.CalledProcessError:
        print("⚠️ Chocolatey not found.")
        return False

def install_ffmpeg_manual():
    print("\n🌐 Downloading FFmpeg (manual install)...")
    url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    zip_path = "ffmpeg.zip"
    install_dir = "C:\\ffmpeg"

    urllib.request.urlretrieve(url, zip_path)
    print("📦 Extracting FFmpeg...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall("ffmpeg_temp")

    for folder in os.listdir("ffmpeg_temp"):
        if folder.startswith("ffmpeg"):
            shutil.move(f"ffmpeg_temp/{folder}", install_dir)
            break

    shutil.rmtree("ffmpeg_temp")
    os.remove(zip_path)

    # Add to PATH for current session
    bin_path = os.path.join(install_dir, "bin")
    os.environ["PATH"] += os.pathsep + bin_path
    print(f"✅ FFmpeg installed at: {bin_path}")
    print("⚠️ Please add this to your system PATH manually or use a launcher script.")

def main():
    print("💻 Starting Windows dependency installer...\n")
    install_python_packages()

    if not install_ffmpeg_choco():
        install_ffmpeg_manual()

    print("\n✅ All dependencies installed successfully!")

if __name__ == "__main__":
    main()
