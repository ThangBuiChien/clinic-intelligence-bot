from langchain_community.utilities import SQLDatabase
from typing import Dict, List
import sqlalchemy
import sqlparse
from sqlparse.sql import IdentifierList, Identifier
from sqlparse.tokens import Keyword, DML


# Define restricted tables and columns
RESTRICTED_TABLES = ["doctor", "department"]
RESTRICTED_COLUMNS = {
    "patient": ["password", "email", "id"],
    "appointment": ["id"]
}

class RestrictedSQLDatabase(SQLDatabase):
    def get_table_info(self) -> str:
        """Include all tables and columns, marking restricted ones."""
        inspector = sqlalchemy.inspect(self._engine)
        all_tables = inspector.get_table_names()
        
        schema_info = []
        for table in all_tables:
            columns = inspector.get_columns(table)
            column_definitions = []
            for column in columns:
                col_name = column["name"]
                # Mark restricted columns
                if col_name in RESTRICTED_COLUMNS.get(table, []):
                    col_name += " -- RESTRICTED COLUMN"
                column_definitions.append(col_name)
            table_def = f"CREATE TABLE {table} ({', '.join(column_definitions)})"
            # Mark restricted tables
            if table in RESTRICTED_TABLES:
                table_def += " -- RESTRICTED TABLE"
            schema_info.append(table_def)
        
        return "\n".join(schema_info)
    
    def is_query_valid(self, query: str) -> bool:
        """Check if the query tries to access restricted tables or columns."""
        # Parse the SQL query
        parsed = sqlparse.parse(query)
        for statement in parsed:
            # Only consider SELECT statements or other allowed statements
            if statement.get_type() not in ('SELECT'):
                return False
            # Extract table and column names
            identifiers = self._extract_identifiers(statement)
            # Check for restricted tables and columns
            for identifier in identifiers:
                name = identifier.get_real_name()
                # Check for restricted tables
                if name in RESTRICTED_TABLES:
                    return False
                # Check for restricted columns
                for table, columns in RESTRICTED_COLUMNS.items():
                    if name in columns:
                        return False
        return True
    
    def _extract_identifiers(self, token_list):
        """Recursively extract identifiers from parsed tokens."""
        identifiers = []
        for token in token_list.tokens:
            if isinstance(token, IdentifierList):
                for identifier in token.get_identifiers():
                    identifiers.append(identifier)
            elif isinstance(token, Identifier):
                identifiers.append(token)
            elif token.is_group:
                identifiers.extend(self._extract_identifiers(token))
        return identifiers

# db = SQLDatabase.from_uri("mysql+mysqlconnector://root:root@localhost:3306/clinic_management")
db = RestrictedSQLDatabase.from_uri("mysql+mysqlconnector://root:root@localhost:3306/clinic_management")

print(db.dialect)
print(db.get_usable_table_names())

# Print usable table names
print("Usable Tables:", db.get_usable_table_names())

# Print the schema information
print("Schema Information:")
print(db.get_table_info())

