from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


app = FastAPI(docs_url="/docs")
app_name = "app_spa"


# An example of API
@app.get("/spa", tags=["SPA"])
async def read_root():
    return {"Hello": "Connect to the root url after ./start.sh npmrunstart or ./start.sh npmrunbuild."}

# Mount the frontend in the root path (must be the last one)
app.mount("/", StaticFiles(directory=f"{app_name}/frontend_static_build", html = True), name="frontend_static_build")
