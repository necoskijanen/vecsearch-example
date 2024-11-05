from fastapi import FastAPI
from fastapi import Query
from elasticsearch import Elasticsearch
from dotenv import dotenv_values


app = FastAPI()

config = dotenv_values("../.env")

es = Elasticsearch(
    hosts=["https://es01:9200"],
    http_auth=("elastic", config["ELASTIC_PASSWORD"]),
    verify_certs=True,
    ca_certs="../es.crt"
)


@app.on_event("shutdown")
def app_shutdown():
    es.close()


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/search")
def search(q: str = Query(..., min_length=1)):
    query = {
        "_source": ["name", "description"], 
        "knn": {
            "field": "text_embedding.predicted_value",
            "k": 10,
            "num_candidates": 100,
            "query_vector_builder": {
                "text_embedding": {
                    "model_id": "bert-base-japanese-v2", 
                    "model_text": q
                }
            }
        }
    }
    response = es.search(index="japanese-text-with-embeddings", body=query)

    def filter(source):
        return {
            "name": source["name"],
            "description": source["description"]
        }
    filtered = [filter(res["_source"]) for res in response["hits"]["hits"]]
    return filtered
