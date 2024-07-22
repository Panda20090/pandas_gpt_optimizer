import os
import json

def read_json(file_path):
    """
    Read a JSON file and return its contents.

    Parameters:
        file_path (str): Path to the JSON file.

    Returns:
        dict: Contents of the JSON file.
    """
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error reading JSON file {file_path}: {e}")
        return {}

def save_json(data, file_path):
    """
    Save data to a JSON file.

    Parameters:
        data (dict): Data to save.
        file_path (str): Path to the JSON file.
    """
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
        print(f"Data successfully saved to {file_path}")
    except Exception as e:
        print(f"Error saving JSON file {file_path}: {e}")

def create_directory(dir_path):
    """
    Create a directory if it doesn't exist.

    Parameters:
        dir_path (str): Path to the directory.
    """
    try:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(f"Directory created at {dir_path}")
        else:
            print(f"Directory already exists at {dir_path}")
    except Exception as e:
        print(f"Error creating directory {dir_path}: {e}")

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

    try:
        for root, dirs, files in os.walk(root_directory):
            for name in files:
                files_and_dirs["files"].append({
                    "path": os.path.join(root, name),
                    "type": os.path.splitext(name)[1].lower()  # File extension
                })
            for name in dirs:
                files_and_dirs["directories"].append(os.path.join(root, name))

        print(f"Files and directories listed in {root_directory}")
    except Exception as e:
        print(f"Error listing files and directories in {root_directory}: {e}")

    return files_and_dirs

def summarize_files(files_and_dirs, summarize_func):
    """
    Summarize the content of each file and log the summaries.
    
    Parameters:
        files_and_dirs (dict): A dictionary containing lists of files and directories.
        summarize_func (function): Function to summarize the content of a file.
    """
    log_file_path = os.path.join('GPT/iteration/output_files', "GPTlog.txt")
    try:
        with open(log_file_path, 'w') as log_file:
            for file in files_and_dirs["files"]:
                file_path = file["path"]
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                        summary = summarize_func(content)
                        log_file.write(f"File: {file_path}\nSummary:\n{summary}\n\n")
                except Exception as e:
                    print(f"Error reading file {file_path}: {e}")
        print(f"Summaries saved to {log_file_path}")
    except Exception as e:
        print(f"Error writing to log file {log_file_path}: {e}")
