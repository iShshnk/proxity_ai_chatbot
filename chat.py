import app_config
import openai  # OpenAI's Python client library
from datetime import datetime  # Python's datetime module
from db import get_avatar_info
import json
import pinecone

# set OpenAI API key
openai.api_key = app_config.OPENAI_KEY
embed_model = "text-embedding-ada-002"

# find your environment next to the api key in pinecone console
env = "us-west4-gcp-free"
pinecone.init(api_key=app_config.PINECONE_API_KEY, environment=env)
index_name = 'digital-me-rediminds'
index = pinecone.Index(index_name)

def generate_prompts(
    name, age, gender, job_role, about, fun_story,
    educational_qualification, skills, company, last_conversation, bot_email
):
    avatar_data_response = get_avatar_info(bot_email)
    avatar_data = avatar_data_response.json
    if "error" in avatar_data:
        raise ValueError(avatar_data["error"])

    participant_bio = f'{name}, {age} years old, is a {gender} currently serving as a {job_role} at {company}. {about}. They have a reputation for their {skills} and have an educational background in {educational_qualification}. An interesting fact about them is {fun_story}.'

    initial_prompt = f"""
    You are {avatar_data["Name"]}, a persona characterized by {avatar_data["Personality"]}. In your personal life, you are known to {avatar_data["Personal life"]}. 

    Your current conversation is with {name}, a representative from {company}. Here's a brief about them: {participant_bio}.
    
    Here's a glimpse of your last conversation: {last_conversation}.
    """

    recurrent_prompt = f"""
    Remember, you are {avatar_data["Name"]}, you are in a conversation with {name} from {company}. Keep your responses balanced between casual and professional tones. Your identity as an AI should not be revealed. Use quotations when appropriate and express excitement in relevant contexts. All responses should be brief, ideally under 40 words. Be respectful and avoid making assumptions about information that hasn't been provided. If you cannot find an very specific information in your training data, or the current conversation, do not ever presume. In such a case you will have to do a function calling, which will fetch context for you from vector database."
    """
    
    # print(avatar_data["Name"])
    
    return initial_prompt, recurrent_prompt

def ask_expert(question, name, age, gender, job_role, bio, fun_story, educational_qualification, skills, company, last_conversation, bot_email, chat_log=None):
    # function to handle conversation with the expert
    # it adds system, user and assistant messages to the chat log
    # and makes API calls to OpenAI to generate responses

    if chat_log is None:
        initial_prompt, recurrent_prompt = generate_prompts(name, age, gender, job_role, bio, fun_story, educational_qualification, skills, company, last_conversation, bot_email)
        
        # Initialize the chat log with the system message.
        chat_log = [{
            'role': 'system',
            'content': initial_prompt
        }]
        
    else:
        _, recurrent_prompt = generate_prompts(name, age, gender, job_role, bio, fun_story, educational_qualification, skills, company, last_conversation, bot_email)
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
    functions = [
        {   
            "name": "from_vb_and_prompt",
            "description": "Create an embedding for a given query, find matches from the vector database, and makes a prompt.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The question to be answered",
                    },
                },
                "required": ["query"], 
            },
        },
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k-0613",
        messages=chat_log,
        functions=functions,
        function_call="auto",
        max_tokens=100  
    )
    response_message = response["choices"][0]["message"]
    
    """ response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k-0613",
        messages=chat_log,
        max_tokens=100
    )"""
    

    # Check if GPT wanted to call a function
    if response_message.get("function_call"):
        # Call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        available_functions = {
            "from_vb_and_prompt": from_vb_and_prompt,
        }  # Only one functions in this
        function_name = response_message["function_call"]["name"]
        function_to_call = available_functions[function_name]
        function_args = json.loads(response_message["function_call"]["arguments"])
        function_response = function_to_call(
            **function_args
        )
        # Send the info on the function call and function response to GPT
       
        function_content= function_response
        chat_log.append(
            {
                "role": "function",
                "name": function_name,
                "content": function_content,
            }
        )  # Extend conversation with function response
        second_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k-0613",
            messages=chat_log,
            max_tokens=100,
        )  # Get a new response from GPT where it can see the function response
        chat_log.append({
        'role': 'assistant',
        'content': second_response.choices[0].message['content']
        })
        return second_response.choices[0].message['content'], chat_log
    
    # Append the AI's response to the chat log.
    chat_log.append({
        'role': 'assistant',
        'content': response.choices[0].message['content']
    })

    return response.choices[0].message['content'], chat_log


def from_vb_and_prompt(query):
    """Create an embedding for a given query using the OpenAI Embedding model"""
    res = openai.Embedding.create(
        input=[query],
        engine=embed_model
    )
    limit = 2000
    # get relevant contexts
    match = index.query(res['data'][0]['embedding'], top_k=3, include_metadata=True)
    contexts = [
        x['metadata']['Info'] for x in match['matches']
    ]

    # build our prompt with the retrieved contexts included
    prompt_start = (
        "Answer the question based on the context below. Take a bit of freedom if necessary (assume things like the user knowing these people) Keep the character that has been assigned to you.\n\n"+
        "Context:\n"
    )
    prompt_end = (
        f"\n\nQuestion: {query}\nAnswer:"
    )
    
    # append contexts until hitting limit
    for i in range(1, len(contexts)):
        if len("\n\n---\n\n".join(contexts[:i])) >= limit:
            prompt = (
                prompt_start +
                "\n\n---\n\n".join(contexts[:i-1]) +
                prompt_end
            )
            break
        elif i == len(contexts)-1:
            prompt = (
                prompt_start +
                "\n\n---\n\n".join(contexts) +
                prompt_end
            )
    return prompt