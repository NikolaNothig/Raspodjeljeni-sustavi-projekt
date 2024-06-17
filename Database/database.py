import pymongo
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(default_response_class=JSONResponse)

mongoclient = pymongo.MongoClient(
    "mongodb+srv://nnothig:l6z1Ayak7Tp1dYsA@data.mfmvqb8.mongodb.net/"
)
db = mongoclient["Baza_artikala"]  
Artikli = db["Artikli"]  

@app.get("/")
async def message():
    return {"data": "Baza je spojena"}

# uvicorn database:app --reload --port 8004
