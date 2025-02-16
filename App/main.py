from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from llm_helper import generate_bot_response

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

class InputData(BaseModel):
    text: str

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse('home.html', {'request': request})

@app.post("/chat")
async def receive_data(input_data: InputData):
    try :
        sql_query, bot_response, few_shots = generate_bot_response(input_data.text)
        print("\nfew_shots : ", few_shots)
        print("\nsql_query : ", sql_query)
        print("\nbot_response : ", bot_response)
        
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    response_data = {
        "message": bot_response,
        "sql_query": sql_query,
        "few_shots": few_shots
        }
    return response_data