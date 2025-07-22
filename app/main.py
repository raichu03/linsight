from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

from routes import conversation

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(conversation.router)

templates = Jinja2Templates(directory='templates')

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    context = {'request': request}
    return templates.TemplateResponse(
        name="index.html",
        context=context
    )
    
if __name__=="__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000)