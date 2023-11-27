# Assistants Application

## Overview
This project is a web application built with Flask, integrating OpenAI's GPT-based assistants. It allows users to interact with a variety of AI assistants through a user-friendly interface. The application supports dynamic assistant selection, threaded conversations, and markdown rendering for AI responses.

## Features
- **Dynamic Assistant Selection**: Choose from your own AI assistants created in OpenAI.
- **Interactive Chat Interface**: Engage in conversations with chosen AI assistants.
- **Thread Management**: Organize conversations in separate threads.
- **Markdown Rendering**: Enhanced readability of AI responses.
- **Code Copy Functionality**: Easily copy code snippets from responses.

## Installation

### Prerequisites
- Python 3.x
- pip
- Virtual Environment (recommended)

### Setup
1. **Clone the Repository**
   ```sh
   git clone [Your Repository URL]
   cd [Your Repository Name]
   ```

2. **Configure the `run.sh` Script**
   Edit the `run.sh` script to set your `OPENAI_API_KEY` and a `SECRET_KEY` for the Flask session store.

3. **Create and Activate a Virtual Environment** (Optional)
   ```sh
   python3 -m venv local-agents-venv
   source local-agents-venv/bin/activate
   ```

   You will then need to install the dependencies in the virtual environment:
   ```sh
    pip install -r requirements.txt
    ```

    Then run the openai migration script:
    ```sh
    openai migrate
    ```

    Export the OPENAI_API_KEY and SECRET_KEY environment variables:
    ```sh
    export OPENAI_API_KEY=[Your OpenAI API Key]
    export SECRET_KEY=[Your Secret Key]
    ```


4. **Run the Application**
   ```sh
   ./run.sh
   ```
   This script will install the necessary dependencies and start the Flask server.

   You will need to chmod the script to make it executable:
   ```sh
    chmod +x run.sh
    ```

## Usage
After starting the server, visit `http://localhost:5000` to use the application. 

- **Assistant Selection**: You should have created AI assistants associated with your OpenAI API key. Select one from the dropdown menu.
- **Conversing with Assistants**: Type your message and send.
- **Clearing the Chat**: Use the 🧽 Clear Chat button for a new conversation thread.

## Manual Setup
If you prefer to set up the environment manually, you can follow the steps outlined in the `run.sh` script.

## Contributing
Contributions are welcome. Please fork the repo and create a pull request, or open an issue with the tag "enhancement".

## License
This project is licensed under the MIT License - see the `LICENSE` file for details.
