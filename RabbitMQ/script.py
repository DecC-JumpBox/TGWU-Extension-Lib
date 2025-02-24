"""
An example of extension. It does nothing, but you can add transformations
before the return statements to customize the webui behavior.

Starting from history_modifier and ending in output_modifier, the
functions are declared in the same order that they are called at
generation time.
"""

from threading import Thread
import gradio as gr
import torch
from transformers import LogitsProcessor
import pika
import requests

from modules import chat, shared
from modules.text_generation import (
    decode,
    encode,
    generate_reply,
)

params = {
    "display_name": "RebbitMQ Support",
    "is_tab": False,
}

def connectInit():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    rChannel = connection.channel()
    rChannel.queue_declare(queue='T2SQL question')
    rChannel.basic_consume(queue='T2SQL question', on_message_callback=callback,auto_ack=True)
    print(' [*] Waiting for messages. To exit press CTRL+C')
    rChannel.start_consuming()

def callback(ch, method, properties, body):
    print(" [x] Received "+body.decode("utf-8"))
    
    url     = 'http://localhost:5000/v1/chat/completions'
    payload = { "messages": [
      {
        "role": "user",
        "content":body.decode("utf-8")
      }
    ],
    "mode": "chat-instruct" }
    headers = {"Content-Type": "application/json"}
    res = requests.post(url, json=payload, headers=headers)
    if res.status_code == 200:
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        schannel = connection.channel()
        schannel.queue_declare(queue='T2SQL Response')
        schannel.basic_publish(exchange='', routing_key='T2SQL Response',body=res.json()['choices'][0]["message"]['content'])
        print(res.json()['choices'][0]["message"]['content'])
        schannel.close()
    




def history_modifier(history):
    """
    Modifies the chat history.
    Only used in chat mode.
    """
    return history

def state_modifier(state):
    """
    Modifies the state variable, which is a dictionary containing the input
    values in the UI like sliders and checkboxes.
    """
    return state

def chat_input_modifier(text, visible_text, state):
    """
    Modifies the user input string in chat mode (visible_text).
    You can also modify the internal representation of the user
    input (text) to change how it will appear in the prompt.
    """
    return text, visible_text

def input_modifier(string, state, is_chat=False):
    """
    In default/notebook modes, modifies the whole prompt.

    In chat mode, it is the same as chat_input_modifier but only applied
    to "text", here called "string", and not to "visible_text".
    """
    return string

def bot_prefix_modifier(string, state):
    """
    Modifies the prefix for the next bot reply in chat mode.
    By default, the prefix will be something like "Bot Name:".
    """
    return string

def tokenizer_modifier(state, prompt, input_ids, input_embeds):
    """
    Modifies the input ids and embeds.
    Used by the multimodal extension to put image embeddings in the prompt.
    Only used by loaders that use the transformers library for sampling.
    """
    return prompt, input_ids, input_embeds

def logits_processor_modifier(processor_list, input_ids):
    """
    Adds logits processors to the list, allowing you to access and modify
    the next token probabilities.
    Only used by loaders that use the transformers library for sampling.
    """
    
    return processor_list

def output_modifier(string, state, is_chat=False):
    """
    Modifies the LLM output before it gets presented.

    In chat mode, the modified version goes into history['visible'],
    and the original version goes into history['internal'].
    """
    return string

def custom_generate_chat_prompt(user_input, state, **kwargs):
    """
    Replaces the function that generates the prompt from the chat history.
    Only used in chat mode.
    """
    result = chat.generate_chat_prompt(user_input, state, **kwargs)
    return result

def custom_css():
    """
    Returns a CSS string that gets appended to the CSS for the webui.
    """
    return ''

def custom_js():
    """
    Returns a javascript string that gets appended to the javascript
    for the webui.
    """
    return ''

def setup():
    """
    Gets executed only once, when the extension is imported.
    """
    threadMQ = Thread(target=connectInit)
    threadMQ.start()
    pass

def ui():
    """
    Gets executed when the UI is drawn. Custom gradio elements and
    their corresponding event handlers should be defined here.

    To learn about gradio components, check out the docs:
    https://gradio.app/docs/
    """
    
    pass
