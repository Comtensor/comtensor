import gradio as gr
from transformers import pipeline


def translate(input_text, source, target):
    # source_readable = source
    # if source == "Auto Detect" or source.startswith("Detected"):
    #   source, _ = auto_detect_language_code(input_text)
    # if source in source_lang_dict.keys():
    #   source = source_lang_dict[source]
    # target_lang_dict, _ = get_target_languages(source)
    # try:
    #   target = target_lang_dict[target]
    #   model = f"Helsinki-NLP/opus-mt-{source}-{target}"
    #   pipe = pipeline("translation", model=model)
    #   translation = pipe(input_text)
    #   return translation[0]['translation_text'], ""
    # except KeyError:
    #   return "", f"Error: Translation direction {source_readable} to {target} is not supported by Helsinki Translation Models"
  pass

def input_changed(source_language_dropdown, input_text=""):
  pass

source_languages = ['en', 'po']


with gr.Blocks() as demo:
    gr.HTML("""<html>
  <head>
    <style>
      h1 {
        text-align: center;
      }
    </style>
  </head>
  <body>
    <h1>Comtensor Translate</h1>
  </body>
</html>""")
    with gr.Row():
        with gr.Column():
            source_language_dropdown = gr.Dropdown(choices=source_languages,
                                                   value="Auto Detect",
                                                  label="Source Language")
            input_textbox = gr.Textbox(lines=5, placeholder="Enter text to translate", label="Input Text")
        with gr.Column():
            target_language_dropdown = gr.Dropdown(choices=["English", "French", "Spanish"],
                                                   value="English",
                                                   label="Target Language")
            translated_textbox = gr.Textbox(lines=5, placeholder="", label="Translated Text")
    info_label = gr.HTML("")
    btn = gr.Button("Translate")
    source_language_dropdown.change(input_changed, inputs=[source_language_dropdown, input_textbox], outputs=[source_language_dropdown, target_language_dropdown])
    input_textbox.change(input_changed, inputs=[source_language_dropdown, input_textbox], outputs=[source_language_dropdown, target_language_dropdown])
    btn.click(translate, inputs=[input_textbox, source_language_dropdown, target_language_dropdown], outputs=[translated_textbox, info_label])

if __name__ == "__main__":
    demo.launch()