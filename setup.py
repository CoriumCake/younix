import subprocess
import sys
import os
from time import sleep

def clear_screen():
    """Clear the terminal screen in a cross-platform way"""
    os.system('cls' if os.name == 'nt' else 'clear')

def check_pip():
    """Check if pip is installed and install if necessary"""
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], check=True, capture_output=True)
        print("✓ pip is already installed")
        return True
    except subprocess.CalledProcessError:
        print("× pip is not installed. Installing pip...")
        try:
            # Download get-pip.py
            subprocess.run([sys.executable, "-c", 
                "import urllib.request; urllib.request.urlretrieve("
                "'https://bootstrap.pypa.io/get-pip.py', 'get-pip.py')"], check=True)
            
            # Install pip
            subprocess.run([sys.executable, "get-pip.py"], check=True)
            
            # Clean up
            os.remove("get-pip.py")
            print("✓ pip has been installed successfully")
            return True
        except Exception as e:
            print(f"Error installing pip: {e}")
            return False

def install_requirements():
    """Install packages from requirements.txt"""
    try:
        print("Installing required packages...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✓ All packages installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing requirements: {e}")
        return False
    except FileNotFoundError:
        print("× requirements.txt not found in the current directory")
        return False

def main():
    clear_screen()
    print("Setting up YouNix...")
    sleep(1)
    
    if not check_pip():
        print("Failed to set up pip. Please install pip manually.")
        return
    
    if not install_requirements():
        print("Failed to install requirements. Please check requirements.txt")
        return
    
    print("\nSetup completed successfully!")
    print("Starting YouNix...")
    sleep(2)
    clear_screen()
    
    try:
        subprocess.run([sys.executable, "main.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running main.py: {e}")
    except FileNotFoundError:
        print("× main.py not found in the current directory")

if __name__ == "__main__":
    main()