import os
import subprocess
import re
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Ensure the output directories exists
output_dir = os.path.join(os.path.dirname(__file__), '../iteration/output_files')
os.makedirs(output_dir, exist_ok=True)
training_data_dir = os.path.join(os.path.dirname(__file__), '../models/Veronica/training_data')
os.makedirs(training_data_dir, exist_ok=True)


def list_files_and_directories(root_directory):
    """
    List all files and directories within the root_directory.
    Returns a dictionary with files and directories.

    Parameters:
        root_directory (str): The root directory to search for files and directories.

    Returns:
        dict: A dictionary containing lists of files and directories.
    """
    files_and_dirs = {
        "files": [],
        "directories": []
    }

    for root, dirs, files in os.walk(root_directory):
        for name in files:
            files_and_dirs["files"].append({
                "path": os.path.join(root, name),
                "type": os.path.splitext(name)[1].lower()  # File extension
            })
        for name in dirs:
            files_and_dirs["directories"].append(os.path.join(root, name))

    return files_and_dirs

def extract_imports(file_content):
    """
    Extract import statements from the given file content.
    Returns a set of imported modules.

    Parameters:
        file_content (str): The content of the code file.

    Returns:
        set: A set of imported modules or packages.
    """
    imports = re.findall(r'^\s*import\s+(\S+)|^\s*from\s+(\S+)', file_content, re.MULTILINE)
    return set(imp[0] or imp[1] for imp in imports)

def analyze_dependencies(root_directory):
    """
    Analyze dependencies for all Python files in the root_directory.
    Returns a set of all imported modules.

    Parameters:
        root_directory (str): The root directory to analyze for dependencies.

    Returns:
        set: A set of all imported modules or packages.
    """
    files_and_dirs = list_files_and_directories(root_directory)
    dependencies = set()

    for file in files_and_dirs["files"]:
        file_path = file["path"]
        if file["type"] == '.py':  # Only analyze Python files
            with open(file_path, 'r') as f:
                content = f.read()
                imports = extract_imports(content)
                dependencies.update(imports)

    return dependencies

def update_requirements(dependencies, requirements_file="requirements.txt"):
    """
    Update the requirements.txt file with the given dependencies.

    Parameters:
        dependencies (set): The set of dependencies to write to the file.
        requirements_file (str): The name of the requirements file.
    """
    output_path = os.path.join(output_dir, requirements_file)
    with open(output_path, 'w') as f:
        for dependency in dependencies:
            f.write(f"{dependency}\n")

def verify_dependencies(requirements_file="requirements.txt"):
    """
    Verify if the dependencies listed in the requirements file are installed.
    Installs any missing dependencies.

    Parameters:
        requirements_file (str): The name of the requirements file to verify.
    """
    requirements_path = os.path.join(output_dir, requirements_file)
    with open(requirements_path, 'r') as f:
        dependencies = f.readlines()

    for dependency in dependencies:
        dependency = dependency.strip()
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'show', dependency])
            logging.info(f"Dependency {dependency} is installed.")
        except subprocess.CalledProcessError:
            logging.info(f"Dependency {dependency} is not installed. Installing...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', dependency])

if __name__ == "__main__":
    root_directory = os.getenv('ROOT_DIRECTORY')
    if not root_directory:
        logging.error("ROOT_DIRECTORY environment variable is not set.")
    else:
        dependencies = analyze_dependencies(root_directory)
        update_requirements(dependencies)
        verify_dependencies()
