from fastapi import FastAPI, Request
from lib.predictions import Predictions
from lib.config import Config
from lib.auth import Authenticate
from lib.nodes import  Cluster

import datetime

config = Config()
app = FastAPI()
auth = Authenticate()

cluster = Cluster(config.nodes)

@app.post("/predict")
async def predict(
    request: Request, 
):
    data = await request.json()
    image = data["image"]
    token = Authenticate.extract_token(request)
    Authenticate.verify_existing_token(token)
    Authenticate.verify_image_scope(Authenticate.extract_token(request), image)
    new_prediction = Predictions(
        user= config.get_user_by_token(token),
        image=image, 
        started= datetime.datetime.now(),
    )
    cluster.run_prediction(new_prediction)
    return new_prediction




