from flask import Flask, render_template, request, session, jsonify
from pathlib import Path
from langchain.agents import create_sql_agent
from langchain.sql_database import SQLDatabase
from langchain.agents.agent_types import AgentType
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from sqlalchemy import create_engine
import sqlite3
from langchain_community.chat_models import ChatOllama
import logging
import re

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Replace with a secure key for production use
app.logger.setLevel(logging.INFO)

# configuration setup
DATABASE_NAME = "company.db"         # Name of the SQLite database file
DEFAULT_MODEL = "deepseek-r1"         # Default AI model name( you can use any model of your choice)
MAX_QUERY_LENGTH = 200                 # Maximum allowed characters in a user query
ALLOWED_CHARS = re.compile(r'^[\w\s,.?\-()@]+$')  # Regex to allow only specific safe characters

class DatabaseManager:
    """
    Manages the connection to the SQLite database.
    """
    @staticmethod
    def get_db():
        """
        Establishes a read-only connection to the SQLite database.

        Returns:
            SQLDatabase: An object wrapping the SQLAlchemy engine for the SQLite database.

        Raises:
            FileNotFoundError: If the database file is missing.
            Exception: For any other issues during connection setup.
        """
        try:
            db_path = Path(__file__).parent / DATABASE_NAME
            if not db_path.exists():
                raise FileNotFoundError(f"Database file {DATABASE_NAME} not found")
            
            # Use a custom creator function to open the database in read-only mode.
            creator = lambda: sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
            engine = create_engine("sqlite:///", creator=creator)
            return SQLDatabase(engine)
        except Exception as e:
            app.logger.error(f"Database connection failed: {str(e)}")
            raise

class AIManager:
    """
    Handles AI model initialization and SQL agent creation.
    """
    @staticmethod
    def create_agent(model_name):
        """
        Initializes the AI model and creates an SQL agent for processing queries.

        Args:
            model_name (str): The name of the AI model to be used.

        Returns:
            An agent instance capable of handling SQL queries.

        Raises:
            RuntimeError: If there is an issue initializing the AI model or the agent.
        """
        try:
            # Initialize the chat model with specified parameters.
            llm = ChatOllama(model=model_name, temperature=0)
            db = DatabaseManager.get_db()
            toolkit = SQLDatabaseToolkit(db=db, llm=llm)
            
            # Create the SQL agent using a zero-shot react description approach.
            return create_sql_agent(
                llm=llm,
                toolkit=toolkit,
                verbose=True,
                agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            )
        except Exception as e:
            app.logger.error(f"Agent creation failed: {str(e)}")
            raise RuntimeError("Failed to initialize AI model. Please check if the model is available.")

@app.before_request
def initialize_session():
    """
    Ensures that session variables 'messages' and 'model' are initialized before handling requests.
    """
    if 'messages' not in session:
        session['messages'] = []
    if 'model' not in session:
        session['model'] = DEFAULT_MODEL

def validate_query(query):
    """
    Validates the user query for basic constraints like length and allowed characters.

    Args:
        query (str): The query input provided by the user.

    Returns:
        str or None: An error message if the query is invalid, or None if the query passes validation.
    """
    if not query:
        return "Query cannot be empty"
    if len(query) > MAX_QUERY_LENGTH:
        return f"Query too long (max {MAX_QUERY_LENGTH} characters)"
    if not ALLOWED_CHARS.match(query):
        return "Invalid characters in query"
    return None

@app.route('/')
def index():
    """
    Renders the main page of the application with the current session messages and active model.

    Returns:
        The rendered HTML page.
    """
    return render_template('index.html', 
                           messages=session['messages'],
                           current_model=session['model'])

@app.route('/chat', methods=['POST'])
def handle_chat():
    """
    Processes chat messages from the user, sends the query to the AI agent,
    and returns the agent's response along with the updated chat history.

    Returns:
        JSON: A response object containing the agent's answer and the chat history.
    """
    try:
        data = request.get_json()
        user_query = data.get('query', '').strip()
        
        # Validate the user query input
        if validation_error := validate_query(user_query):
            return jsonify({"error": validation_error}), 400
        
        # Append the user's message to the session history
        session['messages'].append({'role': 'user', 'content': user_query})
        session.modified = True
        
        try:
            # Create the agent and process the query
            agent = AIManager.create_agent(session['model'])
            response = agent.run(user_query)
        except Exception as e:
            app.logger.error(f"Query processing error: {str(e)}")
            response = "I encountered an error processing your request. Please check your input and try again."
        
        # Post-process the response to remove markdown-like SQL formatting
        response = response.replace("```sql", "").replace("```", "").strip()
        if not response:
            response = "No results found for your query."
        elif "no results" in response.lower():
            response = "No matching records found. Please check your input parameters."
        
        # Append the agent's response to the session history
        session['messages'].append({'role': 'assistant', 'content': response})
        session.modified = True
        
        return jsonify({
            "response": response,
            "history": session['messages']
        })
        
    except Exception as e:
        app.logger.error(f"Chat error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred. Please try again later."}), 500

@app.route('/clear', methods=['POST'])
def clear_history():
    """
    Clears the chat history stored in the user's session.

    Returns:
        JSON: A response confirming that the history has been cleared.
    """
    session['messages'] = []
    session.modified = True
    return jsonify({"status": "success"})

if __name__ == '__main__':
    try:
        # Verify that the database connection can be established before running the app.
        DatabaseManager.get_db()
        app.run(port=int("5000"), debug=True)
    except Exception as e:
        print(f"Failed to start application: {str(e)}")
