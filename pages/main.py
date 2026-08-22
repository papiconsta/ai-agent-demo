import streamlit as st

st.set_page_config(page_title="AI Agents", page_icon="🤖", layout="centered")


def get_agent_response(user_message: str) -> str:
    """Placeholder for the agent's reply. Wire up the real agent/LLM call here."""
    return "This is a placeholder response. Connect an agent to reply for real."


if "agent_messages" not in st.session_state:
    st.session_state.agent_messages = []

with st.sidebar:

    st.divider()
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.agent_messages = []
        st.rerun()

st.title("🤖 AI Agents")
st.caption("Chatting with: **General Assistant**")

for message in st.session_state.agent_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Type your message...")

if user_input:
    st.session_state.agent_messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    reply = get_agent_response(user_input)
    st.session_state.agent_messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)
