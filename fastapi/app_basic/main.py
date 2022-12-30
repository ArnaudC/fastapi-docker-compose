import os
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID
from time import time as time_now
from datetime import datetime, time, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field, HttpUrl
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi import FastAPI, Query, Path, Body, Cookie, Header, status, Form, UploadFile, File, HTTPException, Depends, Request, BackgroundTasks, Response, WebSocket, WebSocketDisconnect, WebSocketException
from fastapi.templating import Jinja2Templates
from fastapi.routing import APIRoute


# Define reusable tags
class Tags(Enum):
    filesTag = "Request Files"
    dependencyTag = "Dependencies"
    routePriority = "Route priority"
    queryParameterTag = "Query parameter"
    requestBodyTag = "Request body"
    pathTag = "Path()"
    responseModelTag = "Response Model"
    statusCodeTag = "Status Code"
    bodyUpdatesTag = "Body Updates"
    securityOAuth2Tag = "Security OAuth2"
    securityJWTTag = "Security JWT"

# Custom requests and apiRouter class
class RequestLogRoute(APIRoute):
    LOG_FILE_PATH = "log.txt"
    async def log_starlette_request(self, starlette_request: Request, logger_file: File, mode: str) -> None:
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")
        logger_file.write(f"{now}: {mode}: ")
        if (hasattr(starlette_request, 'url') and hasattr(starlette_request.url, '_url')):
            logger_file.write(f"{starlette_request.url._url}, ")
        if (hasattr(starlette_request, 'method')):
            logger_file.write(f"method: {starlette_request.method}, ")
        if (hasattr(starlette_request, 'client') and hasattr(starlette_request.client, 'host')):
            logger_file.write(f"clienthost: {starlette_request.client.host}, ")
        if (hasattr(starlette_request, 'headers')):
            logger_file.write(f"headers: {starlette_request.headers.items()}, ")
        if (hasattr(starlette_request, 'body')):
            if (callable(starlette_request.body)):
                body = await starlette_request.body()
            else:
                body = starlette_request.body
            if (hasattr(body, 'decode') and callable(body.decode)):
                decoded_body = body.decode()
                logger_file.write(f"decoded_body: \n{decoded_body}")
            else:
                logger_file.write(f"body: \n{body}")
        logger_file.write(f"\n")
    def get_route_handler(self) -> None:
        original_route_handler = super().get_route_handler()
        async def custom_route_handler(input_starlette_request: Request) -> Response:
            with open(self.LOG_FILE_PATH, mode="a") as logger_file:
                await self.log_starlette_request(input_starlette_request, logger_file, "Input")
                output_starlette_request: Response = await original_route_handler(input_starlette_request)
                await self.log_starlette_request(output_starlette_request, logger_file, "Output")
                return output_starlette_request
        return custom_route_handler

# Main app
app_name = "app_basic"
app = FastAPI(docs_url="/docs")
app.router.route_class = RequestLogRoute

# Events: startup - shutdown
@app.on_event("startup")
async def startup_event():
    # print("Application startup")
    pass
@app.on_event("shutdown")
def shutdown_event():
    # print("Application shutdown")
    pass

# Static files : go to http://localhost:53187/static/index.html
app.mount("/static", StaticFiles(directory=f"{app_name}/static"), name="static")

# Root page
@app.get("/", tags=["Root api"])
async def read_root():
    return {"Hello": "World"}

# GET params + Optional parameters
@app.get("/items_optional_parameters/{item_id}", tags=["GET params + Optional parameters"])
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}

# Route priority
@app.get("/priority/users/me", tags=[Tags.routePriority])
async def read_user_me():
    return {"user_id": "the current user"}
@app.get("/priority/users/{user_id}", tags=[Tags.routePriority])
async def read_user(user_id: str):
    return {"user_id": user_id}

# Using an enum
class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"
@app.get("/models/{model_name}", tags=["Using an enum"])
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}
    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}
    return {"model_name": model_name, "message": "Have some residuals"}

# QP : In this case, the name of the parameter is file_path, and the last part, :path, tells it that the parameter should match any path.
@app.get("/files/{file_path:path}", tags=[Tags.queryParameterTag])
async def query_parameter_with_slash_inside_ex_file_path(file_path: str):
    return {"file_path": file_path}

# QP : list
fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]
@app.get("/items_query_parameters/", tags=[Tags.queryParameterTag])
async def query_parameter_list(skip: int = 0, limit: int = 10):
    return fake_items_db[skip : skip + limit]

# QP : type conversion
@app.get("/items_type_conversion/{item_id}", tags=[Tags.queryParameterTag])
async def query_parameter_type_conversion(item_id: str, q: str | None = None, short: bool = False):
    item = {"item_id": item_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This item has a long description"}
        )
    return item

# QP : Query() parameter list / multiple values
@app.get("/items_multiple_values/", tags=[Tags.queryParameterTag])
async def list_of_query_parameters(q: list[str] | None = Query(default=None, title="Query string", description="Query string for the items to search in the database that have a good match", min_length=3)):
    query_items = {"q": q}
    return query_items

# QP : Validate parameters
@app.get("/items_validate_qp/", tags=[Tags.queryParameterTag])
async def validate_query_parameters(q: str | None = Query(default=None,  min_length=3, max_length=50, regex="^fixedquery$")):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results

# Request body : Field()
class Item(BaseModel):
    name: str
    description: str | None = Field(default=None, title="The description of the item", max_length=300)
    price: float
    tax: float | None = None
@app.post("/items_request_body/", tags=[Tags.requestBodyTag])
async def field_request_body(item: Item):
    item_dic = item.dict()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dic.update({"price_with_tax": price_with_tax})
    return item_dic

# Request body + path parameters
@app.put("/items_path_parameters/{item_id}", tags=[Tags.requestBodyTag])
async def request_body_and_path_parameters(item_id: int, item: Item):
    return {"item_id": item_id, **item.dict()}

# Path() Parameters and Numeric Validations
@app.get("/items_numeric_validation/{item_id}", tags=[Tags.pathTag])
async def path_numeric_validation(item_id: int = Path(title="The ID of the item to get"), q: str | None = Query(default=None, alias="item-query")):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results

# Path() Number validations: greater than or equal
@app.get("/items_numeric_greater/{item_id}", tags=[Tags.pathTag])
async def path_numeric_greater(*, item_id: float = Path(title="The ID of the item to get", gt=0, le=10.5), q: str):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results

# Body() to add attributes not in the input model
@app.put("/add_attributes_not_in_the_input_model/{item_id}", tags=["Body() to add attributes not in the input model"])
async def update_item(item_id: int, item: Item = Body(embed=True), importance: int = Body(gt=0)):
    results = {"item_id": item_id, "item": item, "importance": importance}
    return results

# Declare a list with a type parameter
class ItemTypeParameter(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: list[str] = []
    dict1: dict[str, str] = {}
    set1: set[str] = set()
@app.put("/items_type_parameter/{item_id}", tags=["Declare a list with a type parameter"])
async def update_item_type(item_id: int, item: ItemTypeParameter):
    results = {"item_id": item_id, "item": item}
    return results

# Nested Models
class ImageNested(BaseModel):
    url: HttpUrl
    name: str
class ItemNested(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = set()
    image: ImageNested | None = None
@app.put("/items_nested/{item_id}", tags=["Nested Models"])
async def update_nested_item(item_id: int, item: ItemNested):
    results = {"item_id": item_id, "item": item}
    return results

# Declare Request Example Data (default value in openapi schema)
class ItemRequestExampleData(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    class Config:
        schema_extra = {
            "example": {
                "name": "Foo",
                "description": "A very nice Item",
                "price": 35.4,
                "tax": 3.2,
            }
        }
@app.put("/items_request_example_data/{item_id}", tags=["Declare Request Example Data (default value in openapi schema)"])
async def update_item(item_id: int, item: ItemRequestExampleData):
    results = {"item_id": item_id, "item": item}
    return results

# Using example to add doc in openapi schema
class Item12(BaseModel):
    name: str = Field(example="Foo")
    description: str | None = Field(default=None, example="A very nice Item")
    price: float = Field(example=35.4)
    tax: float | None = Field(default=None, example=3.2)

# Extra types
@app.put("/items_extra_type/{item_id}", tags=["Extra types"])
async def extra_type(
    item_id: UUID,
    start_datetime: datetime | None = Body(default=None),
    end_datetime: datetime | None = Body(default=None),
    repeat_at: time | None = Body(default="14:23:55.003"),
    process_after: timedelta | None = Body(default=None),
):
    """Ex: '12345678-1234-1234-1234-123456789abc'"""
    start_process = start_datetime + process_after
    duration = end_datetime - start_process
    return {
        "item_id": item_id,
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "repeat_at": repeat_at,
        "process_after": process_after,
        "start_process": start_process,
        "duration": duration,
    }

# Cookie()
@app.get("/items_cookie/", tags=["Cookie()"])
async def read_items_cookies(ads_id: str | None = Cookie(default=None)):
    return {"ads_id": ads_id}

# Header()
@app.get("/items_header/", tags=["Header()"])
async def read_items_header(user_agent: str = Header(None)):
    return {"User-Agent": user_agent}

# Response Model : ensure output is formatted
class UserIn(BaseModel):
    username: str
    password: str
    full_name: str | None = None
class UserOut(BaseModel):
    username: str
    full_name: str | None = None
@app.post("/format_input_output/", response_model=UserOut, tags=[Tags.responseModelTag])
async def format_input_output(user: UserIn):
    return user

# Multiple Response types
class BaseItem(BaseModel):
    description: str
    type: str
class CarItem(BaseItem):
    type = "car"
class PlaneItem(BaseItem):
    type = "plane"
    size: int
items = {
    "item1": {"description": "All my friends drive a low rider", "type": "car"},
    "item2": {
        "description": "Music is my aeroplane, it's my aeroplane",
        "type": "plane",
        "size": 5,
    },
}
@app.get("/multiple_response_types/{item_id}", response_model=PlaneItem | CarItem, tags=[Tags.responseModelTag])
async def multiple_response_types(item_id: str):
    """Enter **item1** or **item2** to see the different responses."""
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    return items[item_id]

# Response Status Code
@app.post("/custom_status_code/", status_code=status.HTTP_201_CREATED, tags=[Tags.statusCodeTag])
async def custom_status_code(name: str):
    return {"name": name}

# Conditional HTTP status code response
tasks = {"foo": "Listen to the Bar Fighters"}
@app.put("/conditional_status_code/{task_id}", status_code=200, tags=[Tags.statusCodeTag])
def get_or_create_task(task_id: str, response: Response):
    if task_id not in tasks:
        tasks[task_id] = "This didn't exist before"
        response.status_code = status.HTTP_201_CREATED
    return tasks[task_id]

# Form Data
@app.post("/login/", tags=["Form Data"])
async def login(username: str = Form(), password: str = Form()):
    return {"username": username}

# Request Files
@app.post("/files/", tags=[Tags.filesTag])
async def create_file(file: bytes = File()):
    return {"file_size": len(file)}
@app.post("/uploadfile/", tags=[Tags.filesTag])
async def create_upload_file(file: UploadFile):
    return {"filename": file.filename}
@app.post("/uploadfiles/", tags=[Tags.filesTag])
async def create_upload_files(
    files: list[UploadFile] = File(description="Multiple files as UploadFile"),
):
    return {"filenames": [file.filename for file in files]}

# Handling Errors
@app.get("/handle_errors/{item_id}", tags=["Handling Errors"])
async def handle_errors(item_id: str):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item": items[item_id]}

# Openapi doc in response and summary
@app.post("/openapi_advanced_doc/", response_model=Item, summary="Create an item", response_description="The created item", tags=["Openapi doc in response and summary"])
async def openapi_advanced_doc(item: Item):
    """
    Create an item with all the information:

    - **name**: each item must have a name
    - **description**: a long description
    - **price**: required
    - **tax**: if the item doesn't have tax, you can omit this
    - **tags**: a set of unique tag strings for this item
    """
    return item

# JSON Compatible Encoder
fake_db = {}
@app.put("/json_compatible_encoder/{id}", tags=["JSON Compatible Encoder"])
def json_compatible_encoder(id: str, item: Item):
    json_compatible_item_data = jsonable_encoder(item)
    fake_db[id] = json_compatible_item_data
    return fake_db

# Body - Updates
@app.put("/items_body_updates/{item_id}", response_model=Item, tags=[Tags.bodyUpdatesTag])
async def items_body_updates(item_id: str, item: Item):
    update_item_encoded = jsonable_encoder(item)
    items[item_id] = update_item_encoded
    return update_item_encoded
@app.patch("/items_body_updates_dict/{item_id}", response_model=Item, tags=[Tags.bodyUpdatesTag])
async def items_body_updates_dict(item_id: str, item: Item):
    stored_item_data = items[item_id]
    stored_item_model = Item(**stored_item_data)
    update_data = item.dict(exclude_unset=True)
    updated_item = stored_item_model.copy(update=update_data)
    items[item_id] = jsonable_encoder(updated_item)
    return updated_item

# Dependencies - First Steps
async def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}
@app.get("/items_dependencies/", tags=[Tags.dependencyTag])
async def items_dependencies(commons: dict = Depends(common_parameters)):
    return commons
@app.get("/users_dependencies/", tags=[Tags.dependencyTag])
async def users_dependencies(commons: dict = Depends(common_parameters)):
    return commons
class CommonQueryParams:
    def __init__(self, q: str | None = None, skip: int = 0, limit: int = 100):
        self.q = q
        self.skip = skip
        self.limit = limit
@app.get("/update_items_dependencies/", tags=[Tags.dependencyTag])
async def update_items_dependencies(commons: CommonQueryParams = Depends()):
    response = {}
    if commons.q:
        response.update({"q": commons.q})
    items = fake_items_db[commons.skip : commons.skip + commons.limit]
    response.update({"items": items})
    return response

# Sub-dependencies
async def query_extractor(q: str | None = None):
    return q
def query_or_cookie_extractor(q: str = Depends(query_extractor), last_query: str | None = Cookie(default=None)):
    if not q:
        return last_query
    return q
@app.get("/read_query_sub_dependencies/", tags=["Sub-dependencies"])
async def read_query_sub_dependencies(query_or_default: str = Depends(query_or_cookie_extractor)):
    return {"q_or_cookie": query_or_default}

# Dependencies in path operation decorators
async def verify_token(x_token: str = Header()):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")
async def verify_key(x_key: str = Header()):
    if x_key != "fake-super-secret-key":
        raise HTTPException(status_code=400, detail="X-Key header invalid")
    return x_key
@app.get("/dependencies_verify_token/", dependencies=[Depends(verify_token), Depends(verify_key)], tags=["Dependencies in path operation decorators"])
async def dependencies_verify_token():
    """Requires x_token = **fake-super-secret-token** and x_key = **fake-super-secret-key**"""
    return [{"item": "Foo"}, {"item": "Bar"}]

# Global Dependencies
# app = FastAPI(dependencies=[Depends(verify_token), Depends(verify_key)], docs_url="/docs")
# @app.get("/items26/")
# async def read_items():
#     return [{"item": "Portal Gun"}, {"item": "Plumbus"}]
# @app.get("/users26/")
# async def read_users():
#     return [{"username": "Rick"}, {"username": "Morty"}]
# A dependency with yield and try
# async def get_db():
#     db = DBSession()
#     try:
#         yield db
#     finally:
#         db.close()

# Context Managers
@app.get("/read_context_manager/", tags=["Context Managers"])
async def read_context_manager():
    with open("./requirements.txt") as f:
        contents = f.read()
    return contents

# Security : Simple OAuth2 with Password and Bearer (Open API Authorize, username = 'johndoe', password = 'secret', client credentials location = 'HTTP header')
oauth2_scheme_simple = OAuth2PasswordBearer(tokenUrl="login_simple_oauth2_with_password_and_bearer")
class UserSimple(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None
class UserInDBSimple(UserSimple):
    hashed_password: str
fake_users_db_simple = {
    "johndoe": {"username": "johndoe", "full_name": "John Doe", "email": "johndoe@example.com", "hashed_password": "fakehashedsecret", "disabled": False, },
    "alice": { "username": "alice", "full_name": "Alice Wonderson", "email": "alice@example.com", "hashed_password": "fakehashedsecret2", "disabled": True, },
    "admin": { "username": "admin", "full_name": "admin simple_oauth2", "email": "admin@simple_oauth2.com", "hashed_password": "fakehashedadmin", "disabled": False, },
}
def fake_hash_password_simple(password: str):
    return "fakehashed" + password
def get_user_OAuth2_simple(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDBSimple(**user_dict)
def fake_decode_token_simple(token):  # This doesn't provide any security at all. Check the next version.
    user = get_user_OAuth2_simple(fake_users_db_simple, token)
    return user
async def get_current_user_simple(token: str = Depends(oauth2_scheme_simple)):
    user = fake_decode_token_simple(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
async def get_current_active_user_simple(current_user: UserSimple = Depends(get_current_user_simple)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
@app.post(f"/login_simple_oauth2_with_password_and_bearer", tags=[Tags.securityOAuth2Tag])
async def login_simple_oauth2_with_password_and_bearer(form_data: OAuth2PasswordRequestForm = Depends()):
    """ OpenAPI -> click authorize -> username = 'admin', password = 'admin', client credentials location = 'HTTP header'. """
    user_dict = fake_users_db_simple.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDBSimple(**user_dict)
    hashed_password = fake_hash_password_simple(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return {"access_token": user.username, "token_type": "bearer"}
@app.get("/get_simple_oauth2_token/", tags=[Tags.securityOAuth2Tag])
async def get_oauth2_token(token: str = Depends(oauth2_scheme_simple)):
    return {"token": token}
@app.get("/read_simple_oauth2_users/me", tags=[Tags.securityOAuth2Tag])
async def read_simple_oauth2_read_current_users(current_user: UserSimple = Depends(get_current_user_simple)):
    return current_user
@app.get("/read_simple_oauth2_user_if_active/me", tags=[Tags.securityOAuth2Tag])
async def read_simple_oauth2_user_if_active(current_user: UserSimple = Depends(get_current_active_user_simple)):
    return current_user

# JWT
oauth2_jwt_scheme = OAuth2PasswordBearer(tokenUrl="login_jwt")
class UserJWT(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None
class UserInDBJWT(UserJWT):
    hashed_password: str
class TokenJwt(BaseModel):
    access_token: str
    token_type: str
class TokenDataJwt(BaseModel):
    username: str | None = None
fake_users_db_jwt = {
    "admin": { "username": "admin", "full_name": "admin jwt", "email": "admin@jwt.com", "hashed_password": "$2a$12$8I1BKp163lUkQOF9Vk.PB.rJfGWauABZOfr3wNoYEGJb28UAaD8bq", "disabled": False, }
}
JWT_SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"  # to get a string like this run : openssl rand -hex 32
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context_jwt = CryptContext(schemes=["bcrypt"], deprecated="auto")
def verify_password_jwt(plain_password, hashed_password):
    return pwd_context_jwt.verify(plain_password, hashed_password)
def get_password_hash_jwt(password):
    return pwd_context_jwt.hash(password)
def get_user_jwt(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDBJWT(**user_dict)
def authenticate_user_jwt(fake_db, username: str, password: str):
    user = get_user_jwt(fake_db, username)
    if not user:
        return False
    print(user)
    if not verify_password_jwt(password, user.hashed_password):
        return False
    return user
def create_access_token_jwt(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt
async def get_current_user_jwt(token: str = Depends(oauth2_jwt_scheme)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"}, )
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenDataJwt(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user_jwt(fake_users_db_jwt, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user
async def get_current_active_user_jwt(current_user: UserJWT = Depends(get_current_user_jwt)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
@app.post("/login_jwt", response_model=TokenJwt, tags=[Tags.securityJWTTag])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """ OpenAPI -> click authorize -> username = 'admin', password = 'admin', client credentials location = 'HTTP header'. """
    user = authenticate_user_jwt(fake_users_db_jwt, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token_jwt(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
@app.get("/jwt/users/me/", response_model=UserJWT, tags=[Tags.securityJWTTag])
async def read_users_me_jwt(current_user: UserJWT = Depends(get_current_active_user_jwt)):
    return current_user
@app.get("/jwt/users/me/items/", tags=[Tags.securityJWTTag])
async def read_own_items_jwt(current_user: UserJWT = Depends(get_current_active_user_jwt)):
    return [{"item_id": "Foo", "owner": current_user.username}]

# Middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time_now()
    response = await call_next(request)
    process_time = time_now() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Background tasks (starlette.background)
def write_log(message: str):
    with open(f"{app_name}/background_task_output.txt", mode="a") as log:
        log.write(message)
def get_query(background_tasks: BackgroundTasks, q: str | None = None):
    if q:
        message = f"found query: {q}\n"
        background_tasks.add_task(write_log, message)
    return q
@app.post("/send-notification/{email}", tags=["Background tasks (starlette.background)"])
async def send_notification(
    email: str, background_tasks: BackgroundTasks, q: str = Depends(get_query)
):
    message = f"message to {email}\n"
    background_tasks.add_task(write_log, message)
    return {"message": "Message sent"}

# Large files
@app.get("/large_file", tags=["Large files"])
async def main():
    return FileResponse(f"{app_name}/background_task_output.txt")

# Custom HTTP headers response
@app.get("/custom_headers/", tags=["Custom headers response"])
def get_headers():
    content = {"message": "Hello World"}
    headers = {"X-Cat-Dog": "a cat in the world", "Content-Language": "en-US"}
    return JSONResponse(content=content, headers=headers)

# Using Requests directly
@app.get("/using_requests_directly/{item_id}", tags=["Using Requests directly"])
def using_requests_directly(item_id: str, request: Request):
    client_host = request.client.host
    return {"client_host": client_host, "item_id": item_id}

# Jinja2 templates
templates = Jinja2Templates(directory=f"{app_name}/templates_jinja2")
@app.get("/jinja2/{id}", response_class=HTMLResponse, tags=["Jinja2 templates"])
async def read_item(request: Request, id: str):
    return templates.TemplateResponse("item.html", {"request": request, "id": id})

# Websockets : basic app
FAST_API_EXTERNAL_PORT=os.environ['FAST_API_WEBSOCKET_PORT']
html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:""" + FAST_API_EXTERNAL_PORT + """/ws_basic_app");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""
@app.get("/websockets_basic_app", tags=["Websockets"])
async def get_basic_app():
    return HTMLResponse(html)
@app.websocket("/ws_basic_app")
async def websocket_endpoint_basic_app(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")

# Websockets : token
html_token = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <label>Item ID: <input type="text" id="itemId" autocomplete="off" value="foo"/></label>
            <label>Token: <input type="text" id="token" autocomplete="off" value="some-key-token"/></label>
            <button onclick="connect(event)">Connect</button>
            <hr>
            <label>Message: <input type="text" id="messageText" autocomplete="off"/></label>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
        var ws = null;
            function connect(event) {
                var itemId = document.getElementById("itemId")
                var token = document.getElementById("token")
                ws = new WebSocket("ws://localhost:""" + FAST_API_EXTERNAL_PORT + """/ws_token/items/" + itemId.value + "/ws?token=" + token.value);
                ws.onmessage = function(event) {
                    var messages = document.getElementById('messages')
                    var message = document.createElement('li')
                    var content = document.createTextNode(event.data)
                    message.appendChild(content)
                    messages.appendChild(message)
                };
                event.preventDefault()
            }
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""
@app.get("/websockets_token", tags=["Websockets"])
async def get():
    return HTMLResponse(html_token)
async def get_cookie_or_token(websocket: WebSocket, session: str|None = Cookie(default=None), token: str|None = Query(default=None), ):
    if session is None and token is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    return session or token
@app.websocket("/ws_token/items/{item_id}/ws")
async def websocket_endpoint_token(
    websocket: WebSocket,
    item_id: str,
    q: int|None = None,
    cookie_or_token: str = Depends(get_cookie_or_token),
):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(
            f"Session cookie or query token value is: {cookie_or_token}"
        )
        if q is not None:
            await websocket.send_text(f"Query parameter q is: {q}")
        await websocket.send_text(f"Message text was: {data}, for item ID: {item_id}")

# Websockets : Handling disconnections and multiple clients
html_multiple_clients = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <h2>Your ID: <span id="ws-id"></span></h2>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var client_id = Date.now()
            document.querySelector("#ws-id").textContent = client_id;
            var ws = new WebSocket(`ws://localhost:""" + FAST_API_EXTERNAL_PORT + """/ws_multiple_clients/${client_id}`);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)
manager = ConnectionManager()
@app.get("/websockets_multiple_clients", tags=["Websockets"])
async def get_multiple_clients():
    return HTMLResponse(html_multiple_clients)
@app.websocket("/ws_multiple_clients/{client_id}")
async def websocket_endpoint_multiple_clients(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")
