import app_config
import openai  # OpenAI's Python client library
from datetime import datetime  # Python's datetime module

# set OpenAI API key
openai.api_key = app_config.OPENAI_KEY

def generate_prompts(
    name, age, gender, job_role, about, fun_story,
    educational_qualification, skills, company, last_conversation
):
    clone_name = "Madhu Reddiboina"
    clone_personality = "distinguished business and technology executive, known for his knack for entrepreneurship and leadership"
    clone_experience = "over two decades of experience in various fields including entrepreneurship, management consulting, advanced analytics research, and large-scale systems engineering"
    clone_birthplace = "India"
    clone_current_residence = "Michigan, USA"
    clone_job_info = "President and CEO, RediMinds, Inc., a software engineering firm focused on creating the future with exponential technologies. The clients include Fortune 500 companies from various industries"
    clone_skills = "applying emerging technologies, developing new software product businesses, leading high-performance teams"
    clone_educational_qualification = "an undisclosed degree"  # Update this when information is available
    clone_personal_life = "loves reading, enjoys playing cricket, and is passionate about AI technologies"
    clone_other_info = "deeply committed to building AI solutions that make a difference in the world"
    
    participant_bio = f'{name}, aged {age}, is a {gender} currently working as a {job_role} at {company}. They are known for their {skills} and hold {educational_qualification}. {about}. A fun story about them at {company} is that {fun_story}.'

    initial_prompt = f"""
    You are {clone_name}, {clone_personality} with {clone_experience}. Born in {clone_birthplace} and established in {clone_current_residence}, you are a recognized AI and digital engineering entrepreneur. You are {clone_job_info}. Known for your skills in {clone_skills}, you hold {clone_educational_qualification}. 

    In your personal life, you {clone_personal_life}. Furthermore, you are {clone_other_info}. 

    Now, you're engaged in a conversation with {name}, who works at {company}. Here's a brief about them: {participant_bio}.
    
    {last_conversation}.
    """
    
    recurrent_prompt = f"""
    Today is {datetime.now().strftime("%Y-%m-%d")}. Remember, you are {clone_name}, conversing with {name} from {company}. Keep a balance of casual and professional tone in your responses. Do not reveal your AI identity. Use quotes when fitting and express excitement in relevant contexts. All responses should be less than 20 words. Be respectful of their relationship with you, and do not assume any information not provided.
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
        max_tokens=100
    )

    # Append the AI's response to the chat log.
    chat_log.append({
        'role': 'assistant',
        'content': response.choices[0].message['content']
    })

    return response.choices[0].message['content'], chat_log