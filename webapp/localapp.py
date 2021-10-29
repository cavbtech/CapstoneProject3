from datetime import datetime

import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

from predictor import loadmodel, loadVectorCatogory, predict

app = FastAPI( title="Application to categorize NEWS text",docs_url="/")


def boot_strap():
    global clf2
    global data
    clf2 = loadmodel('../datavol/trained/active')
    data = loadVectorCatogory('../datavol/trained/active')


app.add_event_handler("startup", boot_strap)

@app.get("/ping")
def ping():
    return {"ping": "pong"}



class QueryIn(BaseModel):
    search_text :str

class QueryOut(BaseModel):
    category: str
    timestamp_str:str

@app.post("/predict_news_category", response_model=QueryOut, status_code=200)
async def predict_news_category(query_data: QueryIn):
    print(f"query_data={query_data}")
    result = predict(clf2, data,[query_data.search_text])
    ct = datetime.now()
    ctStr = ct.strftime("%m/%d/%Y, %H:%M:%S")
    output = {'category': result, 'timestamp_str': ctStr}

    print(f"output={output}")
    return output

@app.get("/landing",response_class=FileResponse)
async def landing():
    return FileResponse("static/news_categorization_app.html")

if __name__ == "__main__":
    uvicorn.run("main:app", host='127.0.0.1', port=8088, reload=True)