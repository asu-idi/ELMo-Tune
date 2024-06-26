import os
import re
from openai import OpenAI

# Environment variables
client = OpenAI()
client.api_key = os.getenv("OPENAI_API_KEY")

def request_gpt(system_content, user_contents, temperature):
    '''
    Function to make an API call to GPT-4

    Parameters:
    - system_content: string containing the system information
    - chunk_string: string containing the chunk of the options file
    - previous_option_files: list of tuples containing the previous option files and their benchmark results
    - temperature: Float (0-1) controlling GPT-4's output randomness.
    - average_cpu_used: Float indicating average CPU usage (default -1.0).
    - average_mem_used: Float indicating average memory usage (default -1.0).
    - test_name: String stating the benchmark test.

    Returns:
    - matches: string containing the options file generated by GPT-4
    '''
    messages = [{"role": "system", "content": system_content}]
    for content in user_contents:
        messages.append({"role": "user", "content": content})


    # Assuming 'client' is already defined and authenticated for GPT-4 API access
    completion = client.chat.completions.create(
        model="gpt-4-0125-preview",
        messages=messages,
        temperature=temperature,
        max_tokens=4096,
        frequency_penalty=0,
        presence_penalty=0,
    )

    # Extract the assistant's reply
    assistant_reply = completion.choices[0].message.content
    matches = re.match("[\s\S]*```([\s\S]*)```([\s\S]*)", assistant_reply)

    # Check if result is good
    if matches is not None:
        return matches 

    # Invalid response
    with open("invalid_assistant_reply.txt", "a") as file:
        file.write(assistant_reply + "\n\n" + "-" * 150 + "\n\n")
    return None
