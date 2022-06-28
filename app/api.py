import json
import os.path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from data_model.database import MongoDB
from data_model.graphs import monsters_by_type
from data_model.schema import MonsterModel
from machine_learning.model import Model

API = FastAPI(
    title="MonsterLib API",
    version="0.0.2",
    docs_url="/",
    description="<h2>Full Description</h2>",
)
API.mongo = MongoDB()
API.model = Model.open(os.path.join("machine_learning", "model.joblib"))
API.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
API.info = {
    "Platform": "FastAPI",
    "Title": API.title,
    "Version": API.version,
    "Docs URL": API.docs_url,
}


@API.get("/info")
async def info():
    """ Returns json: API, Model & Database Info """
    return {
        "Web API": API.info,
        "ML Model": API.model.info,
        "Database": API.mongo.info,
    }


@API.get("/database/findall")
async def find_all_monsters():
    """ Returns all Monsters from the Collection as an Array of JSON Objects """
    return tuple(API.mongo.find_all())


@API.post("/database/insert")
async def insert_monster(monster: MonsterModel):
    """ Inserts one Custom Monster into the Collection

    Monster Schema:
    <pre><code>{
        "name": String,
        "type": String,
        "level": Integer(range[1, 20]),
        "rarity": String,
        "damage": String,
        "health": Float,
        "energy": Float,
        "sanity": Float,
        "time_stamp": String(format[YYYY-MM-DD H:M:S])
    }</pre></code>"""
    API.mongo.insert(vars(monster))
    return await info()


@API.post("/database/seed")
async def seed(amount: int):
    API.mongo.seed_db(amount)
    return {"result": "success"}


@API.get("/database/chart/count/type")
async def chart_count_type():
    return json.loads(monsters_by_type(API.mongo.connect()).to_json())


@API.delete("/database/delete")
async def delete():
    API.mongo.delete({})
    return {"result": "success"}
