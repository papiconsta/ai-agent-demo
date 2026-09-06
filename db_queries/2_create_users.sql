CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    surname VARCHAR(50),
    email VARCHAR(100) UNIQUE,
    age INT
);