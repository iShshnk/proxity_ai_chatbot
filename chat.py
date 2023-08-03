import app_config
import openai  # OpenAI's Python client library
from datetime import datetime  # Python's datetime module
from db import get_avatar_info

# set OpenAI API key
openai.api_key = app_config.OPENAI_KEY

def generate_prompts(name, age, gender, job_role, about, fun_story,educational_qualification, skills, company, last_conversation):

    avatar_data_response = get_avatar_info("madhu.reddiboina@rediminds.com")
    avatar_data = avatar_data_response.json

    if "error" in avatar_data:
        raise ValueError(avatar_data["error"]) 

    participant_bio = f'{name}, {age} years old, is a {gender} currently serving as a {job_role} at {company}. {about}. They have a reputation for their {skills} and have an educational background in {educational_qualification}. An interesting fact about them is {fun_story}.'

    initial_prompt = f"""You are {avatar_data["Name"]}, a persona characterized by {avatar_data["Personality"]}. In your personal life, you are known to {avatar_data["Personal life"]}.
    Your current conversation is with {name}, a representative from {company}. Here's a brief about them: {participant_bio}.
    Here's a glimpse of your last conversation: {last_conversation}.
    """

    recurrent_prompt = f"""Remember, you are {avatar_data["Name"]}, you are in a conversation with {name} from {company}. Keep your responses balanced between casual and professional tones. Your identity as an AI should not be revealed. Use quotations when appropriate and express excitement in relevant contexts. All responses should be brief, ideally under 20 words. Be respectful and avoid making assumptions about information that hasn't been provided."""

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
        max_tokens=40
    )

    # Append the AI's response to the chat log.
    chat_log.append({
        'role': 'assistant',
        'content': response.choices[0].message['content']
    })

    return response.choices[0].message['content'], chat_log