import os
from random import randint
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from llm.rag.search import get_index
from llm.rag.rag import RAGClient
from pages.db import DB_CONFIG
import logging
load_dotenv()
import psycopg2
from psycopg2.extras import RealDictCursor
from db import DB_CONFIG    

OPENAI_MODELS = {
    "gpt-5.6-sol": "GPT-5.6 Sol",
    "gpt-5.6-terra": "GPT-5.6 Terra",
    "gpt-5.6-luna": "GPT-5.6 Luna",
}


def deleteConversation(conversation_id, user_id):
    delete_query = "DELETE FROM chat_history WHERE conversation_id = %s AND user_id = %s"
    try:
        with psycopg2.connect(**DB_CONFIG) as connection:
            with connection.cursor() as cursor:
                cursor.execute(delete_query, (conversation_id, user_id))
            connection.commit()
        logging.info(f"Deleted conversation {conversation_id}")
        return True
    except Exception as e:
        logging.error(f"Error deleting conversation: {e}")
        return False


@st.dialog("Delete Conversation")
def show_delete_confirmation(conversation_id, user_id):
    st.write(f"Are you sure you want to delete **{conversation_id}**?")
    st.write("This action cannot be undone.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Delete", key="confirm_delete"):
            deleteConversation(conversation_id, user_id)
            st.rerun()
    with col2:
        if st.button("Cancel", key="cancel_delete"):
            st.rerun()


def insertIntoChatHistory(conversation_id, user_id, role, message):
    insert_query = """
        INSERT INTO chat_history (conversation_id, user_id, role, message)
        VALUES (%s, %s, %s, %s)
    """
    try:
        with psycopg2.connect(**DB_CONFIG) as connection:
            with connection.cursor() as cursor:
                cursor.execute(insert_query, (conversation_id, user_id, role, message))
            connection.commit()
        logging.info(f"Inserted message into chat_history for conversation_id: {conversation_id}, user_id: {user_id}")
    except Exception as e:
        logging.error(f"Error inserting into chat_history: {e}")


#functions later refactor
def fetchChatHistoryForConversation(conversation_id, user_id):
    fetch_query = """
        SELECT role, message FROM chat_history
        WHERE conversation_id = %s AND user_id = %s
        ORDER BY timestamp ASC
    """
    try:
        with psycopg2.connect(**DB_CONFIG) as connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(fetch_query, (conversation_id, user_id))
                messages = cursor.fetchall()
        logging.info(f"Loaded {len(messages)} messages for conversation {conversation_id}")
        return [{"role": msg["role"], "content": msg["message"]} for msg in messages]
    except Exception as e:
        logging.error(f"Error fetching chat history: {e}")
        return []


def fetchConversationsWithUsernameFromConversationHistory():
    user_id = st.session_state.get("user_id")
    logging.info(f"Fetching conversations for user_id: {user_id}")
    if not user_id:
        logging.warning("No user_id in session state")
        return []
    fetch_query = """
        SELECT DISTINCT conversation_id, MIN(timestamp) as created_at
        FROM chat_history
        WHERE user_id = %s
        GROUP BY conversation_id
        ORDER BY created_at DESC
    """
    try:
        with psycopg2.connect(**DB_CONFIG) as connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(fetch_query, (user_id,))
                conversations = cursor.fetchall()
        logging.info(f"Found {len(conversations)} conversations")
        return conversations if conversations else []
    except Exception as e:
        logging.error(f"Error fetching conversations: {e}")
        return []

def createAConversationID():
    date_str = datetime.now().strftime("%Y%m%d")  # 20260830
    random_suffix = str(randint(1000, 9999))
    return f"conv_{date_str}_{random_suffix}"




# initialization of vars/objects
index = get_index()  # Load data.json and build the index
client = RAGClient(index=index, llm_client=OpenAI(), model="gpt-5.6-luna")
st.session_state.setdefault("chat_history", [])
st.session_state.setdefault("current_conversation_id", None)
previous_conversations = False


user_id = st.session_state.get("user_id")
conversation_id = st.session_state.get("current_conversation_id")


with st.sidebar:
    st.subheader("Model")
    st.selectbox(
        "Model",
        options=list(OPENAI_MODELS.keys()),
        format_func=lambda model_id: OPENAI_MODELS[model_id],
        key="selected_model",
        label_visibility="collapsed",
    )

with st.sidebar:
    st.subheader("Previous Conversations")
    previous_conversations = fetchConversationsWithUsernameFromConversationHistory()
    for conv in previous_conversations:
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button(f"{conv['conversation_id']}", key=conv['conversation_id']):
                st.session_state.current_conversation_id = conv['conversation_id']
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"delete_{conv['conversation_id']}"):
                show_delete_confirmation(conv['conversation_id'], user_id)

    if st.button("➕ New Conversation"):
        st.session_state.current_conversation_id = None
        st.session_state.chat_history = []
        st.rerun()

# so here we appear the conversation history, and if the user clicks on one of them, we load the chat history for that conversation.
if previous_conversations and conversation_id:
    
    st.title("Warehouse AI Demo")
    st.session_state.chat_history = fetchChatHistoryForConversation(conversation_id, user_id)


    for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
    
    if prompt := st.chat_input("Ask a question"):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        insertIntoChatHistory(conversation_id, user_id, "user", prompt)  # Insert user message into chat_history table
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = client.rag(prompt, history=st.session_state.chat_history[:-1], conversation_id=conversation_id)  # Pass history MINUS the current turn
            st.write(answer)
        insertIntoChatHistory(conversation_id, user_id, "assistant", answer)
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.write("history ->>>", st.session_state.chat_history)
else:

    
    st.title("Warehouse AI Demo")
    st.write("Welcome to the Warehouse AI Demo! You are logged in.")
    st.write("You can now access the Warehouse AI features of the application.")
    st.session_state.chat_history = []

    # here is a new chat from the user
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if prompt := st.chat_input("Ask a question"):
        if not st.session_state.current_conversation_id:
            st.session_state.current_conversation_id = createAConversationID()
            logging.info(f"New conversation started with ID: {st.session_state.current_conversation_id}")
        conversation_id = st.session_state.current_conversation_id
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        insertIntoChatHistory(conversation_id, user_id, "user", prompt)  # Insert user message into chat_history table
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = client.rag(prompt, history=st.session_state.chat_history[:-1], conversation_id=conversation_id)  # Pass history MINUS the current turn
            st.write(answer)
        insertIntoChatHistory(conversation_id, user_id, "assistant", answer)
        st.session_state.chat_history.append({"role": "assistant", "content": answer})

