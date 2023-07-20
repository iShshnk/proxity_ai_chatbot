# import all required libraries
import requests
import msal
import app_config
from flask import Flask, render_template, request, session, redirect, url_for, send_from_directory, jsonify, send_file, Response # Flask libraries for creating web application
from flask_session import Session 
import openai  # OpenAI's Python client library
import os
from datetime import datetime
import requests
import json
import time


# modules with various implementations and helper functions
from db import retrieve_data, update_summary, save_media, save_voice_id
from chat import generate_prompts, ask_expert
from msal_helper import _build_auth_code_flow, _load_cache, _build_msal_app, _save_cache, _get_token_from_cache
from removebg import remove_bg
from voice_clone import get_voice_clone

import boto3
from botocore.exceptions import NoCredentialsError

s3 = boto3.client('s3', aws_access_key_id=app_config.aws_access_key_id,
                  aws_secret_access_key=app_config.aws_secret_access_key)

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
from werkzeug.utils import secure_filename
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)



# route for landing page
@app.route("/")
def index():
    if not session.get("user") or session.get("role")!="user":
        return redirect(url_for("login"))
    return render_template('index.html', user=session["user"], version=msal.__version__)

# This is defining a route for '/admin_panel' in the Flask web application.
@app.route('/admin_panel')
def admin_panel():
    # The 'if' condition checks two things:
    # 1. If there is no 'user' key in the session object, it means no user is currently logged in, so it redirects to the login page.
    # 2. If there is a 'user' key in the session but the role of the user is not 'admin', it again redirects to the login page.
    # 'session' is a special object that Flask provides for storing user-specific data across requests. 
    if not session.get("user") or session.get("role") != "admin":
        # 'redirect' is a function provided by Flask that redirects the user to a different page.
        # 'url_for' is another Flask function that generates the URL for a given endpoint. In this case, the 'login' endpoint.
        return redirect(url_for("login"))  # or redirect to a "not authorized" page
    # If the 'if' condition fails, it means the user is logged in and is an admin. 
    # In this case, it continues to the line below and returns the 'admin_panel.html' page.
    return render_template('admin_panel.html')

@app.route('/my_avatar', methods=['GET','POST'])
def my_avatar():
    if not session.get("user") or session.get("role") != "admin":
        return redirect(url_for("login"))
    
    if request.method == "POST":
        image_file = request.files['image']
        audio_files = request.files.getlist('audio')

        if image_file and allowed_img_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.root_path, 'static/img', filename)
            image_file.save(image_path)
            image_file = remove_bg(image_path)
            image_file.save(image_path)

            # Save image_path to MongoDB
            save_media({'type': 'image', 'path': image_path}, session["user"]["preferred_username"])
            
        audio_samples_path = []

        for audio_file in audio_files:
            if audio_file and allowed_audio_file(audio_file.filename):
                filename = secure_filename(audio_file.filename)
                audio_path = os.path.join(app.root_path, 'static/img', filename)
                audio_file.save(audio_path)
                audio_samples_path.append(audio_path)
        
        voice_id = get_voice_clone(session["user"]["preferred_username"], audio_samples_path)
        save_voice_id(session["user"]["preferred_username"], voice_id)
        
        return jsonify({'success': True, 'message': 'Avatar created successfully!'})

    return render_template('my_avatar.html')

def allowed_img_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['jpg', 'png', 'jpeg']

def allowed_audio_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['mp3']


@app.route('/your_convo', methods=['GET'])
def your_convo():
    if not session.get("user") or session.get("role") != "admin":
        return redirect(url_for("login"))
    
    return render_template('your_convo.html')


@app.route('/interact_avatar', methods=['GET'])
def interact_avatar():
    if not session.get("user") or session.get("role") != "admin":
        return redirect(url_for("login"))
    
    return render_template('interact_avatar.html')


# chat route with chatbot integration
@app.route('/chat', methods=['GET', 'POST'])
def chat():
    # define chat endpoint
    # this is the main entry point of the application
    # it handles GET and POST requests 
    
    if not session.get("user") or session.get("role")!="user":
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
    if request.method == 'POST' and request.is_json:
        req = request.get_json()
        if 'new_conversation' in req and req['new_conversation']:
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
        print(session['chat_log'])
        return render_template('chat.html', response=response, chat_log=session['chat_log'])

    # GET request to show the chat page with the current chat log
    return render_template('chat.html', chat_log=session['chat_log'])

# route for login page
@app.route("/login")
def login():
    # Technically we could use empty list [] as scopes to do just sign in,
    # here we choose to also collect end user consent upfront
    session["flow"] = _build_auth_code_flow(scopes=app_config.SCOPE)
    session["role"] = "user"
    return render_template("login.html", auth_url=session["flow"]["auth_uri"],admin_dashboard="admin_login", version=msal.__version__)

@app.route("/admin_login")
def admin_login():
    # Technically we could use empty list [] as scopes to do just sign in,
    # here we choose to also collect end user consent upfront
    session["flow"] = _build_auth_code_flow(scopes=app_config.SCOPE)
    session["role"] = "admin"
    return render_template("admin_login.html", auth_url=session["flow"]["auth_uri"], version=msal.__version__)

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
    if session.get("role") == 'user':
        return redirect(url_for("index"))
    return redirect(url_for("admin_panel"))

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


@app.route('/get_audio')
def get_audio():
    url = "https://api.elevenlabs.io/v1/text-to-speech/pTL1YWXSHGzMbeBqSp5z/stream"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": "f847bcf3852b9864940d67cdb2ff7ccc",
    }
    data = {
        "text": session['chat_log'][-1]['content'] if 'chat_log' in session and len(session['chat_log']) > 0 else '',
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.7,
        },
    }

    response = requests.post(url, headers=headers, json=data)

    # Generate a unique filename based on the current time
    filename = f"audio.mp3"

    # Upload to S3
    try:
        s3.put_object(Body=response.content, Bucket='digital-me-rediminds', Key=filename)
    except NoCredentialsError:
        return {"error": "S3 credentials not found"}

    # Return the URL to the audio file
    public_url = f"https://digital-me-rediminds.s3.amazonaws.com/{filename}"
    return {"audio_url": public_url}


"""@app.route('/latest-response')
def latest_response():
    # Get the latest response from chat log
    last_response = session['chat_log'][-1] if 'chat_log' in session and len(session['chat_log']) > 0 else {}

    # Return the response as JSON
    return jsonify(last_response)"""

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
    app.run(port=5006, ssl_context=('cert.pem', 'key.pem'),debug=True)

