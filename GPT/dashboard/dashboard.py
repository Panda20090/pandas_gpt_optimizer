import tkinter as tk
from tkinter import ttk, messagebox
import os
import subprocess
import json
import shutil
import platform

def run_integration():
    """
    Run the integration setup script.
    """
    try:
        subprocess.run(['python', 'setup/run_integration_setup.py'], check=True)
        messagebox.showinfo("Integration", "Integration setup completed successfully.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Integration Error", f"Failed to run integration setup: {e}")

def switch_model(model_choice):
    """
    Switch between OpenAI API and Veronica model.
    
    Parameters:
    model_choice (str): The chosen model ("OpenAI" or "Veronica").
    """
    try:
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
        with open(config_path, 'w') as config_file:
            json.dump({"model": model_choice}, config_file)
        messagebox.showinfo("Model Switch", f"Switched to {model_choice} model")
    except Exception as e:
        messagebox.showerror("Model Switch Error", f"Failed to switch model: {e}")

def save_runtime_log():
    """
    Save the integration log to the runtime log file.
    """
    integration_log_path = os.path.join(os.path.dirname(__file__), 'integration_log.txt')
    runtime_log_path = os.path.join(os.path.dirname(__file__), 'runtime_log.txt')
    shutil.copyfile(integration_log_path, runtime_log_path)

def revert_changes():
    """
    Revert changes made during the deployment process.
    """
    project_root = os.getenv('PROJECT_ROOT')
    gpt_directory = os.path.join(project_root, 'GPT')
    backup_directory = os.path.join(project_root, 'GPT_backup')

    if os.path.exists(backup_directory):
        shutil.rmtree(gpt_directory)
        shutil.copytree(backup_directory, gpt_directory)
    else:
        print("Backup directory does not exist. No changes to revert.")

def prompt_user_deployment_verification():
    """
    Prompt user to verify the deployment, write logs, or revert changes.
    """
    def on_yes():
        save_runtime_log()
        messagebox.showinfo("Deployment Verified", "Deployment verified successfully.")
        root.destroy()
        create_dashboard()

    def on_no():
        revert_changes()
        messagebox.showinfo("Deployment Reverted", "Changes have been reverted.")
        root.destroy()
        create_dashboard()

    root = tk.Tk()
    root.title("Deployment Verification")

    label = ttk.Label(root, text="Do you verify that all tests have passed and you want to deploy the integration?")
    label.pack(pady=20)

    yes_button = ttk.Button(root, text="Yes", command=on_yes)
    yes_button.pack(side="left", padx=20, pady=20)

    no_button = ttk.Button(root, text="No", command=on_no)
    no_button.pack(side="right", padx=20, pady=20)

    root.mainloop()

def deploy_integration():
    """
    Deploy the integration by setting up a new virtual environment.
    """
    project_root = os.getenv('PROJECT_ROOT')
    gpt_directory = os.path.join(project_root, 'GPT')

    # Cleanup the test virtual environment
    if platform.system() == 'Windows':
        venv_path = os.path.join(gpt_directory, 'setup', 'venv')
        if os.path.exists(venv_path):
            subprocess.run(f'rd /s /q "{venv_path}"', shell=True)
    else:
        venv_path = os.path.join(gpt_directory, 'setup', 'venv')
        if os.path.exists(venv_path):
            subprocess.run(['rm', '-rf', venv_path], shell=False)

    # Set up a new virtual environment in the main project directory
    if platform.system() == 'Windows':
        setup_command = f'python -m venv {os.path.join(project_root, "venv")}'
        subprocess.run(setup_command, shell=True)
        activate_command = f'call {os.path.join(project_root, "venv", "Scripts", "activate.bat")}'
        subprocess.run(activate_command + ' && pip install -r requirements.txt', shell=True)
    else:
        setup_command = f'python -m venv {os.path.join(project_root, "venv")}'
        subprocess.run(setup_command, shell=False)
        activate_command = f'source {os.path.join(project_root, "venv", "bin", "activate")}'
        subprocess.run(activate_command + ' && pip install -r requirements.txt', shell=True)

    print("Deployment complete. The integration is now running in the main project directory.")

def create_dashboard():
    """
    Create and display the Tkinter dashboard for the GPT integration.
    """
    root = tk.Tk()
    root.title("GPT Integration Dashboard")

    mainframe = ttk.Frame(root, padding="10 10 10 10")
    mainframe.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    model_label = ttk.Label(mainframe, text="Choose Model:")
    model_label.grid(column=1, row=1, sticky=tk.W)

    model_choice = tk.StringVar(value="OpenAI")
    models = ["OpenAI", "Veronica"]
    model_menu = ttk.OptionMenu(mainframe, model_choice, *models)
    model_menu.grid(column=2, row=1, sticky=(tk.W, tk.E))

    run_button = ttk.Button(mainframe, text="Set Up New Project", command=run_integration)
    run_button.grid(column=1, row=2, sticky=tk.W)

    switch_button = ttk.Button(mainframe, text="Switch Model", command=lambda: switch_model(model_choice.get()))
    switch_button.grid(column=2, row=2, sticky=tk.W)

    deploy_button = ttk.Button(mainframe, text="Deploy Integration", command=prompt_user_deployment_verification)
    deploy_button.grid(column=1, row=3, sticky=tk.W)

    log_text = tk.Text(mainframe, height=20, width=80)
    log_text.grid(column=1, row=4, columnspan=2, sticky=(tk.W, tk.E))

    log_scrollbar = ttk.Scrollbar(mainframe, orient=tk.VERTICAL, command=log_text.yview)
    log_scrollbar.grid(column=3, row=4, sticky=(tk.N, tk.S))
    log_text['yscrollcommand'] = log_scrollbar.set

    root.after(2000, lambda: update_log(log_text))

    for child in mainframe.winfo_children():
        child.grid_configure(padx=5, pady=5)

    root.mainloop()

def update_log(log_text):
    """
    Update the log text widget with the latest log messages.
    
    Parameters:
    log_text (tk.Text): The text widget to update.
    """
    log_file_path = os.path.join(os.path.dirname(__file__), 'integration_log.txt')
    if os.path.exists(log_file_path):
        with open(log_file_path, 'r') as log_file:
            log_text.delete(1.0, tk.END)
            log_text.insert(tk.END, log_file.read())
    log_text.after(2000, lambda: update_log(log_text))

if __name__ == "__main__":
    create_dashboard()
