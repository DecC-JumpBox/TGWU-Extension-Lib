"""
An example of extension. It does nothing, but you can add transformations
before the return statements to customize the webui behavior.

Starting from history_modifier and ending in output_modifier, the
functions are declared in the same order that they are called at
generation time.
"""

import gradio as gr
import torch
from transformers import LogitsProcessor
from typing_extensions import Annotated
from modules import chat, shared
from modules.text_generation import (
    decode,
    encode,
    generate_reply,
)
from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool

from langchain import hub
from typing_extensions import TypedDict
import pika

params = {
    "display_name": "T2SQL POC",
    "is_tab": True,
}

dbconstr:str = ""
db:SQLDatabase = None
isEnable:bool = False
query_prompt_template:str = ""

class SQLAnswer (TypedDict):
   question:str
   query:str
   result:str
   answer:str
   def __init__(self):
        pass 
pass
"""
class MyLogits(LogitsProcessor):
    
    Manipulates the probabilities for the next token before it gets sampled.
    Used in the logits_processor_modifier function below.
    
    def __init__(self):
        pass

    def __call__(self, input_ids, scores):
        # probs = torch.softmax(scores, dim=-1, dtype=torch.float)
        # probs[0] /= probs[0].sum()
        # scores = torch.log(probs / (1 - probs))
        return scores

"""
def SetConstr(value:str):
    global dbconstr 
    global db 
    dbconstr= value
    db= SQLDatabase.from_uri(value)
    gr.Info("Connection String Set Successfully. New Connection String is "+dbconstr)
pass
def SetUi():
    global isEnable 
    
    isEnable = not isEnable
    return gr.update(visible=isEnable)
pass




def chat_input_modifier(text, visible_text, state):
    """
    Modifies the user input string in chat mode (visible_text).
    You can also modify the internal representation of the user
    input (text) to change how it will appear in the prompt.
    """
    return text, visible_text

def input_modifier(string, state, is_chat=True):
    """
    In default/notebook modes, modifies the whole prompt.

    In chat mode, it is the same as chat_input_modifier but only applied
    to "text", here called "string", and not to "visible_text".
    """
    if isEnable:


        assert len(query_prompt_template.messages) == 1
        ##query_prompt_template.messages[0].pretty_print()
        prompt= query_prompt_template.invoke(
            {
                "dialect": db.dialect,
                "top_k": 10,
                "table_info": db.get_table_info(),
                "input": string,
            }
        )
        return prompt.messages[0].content + "\n The result should only show the query."
    else:
        return string
    
    
    

def bot_prefix_modifier(string, state):
    """
    Modifies the prefix for the next bot reply in chat mode.
    By default, the prefix will be something like "Bot Name:".
    """
    return string

def logits_processor_modifier(processor_list, input_ids):
    """
    Adds logits processors to the list, allowing you to access and modify
    the next token probabilities.
    Only used by loaders that use the transformers library for sampling.
    """

    return processor_list

def output_modifier(string, state, is_chat=True):
    """
    Modifies the LLM output before it gets presented.

    In chat mode, the modified version goes into history['visible'],
    and the original version goes into history['internal'].
    """
    if isEnable:
        print(string)
        execute_query_tool = QuerySQLDataBaseTool(db=db)
        return execute_query_tool.invoke(string)
    else:
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
    global query_prompt_template
    query_prompt_template = hub.pull("langchain-ai/sql-query-system-prompt")
    


pass#setup End

def ui():
    """
    Gets executed when the UI is drawn. Custom gradio elements and
    their corresponding event handlers should be defined here.
    To learn about gradio components, check out the docs:
    https://gradio.app/docs/
    """ 
    enableCheck=gr.Checkbox(value=isEnable,label="Enable")    
    inputConstr:str=""
    with gr.Group(visible=isEnable) as group:
        input1 = gr.Textbox(value= inputConstr,label="DB Connection string")
        confirmBTN = gr.Button(value="Set Connection String")
        confirmBTN.click(SetConstr,input1)
    enableCheck.change(SetUi,outputs=group)
    
pass #ui End
