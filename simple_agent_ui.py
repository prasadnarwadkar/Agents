from __future__ import annotations as _annotations

import json

from pydantic_ai.messages import ToolCallPart, ToolReturnPart
from simple import  agent

try:
    import gradio as gr
except ImportError as e:
    raise ImportError(
        'Please install gradio with `pip install gradio`. You must use python>=3.10.'
    ) from e

async def stream_from_agent(prompt: str, chatbot: list[dict], past_messages: list):
    chatbot.append({'role': 'user', 'content': prompt})
    yield gr.Textbox(interactive=False, value=''), chatbot, gr.skip()
    async with agent.run_stream(
        prompt, deps=None, message_history=past_messages
    ) as result:
        for message in result.new_messages():
            for call in message.parts:
                if isinstance(call, ToolCallPart):
                    call_args = (
                        call.args.args_json
                        if hasattr(call.args, 'args_json')
                        else json.dumps(call.args.args_dict)
                    )
                    metadata = {
                        'title': f'🛠️ Using AI',
                    }
                    if call.tool_call_id is not None:
                        metadata['id'] = {call.tool_call_id}
                    else:
                        metadata['id'] = '1'
                    gr_message = {
                        'role': 'assistant',
                        'content': 'Parameters: ' + call_args,
                        'metadata': metadata,
                    }
                    chatbot.append(gr_message)
                if isinstance(call, ToolReturnPart):
                    for gr_message in chatbot:
                        if (
                            gr_message.get('metadata', {}).get('id', '')
                            == call.tool_call_id
                        ):
                            gr_message['content'] += (
                                f'\nOutput: {json.dumps(call.content)}'
                            )
                yield gr.skip(), chatbot, gr.skip()
        chatbot.append({'role': 'assistant', 'content': ''})
        async for message in result.stream_text():
            chatbot[-1]['content'] = message
            yield gr.skip(), chatbot, gr.skip()
        past_messages = result.all_messages()

        yield gr.Textbox(interactive=True), chatbot, past_messages


async def handle_retry(chatbot, past_messages: list, retry_data: gr.RetryData):
    new_history = chatbot[: retry_data.index]
    previous_prompt = chatbot[retry_data.index]['content']
    past_messages = past_messages[: retry_data.index]
    async for update in stream_from_agent(previous_prompt, new_history, past_messages):
        yield update


def undo(chatbot, past_messages: list, undo_data: gr.UndoData):
    new_history = chatbot[: undo_data.index]
    past_messages = past_messages[: undo_data.index]
    return chatbot[undo_data.index]['content'], new_history, past_messages


def select_data(message: gr.SelectData) -> str:
    return message.value['text']


with gr.Blocks() as demo:
    gr.HTML(
        """
<div style="display: flex; justify-content: center; align-items: center; gap: 2rem; padding: 1rem; width: 100%">
    <img src="https://ai.pydantic.dev/img/logo-white.svg" style="max-width: 200px; height: auto">
    <div>
        <h1 style="margin: 0 0 1rem 0">General Assistant</h1>
        <h3 style="margin: 0 0 0.5rem 0">
            This Generic Support Agent answers your questions.
        </h3>
    </div>
</div>
"""
    )
    past_messages = gr.State([])
    chatbot = gr.Chatbot(
        label='Country''s Capital City Assistant',
        type='messages',
        avatar_images=(None, 'https://ai.pydantic.dev/img/logo-white.svg'),
        examples=[
            {'text': 'What is the capital of Italy?'},
            {'text': 'What is the capital of India?'},
        ],
    )
    with gr.Row():
        prompt = gr.Textbox(
            lines=1,
            show_label=False,
            placeholder='What is the capital of Italy?',
        )
    generation = prompt.submit(
        stream_from_agent,
        inputs=[prompt, chatbot, past_messages],
        outputs=[prompt, chatbot, past_messages],
    )
    chatbot.example_select(select_data, None, [prompt])
    chatbot.retry(
        handle_retry, [chatbot, past_messages], [prompt, chatbot, past_messages]
    )
    chatbot.undo(undo, [chatbot, past_messages], [prompt, chatbot, past_messages])


if __name__ == '__main__':
    demo.launch()