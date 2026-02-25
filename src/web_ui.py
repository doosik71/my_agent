from src.agent_core import MyAgent
from src.tools.tool_definitions import doc_manager
import streamlit as st  # pyright: ignore[reportMissingImports]
import os


st.set_page_config(page_title="My Agent", layout="wide")

st.title("🤖 My Agent")
st.markdown("### Gemini-Powered Autonomous Agent")
st.markdown("---")

# Initialize MyAgent
if "my_agent_instance" not in st.session_state:
    st.session_state.my_agent_instance = MyAgent(
        model_name=os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash"))

agent = st.session_state.my_agent_instance

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize chat session if it doesn't exist
if "chat_session" not in st.session_state:
    st.session_state.chat_session = agent.client.chats.create(
        model=agent.model_name,
        config=agent.config
    )

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
        # agent_core의 send_message 호출
        response_obj = agent.send_message(
            prompt, st.session_state.chat_session)

        full_response_content = ""
        with st.chat_message("assistant"):
            if hasattr(response_obj, 'candidates') and response_obj.candidates:
                for part in response_obj.candidates[0].content.parts:
                    if part.text:
                        st.markdown(part.text)
                        full_response_content += part.text

                    if part.function_call:
                        call = part.function_call
                        st.info(
                            f"🛠️ **도구 실행:** `{call.name}`\n\n"
                            f"**입력값:** `{call.args}`"
                        )
            else:
                st.error(getattr(response_obj, 'text',
                         "Unknown Error Occurred"))
                full_response_content = getattr(response_obj, 'text', "")

    st.session_state.messages.append(
        {"role": "assistant", "content": full_response_content})

st.sidebar.title("🤖 My Agent")

with st.sidebar:
    st.subheader("Existing Documents")
    docs_raw = doc_manager.list_docs()
    documents_list = docs_raw.split('\n') if docs_raw else []

    if documents_list and documents_list[0] != "No documents found.":
        selected_doc = st.selectbox(
            "Select a document to view:", documents_list)
        if selected_doc:
            doc_content = doc_manager.read_doc(selected_doc)
            st.text_area(f"Content of {selected_doc}", doc_content, height=600)
    else:
        st.info("No documents found yet. Ask my_agent to create one!")

st.sidebar.info(
    "https://github.com/doosik71/my_agent/")
