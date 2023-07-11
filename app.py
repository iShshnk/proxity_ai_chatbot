# import all required libraries
import requests
import msal
import app_config
from flask import Flask, render_template, request, session, redirect, url_for, send_from_directory, jsonify # Flask libraries for creating web application
from flask_session import Session 
import openai  # OpenAI's Python client library
import os
from datetime import datetime  # Python's datetime module


# modules with various implementations and helper functions
from db import retrieve_data, update_summary
from chat import generate_prompts, ask_expert
from msal_helper import _build_auth_code_flow, _load_cache, _build_msal_app, _save_cache, _get_token_from_cache




# create Flask app
app = Flask(__name__)

# set secret key for session
app.secret_key = 'xo'

# config file for app
app.config.from_object(app_config)
Session(app)

# set OpenAI API key
openai.api_key = app_config.OPENAI_KEY

from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)




# route for landing page
@app.route("/")
def index():
    if not session.get("user"):
        return redirect(url_for("login"))
    return render_template('index.html', user=session["user"], version=msal.__version__)




# chat route with chatbot integration
@app.route('/chat', methods=['GET', 'POST'])
def chat():
    # define chat endpoint
    # this is the main entry point of the application
    # it handles GET and POST requests 
    
    if not session.get("user"):
        return redirect(url_for("login"))
    
    current_email = session["user"]["preferred_username"]
    
    data = retrieve_data(current_email)
    name = data['Name']
    age = data['Age']
    gender = data['Gender']
    job_role = data['Job Role']
    bio = data['About']
    fun_story = data['Fun Story']
    last_conversation = data.get('Last Conversation Summary', 'No prior conversation')
    educational_qualification = data['Educational Qualification']
    skills = data['Skills']
    company = "RediMinds"
    

     # POST request to start a new conversation
    if request.method == 'POST' and 'new_conversation' in request.form:
        chat_log = session.get('chat_log')
        user_and_assistant_msgs = [msg['content'] for msg in chat_log if msg['role'] in ['user', 'assistant']]
        conversation = ' '.join(user_and_assistant_msgs)

        # Construct a prompt for the summary.
        summary_prompt =  f"Please summarize in detail the following conversation between {name} and Madhu The conversation occured at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} and is as follows: {conversation} - make sure this is the priority and comes first in the summary.  Also, provide a succinct summary of a previous conversation: '{last_conversation}', ensuring to timestamp it correctly (should be in the summmary) and highlight that it was discussed prior to the current conversation. The format should be: 'summary of conversation at 'timestamp'- 'summary''. Keep the total word count about 400 words."

        # Generate a summary using the GPT-3.5 model.
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k-0613",
            max_tokens=700,
            messages=[
                {"role": "system", "content": "You are an expert conversation summarizer and catch nuances in a conversation in a crisp manner.When writing the summary, do so from the perspective of an objective third party who is recounting the interaction to Madhu (he is essentially one of the people talking, you will need to figure out who). Consider the emotional tone, key points, and conclusions drawn from the conversation."},
                {"role": "user", "content": summary_prompt}
            
            ]
        )
        session['summary'] = response.choices[0].message['content']

        update_summary(current_email, session['summary'])
        print(last_conversation)


        # Clear the session and render the chat page without any previous conversation.
        session.clear()
        return render_template('chat.html', chat_log=[])

    elif 'chat_log' not in session:
        # Initialize the chat log with the system message for some edge cases.
        initial_prompt, _ = generate_prompts(name, age, gender, job_role, bio, fun_story, educational_qualification, skills, company, last_conversation)
        # initial_prompt, _ = generate_prompts(name, company, bio, last_conversation)
        session['chat_log'] = [{
            'role': 'system',
            'content': initial_prompt
        }]
    
    # POST request to continue the conversation
    elif request.method == 'POST' and 'user_msg' in request.form:
        # if the request method is POST and there is a 'user_msg' field in the form,
        # get the user's question, generate a response from the assistant,
        # and add the response to the session's chat log.
        # then, render the chat page with the response and the updated chat log.
        question = request.form.get('user_msg')
        response, chat_log = ask_expert(question, name, age, gender, job_role, bio, fun_story, educational_qualification, skills, company, last_conversation, session.get('chat_log'))
        session['chat_log'] = chat_log
        return render_template('chat.html', response=response, chat_log=session['chat_log'])

    # GET request to show the chat page with the current chat log
    return render_template('chat.html', chat_log=session['chat_log'])




# route for login page
@app.route("/login")
def login():
    # Technically we could use empty list [] as scopes to do just sign in,
    # here we choose to also collect end user consent upfront
    session["flow"] = _build_auth_code_flow(scopes=app_config.SCOPE)
    return render_template("login.html", auth_url=session["flow"]["auth_uri"], version=msal.__version__)

# route for logout
@app.route("/logout")
def logout():
    session.clear()  # Wipe out user and its token cache from session
    return redirect(url_for("index", _external=True))

# auth config
@app.route(app_config.REDIRECT_PATH)  # Its absolute URL must match your app's redirect_uri set in AAD
def authorized():
    try:
        cache = _load_cache()
        result = _build_msal_app(cache=cache).acquire_token_by_auth_code_flow(
            session.get("flow", {}), request.args)
        if "error" in result:
            return render_template("auth_error.html", result=result)
        session["user"] = result.get("id_token_claims")
        _save_cache(cache)
    except ValueError:  # Usually caused by CSRF
        pass  # Simply ignore them
    return redirect(url_for("index"))

app.jinja_env.globals.update(_build_auth_code_flow=_build_auth_code_flow)  # Used in template




# route for graphcall ***To be removed in production***
@app.route("/graphcall")
def graphcall():
    token = _get_token_from_cache(app_config.SCOPE)
    if not token:
        return redirect(url_for("login"))
    graph_data = requests.get(  # Use token to call downstream service
        app_config.ENDPOINT,
        headers={'Authorization': 'Bearer ' + token['access_token']},
        ).json()
    return render_template('display.html', result=graph_data)




# misc/helper/additional routes
  
@app.route('/latest-response')
def latest_response():
    # Get the latest response from chat log
    last_response = session['chat_log'][-1] if 'chat_log' in session and len(session['chat_log']) > 0 else {}

    # Return the response as JSON
    return jsonify(last_response)

@app.route("/api/config")
def get_config():
    return jsonify({"key": app_config.API_KEY, "url": app_config.API_URL})

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')
@app.route('/idle.mp4')
def video():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'idle.mp4')




# run the Flask app in debug mode
if __name__ == '__main__':
    app.run(port=5000, ssl_context=('cert.pem', 'key.pem'),debug=True)

