import subprocess
import sys

def install_python_dependencies():
    # Update pip
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    
    # Install the required Python packages from requirements.txt
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    except Exception as e:
        print(f"Failed to install Python dependencies: {e}")

if __name__ == "__main__":
    install_python_dependencies()
