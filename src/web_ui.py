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
    if prompt.strip() == "/clear":
        st.session_state.messages = []
        st.session_state.chat_session = agent.client.chats.create(
            model=agent.model_name,
            config=agent.config
        )
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

                    if part.function_call:
                        call = part.function_call
                        st.info(
                            f"🛠️ **Tool Called:** `{call.name}`\n\n"
                            f"**Input:** `{call.args}`"
                        )
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
                if st.button("Show in Conversation Window"):
                    st.session_state.messages.append(
                        {"role": "assistant", "content": f"**📄 Document: {selected_doc}**\n\n{doc_content}"})
                    st.rerun()
        else:
            st.info("No matching documents.")
    else:
        st.info("No documents found yet. Ask my_agent to create one!")


with st.sidebar:
    document_explorer()
    st.markdown("---")
    st.info("https://github.com/doosik71/my_agent/")
