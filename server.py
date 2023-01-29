import uvicorn
import hashids
import redis
from fastapi import FastAPI, Request, Response
from pydantic import BaseModel
from urllib.parse import urlparse

app = FastAPI()

class Item(BaseModel):
    long_url: str

# Create a hashids object to generate short URLs
hashids = hashids.Hashids(salt='my_salt', min_length=5)

r = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)

@app.post("/shorten")
async def shorten_url(request: Request, item: Item):
    long_url = item.long_url
    counter_key = r.incr('counter_key')
    short_id = hashids.encode(counter_key)
    parsed_url = urlparse(request.url._url)
    short_url = f"{parsed_url.scheme}://{parsed_url.netloc}/" + short_id
    r.set(short_id, long_url)
    return {"short_url": short_url}

@app.get("/{short_id}")
async def redirect_url(short_id: str):
    long_url = str(r.get(short_id))
    print(long_url)
    if long_url:
        return Response(status_code=301, headers={"location": long_url})
    else:
        return Response(status_code=404, content="URL not found")

# if __name__ == "__main__":
#     uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)