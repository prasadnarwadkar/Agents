import streamlit as st
import subprocess
import streamlit.components.v1 as components

@st.cache_resource
def run_gradio():
    return subprocess.Popen(["python", "simple_agent_ui.py"])

run_gradio()

components.html("""
                <div><a href="http://localhost:7860/">Agent</a></div>
                """, width=800, height=600)
my_component = components.declare_component("my_component", url="http://localhost:7860/")

return_value = my_component(name="Blackbeard", ship="Queen Anne's Revenge")
