from flask import Flask, render_template, request, session, jsonify
from openai import OpenAI
from markdown2 import markdown
from markupsafe import escape
import time
from flask_session import Session  # Make sure to install Flask-Session
from bs4 import BeautifulSoup
import traceback
import os, sys

if os.environ.get("OPENAI_API_KEY") is None:
    print("Please set your OPENAI_API_KEY environment variable and try again.")
    sys.exit(1)

if os.environ.get("SECRET_KEY") is None:
    print("Please set your SECRET_KEY environment variable and try again.")
    sys.exit(1)


# Instantiate OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
ASSISTANT_OPTIONS = [{'id': asst.id, 'name': asst.name} for asst in client.beta.assistants.list().data]
ASSISTANT_MAP = {item['id']: item['name'] for item in ASSISTANT_OPTIONS}

app = Flask(__name__)
# Check Flask-Session documentation for proper secret key settings
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Set the default selected assistant ID in session on app startup
app.config['DEFAULT_ASSISTANT_ID'] = ASSISTANT_OPTIONS[0]['id']

@app.route('/assistant_options', methods=['POST', 'GET'])
def assistant_options():
    try:
        default_assistant_id = app.config.get('DEFAULT_ASSISTANT_ID')
        if request.method == 'GET':
            options_html = render_template('assistant_options.html', assistants=ASSISTANT_OPTIONS, selected_assistant_id=session.get('selected_assistant_id', default_assistant_id))
            return options_html
        
        if request.method == 'POST':
            agent_id = request.form.get('id', default_assistant_id)
            if agent_id not in ASSISTANT_MAP:
                return jsonify({'status': 'error', 'message': f"Invalid assistant ID {agent_id}"}), 400
            
            session['selected_assistant_id'] = agent_id
            options_html = render_template('assistant_options.html', assistants=ASSISTANT_OPTIONS, selected_assistant_id=session.get('selected_assistant_id', default_assistant_id))
            print(f"We are now using: '{ASSISTANT_MAP[agent_id]}'")
            return options_html
        
    except Exception as e:
        tbe = traceback.format_exc()
        print(f"Exception during assistant selection: `{tbe}`")
        return jsonify({'status': 'error', 'message': 'invalid action'}), 500


@app.route('/')
def index():
    session['thread_id'] = None  # Initialize the thread_id in session
    if 'selected_assistant_id' not in session:
        session['selected_assistant_id'] = app.config['DEFAULT_ASSISTANT_ID']
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit():
    default_assistant_id = app.config.get('DEFAULT_ASSISTANT_ID')
    user_message = request.form['message']
    thread_id = session.get('thread_id')
    selected_assistant_id = session.get('selected_assistant_id', default_assistant_id)

    if not thread_id:
        thread = client.beta.threads.create()
        session['thread_id'] = thread.id  # Save the thread ID in the session
    else:
        thread = client.beta.threads.retrieve(thread_id=thread_id)

    run = submit_message(selected_assistant_id, thread, user_message)
    run = wait_on_run(run, thread)
    messages = get_response(thread)

    # Format the AI's latest response for display
    ai_reply = messages[-1].content[0].text.value if messages else ""
    assistant_name = ASSISTANT_MAP.get(selected_assistant_id, "Unknown Assistant")

    # Convert markdown to HTML and sanitize
    ai_reply_html = markdown(ai_reply, extras=["tables", "fenced-code-blocks", "spoiler", "strike"])
    
    # Create a BeautifulSoup object to parse HTML
    soup = BeautifulSoup(ai_reply_html, 'html.parser')
    
    # Find all code blocks and update them
    for pre in soup.find_all('pre'):
        # Create a copy button and insert it at the beginning of the `pre` element
        copy_button = soup.new_tag('button', **{
            'class': 'copy-button', 
            'onclick': 'copyCode(this)',
            'title': 'Copy to clipboard'  # Adding a title for accessibility
        })
        copy_button.string = 'Copy'
        # Insert the copy button as the first child of the `pre` element
        pre.insert(0, copy_button)
    
    # Convert the soup object back to a string
    ai_reply_html = str(soup)

    # Escaping user_message for security reasons
    user_message_safe = escape(user_message)

    chat_html = f'<div class="user-message">{user_message_safe}</div>'
    chat_html += f'<div class="ai-message"><div class="ai-agent-name">{assistant_name}</div> {ai_reply_html}</div>'
    return chat_html

@app.route('/clear', methods=['POST'])
def clear():
    # Clear the current thread ID from the session
    session.pop('thread_id', None)
    # Create a new thread to start fresh
    thread = client.beta.threads.create()
    session['thread_id'] = thread.id
    # The response doesn't need to change since HTMX will handle the reloading
    return '', 204



def submit_message(assistant_id, thread, user_message):
    client.beta.threads.messages.create(thread_id=thread.id, role="user", content=user_message)
    return client.beta.threads.runs.create(thread_id=thread.id, assistant_id=assistant_id)


def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        time.sleep(0.75)
    return run


def get_response(thread):
    messages_page = client.beta.threads.messages.list(thread_id=thread.id, order="asc")
    print(f"Got {len(messages_page.data)} messages")
    return [message for message in messages_page.data]


if __name__ == '__main__':
    app.run(debug=True)
