import os
from dotenv import load_dotenv
import openai

def read_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read().strip()
    return content

def save_to_file(file_path, content):
    with open(file_path, 'w') as file:
        file.write(content)

def print_message(role, content, color):
    print(f"{role}: {content}", color)

def truncate_text(text, max_length):
    if len(text) <= max_length:
        return text
    else:
        return text[:max_length - 3] + "..."  # Truncate and add ellipsis

def chatgpt3(editor_instructions_file, writer_input_file, trigger_message_file):
    editor_instructions = read_file(editor_instructions_file)
    writer_input = read_file(writer_input_file)
    trigger_message = read_file(trigger_message_file)

    messagein = [
        {"role": "system", "content": "You are Agent 1, the editor."},
        {"role": "system", "content": "You are Agent 2, the writer."},
        {"role": "user", "content": truncate_text(trigger_message, 400)},
        {"role": "user", "content": truncate_text(editor_instructions, 400)},
        {"role": "user", "content": truncate_text(writer_input, 400)}
    ]

    while True:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messagein,
            max_tokens=100
        )

        message = response.choices[0].message
        role = message["role"]
        content = message["content"]

        messagein.append({"role": role, "content": content})

        if "Ready to publish" in content:
            break

        color = "\033[32m" if role == "user" else "\033[34m"
        print_message(role, content, color)

    final_blog_post = '\n'.join([message['content'] for message in messagein if message['role'] == 'user'])
    save_to_file('final_blog_post.txt', final_blog_post)
    print('\nFinal blog post saved as "final_blog_post.txt."')

    return messagein

def main():
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")
    editor_instructions_file = "editor_instructions.txt"
    writer_input_file = "writer_input.txt"
    trigger_message_file = "trigger_message.txt"
    conversation = chatgpt3(editor_instructions_file, writer_input_file, trigger_message_file)

if __name__ == '__main__':
    main()
