CREATE TABLE IF NOT EXISTS chat_history (
    id SERIAL PRIMARY KEY,
    conversation_id VARCHAR(50) NOT NULL,
    user_id INT REFERENCES users(id),
    role VARCHAR(20) NOT NULL,  -- 'user' or 'assistant'
    message TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
