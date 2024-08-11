from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool

from lib.predictions import Predictions
from lib.config import Config
from lib.auth import Authenticate
from lib.cluster import  Cluster
import json
import datetime
import os


config = Config()
cors_origins = os.getenv("API_CORS_ORIGIN").split(",")

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define our static folder, where will be our svelte build later
app.mount("/dashboard", StaticFiles(directory="public"), name="dashboard")
app.mount("/_app", StaticFiles(directory="public/_app"), name="_app")

auth = Authenticate()

cluster = Cluster(config.nodes, config.co2["port"],config.co2["carbon_intensity"])

@app.post("/predict")
async def predict(
    request: Request, 
):
    data = await request.json()
    image = data["image"]
    input_data = data["input"]

    token = Authenticate.extract_token(request)
    Authenticate.verify_existing_token(token)
    Authenticate.verify_image_scope(token, image)

    new_prediction = Predictions(
        user= config.get_user_by_token(token),
        image=image, 
        input= input_data,
        started= datetime.datetime.now(),
    )
    new_prediction.create()
    return await run_in_threadpool(cluster.queue_prediction, new_prediction)

@app.post("/image/openapi")
async def get_image_openapi(
    request: Request, 
):
    data = await request.json()
    image = data["image"]
    token = Authenticate.extract_token(request)
    Authenticate.verify_existing_token(token)
    Authenticate.verify_image_scope(token, image)

    return await run_in_threadpool(cluster.queue_openai_spec, image)


@app.get("/status")
async def status(
    request: Request,
):
    token = Authenticate.extract_token(request)
    Authenticate.verify_existing_token(token)

    return {"status": cluster.global_status()}


@app.get("/predictions/",include_in_schema=False)
async def list_predictions(
    request: Request,
):
    token = Authenticate.extract_token(request)
    Authenticate.verify_existing_token(token)
    Authenticate.verify_token_admin(token)
    predictions = Predictions.get_all()
    return(predictions)

@app.get("/tokens")
async def list_tokens(
    request: Request,
):
    token = Authenticate.extract_token(request)
    Authenticate.verify_existing_token(token)
    Authenticate.verify_token_admin(token)
    return Authenticate.get_all_tokens()

@app.get("/users")
async def list_users(
    request: Request,
):
    token = Authenticate.extract_token(request)
    Authenticate.verify_existing_token(token)
    Authenticate.verify_token_admin(token)
    return Authenticate.get_all_users()


@app.post("/user/")
async def return_user(
    request: Request,
):
    token = Authenticate.extract_token(request)
    Authenticate.verify_existing_token(token)
    return Authenticate.get_user(token)


@app.post("/user/predictions")
async def list_users(
    request: Request,
):
    data = await request.json()
    user = data["user"]
    token = Authenticate.extract_token(request)
    Authenticate.verify_existing_token(token)
    Authenticate.verify_token_user(token,user)
    data = await request.json()
    user = data["user"]
    return Predictions.filter_by_user(user)

@app.get("/nodes")
async def list_nodes(
    request: Request,
):
    token = Authenticate.extract_token(request)
    Authenticate.verify_existing_token(token)
    Authenticate.verify_token_admin(token)
    nodes = []
    for node in cluster.nodes:
        nodes.append({'name': node.name, 'host': node.host, 'weight': node.weight, 'state': node.state })
    return nodes

# Frontend routes for Svelte app
@app.get("/dashboard", response_class=FileResponse)
async def main():
    return "public/index.html"

@app.get("/dashboard/_app/{path}", response_class=FileResponse)
async def main(path):
    return "public/_app/" + path
