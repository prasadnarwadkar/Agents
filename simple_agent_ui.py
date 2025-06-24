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

def chat_with_openai(input_text:str,  chatbot: list[dict], message_history: list):
    # Append user message to history
    message_history.append({"role": "user", "content": input_text})
    chatbot.append({"role": "user", "content": input_text})

    response_stream = client.responses.create(
        model="gpt-4o-mini",
        stream=True,
        input=message_history,
        tools=[
            {
                "type": "file_search",
                "vector_store_ids": [vector_store.id],
            }
        ],
    )

    chatbot.append({'role': 'assistant', 'content': ''})
    
    response_text = ""
    for event in response_stream:
        if event.type == "response.output_text.delta":
            print(event.delta, end="")
            response_text += event.delta
        elif event.type == "response.error":
            print(f"\nError occurred: {event.error}")
        # Append assistant response to history
        message_history.append({"role": "assistant", "content": response_text})
        chatbot[-1]['content'] = response_text
            
        yield gr.skip(), chatbot, gr.skip()

    yield gr.Textbox(interactive=True), chatbot, message_history

def select_data(message: gr.SelectData) -> str:
    return message.value['text']


with gr.Blocks() as demo:
    # Maintain message history
    message_history = gr.State([])
    chatbot = gr.Chatbot(
        label='Bank Assistant',
        type='messages',
        
        avatar_images=(None, 'https://ai.pydantic.dev/img/logo-white.svg'),
        examples=[
            {'text': 'What is Masre Dox?', 'alt_text': ''},
        ],
    )
    with gr.Row():
        with gr.Column():
            user_input = gr.Textbox(label="Ask something")

    user_input.submit(fn=chat_with_openai, inputs=[user_input,chatbot,message_history], outputs=[user_input,chatbot,message_history])
    chatbot.example_select(select_data, None, [user_input])
    demo.queue()
    demo.launch()
