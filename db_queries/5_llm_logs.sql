CREATE TABLE IF NOT EXISTS llm_call_records (
    id SERIAL PRIMARY KEY,
    conversation_id VARCHAR(50) NOT NULL,
    model VARCHAR(255),
    prompt TEXT,
    instructions TEXT,
    answer TEXT,
    prompt_tokens INT,
    completion_tokens INT,
    total_tokens INT,
    response_time FLOAT,
    cost FLOAT,
    timestamp_created TIMESTAMP,
    timestamp_inserted_to_db TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
