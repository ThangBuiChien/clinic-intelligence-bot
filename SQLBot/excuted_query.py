from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool

from app_state import State
from connect_db import db

def execute_query(state: State):
    """Execute SQL query after validation."""
    query = state["query"]
    # Validate the query
    if not db.is_query_valid(query):
        return {"result": "I'm sorry, but I cannot provide information regarding that request."}
    # Execute the query if valid
    execute_query_tool = QuerySQLDataBaseTool(db=db)
    return {"result": execute_query_tool.invoke(state["query"])}