import os
import json
import subprocess
import re
import openai
import sys
import unittest
from tkinter import Tk, Text, Scrollbar, END

openai.api_key = os.getenv('API_KEY')  # Ensure to use environment variable for API key

# Ensure the test output directory exists
test_output_dir = os.path.join(os.path.dirname(__file__), 'test_output_files')
os.makedirs(test_output_dir, exist_ok=True)

def summarize_code(file_content):
    response = openai.Completion.create(
        model="gpt-4o-mini",
        prompt=f"Summarize the following code:\n\n{file_content}",
        temperature=0.5,
        max_tokens=150
    )
    return response.choices[0].text.strip()

def verify_code(file_content):
    response = openai.Completion.create(
        model="gpt-3.5-turbo-0125",
        prompt=f"Verify the following code and its dependencies:\n\n{file_content}",
        temperature=0.5,
        max_tokens=200
    )
    return response.choices[0].text.strip()

def get_corrections(file_content):
    response = openai.Completion.create(
        model="gpt-4o-mini",
        prompt=f"Provide corrections for the following code:\n\n{file_content}",
        temperature=0.5,
        max_tokens=150
    )
    return response.choices[0].text.strip()

def list_files_and_directories(root_directory):
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
    with open(file_path, 'r') as file:
        content = file.read()
        for i in range(0, len(content), chunk_size):
            yield content[i:i + chunk_size]

def save_file_list(root_directory, output_file="file_list.txt"):
    output_path = os.path.join(test_output_dir, output_file)
    files_and_dirs = list_files_and_directories(root_directory)

    with open(output_path, 'w') as file:
        json.dump(files_and_dirs, file, indent=4)

    print(f"File list saved to {output_path}")

    process_files(files_and_dirs)

def process_files(files_and_dirs):
    log_file_path = os.path.join(test_output_dir, "GPTlog.txt")
    corrections_file_path = os.path.join(test_output_dir, "corrections_list.txt")
    with open(log_file_path, 'w') as log_file, open(corrections_file_path, 'w') as corrections_file:
        corrections_file.write("Corrections:\n")
        for file in files_and_dirs["files"]:
            file_path = file["path"]
            if os.path.getsize(file_path) > 5000:
                process_large_file(file_path, log_file, corrections_file)
            else:
                process_small_file(file_path, log_file, corrections_file)

def process_large_file(file_path, log_file, corrections_file):
    chunk_number = 1
    for chunk in chunk_file(file_path):
        chunk_path = os.path.join(test_output_dir, f"{os.path.basename(file_path)}.chunk{chunk_number}")
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
    with open(file_path, 'r') as f:
        content = f.read()
        summary = summarize_code(content)
        verification = verify_code(content)
        corrections = get_corrections(content)
        log_file.write(f"File: {file_path}\nSummary:\n{summary}\n\nVerification:\n{verification}\n\n")
        if "Failed" in verification:
            corrections_file.write(f"{file_path} needs correction:\n{corrections}\n")

def extract_imports(file_content):
    imports = re.findall(r'^\s*import\s+(\S+)|^\s*from\s+(\S+)', file_content, re.MULTILINE)
    return set(imp[0] or imp[1] for imp in imports)

def analyze_dependencies(root_directory):
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
    output_path = os.path.join(test_output_dir, requirements_file)
    with open(output_path, 'w') as f:
        for dependency in dependencies:
            f.write(f"{dependency}\n")

def verify_dependencies(requirements_file="requirements.txt"):
    requirements_path = os.path.join(test_output_dir, requirements_file)
    with open(requirements_path, 'r') as f:
        dependencies = f.readlines()

    for dependency in dependencies:
        dependency = dependency.strip()
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'show', dependency])
            print(f"Dependency {dependency} is installed.")
        except subprocess.CalledProcessError:
            print(f"Dependency {dependency} is not installed. Installing...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', dependency])

def update_status_and_logs(root_directory):
    files_and_dirs = list_files_and_directories(root_directory)
    status_file_path = os.path.join(test_output_dir, "current_status.txt")
    test_file_path = os.path.join(test_output_dir, "test.txt")

    with open(status_file_path, 'w') as status_file, open(test_file_path, 'w') as test_file:
        for file in files_and_dirs["files"]:
            file_path = file["path"]
            with open(file_path, 'r') as f:
                content = f.read()
                verification = verify_code(content)
                status_file.write(f"File: {file_path}\nStatus: {'Verified' if 'Verified' in verification else 'Failed'}\n\n")
                test_file.write(f"Test: {file_path}\nResult: {'Pass' if 'Verified' in verification else 'Fail'}\n\n")

def compare_with_scope(scope_file="project_scope.txt"):
    scope_path = os.path.join(test_output_dir, scope_file)
    with open(scope_path, 'r') as file:
        scope_content = file.read()

    comparison_file_path = os.path.join(test_output_dir, "comparison.txt")
    with open(comparison_file_path, 'w') as comparison_file:
        comparison_file.write("Comparisons:\n")
        comparison_file.write(f"Scope:\n{scope_content}\n\n")
        # Add comparison logic here

def create_corrections(corrections_file="corrections_list.txt"):
    corrections_path = os.path.join(test_output_dir, corrections_file)
    with open(corrections_path, 'r') as file:
        corrections = file.readlines()

    for correction in corrections:
        # Implement correction logic here
        pass

def run_tests():
    result = subprocess.run(['python', '-m', 'unittest', 'discover', 'tests'], capture_output=True, text=True)
    test_results_path = os.path.join(test_output_dir, "test_results.txt")
    with open(test_results_path, 'w') as file:
        file.write(result.stdout)
    print(result.stdout)
    _display_test_output(result.stdout)

def _display_test_output(output):
    root = Tk()
    root.title("Test Output")

    text = Text(root)
    scroll = Scrollbar(root, command=text.yview)
    text.configure(yscrollcommand=scroll.set)
    text.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")

    text.insert(END, output)

    root.after(5000, root.destroy)  # Automatically close after 5 seconds
    root.mainloop()

class TestIterativeImprovement(unittest.TestCase):
    def setUp(self):
        self.root_directory = os.getenv('ROOT_DIRECTORY', 'path_to_test_root_directory')
        os.makedirs(self.root_directory, exist_ok=True)
        # Setup code to create test files and directories as needed

    def tearDown(self):
        # Cleanup code to remove test files and directories
        pass

    def test_save_file_list(self):
        save_file_list(self.root_directory)
        output_file = os.path.join(test_output_dir, "file_list.txt")
        self.assertTrue(os.path.exists(output_file))

    def test_analyze_dependencies(self):
        dependencies = analyze_dependencies(self.root_directory)
        self.assertIsInstance(dependencies, set)

    def test_update_requirements(self):
        dependencies = {"dependency1", "dependency2"}
        update_requirements(dependencies)
        requirements_file = os.path.join(test_output_dir, "requirements.txt")
        self.assertTrue(os.path.exists(requirements_file))

    def test_verify_dependencies(self):
        verify_dependencies()
        # Add assertions based on expected results

    def test_update_status_and_logs(self):
        update_status_and_logs(self.root_directory)
        status_file = os.path.join(test_output_dir, "current_status.txt")
        self.assertTrue(os.path.exists(status_file))

    def test_compare_with_scope(self):
        compare_with_scope()
        comparison_file = os.path.join(test_output_dir, "comparison.txt")
        self.assertTrue(os.path.exists(comparison_file))

    def test_create_corrections(self):
        create_corrections()
        corrections_file = os.path.join(test_output_dir, "corrections_list.txt")
        self.assertTrue(os.path.exists(corrections_file))

    def test_run_tests(self):
        run_tests()
        test_results_file = os.path.join(test_output_dir, "test_results.txt")
        self.assertTrue(os.path.exists(test_results_file))

if __name__ == "__main__":
    unittest.main()

