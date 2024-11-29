from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool

from app_state import State
from connect_db import db

def execute_query(state: State):
    """Execute SQL query."""
    execute_query_tool = QuerySQLDataBaseTool(db=db)
    return {"result": execute_query_tool.invoke(state["query"])}