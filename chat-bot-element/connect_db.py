from langchain_community.utilities import SQLDatabase
from typing import Dict, List
import sqlalchemy


# Define restricted tables and columns
RESTRICTED_TABLES = ["doctor", "department"]
RESTRICTED_COLUMNS = {
    "patient": ["password", "email", "id"],
    "appointment": ["id"]
}

class RestrictedSQLDatabase(SQLDatabase):
    def get_table_info(self) -> str:
        """Override to filter out restricted tables and columns"""
        # Get all tables
        inspector = sqlalchemy.inspect(self._engine)
        all_tables = inspector.get_table_names()
        
        # Build filtered schema info
        filtered_schema = []
        for table in all_tables:
            # Skip restricted tables
            if table in RESTRICTED_TABLES:
                continue
                
            columns = inspector.get_columns(table)
            # Filter out restricted columns
            filtered_columns = []
            for column in columns:
                if column["name"] not in RESTRICTED_COLUMNS.get(table, []):
                    filtered_columns.append(column["name"])
                    
            if filtered_columns:
                filtered_schema.append(
                    f"CREATE TABLE {table} ({', '.join(filtered_columns)})"
                )
                
        return "\n".join(filtered_schema)

# db = SQLDatabase.from_uri("mysql+mysqlconnector://root:root@localhost:3306/clinic_management")
db = RestrictedSQLDatabase.from_uri("mysql+mysqlconnector://root:root@localhost:3306/clinic_management")

print(db.dialect)
print(db.get_usable_table_names())

