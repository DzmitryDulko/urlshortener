import uvicorn
import hashids
import redis
from fastapi import FastAPI, Request, Response
from pydantic import BaseModel
from urllib.parse import urlparse
import logging
from pythonjsonlogger import jsonlogger
from datetime import datetime
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

# Configure json logging
logHandler = logging.StreamHandler()

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        if not log_record.get('timestamp'):
            # this doesn't use record.created, so it is slightly off
            now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            log_record['timestamp'] = now
        if log_record.get('level'):
            log_record['level'] = log_record['level'].upper()
        else:
            log_record['level'] = record.levelname

formatter = CustomJsonFormatter('%(timestamp)s %(level)s %(name)s %(message)s')
logHandler.setFormatter(formatter)

serverLogger = logging.getLogger("server")
serverLogger.addHandler(logHandler)
serverLogger.setLevel(logging.DEBUG)

fastapiLogger = logging.getLogger("fastapi")
fastapiLogger.setLevel(logging.CRITICAL)
fastapiLogger.handlers = [logHandler]

uvicornLogger = logging.getLogger("uvicorn")
uvicornLogger.handlers = [logHandler]

# Data payload schema for post request
class Item(BaseModel):
    long_url: str

# Create a hashids object to generate short URLs
hashids = hashids.Hashids(salt='my_salt', min_length=5)

# Connect to redis
r = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)

@app.on_event("startup")
async def startup():
    Instrumentator().instrument(app).expose(app)
    
@app.post("/shorten")
async def shorten_url(request: Request, item: Item):
    serverLogger.info(msg={f"Writing {item}"})

    long_url = item.long_url
    counter_key = r.incr('counter_key')
    short_id = hashids.encode(counter_key)
    parsed_url = urlparse(request.url._url)
    short_url = f"{parsed_url.scheme}://{parsed_url.netloc}/" + short_id
    r.set(short_id, long_url)
    return {"short_url": short_url}

@app.get("/{short_id}")
async def redirect_url(short_id: str):
    serverLogger.info(msg={f"Reading {short_id}"})

    long_url = str(r.get(short_id))
    if long_url:
        return Response(status_code=301, headers={"location": long_url})
    else:
        return Response(status_code=404, content="URL not found")

# if __name__ == "__main__":
#     uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)