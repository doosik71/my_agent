from src.agent_core import MyAgent
from src.tools.tool_definitions import doc_manager
import streamlit as st  # pyright: ignore[reportMissingImports]
import os


st.set_page_config(
    page_title="My Agent",
    layout="wide",
    page_icon=os.path.join(os.path.dirname(__file__), "assets", "favicon.ico")
)

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


# Use a container to hold messages
msg_container = st.container()

with msg_container:
    # Display chat messages from history
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
            user_prompt_for_agent = f"Please output the content of the file at '{selected_doc}'."
            _ = agent.send_message(
                user_prompt_for_agent, st.session_state.chat_session)

# User input (this will naturally sit below the container if it doesn't float)
if prompt := st.chat_input("Ask my_agent a question or give a command..."):
    if prompt.strip() == "/clear":
        st.session_state.messages = []
        st.session_state.chat_session = agent.create_session()
        st.rerun()

    st.session_state.messages.append({"role": "user", "content": prompt})

    with msg_container:
        with st.chat_message("user"):
            st.markdown(prompt)

    with st.spinner("my_agent is thinking..."):
        # agent_core의 send_message 호출
        response_obj = agent.send_message(
            prompt, st.session_state.chat_session)

        full_response_content = ""

        with msg_container:
            with st.chat_message("assistant"):
                if hasattr(response_obj, 'candidates') and response_obj.candidates:
                    for part in response_obj.candidates[0].content.parts:
                        if part.text:
                            st.markdown(part.text)
                            full_response_content += part.text
                else:
                    st.error(getattr(response_obj, 'text',
                                     "Unknown Error Occurred"))
                    full_response_content = getattr(
                        response_obj, 'text', "")

    st.session_state.messages.append(
        {"role": "assistant", "content": full_response_content})


st.sidebar.title("🤖 My Agent")


@st.fragment
def document_explorer():
    st.subheader("Existing Documents")

    docs_raw = doc_manager.list_docs()
    # 빈 줄 제외, 리스트 변환 및 정렬하여 순서 보장
    documents_list = sorted([d.strip()
                             for d in docs_raw.split('\n') if d.strip()]) if docs_raw else []

    if documents_list and documents_list[0] != "No documents found.":
        # Extract unique folders and sort them
        folder_set = set()
        for d in documents_list:
            folder = os.path.dirname(d)
            folder_set.add(folder if folder else ".")

        folders = ["All"] + sorted(list(folder_set))

        # 1. 전용 세션 상태 변수 초기화 및 값 유지
        if "last_folder" not in st.session_state:
            st.session_state.last_folder = "All"

        try:
            folder_index = folders.index(st.session_state.last_folder)
        except ValueError:
            folder_index = 0

        def on_folder_change():
            st.session_state.last_folder = st.session_state.folder_selectbox

        selected_folder = st.selectbox(
            "Select Folder",
            folders,
            index=folder_index,
            key="folder_selectbox",
            on_change=on_folder_change,
            label_visibility="collapsed"
        )

        filter_query = st.text_input(
            "Filter documents",
            placeholder="Search (Press Enter to apply)",
            label_visibility="collapsed",
            key="doc_filter_input"
        ).lower()

        # Filter by folder
        if selected_folder != "All":
            filtered_docs = [
                d for d in documents_list if (os.path.dirname(d) or ".") == selected_folder]
        else:
            filtered_docs = documents_list

        # 필터링 적용 (Search query)
        if filter_query:
            filtered_docs = [
                doc for doc in filtered_docs if filter_query in doc.lower()]

        if filtered_docs:
            # 2. 문서 선택 상태 유지
            if "last_doc" not in st.session_state:
                st.session_state.last_doc = filtered_docs[0]

            try:
                doc_index = filtered_docs.index(st.session_state.last_doc)
            except ValueError:
                doc_index = 0

            def on_doc_change():
                st.session_state.last_doc = st.session_state.doc_selectbox

            selected_doc = st.selectbox(
                "Select a document to view:",
                filtered_docs,
                index=doc_index,
                key="doc_selectbox",
                on_change=on_doc_change
            )

            if selected_doc:
                doc_content = doc_manager.read_doc(selected_doc)
                st.text_area(f"Content of {selected_doc}",
                             doc_content, height=600)

                # Use columns for two buttons side-by-side
                col1, col2 = st.columns(2)

                with col1:
                    if st.button("Print Document 🖨️", key="print_doc_btn", use_container_width=True):
                        agent_response_for_document = f"The content of the file `{selected_doc}` is as follows:\n\n{doc_content}"
                        st.session_state.messages.append(
                            {"role": "assistant", "content": agent_response_for_document})
                        st.rerun()

                with col2:
                    if st.button("Add to Conversation 💬", key="add_doc_btn", use_container_width=True):
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
