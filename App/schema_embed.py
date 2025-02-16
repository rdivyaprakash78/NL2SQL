from langchain_community.utilities import SQLDatabase
from sqlalchemy import create_engine, inspect
import pandas as pd
from get_embed import generate_embeddings
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance

username = "divyaprakash"
password = "new_password"
host = "localhost"
db_name = "northwind"

engine = create_engine(f'postgresql://{username}:{password}@{host}:5432/{db_name}')
db = SQLDatabase(engine)
inspector = inspect(engine)

client = QdrantClient(
    url="https://a2a0ba0a-cc68-4eee-8624-be47a1c61f6c.europe-west3-0.gcp.cloud.qdrant.io:6333",
    api_key= "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwiZXhwIjoxNzQ3NDc0OTcyfQ.rJzs3sTQZtN-MoOiPnwzh00uos3QqNnNK6rvWqNLp6k" # Required for authentication
)

if __name__ == "__main__":

    table_names = inspector.get_table_names()

    table_schemas = {}
    table_constraints = {}

    for table_name in table_names:
        columns = inspector.get_columns(table_name)
        primary_keys = inspector.get_pk_constraint(table_name)['constrained_columns']
        foreign_keys = inspector.get_foreign_keys(table_name)
        unique_constraints = inspector.get_unique_constraints(table_name)
        table_constraints[table_name] = {
            'primary_keys': primary_keys,
            'foreign_keys': foreign_keys,
            'unique_constraints': unique_constraints
        }
        schema = []
        for column in columns:
            schema.append(f"{column['name']} ({column['type']})")
        table_schemas[table_name] = schema

    table_details = []

    for table, content in table_schemas.items():
        table_detail = f"""Table name: {table}\nTable schema: {content}"""
        table_details.append(table_detail)

    for index, (table, content) in enumerate(table_constraints.items()):
        table_details[index] += f"""\nTable constraints: {content}"""
        first_3_rows = db.run(f"SELECT * FROM {table_names[index]} LIMIT 3;")
        table_details[index] += f"""\nSample rows from the table:\n{first_3_rows}"""

    tables_dict = {
        "name" : table_names,
        "table_details" : table_details
    }

    tables_df = pd.DataFrame(tables_dict)

    points = []
    for _, row in tables_df.iterrows():
        table_name = row['name']
        schema_details = row['table_details']

        schema_embedding = generate_embeddings(schema_details)

        metadata = {"table_name": table_name}

        point = {
            "id": _,  # Unique ID for each point
            "vector": schema_embedding,  # Convert embedding to list
            "payload": {
                "table_name": row['name'],
                "schema" : row["table_details"]
            }
        }
            
        points.append(point)
        print(f"Stored table: {table_name}")

    client.recreate_collection(
        collection_name="table_schemas",
        vectors_config=VectorParams(size=768, distance=Distance.COSINE)  # Size based on 'all-MiniLM-L6-v2'
    )

    client.upsert(collection_name="table_schemas",points=points)
    








