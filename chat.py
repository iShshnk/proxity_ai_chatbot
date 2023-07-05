import app_config
import openai  # OpenAI's Python client library
from datetime import datetime  # Python's datetime module

# set OpenAI API key
openai.api_key = app_config.OPENAI_KEY

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
    The current date is {datetime.now().strftime("%Y-%m-%d")}. Remember you are Madhu Reddiboina and you are talking to {name} from {company}. Maintain a mix of casual and professional tone. Do not mention you are an AI model. Use quotes where relevant, and ensure to speak with excitement. All responses should be below 20 words. Respond with respect to their relation with you. Don't assume anything about your interaction or relationship with them than already speciifed.
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
        max_tokens=40
    )

    # Append the AI's response to the chat log.
    chat_log.append({
        'role': 'assistant',
        'content': response.choices[0].message['content']
    })

    return response.choices[0].message['content'], chat_log