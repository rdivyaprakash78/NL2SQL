from langchain_core.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
from get_embed import generate_embeddings
from schema_embed import client
from response_models import SQLQuery, NLResponse
from prompts import prompts
from schema_embed import db

load_dotenv()

key = os.getenv("GROQ_API_KEY")
#llm = ChatGroq(model="llama3-70b-8192",temperature=0, api_key = key)
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash",temperature=0)
query_embedding = []

def retrieve_schema(user_query):
    global query_embedding
    threshold = 0.6
    query_embedding = generate_embeddings(user_query)
    search_results = client.search(
        collection_name="table_schemas",
        query_vector=query_embedding,
        limit=3,  
        score_threshold=threshold
    )

    schema_string = ""
    for result in search_results:
        schema_string += result.payload["schema"]

    return schema_string

def retrieve_fewshots():
    global query_embedding
    threshold = 0.7
    search_results = client.search(
        collection_name="few_shots",
        query_vector=query_embedding,
        limit=2,  
        score_threshold=threshold
    )

    few_shot_string = ""
    for result in search_results:
        few_shot_string += result.payload["few_shot"]

    return few_shot_string

def helper(agent, response_model, input_values):
    system_message = prompts[agent]["system"]
    human_message = prompts[agent]["human"]

    prompt_tuple = [
            ("system", system_message),
            ("human", human_message)
        ]
    
    prompt = ChatPromptTemplate.from_messages(prompt_tuple)
    parser = PydanticOutputParser(pydantic_object=response_model)
    format_instructions =  parser.get_format_instructions()
    input_values["format_instructions"] = str(format_instructions)

    chain = prompt | llm
    response = chain.invoke(input_values)
    result = parser.parse(response.content)

    return result

def generate_bot_response(user_query):
    schema = retrieve_schema(user_query)
    few_shots = retrieve_fewshots()
    input_values_dict = {
        "schema": schema,
        "user_question":user_query,
        "few_shots": few_shots
    }

    sql_query = helper(agent="query generater", response_model = SQLQuery, input_values = input_values_dict)
    sql_query = sql_query.query
    query_result = db.run(sql_query)

    input_values_dict = {
        "user_question" : user_query,
        "generated_query": query_result,
        "result" : query_result
    }

    nl_response = helper(agent="final response generater", response_model=NLResponse, input_values = input_values_dict)
    nl_response = nl_response.response

    return sql_query, nl_response, few_shots

