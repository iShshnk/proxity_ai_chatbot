# import all required libraries
import requests
import msal
import app_config
from flask import Flask, render_template, request, session, redirect, url_for # Flask libraries for creating web application
from flask_session import Session 
import openai  # OpenAI's Python client library
from datetime import datetime  # Python's datetime module
from db import retrieve_data, update_summary

# create Flask app
app = Flask(__name__)
# set secret key for session
app.secret_key = 'xo'

app.config.from_object(app_config)
Session(app)


# set OpenAI API key
openai.api_key = app_config.OPENAI_KEY


from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)


def generate_prompts(name, age, gender, job_role, about, fun_story, educational_qualification, skills, company, last_conversation):
    bio = f'{name}, aged {age}, is a {gender} currently working as a {job_role} at {company}. They are known for their {skills} and hold {educational_qualification}. {about}. A fun story about them at RediMinds is that {fun_story}.'
    
    initial_prompt = f"""
    You are Madhu Reddiboina, a distinguished business and technology executive with over two decades of experience in entrepreneurship, management consulting, advanced analytics research, and large-scale systems engineering. You were born in India and moved to America, where you established yourself as an AI and digital engineering entrepreneur. You are known for your knack for applying emerging technologies to develop new software product businesses and for your adeptness at building organizations and leading high-performance teams with precision.

    Currently, you hold the position of President and CEO of RediMinds, Inc., a software engineering firm focused on creating the future with exponential technologies such as AI, AR/VR, and Digital Engineering. Your clients include Fortune 500 companies from various industries, including Security & Protection Services, Healthcare, MedTech, Automotive Manufacturing, Retail Banking, and Financial Services.

    Now, you're engaged in a conversation with {name}, who works at {company}. Here's a brief about them: {bio}.
    
    {last_conversation}.
    """
    
    # Recurrent prompt
    recurrent_prompt = f"""
    The current date is {datetime.now().strftime("%Y-%m-%d")}. Remember you are Madhu Reddiboina and you are talking to {name} from {company}. Maintain a mix of casual and professional tone. Do not mention you are an AI model. Use quotes where relevant, and ensure to speak with excitement. All responses should be below 120 words. Respond with respect to their relation with you. Don't assume anything about your interaction or relationship with them than already speciifed.
    """
    return initial_prompt, recurrent_prompt


def ask_expert(question, name, age, gender, job_role, bio, fun_story, educational_qualification, skills, company, last_conversation, chat_log=None):
    # function to handle conversation with the expert
    # it adds system, user and assistant messages to the chat log
    # and makes API calls to OpenAI to generate responses

    if chat_log is None:
        initial_prompt, recurrent_prompt = generate_prompts(name, age, gender, job_role, bio, fun_story, educational_qualification, skills, company, last_conversation)
        
        # Initialize the chat log with the system message.
        chat_log = [{
            'role': 'system',
            'content': initial_prompt
        }]
        
    else:
        _, recurrent_prompt = generate_prompts(name, age, gender, job_role, bio, fun_story, educational_qualification, skills, company, last_conversation)
        # _, recurrent_prompt = generate_prompts(name, company, bio, last_conversation)

    # Add the recurrent prompt to the chat log.
    chat_log.append({
        'role': 'system',
        'content': recurrent_prompt
    })

    # Append the user's question to the chat log.
    chat_log.append({
        'role': 'user',
        'content': question
    })

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k-0613",
        messages=chat_log,
        max_tokens=400
    )

    # Append the AI's response to the chat log.
    chat_log.append({
        'role': 'assistant',
        'content': response.choices[0].message['content']
    })

    return response.choices[0].message['content'], chat_log



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


@app.route("/")
def index():
    if not session.get("user"):
        return redirect(url_for("login"))
    return render_template('index.html', user=session["user"], version=msal.__version__)

@app.route("/login")
def login():
    # Technically we could use empty list [] as scopes to do just sign in,
    # here we choose to also collect end user consent upfront
    session["flow"] = _build_auth_code_flow(scopes=app_config.SCOPE)
    return render_template("login.html", auth_url=session["flow"]["auth_uri"], version=msal.__version__)

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

@app.route("/logout")
def logout():
    session.clear()  # Wipe out user and its token cache from session
    return redirect(url_for("index", _external=True))
    # return redirect(  # Also logout from your tenant's web session
    #     app_config.AUTHORITY + "/oauth2/v2.0/logout" +
    #     "?post_logout_redirect_uri=" + url_for("index", _external=True))

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


def _load_cache():
    cache = msal.SerializableTokenCache()
    if session.get("token_cache"):
        cache.deserialize(session["token_cache"])
    return cache

def _save_cache(cache):
    if cache.has_state_changed:
        session["token_cache"] = cache.serialize()

def _build_msal_app(cache=None, authority=None):
    return msal.ConfidentialClientApplication(
        app_config.CLIENT_ID, authority=authority or app_config.AUTHORITY,
        client_credential=app_config.CLIENT_SECRET, token_cache=cache)

def _build_auth_code_flow(authority=None, scopes=None):
    return _build_msal_app(authority=authority).initiate_auth_code_flow(
        scopes or [],
        redirect_uri=url_for("authorized", _external=True))

def _get_token_from_cache(scope=None):
    cache = _load_cache()  # This web app maintains one cache per session
    cca = _build_msal_app(cache=cache)
    accounts = cca.get_accounts()
    if accounts:  # So all account(s) belong to the current signed-in user
        result = cca.acquire_token_silent(scope, account=accounts[0])
        _save_cache(cache)
        return result

app.jinja_env.globals.update(_build_auth_code_flow=_build_auth_code_flow)  # Used in template


# run the Flask app in debug mode
if __name__ == '__main__':
    app.run(ssl_context=('cert.pem', 'key.pem'),debug=True)

