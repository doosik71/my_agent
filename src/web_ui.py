import streamlit as st
from agent_core import get_agent_response, doc_manager, model # Import 'model' to start chat session
import os
import google.generativeai as genai # Import genai to access ToolCode and FunctionCall

st.set_page_config(page_title="my_agent Web UI", layout="wide")

st.title("🤖 my_agent: Gemini-Powered Autonomous Agent")
st.markdown("---")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize chat session if it doesn't exist
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(enable_automatic_function_calling=True)

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("Ask my_agent a question or give a command..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("my_agent is thinking..."):
        # Get full response object from agent_core.py, passing the persistent chat session
        response_obj = get_agent_response(prompt, st.session_state.chat_session)
        
        # Process the response object
        full_response_content = ""
        with st.chat_message("assistant"):
            for part in response_obj.parts:
                if part.text:
                    st.markdown(part.text)
                    full_response_content += part.text
                if part.function_call:
                    st.info(f"Agent called tool: **{part.function_call.name}** with args: `{part.function_call.args}`")
                    # The output of the tool call is automatically added to the chat history for the next turn.

    # Add agent's full response (text content only) to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response_content})

st.sidebar.title("📚 Documents in Sandbox")
st.sidebar.markdown("---")

# Display documents in the sidebar
with st.sidebar:
    st.subheader("Existing Documents")
    documents_list = doc_manager.list_docs().split('\n')
    
    if documents_list and documents_list[0] != "No documents found.":
        selected_doc = st.selectbox("Select a document to view:", documents_list)
        if selected_doc:
            doc_content = doc_manager.read_doc(selected_doc)
            st.text_area(f"Content of {selected_doc}", doc_content, height=300)
    else:
        st.info("No documents found yet. Ask my_agent to create one!")

st.sidebar.markdown("---")
st.sidebar.info("You can instruct my_agent to 'write_doc(\"path/to/file.md\", \"Your content here\")' or 'read_doc(\"path/to/file.md\")'.")
