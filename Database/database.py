import pymongo
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(default_response_class=JSONResponse)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
)

mongoclient = pymongo.MongoClient(
    "mongodb+srv://nnothig:12345@data.mfmvqb8.mongodb.net/?retryWrites=true&w=majority&appName=Data"
)
db = mongoclient["Baza_artikala"]
Artikli = db["Artikli"]

@app.get("/")
async def message():
    return {"data": "Baza je spojena"}

@app.get("/get_data")
async def get_data():
    data = list(Artikli.find({}, {"_id": 0}))
    return {"data": data}

@app.delete("/clear_data")
async def clear_data():
    result = Artikli.delete_many({})
    return {"message": f"Deleted {result.deleted_count} items."}
