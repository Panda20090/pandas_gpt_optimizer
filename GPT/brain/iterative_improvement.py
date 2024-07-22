import os
import json
import subprocess
import re
import openai
import sys
import logging
import time


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Ensure the OpenAI API key is set via environment variable
openai.api_key = os.getenv('API_KEY')

# Ensure the output directory exists
output_dir = os.path.join(os.path.dirname(__file__), '../iteration/output_files')
os.makedirs(output_dir, exist_ok=True)

# Ensure the training data directory exists
training_data_dir = os.path.join(os.path.dirname(__file__), '../models/Veronica/training_data')
os.makedirs(training_data_dir, exist_ok=True)

def summarize_code(file_content):
    """
    Summarize the provided code content using OpenAI API.
    
    Parameters:
        file_content (str): The content of the code file.

    Returns:
        str: Summary of the code.
    """
    try:
        response = openai.Completion.create(
            model="gpt-4o-mini",
            prompt=f"Summarize the following code:\n\n{file_content}",
            temperature=0.5,
            max_tokens=150
        )
        summary = response.choices[0].text.strip()
        log_training_data('summarize', file_content, summary)
        return summary
    except Exception as e:
        logging.error(f"Error summarizing code: {e}")
        return ""

def verify_code(file_content):
    """
    Verify the provided code content using OpenAI API.
    
    Parameters:
        file_content (str): The content of the code file.

    Returns:
        str: Verification result of the code.
    """
    try:
        response = openai.Completion.create(
            model="gpt-3.5-turbo-0125",
            prompt=f"Verify the following code and its dependencies:\n\n{file_content}",
            temperature=0.5,
            max_tokens=200
        )
        verification = response.choices[0].text.strip()
        log_training_data('verify', file_content, verification)
        return verification
    except Exception as e:
        logging.error(f"Error verifying code: {e}")
        return ""

def get_corrections(file_content):
    """
    Get corrections for the provided code content using OpenAI API.
    
    Parameters:
        file_content (str): The content of the code file.

    Returns:
        str: Corrections for the code.
    """
    try:
        response = openai.Completion.create(
            model="gpt-4o-mini",
            prompt=f"Provide corrections for the following code:\n\n{file_content}",
            temperature=0.5,
            max_tokens=150
        )
        corrections = response.choices[0].text.strip()
        log_training_data('corrections', file_content, corrections)
        return corrections
    except Exception as e:
        logging.error(f"Error getting corrections for code: {e}")
        return ""
    
def log_training_data(operation, input_data, output_data):
    """
    Log training data for the Veronica model.

    Parameters:
        operation (str): The operation performed (summarize, verify, corrections).
        input_data (str): The input data provided to the model.
        output_data (str): The output data generated by the model.
    """
    log_entry = {
        'operation': operation,
        'input': input_data,
        'output': output_data
    }
    log_file = os.path.join(training_data_dir, f"{operation}_{int(time.time())}.json")
    with open(log_file, 'w') as f:
        json.dump(log_entry, f, indent=4)

def list_files_and_directories(root_directory):
    """
    List all files and directories within the root_directory.
    
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

def chunk_file(file_path, chunk_size=5000):
    """
    Chunk a file into smaller parts.
    
    Parameters:
        file_path (str): Path to the file.
        chunk_size (int): Size of each chunk in characters.

    Yields:
        str: Chunk of file content.
    """
    with open(file_path, 'r') as file:
        content = file.read()
        for i in range(0, len(content), chunk_size):
            yield content[i:i + chunk_size]

def save_file_list(root_directory, output_file="file_list.txt"):
    """
    Save a list of files and directories in the root directory to a JSON file.
    
    Parameters:
        root_directory (str): The root directory to list files and directories from.
        output_file (str): The name of the output file.
    """
    output_path = os.path.join(output_dir, output_file)
    files_and_dirs = list_files_and_directories(root_directory)

    with open(output_path, 'w') as file:
        json.dump(files_and_dirs, file, indent=4)

    logging.info(f"File list saved to {output_path}")

    process_files(files_and_dirs)

def process_files(files_and_dirs):
    """
    Process each file by summarizing and verifying it. Logs the results.
    
    Parameters:
        files_and_dirs (dict): A dictionary containing lists of files and directories.
    """
    log_file_path = os.path.join(output_dir, "GPTlog.txt")
    corrections_file_path = os.path.join(output_dir, "corrections_list.txt")

    with open(log_file_path, 'w') as log_file, open(corrections_file_path, 'w') as corrections_file:
        corrections_file.write("Corrections:\n")
        for file in files_and_dirs["files"]:
            file_path = file["path"]
            if os.path.getsize(file_path) > 5000:
                process_large_file(file_path, log_file, corrections_file)
            else:
                process_small_file(file_path, log_file, corrections_file)

def process_large_file(file_path, log_file, corrections_file):
    """
    Process a large file by chunking, summarizing, and verifying each chunk.
    
    Parameters:
        file_path (str): Path to the file.
        log_file (file): Log file to write summaries and verifications.
        corrections_file (file): File to log corrections needed.
    """
    chunk_number = 1
    for chunk in chunk_file(file_path):
        chunk_path = os.path.join(output_dir, f"{os.path.basename(file_path)}.chunk{chunk_number}")
        with open(chunk_path, 'w') as chunk_file:
            chunk_file.write(chunk)
        summary = summarize_code(chunk)
        verification = verify_code(chunk)
        corrections = get_corrections(chunk)
        log_file.write(f"File: {chunk_path}\nSummary:\n{summary}\n\nVerification:\n{verification}\n\n")
        if "Failed" in verification:
            corrections_file.write(f"{chunk_path} needs correction:\n{corrections}\n")
        chunk_number += 1

def process_small_file(file_path, log_file, corrections_file):
    """
    Process a small file by summarizing and verifying it.
    
    Parameters:
        file_path (str): Path to the file.
        log_file (file): Log file to write summaries and verifications.
        corrections_file (file): File to log corrections needed.
    """
    with open(file_path, 'r') as f:
        content = f.read()
        summary = summarize_code(content)
        verification = verify_code(content)
        corrections = get_corrections(content)
        log_file.write(f"File: {file_path}\nSummary:\n{summary}\n\nVerification:\n{verification}\n\n")
        if "Failed" in verification:
            corrections_file.write(f"{file_path} needs correction:\n{corrections}\n")

def extract_imports(file_content):
    """
    Extract import statements from the given file content.
    
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

def update_status_and_logs(root_directory):
    """
    Update the status and logs for all files in the root_directory.
    
    Parameters:
        root_directory (str): The root directory to update status and logs for.
    """
    files_and_dirs = list_files_and_directories(root_directory)
    status_file_path = os.path.join(output_dir, "current_status.txt")
    test_file_path = os.path.join(output_dir, "test.txt")

    with open(status_file_path, 'w') as status_file, open(test_file_path, 'w') as test_file:
        for file in files_and_dirs["files"]:
            file_path = file["path"]
            with open(file_path, 'r') as f:
                content = f.read()
                verification = verify_code(content)
                status_file.write(f"File: {file_path}\nStatus: {'Verified' if 'Verified' in verification else 'Failed'}\n\n")
                test_file.write(f"Test: {file_path}\nResult: {'Pass' if 'Verified' in verification else 'Fail'}\n\n")

def compare_with_scope(scope_file="project_scope.txt"):
    """
    Compare current project status with the project scope.
    
    Parameters:
        scope_file (str): The name of the project scope file.
    """
    scope_path = os.path.join(output_dir, scope_file)
    with open(scope_path, 'r') as file:
        scope_content = file.read()

    comparison_file_path = os.path.join(output_dir, "comparison.txt")
    with open(comparison_file_path, 'w') as comparison_file:
        comparison_file.write("Comparisons:\n")
        comparison_file.write(f"Scope:\n{scope_content}\n\n")
        # Add comparison logic here

def create_corrections(corrections_file="corrections_list.txt"):
    """
    Create corrections based on the corrections list file.
    
    Parameters:
        corrections_file (str): The name of the corrections list file.
    """
    corrections_path = os.path.join(output_dir, corrections_file)
    with open(corrections_path, 'r') as file:
        corrections = file.readlines()

    for correction in corrections:
        # Implement correction logic here
        pass

def run_tests():
    """
    Run unit tests and capture the output.
    """
    result = subprocess.run(['python', '-m', 'unittest', 'discover', 'tests'], capture_output=True, text=True)
    test_results_path = os.path.join(output_dir, "test_results.txt")
    with open(test_results_path, 'w') as file:
        file.write(result.stdout)
    logging.info(result.stdout)

if __name__ == "__main__":
    root_directory = os.getenv('ROOT_DIRECTORY')
    if not root_directory:
        logging.error("ROOT_DIRECTORY environment variable is not set.")
    else:
        save_file_list(root_directory)
        dependencies = analyze_dependencies(root_directory)
        update_requirements(dependencies)
        verify_dependencies()
        update_status_and_logs(root_directory)
        compare_with_scope()
        create_corrections()
        # Commenting out run_tests() since initial tests are run on startup
        # run_tests()

