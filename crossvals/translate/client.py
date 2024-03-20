import os
import gradio as gr
import requests
from languages import LANGUAGE_MAPPING
from dotenv import load_dotenv, find_dotenv



languages_list = LANGUAGE_MAPPING.values()

# HOST = os.environ.get("HOST_ADDRESS")
# PORT = int(os.environ.get("PORT"))
# API_URL = f"http://{HOST}:{PORT}/prompting"


def get_key_from_value(my_dict, value):
    for key, val in my_dict.items():
        if val == value:
            return key
    return None 

def translate(input_text, source, target):
    
    source_language_code = get_key_from_value(LANGUAGE_MAPPING, source)
    target_language_code = get_key_from_value(LANGUAGE_MAPPING, target)

    headers = {
      "Content-Type": "application/json",
      "Authorization": f"Bearer token",
    }

    payload = {
      "messages": [{"source": f"{source_language_code}", "target": f"{target_language_code}", "input_text": f"{input_text}"}],
    }

    
    try:
      # response = requests.post(API_URL, headers=headers, json=payload, stream=True)   
      # reply = response.json()
      
      return f'{input_text}:translation_text', ""
    except KeyError:
      return "", f"Error: Translation direction {source} to {target} is not supported by Helsinki Translation Models"



def input_changed(source_language):
  source_dropdown = gr.Dropdown(choices=languages_list,  value=source_language, label="Target Language")
  
  return source_dropdown



with gr.Blocks() as demo:
  
  title = """<h1 align="center">Comtensor Translate (Subnet 02)</h1>"""
  theme = gr.themes.Default(primary_hue="green")      
  gr.HTML(title)

  with gr.Row():
    with gr.Column():
      source_language_dropdown = gr.Dropdown(choices=languages_list, value="English", label="Source Language")
      input_textbox = gr.Textbox(lines=5, placeholder="Enter text to translate", label="Input Text")
    with gr.Column():
      target_language_dropdown = gr.Dropdown(choices=languages_list, value="English", label="Target Language")
      translated_textbox = gr.Textbox(lines=5, placeholder="", label="Translated Text")

  info_label = gr.HTML("")
  btn = gr.Button("Translate")
  source_language_dropdown.change(input_changed, inputs=[source_language_dropdown], outputs=[source_language_dropdown])
  btn.click(translate, inputs=[input_textbox, source_language_dropdown, target_language_dropdown], outputs=[translated_textbox, info_label])

if __name__ == "__main__":
  demo.queue(max_size=20, api_open=False).launch(share=True)
