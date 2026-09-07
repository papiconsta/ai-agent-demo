import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor

from pages.db import DB_CONFIG

st.title("Monitor")


def fetch_user_conversation_ids(user_id):
    query = """
        SELECT DISTINCT conversation_id, MIN(timestamp) as created_at
        FROM chat_history
        WHERE user_id = %s
        GROUP BY conversation_id
        ORDER BY created_at DESC
    """
    try:
        with psycopg2.connect(**DB_CONFIG) as connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, (user_id,))
                return cursor.fetchall()
    except Exception as e:
        st.error(f"Error fetching conversations: {e}")
        return []


def fetch_llm_call_records(conversation_id):
    query = """
        SELECT model, prompt, instructions, answer,
               prompt_tokens, completion_tokens, total_tokens,
               response_time, cost, timestamp_created
        FROM llm_call_records
        WHERE conversation_id = %s
        ORDER BY timestamp_created ASC
    """
    try:
        with psycopg2.connect(**DB_CONFIG) as connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, (conversation_id,))
                return cursor.fetchall()
    except Exception as e:
        st.error(f"Error fetching LLM call records: {e}")
        return []


user_id = st.session_state.get("user_id")

if not user_id:
    st.write("Please log in to view statistics.")
else:
    conversations = fetch_user_conversation_ids(user_id)

    if not conversations:
        st.write("No conversations found yet.")
    else:
        conversation_id = st.selectbox(
            "Conversation",
            options=[c["conversation_id"] for c in conversations],
        )

        records = fetch_llm_call_records(conversation_id)

        if not records:
            st.write("No LLM call records found for this conversation.")
        else:
            total_calls = len(records)
            total_tokens = sum(r["total_tokens"] or 0 for r in records)
            total_cost = sum(r["cost"] or 0 for r in records)
            avg_response_time = sum(r["response_time"] or 0 for r in records) / total_calls

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("LLM calls", total_calls)
            col2.metric("Total tokens", total_tokens)
            col3.metric("Total cost", f"${total_cost:.4f}")
            col4.metric("Avg response time", f"{avg_response_time:.2f}s")

            st.subheader("All calls")
            table_rows = [
                {
                    "model": r["model"],
                    "prompt_tokens": r["prompt_tokens"],
                    "completion_tokens": r["completion_tokens"],
                    "total_tokens": r["total_tokens"],
                    "response_time": r["response_time"],
                    "cost": r["cost"],
                    "timestamp": r["timestamp_created"],
                }
                for r in records
            ]
            st.dataframe(table_rows, use_container_width=True)

            st.subheader("Call details")
            for i, record in enumerate(records, start=1):
                with st.expander(f"Call {i} · {record['model']} · {record['timestamp_created']}"):
                    col1, col2, col3, col4, col5 = st.columns(5)
                    col1.metric("Prompt tokens", record["prompt_tokens"])
                    col2.metric("Completion tokens", record["completion_tokens"])
                    col3.metric("Total tokens", record["total_tokens"])
                    col4.metric("Cost", f"${(record['cost'] or 0):.4f}")
                    col5.metric("Response time", f"{(record['response_time'] or 0):.2f}s")

                    st.markdown("**Instructions**")
                    st.write(record["instructions"])

                    st.markdown("**Prompt**")
                    st.write(record["prompt"])

                    st.markdown("**Answer**")
                    st.write(record["answer"])
