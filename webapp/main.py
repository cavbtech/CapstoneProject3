## The webapp application is deployed as microservice
## This server every day at 2:00 A.M takes new model created by model docker
## As of not is it not a production ready code i.,e there are chances that at times the service may be down
## Mostly around 2:00 A.M in the morning this service may be down.  There are ways to handle this but noew
## it hasnt been handled
from datetime import datetime
from time import sleep

import schedule
import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

from predictor import loadmodel, loadVectorCatogory, predict

app = FastAPI( title="Application to categorize NEWS text",docs_url="/")


def boot_strap():
    global clf2
    global data
    count = 0
    exitWhile=False
    while count<10 and exitWhile==False:
        print(f"count={count} and exitWhile={exitWhile}")
        count = count + 1
        try:
            clf2 = loadmodel('datavol/trained/active')
            data = loadVectorCatogory('datavol/trained/active')
            exitWhile = True
        except:
            ## wait for 2 mins
            sleep(2*60)
        if count == 9 :
            exitWhile=True
            print(f" Pickle files datavol/trained/active/model2  or datavol/trained/active/vectorCategory.pkl are not "
                  f" available. Please check the same ")
            break

app.add_event_handler("startup", boot_strap)

## schedule every day at 2:00 AM use the new model
schedule.every().day.at("02:00").do(boot_strap)

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
    uvicorn.run("main:app", host='0.0.0.0', port=11030, reload=True)
