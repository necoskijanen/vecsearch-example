curl --cacert es.crt -u elastic:$ELASTIC_PASSWORD https://es01:9200/_cat/nodes

cd backend
uv run uvicorn main:app --reload --host 0.0.0.0
