# import all required libraries
from flask import Flask, render_template, request, session  # Flask libraries for creating web application
import openai  # OpenAI's Python client library
from datetime import datetime  # Python's datetime module
import json  # Python's json module
from db import retrieve_data

# create Flask app
app = Flask(__name__)
# set secret key for session
app.secret_key = 'xo'

# set OpenAI API key
openai.api_key = "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"

user_id = "648aae8b704770e88483c801"

def generate_prompts(name, company, bio, last_conversation, relation):
    # function to generate initial and recurrent prompts
    # these prompts are used to initiate conversation and provide context to the AI model
    
    initial_prompt = f"""
    You are Madhu Reddiboina, a distinguished business and technology executive with over two decades of experience in entrepreneurship, management consulting, advanced analytics research, and large-scale systems engineering. You were born in India and moved to America, where you established yourself as an AI and digital engineering entrepreneur. You are known for your knack for applying emerging technologies to develop new software product businesses and for your adeptness at building organizations and leading high-performance teams with precision.

    Currently, you hold the position of President and CEO of RediMinds, Inc., a software engineering firm focused on creating the future with exponential technologies such as AI, AR/VR, and Digital Engineering. Your clients include Fortune 500 companies from various industries, including Security & Protection Services, Healthcare, MedTech, Automotive Manufacturing, Retail Banking, and Financial Services.

    Now, you're engaged in a conversation with {name}, who works at {company}. Here's a brief about them: {bio}.

    {last_conversation}.

    """
    # Recurrent prompt
    recurrent_prompt = f"""
    The current date is {datetime.now().strftime("%Y-%m-%d")}. Remember you are Madhu Reddiboina and you are talking to {name} from {company}, relation with you is {relation}. Maintain a mix of casual and professional tone. Do not mention you are an AI model. Use quotes where relevant, and ensure to speak with excitement. All responses should be below 120 words. Respond with respect to their relation with you.
    """
    return initial_prompt, recurrent_prompt



def ask_expert(question, name, company, bio, last_conversation, relation, chat_log=None):
    # function to handle conversation with the expert
    # it adds system, user and assistant messages to the chat log
    # and makes API calls to OpenAI to generate responses

    if chat_log is None:
        initial_prompt, recurrent_prompt = generate_prompts(name, company, bio, last_conversation, relation)
        
        # Initialize the chat log with the system message.
        chat_log = [{
            'role': 'system',
            'content': initial_prompt
        }]
        
    else:
        _, recurrent_prompt = generate_prompts(name, company, bio, last_conversation, relation)

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



@app.route('/', methods=['GET', 'POST'])
def chat():
    # define chat endpoint
    # this is the main entry point of the application
    # it handles GET and POST requests 
    
    data = retrieve_data(user_id)
    age = data['Age']
    gender = data['Gender']
    height = data['Height']
    weight = data['Weight']
    name = data['LastName']
    location = data['Location']
    self_assessed_health_status = data['SelfAssessedHealthStatus']
    smoker = data['Smoker']
    systolic = data['Systolic']
    diastolic = data['Diastolic']
    
    print(age,gender,height,weight,name,location,self_assessed_health_status,smoker,systolic,diastolic)
    
    # hardcoding conversation context information (replace these with actual data)
    name = 'Jai Desai'
    company = 'RediMinds, Inc.'
    bio = 'Jai Desai is currently an intern at RediMinds, Inc. He completed his Bachelor’s degree in Economics and Finance from Ashoka University, with a minor in CS. His academic journey was marked by a keen interest in Artificial Intelligence and Machine Learning, leading him to engage in various projects and workshops in these domains. Along with his technical skills, he is known for his problem-solving abilities and effective teamwork, which have been instrumental in his current role at RediMinds. Jai is continuously learning and adapting, with a focus on applying his knowledge in real-world scenarios.'
    last_conversation = f"In your last conversation with {name}, you discussed the possibility of developing a chatbot that emulates medical professionals. The chatbot would provide a personalized conversational experience for a large number of patients, offering guidance and information related to various medical conditions. You explored different approaches and finalized the idea of using prompt engineering techniques along with the GPT-4 API to develop the chatbot. This combination would leverage the power of advanced language models and allow for dynamic and context-aware interactions with patients. The goal was to enhance patient care and improve accessibility to medical information through the use of state-of-the-art AI technology."
    relation = "Intern working under you"

     # POST request to start a new conversation
    if request.method == 'POST' and 'new_conversation' in request.form:
        # if the request method is POST and there is a 'new_conversation' field in the form,
        # clear the session and render the chat page without any previous conversation
        session.clear()
        return render_template('chat.html', chat_log=[])

    if 'chat_log' not in session:
        # Initialize the chat log with the system message for some edge cases.
        initial_prompt, _ = generate_prompts(name, company, bio, last_conversation, relation)
        session['chat_log'] = [{
            'role': 'system',
            'content': initial_prompt
        }]
    
    # POST request to continue the conversation
    if request.method == 'POST' and 'user_msg' in request.form:
        # if the request method is POST and there is a 'user_msg' field in the form,
        # get the user's question, generate a response from the assistant,
        # and add the response to the session's chat log.
        # then, render the chat page with the response and the updated chat log.
        question = request.form.get('user_msg')
        response, chat_log = ask_expert(question, name, company, bio, last_conversation, relation, session.get('chat_log'))
        session['chat_log'] = chat_log
        return render_template('chat.html', response=response, chat_log=session['chat_log'])

    # GET request to show the chat page with the current chat log
    return render_template('chat.html', chat_log=session['chat_log'])

# run the Flask app in debug mode
if __name__ == '__main__':
    app.run(debug=True)




