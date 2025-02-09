# Flask SQL Chatbot with DeepSeek R1

## Overview
This project is a Flask-based web application that provides a conversational SQL chatbot. It leverages a locally downloaded DeepSeek R1 model from Ollama to interpret natural language queries and translate them into SQL commands against an SQLite database (`company.db`).

## How It Works
1. **AI Model**: Utilizes the locally downloaded DeepSeek R1 model via the ChatOllama interface for natural language understanding and response generation.
2. **Database Management**: Establishes a read-only connection to an SQLite database (`company.db`).
3. **SQL Agent**: Uses LangChain's SQL agent to process queries, converting natural language into SQL and retrieving results.
4. **Flask Framework**: Manages the user interface and backend logic, including chat sessions, query validation, and error handling.
5. **Validation**: Ensures that user queries meet defined constraints (length and allowed characters) before processing.

## Features
- **Conversational Querying**: Engage with a chatbot that can fetch database records using natural language.
- **Session Management**: Maintains chat history for each user session.
- **Input Validation**: Checks for safe characters and enforces a maximum query length.
- **Error Handling**: Gracefully manages database connection issues and invalid queries.
- **Customizable Models**: Easily switch to a different AI model by modifying the configuration.

## Prerequisites
- Python 3.8 or above.
- An SQLite database file named `company.db` in the project directory.
- The DeepSeek R1 model downloaded locally using Ollama.
- Docker (for deployement).

## Installation and Usage

### Step 1: Clone the Repository
```bash
git clone https://github.com/vn33/Flask-SQL-Chatbot-with-DeepSeek-R1.git
```
