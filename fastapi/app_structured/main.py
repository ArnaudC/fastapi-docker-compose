from fastapi import Depends, FastAPI

from .dependencies import get_query_token, get_token_header
from .internal import admin
from .routers import items, users

app = FastAPI(docs_url="/docs", dependencies=[Depends(get_query_token)])


app.include_router(users.router)
app.include_router(items.router)
# Let's say that because it is shared with other projects in the organization, we cannot modify it and add a prefix, dependencies, tags, etc. directly to the APIRouter
# We can declare all that without having to modify the original APIRouter by passing those parameters to app.include_router()
app.include_router(
    admin.router,
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_token_header)],
    responses={418: {"description": "I'm a teapot"}},
)


# We can also add path operations directly to the FastAPI app.
@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}
