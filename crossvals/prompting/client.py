import gradio as gr
import os
import sys
import json 
import requests
from dotenv import load_dotenv, find_dotenv


_ = load_dotenv(find_dotenv())

HOST = os.environ.get("HOST_ADDRESS")
PORT = int(os.environ.get("PORT"))
API_URL = f"http://{HOST}:{PORT}/prompting"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def exception_handler(exception_type, exception, traceback):
    print("%s: %s" % (exception_type.__name__, exception))
sys.excepthook = exception_handler
sys.tracebacklimit = 0


def parse_codeblock(text):
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if "```" in line:
            if line != "```":
                lines[i] = f'<pre><code class="{lines[i][3:]}">'
            else:
                lines[i] = '</code></pre>'
        else:
            if i > 0:
                lines[i] = "<br/>" + line.replace("<", "&lt;").replace(">", "&gt;")
    return "".join(lines)
    
def predict(inputs, chat_counter, chatbot, history, request:gr.Request):
    payload = {
        "messages": [{"role": "user", "content": f"{inputs}"}],
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}",
    }


    if chat_counter != 0 :
        messages = []
        for i, data in enumerate(history):
            if i % 2 == 0:
                role = 'user'
            else:
                role = 'assistant'
            message = {}
            message["role"] = role
            message["content"] = data
            messages.append(message)
        
        message = {}
        message["role"] = "user" 
        message["content"] = inputs
        messages.append(message)
        payload = {
            "messages": messages,
        }

    chat_counter += 1

    history.append(inputs)

    try:
        response = requests.post(API_URL, headers=headers, json=payload, stream=True)   

        response_code = f"{response}"
        if response_code.strip() != "<Response [200]>":
            print(f"response code - {response}")
            raise Exception(f"Sorry, hitting rate limit. Please try again later. {response}")
        
        reply = response.json()
        history.append(reply)

        yield [(parse_codeblock(history[i]), parse_codeblock(history[i + 1])) for i in range(0, len(history) - 1, 2) ], history, chat_counter, response, gr.update(interactive=True), gr.update(interactive=True)
       
    except Exception as e:
        print (f'error found: {e}')
    yield [(parse_codeblock(history[i]), parse_codeblock(history[i + 1])) for i in range(0, len(history) - 1, 2) ], history, chat_counter, response, gr.update(interactive=True), gr.update(interactive=True)


def reset_textbox():
    return gr.update(value='', interactive=False), gr.update(interactive=False)

title = """<h1 align="center">Comtensor Prompting (Subnet 01)</h1>"""

theme = gr.themes.Default(primary_hue="green")                

with gr.Blocks(css = """#col_container { margin-left: auto; margin-right: auto;} #chatbot {height: 520px; overflow: auto;}""", theme=theme) as demo:
    gr.HTML(title)
    with gr.Column(elem_id = "col_container", visible=True) as main_block:

        chatbot = gr.Chatbot(elem_id='chatbot') #c
        inputs = gr.Textbox(placeholder= "Hi there!", label= "Type an input and press Enter") #t
        state = gr.State([]) #s
        with gr.Row():
            with gr.Column(scale=7):
                b1 = gr.Button(visible=False)
            with gr.Column(scale=3):
                server_status_code = gr.Textbox(label="Status code from OpenAI server", )
    
        chat_counter = gr.Number(value=0, visible=False, precision=0)
        
    


    inputs.submit(reset_textbox, [], [inputs, b1], queue=False)
    inputs.submit(predict, [inputs, chat_counter, chatbot, state], [chatbot, state, chat_counter, server_status_code, inputs, b1],)   
    b1.click(reset_textbox, [], [inputs, b1], queue=False)
    b1.click(predict, [inputs, chat_counter, chatbot, state], [chatbot, state, chat_counter, server_status_code, inputs, b1],)  
             
    demo.queue(max_size=20, api_open=False).launch(share=True)