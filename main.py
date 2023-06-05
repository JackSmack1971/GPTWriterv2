import openai
import os
from dotenv import load_dotenv
import signal

# ANSI escape codes for color formatting
COLOR_EDITOR = '\033[34m'  # Blue color for editor
COLOR_WRITER = '\033[35m'  # Magenta color for writer
COLOR_RESET = '\033[0m'    # Reset color to default

def read_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read().strip()
    return content

def chatgpt3(editor_instructions_file, writer_input_file, trigger_message_file, temperature=0.7, frequency_penalty=0, presence_penalty=0):
    editor_instructions = read_file(editor_instructions_file)
    writer_input = read_file(writer_input_file)
    trigger_message = read_file(trigger_message_file)
    
    messagein = [
        {"role": "system", "content": "You are Agent 1, the editor."},
        {"role": "system", "content": "You are Agent 2, the writer."},
        {"role": "user", "content": trigger_message},
        {"role": "user", "content": editor_instructions},
        {"role": "user", "content": writer_input}
    ]
    
    conversation = []  # Store the conversation
    
    def handle_interrupt(signal, frame):
        print('\nConversation interrupted. Exiting gracefully...')
        exit(0)
    
    # Register the interrupt handler
    signal.signal(signal.SIGINT, handle_interrupt)
    
    while True:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messagein,
                temperature=temperature,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty
            )
            text = response['choices'][0]['message']['content']
            
            messagein.append({"role": "user", "content": text})
            conversation.append({"role": "agent1", "content": text})
            
            if "stellar" in text:
                break
            
            messagein.append({"role": "user", "content": ""})
            conversation.append({"role": "agent2", "content": ""})
            
            # Print the latest message with the respective color
            print_message(conversation[-1])
            
            # Print the API response for debugging
            print("API Response:", text)
        
        except openai.error.APIError as e:
            print('\nConversation stopped due to an API error:', e)
            exit(1)
    
    return conversation

def print_message(message):
    role = message['role']
    content = message['content']
    
    if role == 'agent1':
        print(COLOR_EDITOR + 'Editor: ' + content + COLOR_RESET)
    elif role == 'agent2':
        print(COLOR_WRITER + 'Writer: ' + content + COLOR_RESET)
    else:
        print(content)

# Load environment variables from .env file
load_dotenv()

# Access the OpenAI API key from the environment variable
api_key = os.getenv("OPENAI_API_KEY")

# Set the OpenAI API key
openai.api_key = api_key

# File paths for editor instructions, writer input, and trigger message
editor_instructions_file = 'editor_instructions.txt'
writer_input_file = 'writer_input.txt'
trigger_message_file = 'trigger_message.txt'

# Call the chatgpt3 function with the file paths
conversation = chatgpt3(editor_instructions_file, writer_input_file, trigger_message_file)

# Print the entire conversation
for message in conversation:
    print_message(message)
