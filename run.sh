#!/bin/bash

# Define the name of the virtual environment
VENV_NAME="local-agents-venv"

# Step 1: Check for the virtual environment
if [ ! -d "$VENV_NAME" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_NAME"
    FIRST_RUN=true
else
    echo "Virtual environment already exists."
    FIRST_RUN=false
fi

# Step 2: Activate the virtual environment
source "$VENV_NAME/bin/activate"

# Step 3: Install requirements
if [ $FIRST_RUN == true ]; then
    echo "Installing requirements..."
    pip install -r requirements.txt
fi

# Step 4: Export environment variable
export OPENAI_API_KEY=sk-exxxxxxxxxxxxxxxxxxxx
export SECRET_KEY=something-secret-123

# Step 5: Message about openai migrate
if [ $FIRST_RUN == true ]; then
    echo "Please run 'openai migrate' to migrate your codebase"
    openai migrate
fi

# Step 6: Run Flask app
echo "Starting Flask app..."
FLASK_APP=app FLASK_ENV=development flask run --reload &

# Open the browser after a short delay to allow the server to start
sleep 2
xdg-open http://localhost:5000
