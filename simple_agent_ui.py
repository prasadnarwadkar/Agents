import os
from openai import OpenAI
import mysettings

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

vector_store_id = mysettings.MySettings.get_static()
vector_store = client.vector_stores.retrieve(
    vector_store_id=vector_store_id
)

try:
    import gradio as gr
except ImportError as e:
    raise ImportError(
        "Please install gradio with `pip install gradio`. You must use python>=3.10."
    ) from e

def chat_with_openai(input_text):
    response_stream = client.responses.create(
        model="gpt-4o-mini",
        stream=True,
        input= input_text,
        tools=[
            {
                "type": "file_search",
                "vector_store_ids": [vector_store.id],
            }
        ],
    )
    response_text = ""
    for event in response_stream:
        if event.type == "response.output_text.delta":
            print(event.delta, end="")
            response_text += event.delta
        elif event.type == "response.error":
            print(f"\nError occurred: {event.error}")
        yield response_text

with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column():
            user_input = gr.Textbox(label="Ask something")
            submit_btn = gr.Button("Submit")
        with gr.Column():
            output = gr.Textbox(label="Response")

    submit_btn.click(fn=chat_with_openai, inputs=user_input, outputs=output)
    demo.queue()
    demo.launch()

if __name__ == "__main__":
    demo.queue()

    demo.launch()
