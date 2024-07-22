import os
import subprocess
import sys
import platform
from tkinter import Tk, Text, Scrollbar, Button, Label, END
from dashboard import create_dashboard

def set_project_root():
    project_root = os.getenv('PROJECT_ROOT')
    if not project_root:
        project_root = input("Please enter the root directory of your project: ")
        os.environ['PROJECT_ROOT'] = project_root
    
    if not os.path.exists(project_root):
        print(f"The specified PROJECT_ROOT directory does not exist: {project_root}")
        sys.exit(1)
    
    return project_root

def get_api_key():
    api_key = os.getenv('API_KEY')
    if not api_key:
        api_key = input("Please enter your OpenAI API key: ")
        os.environ['API_KEY'] = api_key
    
    if not api_key:
        print("API_KEY is required.")
        sys.exit(1)
    
    return api_key

def run_setup_script():
    project_root = os.getenv('PROJECT_ROOT')
    setup_directory = os.path.join(project_root, 'GPT', 'setup')

    if platform.system() == 'Windows':
        print("Detected Windows OS.")
        setup_script = os.path.join(setup_directory, 'setup_env.bat')
        subprocess.run(setup_script, shell=True)
    else:
        print("Detected Unix-like OS.")
        setup_script = os.path.join(setup_directory, 'setup_env.sh')
        subprocess.run(['bash', setup_script])

def run_tests():
    project_root = os.getenv('PROJECT_ROOT')
    gpt_directory = os.path.join(project_root, 'GPT')

    if platform.system() == 'Windows':
        test_command = f"call {os.path.join(gpt_directory, 'venv', 'Scripts', 'activate.bat')} && python -m unittest discover {os.path.join(gpt_directory, 'tests')}"
        result = subprocess.run(test_command, shell=True, capture_output=True, text=True)
    else:
        test_command = f"source {os.path.join(gpt_directory, 'venv', 'bin', 'activate')} && python -m unittest discover {os.path.join(gpt_directory, 'tests')}"
        result = subprocess.run(['bash', '-c', test_command], capture_output=True, text=True)

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

def prompt_user_deployment_verification():
    root = Tk()
    root.title("Deployment Verification")

    def on_yes():
        print("User verified the deployment.")
        root.destroy()
        create_dashboard()  # Open the dashboard after verification

    def on_cancel():
        print("User canceled the procedure.")
        root.destroy()
        sys.exit(1)

    label = Label(root, text="Do you verify that all tests have passed and you want to deploy the integration?")
    label.pack(pady=20)

    yes_button = Button(root, text="Yes", command=on_yes)
    yes_button.pack(side="left", padx=20, pady=20)

    cancel_button = Button(root, text="Cancel", command=on_cancel)
    cancel_button.pack(side="right", padx=20, pady=20)

    root.mainloop()

if __name__ == "__main__":
    set_project_root()
    get_api_key()
    run_setup_script()
    run_tests()
    prompt_user_deployment_verification()
