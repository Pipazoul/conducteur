from fastapi import FastAPI, Request
from lib.predictions import Predictions
from lib.config import Config
from lib.auth import Authenticate
from lib.nodes import  Cluster


config = Config()
app = FastAPI()
auth = Authenticate()

cluster = Cluster(config.nodes)



# TEST #############################
prediction = Predictions(
    user="John Doe", 
    image="docker image", 
    started="2022-03-17 10:00:00", 
    finished="2022-03-17 10:10:00", 
    duration=10.0
)

prediction.add()



###########################################




@app.post("/predict")
async def predict(
    request: Request, 
):
    data = await request.json()
    image = data["image"]
    Authenticate.verify_existing_token(Authenticate.extract_token(request))
    Authenticate.verify_image_scope(Authenticate.extract_token(request), image)
    print(cluster.nodes)
    return {"cluster": str(cluster.nodes)}




