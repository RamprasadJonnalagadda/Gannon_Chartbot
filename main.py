import json
import logging
import os
import requests as requests
from rasa import train
from rasa import test
from rasa import run
import warnings
import sys

method = sys.argv[-1]
modelName = 'CollegeBot'
warnings.simplefilter('ignore')

# logging module
logger = logging.getLogger()
logger.setLevel(logging.INFO)
fmt = logging.Formatter('%(asctime)s: [ %(message)s ]', '%m/%d/%Y %I:%M:%S %p')
console = logging.StreamHandler()
console.setFormatter(fmt)
logger.addHandler(console)


def training():
    logger.info("Data initialisation")
    configPath = "./data/config.yml"
    DataPath = "./data"
    domain_file = './data/domain.yml'
    storiesPath = "./data/stories_converted.yml"
    nluPath = "./data/nlu_converted.yml"

    logger.info("Training Starting!!!")
    train(domain=domain_file,
          config=configPath,
          training_files=DataPath,
          force_training=True,
          fixed_model_name=modelName,
          persist_nlu_training_data=True)
    logger.info("Training completed!!!")

    logger.info("Validation Starting!!!")
    test(model="models/CollegeBot.tar.gz",
         stories=storiesPath,
         nlu_data=nluPath)
    logger.info("Validation is completed. Please check the result directory")


def serverRun():
    logger.info("Starting server for loading model")
    logger.info("Model : {}".format("models/CollegeBot.tar.gz"))
    run(model="models/CollegeBot.tar.gz", endpoints="./endpoints.yml")


def predict():
    logger.info("Sample check for the model using test data")
    data = json.dumps({"sender": "Rasa", "message": "i want to know the admission process"})
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    logger.info("Calling rasa server")
    res = requests.post('http://localhost:5005/webhooks/rest/webhook', data=data, headers=headers).json()
    logger.info(res)
    logger.info("model is working fine")


if __name__ == '__main__':
    if method == 'train':
        training()
    elif method == 'server':
        serverRun()
    else:
        predict()
