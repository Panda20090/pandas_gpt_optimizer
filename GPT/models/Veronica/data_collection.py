import os
import json

def collect_data(log_directory, output_file):
    """
    Collect data from log files and save it to a JSON file.

    Parameters:
        log_directory (str): Directory containing the log files.
        output_file (str): Path to the output JSON file.
    """
    data = []

    for root, _, files in os.walk(log_directory):
        for name in files:
            if name.endswith(".txt"):
                file_path = os.path.join(root, name)
                with open(file_path, 'r') as file:
                    content = file.read()
                    data.append({"file": name, "content": content})

    with open(output_file, 'w') as out_file:
        json.dump(data, out_file, indent=4)

    print(f"Data collected and saved to {output_file}")

if __name__ == "__main__":
    # Define the directories for output and training data
    iteration_output_dir = "../GPT/iteration/output_files"
    veronica_training_data_dir = "../models/Veronica/training_data"

    # Ensure directories exist
    os.makedirs(iteration_output_dir, exist_ok=True)
    os.makedirs(veronica_training_data_dir, exist_ok=True)

    # Collect data for iteration output
    log_directory = iteration_output_dir
    output_file = os.path.join(iteration_output_dir, "training_data.json")
    collect_data(log_directory, output_file)

    # Collect data for Veronica's training
    log_directory = iteration_output_dir
    output_file = os.path.join(veronica_training_data_dir, "training_data.json")
    collect_data(log_directory, output_file)
