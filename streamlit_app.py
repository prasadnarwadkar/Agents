import streamlit as st
import subprocess
import streamlit.components.v1 as components

@st.cache_resource
def run_gradio():
    gradio_app = subprocess.Popen(["python", "simple_agent_ui.py"])
    print (gradio_app.returncode)

run_gradio()

components.html("""
                <div><a href="https://bookish-space-couscous-9gvgrx7jvr3x7px-7860.app.github.dev/">Use Your Agent</a>&nbsp;<a href="https://skolo-ai-agent.ams3.cdn.digitaloceanspaces.com/pydantic/the_seven_realms.pdf" target="_blank">The context from this PDF is added to the model using RAG pipeline</a>&nbsp;<span>Please read this PDF and ask questions from it.</span></div>
                """, width=1000, height=1000)

