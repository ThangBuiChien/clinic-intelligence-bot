from langchain import hub
from connect_db import RESTRICTED_TABLES, RESTRICTED_COLUMNS


query_prompt_template = hub.pull("langchain-ai/sql-query-system-prompt")

# Add information about restricted tables and columns
# RESTRICTED_INFO = (
#     "\n\nImportant:\n"
#     "The following tables and columns are **restricted** and should **not** be accessed in any queries.\n\n"
#     f"Restricted Tables: {', '.join(RESTRICTED_TABLES)}\n"
#     "Restricted Columns:\n" +
#     "\n".join([f"- {table}: {', '.join(columns)}" for table, columns in RESTRICTED_COLUMNS.items()])
#     + "\n\n"
# )

# query_prompt_template.messages[0] += RESTRICTED_INFO


assert len(query_prompt_template.messages) == 1
query_prompt_template.messages[0].pretty_print()