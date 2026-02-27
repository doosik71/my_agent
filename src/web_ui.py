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
    st.session_state.my_agent_instance = MyAgent()

agent = st.session_state.my_agent_instance

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize chat session if it doesn't exist
if "chat_session" not in st.session_state:
    st.session_state.chat_session = agent.create_session()

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle showing document content in chat window triggered by sidebar button
if st.session_state.get("show_doc_in_chat_trigger"):
    st.session_state.show_doc_in_chat_trigger = False  # Reset the trigger
    doc_info = st.session_state.pop("doc_to_show_in_chat", None)

    if doc_info:
        selected_doc = doc_info["selected_doc"]

        with st.spinner("my_agent is reading..."):
            # Send to agent as if user typed it
            # This call is blocking, and the spinner will be visible during its execution.
            user_prompt_for_agent = f"Please output the content of the file at '{selected_doc}'."
            _ = agent.send_message(
                user_prompt_for_agent, st.session_state.chat_session)

# User input
if prompt := st.chat_input("Ask my_agent a question or give a command..."):
    if prompt.strip() == "/clear":
        st.session_state.messages = []
        st.session_state.chat_session = agent.create_session()
        st.rerun()

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
            else:
                st.error(getattr(response_obj, 'text',
                         "Unknown Error Occurred"))
                full_response_content = getattr(response_obj, 'text', "")

    st.session_state.messages.append(
        {"role": "assistant", "content": full_response_content})

st.sidebar.title("🤖 My Agent")


@st.fragment
def document_explorer():
    st.subheader("Existing Documents")

    filter_query = st.text_input(
        "Filter documents",
        placeholder="Search (Press Enter to apply)",
        label_visibility="collapsed",
        key="doc_filter_input"
    ).lower()

    docs_raw = doc_manager.list_docs()
    # 빈 줄 제외 및 리스트 변환
    documents_list = [d.strip()
                      for d in docs_raw.split('\n') if d.strip()] if docs_raw else []

    if documents_list and documents_list[0] != "No documents found.":
        # 필터링 적용
        if filter_query:
            filtered_docs = [
                doc for doc in documents_list if filter_query in doc.lower()]
        else:
            filtered_docs = documents_list

        if filtered_docs:
            selected_doc = st.selectbox(
                "Select a document to view:",
                filtered_docs,
                key="doc_selectbox"
            )
            if selected_doc:
                doc_content = doc_manager.read_doc(selected_doc)
                st.text_area(f"Content of {selected_doc}",
                             doc_content, height=600)

                # CSS to right-align the button within its container without word-wrapping
                st.markdown(
                    """
                    <style>
                    div.stElementContainer:has(> .stButton) {
                        display: flex;
                        justify-content: flex-end;
                        width: 100%;
                    }
                    .stButton {
                        width: auto !important;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True
                )

                if st.button("Show in Conversation Window", key="show_doc_conv_btn"):
                    agent_response_for_document = f"The content of the file `{selected_doc}` is as follows:\n\n{doc_content}"
                    st.session_state.messages.append(
                        {"role": "assistant", "content": agent_response_for_document})

                    st.session_state.show_doc_in_chat_trigger = True
                    st.session_state.doc_to_show_in_chat = {
                        "selected_doc": selected_doc
                    }

                    st.rerun()
        else:
            st.info("No matching documents.")
    else:
        st.info("No documents found yet. Ask my_agent to create one!")


with st.sidebar:
    document_explorer()
    st.info("https://github.com/doosik71/my_agent/")
