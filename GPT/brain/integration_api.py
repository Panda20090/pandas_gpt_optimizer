from flask import Flask, request, jsonify
import os
import json
import subprocess
import openai
import re
import sys
import logging
from datetime import datetime

from brain.dependency_analysis import verify_dependencies, analyze_dependencies
from tests.test_iterative_improvement import run_tests
from brain.iterative_improvement import update_requirements

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set OpenAI API key from environment variable
openai.api_key = os.getenv('API_KEY')

# Ensure the output directory exists
output_dir = os.path.join(os.path.dirname(__file__), '../output_files')
os.makedirs(output_dir, exist_ok=True)

# Training data directory
training_data_dir = os.path.join(os.path.dirname(__file__), '../models/Veronica/training_data')
os.makedirs(training_data_dir, exist_ok=True)

# Error log file
error_log_path = os.path.join(output_dir, "error.txt")

# Helper functions from existing scripts
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
        log_error(file_content, str(e))
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
        log_error(file_content, str(e))
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
        log_error(file_content, str(e))
        logging.error(f"Error getting corrections for code: {e}")
        return ""

def log_training_data(operation, input_data, output_data):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_entry = {
        'timestamp': timestamp,
        'operation': operation,
        'input': input_data,
        'output': output_data
    }
    log_file = os.path.join(training_data_dir, f"{operation}_{timestamp}.json")
    with open(log_file, 'w') as f:
        json.dump(log_entry, f, indent=4)

def log_error(input_data, error_message):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    error_entry = {
        'timestamp': timestamp,
        'input': input_data,
        'error': error_message
    }
    with open(error_log_path, 'a') as f:
        json.dump(error_entry, f, indent=4)
        f.write("\n")

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

def process_files(files_and_dirs):
    """
    Process each file by summarizing, verifying, and logging the results.
    
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

def batch_summarize(files):
    """
    Summarize a batch of files using OpenAI API.

    Parameters:
        files (list): List of file contents to summarize.

    Returns:
        list: List of summaries.
    """
    try:
        batch_requests = [
            {
                "model": "gpt-4o-mini",
                "prompt": f"Summarize the following code:\n\n{content}",
                "max_tokens": 150
            }
            for content in files
        ]
        response = openai.BatchCompletion.create(requests=batch_requests, timeout=86400)  # 24 hours
        return [res["choices"][0]["text"].strip() for res in response["data"]]
    except Exception as e:
        logging.error(f"Error in batch summarizing code: {e}")
        return []

def batch_verify(files):
    """
    Verify a batch of files using OpenAI API.

    Parameters:
        files (list): List of file contents to verify.

    Returns:
        list: List of verification results.
    """
    try:
        batch_requests = [
            {
                "model": "gpt-3.5-turbo-0125",
                "prompt": f"Verify the following code and its dependencies:\n\n{content}",
                "max_tokens": 200
            }
            for content in files
        ]
        response = openai.BatchCompletion.create(requests=batch_requests, timeout=86400)  # 24 hours
        return [res["choices"][0]["text"].strip() for res in response["data"]]
    except Exception as e:
        logging.error(f"Error in batch verifying code: {e}")
        return []

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

def process_large_file(file_path, log_file, corrections_file):
    """
    Process a large file by chunking, summarizing, verifying, and logging each chunk.
    
    Parameters:
        file_path (str): Path to the file.
        log_file (file): Log file to write summaries and verifications.
        corrections_file (file): File to log corrections needed.
    """
    chunk_number = 1
    chunks = list(chunk_file(file_path))
    summaries = batch_summarize(chunks)
    verifications = batch_verify(chunks)
    corrections = [get_corrections(chunk) for chunk in chunks]

    for chunk, summary, verification, correction in zip(chunks, summaries, verifications, corrections):
        chunk_path = os.path.join(output_dir, f"{os.path.basename(file_path)}.chunk{chunk_number}")
        with open(chunk_path, 'w') as chunk_file:
            chunk_file.write(chunk)
        log_file.write(f"File: {chunk_path}\nSummary:\n{summary}\n\nVerification:\n{verification}\n\n")
        if "Failed" in verification:
            corrections_file.write(f"{chunk_path} needs correction:\n{correction}\n")
        chunk_number += 1

def process_small_file(file_path, log_file, corrections_file):
    """
    Process a small file by summarizing, verifying, and logging it.
    
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


@app.route('/summarize', methods=['POST'])
def summarize():
    """
    API endpoint to summarize the provided content.
    """
    content = request.json.get('content')
    if content:
        summary = summarize_code(content)
        return jsonify({"summary": summary})
    return jsonify({"error": "No content provided"}), 400

@app.route('/verify', methods=['POST'])
def verify():
    """
    API endpoint to verify the provided content.
    """
    content = request.json.get('content')
    if content:
        verification = verify_code(content)
        return jsonify({"verification": verification})
    return jsonify({"error": "No content provided"}), 400

@app.route('/corrections', methods=['POST'])
def corrections():
    """
    API endpoint to get corrections for the provided content.
    """
    content = request.json.get('content')
    if content:
        corrections = get_corrections(content)
        return jsonify({"corrections": corrections})
    return jsonify({"error": "No content provided"}), 400

@app.route('/dependencies', methods=['GET'])
def dependencies():
    """
    API endpoint to get the list of dependencies for the project.
    """
    root_directory = os.getenv('ROOT_DIRECTORY')
    if root_directory:
        dependencies = analyze_dependencies(root_directory)
        return jsonify({"dependencies": list(dependencies)})
    return jsonify({"error": "Root directory not set"}), 400

@app.route('/update-requirements', methods=['POST'])
def update_requirements_endpoint():
    """
    API endpoint to update the requirements file with the provided dependencies.
    """
    dependencies = request.json.get('dependencies')
    if dependencies:
        update_requirements(set(dependencies))
        return jsonify({"message": "Requirements updated"})
    return jsonify({"error": "No dependencies provided"}), 400

@app.route('/verify-dependencies', methods=['POST'])
def verify_dependencies_endpoint():
    """
    API endpoint to verify and install any missing dependencies.
    """
    try:
        verify_dependencies()
        return jsonify({"message": "Dependencies verified and installed"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/run-tests', methods=['POST'])
def run_tests_endpoint():
    """
    API endpoint to run unit tests.
    """
    test_results = run_tests()
    return jsonify({"test_results": test_results})

if __name__ == '__main__':
    app.run(debug=True)
