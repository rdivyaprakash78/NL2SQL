from pydantic import BaseModel, Field

class SQLQuery(BaseModel):
    query: str = Field(description="The SQL query to execute.")

class NLResponse(BaseModel):
    response: str = Field(description="Final natural language response for the user question.")
