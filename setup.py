# First time setup of repository

import os
import sys 
import subprocess

# Set up blank venv
def setup_venv():
    try:
        if sys.executable is None:
            print("Error: sys.executable is None.  Unable to determine Python interpreter path.")
            return False
        command = [sys.executable, "-m", "venv", "myenv"]
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        if result.returncode == 0:
                print("New venv created!")
                return True
        else:
            print("Error: Virtual environment creation failed.")
            print(f"Return code: {result.returncode}")
            if result.stdout:
                print("--- Venv Creation Standard Output ---")
                print(result.stdout)
                print("-----------------------------------")
            if result.stderr: 
                print("--- Venv Creation Standard Error ---")
                print(result.stderr)
                print("----------------------------------")
                return False
    except FileNotFoundError:
        print("venv module was not found")
        return False
    except Exception as e:
        print("Unexpected error in setting up venv:", e)
        return False 

# Install correct packages 
def setup_packages():
    print("Install packages")
    pip_exe = "myenv/bin/pip"
    install_command = [pip_exe,"install","-r","requirements.txt"]
    try:
        result = subprocess.run(install_command,check=True,capture_output=True, text=True)
        if result.stdout:
            print("Pip:", result.stdout)
            return True
    except Exception as e:
         print("Unexpected error in setting up packages:", e)
    print("Install command is ", install_command)
    return True

if __name__ == '__main__':
    if not setup_venv(): sys.exit(1)
    if not setup_packages(): sys.exit(1)
    print("Setup complete!")
    print("To activate your venv to run")
    print("Please run: source myenv/bin/activate")
    sys.exit(0)
