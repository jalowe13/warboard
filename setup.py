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
    if sys.platform == "win32":
        pip_exe = os.path.join("myenv", "Scripts", "pip.exe")
    else:
        pip_exe = os.path.join("myenv", "bin", "pip")
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

# Check and install ollama
def setup_ollama():
    # Check if ollama is already installed
    try:
        check_result = subprocess.run(["ollama", "--version"], capture_output=True, text=True, check=False)
        if check_result.returncode == 0:
            print("Ollama is already installed!")
            return True
    except Exception as e:
        install_cmd = "curl -fsSL https://ollama.com/install.sh | sh" 
        result = subprocess.run(install_cmd, shell=True, text=True, capture_output=True)
        if result.stdout:
            print("--- Ollama Install Script STDOUT ---")
            print(result.stdout)
            print("------------------------------------")
        if result.stderr:
            print("--- Ollama Install Script STDERR ---")
            print(result.stderr) # This might contain errors from curl or sh, or from the script
            print("------------------------------------")

        if result.returncode == 0:
            print("Ollama installation script executed. Verification will follow.")
            return True # Indicates the command itself ran without the shell erroring out.
        else:
            print(f"Ollama installation script execution failed with return code {result.returncode}.")
            return False

# Prompt install question 
def prompt_model():
    choice = input("Would you like to install/run any models? [y/n]") 
    if choice == 'y':
        print("Got y")
        return True
    elif choice == 'n':
        print("Okay! No models to install...")
        return False
    print("Incorrect type input. Please choose y for yes or n for no")
    prompt_model()

# Model choice for install
def prompt_model_install():
    print("1. Deepseek R1 7b")
    print("2. Deepseek R1 8b")
    print("3. LLAMA 3.1 8b ")
    print("4. None")
    user_input_str = input("Enter your choice (1-4): ")
    model_to_run = None

    try:
        choice_int = int(user_input_str)

        match choice_int:
            case 1:
                model_to_run = "deepseek-r1:7b"
            case 2:
                model_to_run = "deepseek-r1:8b"
            case 3:
                print("Running llama3")
                model_to_run = "llama3.1:8b"
            case 4: # Default return for no selection
                return True 
            case _:
                print("Invalid numeric choice. Please select from the available options.")
                return False

    except ValueError:
        print("Invalid input: Please enter a number (1-4).")
        prompt_model_install()
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False

    if model_to_run is not None:
        try:
            result = subprocess.run(["ollama","run",model_to_run])
        except Exception as e:
            print(f"Ollama model execution failed {e}")
            
        return True
    return False

if __name__ == '__main__':
    if not setup_venv(): sys.exit(1)
    if not setup_packages(): sys.exit(1)
    if not setup_ollama(): sys.exit(1)
    install = prompt_model()
    if install:
        prompt_model_install()


    print("Setup complete!")
    print("To activate your venv to run")
    print("Please run: source myenv/bin/activate")
    print("Then you can play the game by running")
    print("python 3 Wargame.py")
    sys.exit(0)
