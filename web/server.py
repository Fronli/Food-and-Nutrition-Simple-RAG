from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from vrag import main_invoke

app = FastAPI()

# @app.get("/")
# def gree():
#     return "Welcome to server"

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# optional: hidupkan auto_reload saat develop
templates.env.auto_reload = True
templates.env.cache = {}

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # selalu sertakan 'request' pada context Jinja2Templates
    return templates.TemplateResponse("home.html", {"request": request, "title": "RAG Chat"})


@app.post("/api/ask")
async def ask(request: Request):
    data = await request.json()          # ambil JSON body
    question = data.get("question")      # ambil field 'question'
    print("Pertanyaan diterima:", question)
    answer = main_invoke(question)
    print(answer)
    return {"answer": answer}