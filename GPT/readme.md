# Pandas GPT Optimizer

## Overview

Pandas GPT Optimizer is an advanced tool designed to integrate OpenAI's API to assist in the optimization, creation, organization, and refactoring of software codebases. This integration provides read/write capabilities in a specified directory, automating several tasks including code summarization, dependency analysis, and iterative improvements.

## Features

- **Code Summarization**: Automatically summarize code files using OpenAI's models.
- **Code Verification**: Verify code and dependencies, providing corrections where necessary.
- **Dependency Analysis**: Identify and document dependencies for each file.
- **Iterative Improvement**: Continuously improve and verify the codebase.
- **Automated Testing**: Run unit tests and display results.

## Installation

### Prerequisites

- Python 3.8+
- OpenAI API Key
- Flask

### Setup

1. **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/pandas_gpt_optimizer.git
    cd pandas_gpt_optimizer
    ```

2. **Set up the virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Set environment variables**:
    ```bash
    export API_KEY='your-openai-api-key'
    export ROOT_DIRECTORY='path-to-your-project-directory'
    ```

### Running the Application

1. **Activate the virtual environment**:
    ```bash
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

2. **Run the Flask app**:
    ```bash
    python brain/integration_api.py
    ```

## Usage

### API Endpoints

1. **Summarize Code**: Summarize the provided code content.
    - **Endpoint**: `/summarize`
    - **Method**: `POST`
    - **Request Body**:
        ```json
        {
            "content": "code content here"
        }
        ```
    - **Response**:
        ```json
        {
            "summary": "summary of the code"
        }
        ```

2. **Verify Code**: Verify the provided code content.
    - **Endpoint**: `/verify`
    - **Method**: `POST`
    - **Request Body**:
        ```json
        {
            "content": "code content here"
        }
        ```
    - **Response**:
        ```json
        {
            "verification": "verification result of the code"
        }
        ```

3. **Get Corrections**: Get corrections for the provided code content.
    - **Endpoint**: `/corrections`
    - **Method**: `POST`
    - **Request Body**:
        ```json
        {
            "content": "code content here"
        }
        ```
    - **Response**:
        ```json
        {
            "corrections": "corrections for the code"
        }
        ```

4. **Analyze Dependencies**: Get the list of dependencies for the project.
    - **Endpoint**: `/dependencies`
    - **Method**: `GET`
    - **Response**:
        ```json
        {
            "dependencies": ["dependency1", "dependency2", ...]
        }
        ```

5. **Update Requirements**: Update the requirements file with the provided dependencies.
    - **Endpoint**: `/update-requirements`
    - **Method**: `POST`
    - **Request Body**:
        ```json
        {
            "dependencies": ["dependency1", "dependency2", ...]
        }
        ```
    - **Response**:
        ```json
        {
            "message": "Requirements updated"
        }
        ```

6. **Verify Dependencies**: Verify and install any missing dependencies.
    - **Endpoint**: `/verify-dependencies`
    - **Method**: `POST`
    - **Response**:
        ```json
        {
            "message": "Dependencies verified and installed"
        }
        ```

7. **Run Tests**: Run unit tests.
    - **Endpoint**: `/run-tests`
    - **Method**: `POST`
    - **Response**:
        ```json
        {
            "test_results": "results of the tests"
        }
        ```

## Models Directory

The `models` directory is designed to house various models for training and integration with the GPT system.

### Structure

- **models/**
  - **Veronica/**: This directory contains the main model, Veronica, which is trained on the entire GPT integration and assumes more responsibilities as the integration evolves.
  - **other_models/**: This directory houses additional models from various GitHub repositories that are integrated into the GPT system.

### Usage

- **Veronica Model**: The Veronica model is the core model trained on all capabilities of the GPT integration.
- **Other Models**: Additional models can be added to the `other_models` directory to extend the functionalities of the GPT integration.

### Adding New Models

To add a new model, simply place the model files in the `other_models` directory and update the integration to utilize the new model as needed.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any changes or improvements.

## License

This project is licensed under the MIT License.

## Acknowledgements

Special thanks to the OpenAI team for providing the models and API that make this project possible.
