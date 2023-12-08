from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from models import *

#Auth
from authentication import *
from fastapi.security import (OAuth2PasswordBearer, OAuth2PasswordRequestForm)

#signals
from tortoise.signals import post_save
from typing import List, Optional, Type
from tortoise import BaseDBAsyncClient

#image upload
from fastapi import File, UploadFile
import secrets
# static files
from fastapi.staticfiles import StaticFiles
# pillow
from PIL import Image

app = FastAPI()

oath2_scheme = OAuth2PasswordBearer(tokenUrl = 'token')

#static file setup config
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post('/token')
async def generate_token(request_form: OAuth2PasswordRequestForm = Depends()):
    token = await token_generator(request_form.username, request_form.password)
    return {'access_token' : token, 'token_type' : 'bearer'}

async def get_current_user(token: str = Depends(oath2_scheme)):
    try:
        payload = jwt.decode(token, config_credentials["SECRET"], algorithms = ['HS256'])
        user = await User.get(id = payload.get("id"))
    except:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED, 
            detail = "Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return await user

@app.post('/user/me')
async def user_login(user: user_pydantic = Depends(get_current_user)):
    game = await Game.get(owner = user)
    return {"status" : "ok", 
            "data" :{
                    "username" : user.username,
                    "email" : user.email,
                    "verified" : user.verified,
                }
            }
@post_save(User)
async def create_game(
    sender: "Type[User]",
    instance: User,
    created: bool,
    using_db: "Optional[BaseDBAsyncClient]",
    update_fields: List[str]
) ->None:    
    if created:
        game_obj = await Game.create(
            game_name = instance.username, owner = instance)
        await game_pydantic.from_tortoise_orm(game_obj)

@app.post("/registration")
async def user_registration(user: user_pydanticIn):
    user_info = user.dict(exclude_unset=True)
    user_info ["password"] = get_hash(user_info["password"])
    user_obj = await User.create(**user_info)
    new_user = await user_pydantic.from_tortoise_orm(user_obj)
    return{
        "status" : "ok",
        "data" : f"Hello {new_user.username}"
    }

@app.get("/")
def index():
    return{"Msg" : "Hello World"}

#upload image
@app.post("/uploadfile/logo")
async def create_upload_file(file: UploadFile = File(...), 
                                user: user_pydantic = Depends(get_current_user)):
    FILEPATH = "./static/images/"
    filename = file.filename
    extension = filename.split(".")[1]

    if extension not in ["jpg", "png"]:
        return {"status" : "error", "detail" : "only upload jpg or png file"}

    token_name = secrets.token_hex(10)+"."+extension
    generated_name = FILEPATH + token_name
    file_content = await file.read()
    with open(generated_name, "wb") as file:
        file.write(file_content)


#pillow
    img = Image.open(generated_name)
    img = img.resize(size = (200,200))
    img.save(generated_name)
    file.close()
    Game.logo = token_name
    await Game.save()
    file_url = "localhost:8000" + generated_name[1:]
    return {"status": "ok", "filename": file_url}

@app.post("/uploadfile/coach/{id}")
async def create_upload_file(id: int, file: UploadFile = File(...), 
                                user: user_pydantic = Depends(get_current_user)):
    FILEPATH = "./static/images/"
    filename = file.filename
    extension = filename.split(".")[1]

    if extension not in ["jpg", "png"]:
        return {"status" : "error", "detail" : "only upload jpg or png file"}

    token_name = secrets.token_hex(10)+"."+extension
    generated_name = FILEPATH + token_name
    file_content = await file.read()
    with open(generated_name, "wb") as file:
        file.write(file_content)


    # pillow
    img = Image.open(generated_name)
    img = img.resize(size = (200,200))
    img.save(generated_name)

    file.close()

    #get coach details
    coach = await Coach.get(id = id)
    game = await coach.game
    owner = await game.owner
    coach.coach_image = token_name
    await coach.save()
    file_url = "localhost:8000" + generated_name[1:]
    return {"status": "ok", "filename": file_url}

#add coach
@app.post("/choaches")
async def add_new_coach(coach: coach_pydanticIn, user: user_pydantic = Depends(get_current_user)):
    coach = coach.dict(exclude_unset = True)
    coach_obj = await Coach.create(**coach, game = user)
    coach_obj = await coach_pydantic.from_tortoise_orm(coach_obj)
    return {"status" : "ok", "data" : coach_obj}

#get all coach
@app.get("/coaches")
async def get_coaches():
    response = await coach_pydantic.from_queryset(Coach.all())
    return {"status" : "ok", "data" : response}

#get specific coach
@app.get("/choaches/{id}")
async def get_specific_coach(id: int,):
    coach = await Coach.get(id = id)
    game = await coach.game
    owner = await game.owner
    response = await coach_pydantic.from_queryset_single(Coach.get(id = id))
    print(type(response))
    return {"status" : "ok",
            "data" : {"coach_details" : response}
            }

#delete coach
@app.delete("/coaches/{id}")
async def delete_coach(id: int, user: user_pydantic = Depends(get_current_user)):
    coach = await Coach.get(id = id)
    game =  await coach.game
    owner = await game.owner
    coach.delete()
    return {"status" : "ok"}

#add game
@app.post("/games")
async def add_new_game(game: game_pydanticIn, user: user_pydantic = Depends(get_current_user)):
    game = game.dict(exclude_unset = True)
    game_obj = await Game.create(**game, game = user)
    game_obj = await game_pydantic.from_tortoise_orm(game_obj)
    return {"status" : "ok", "data" : game_obj}

#get all game
@app.get("/games")
async def get_games():
    response = await game_pydantic.from_queryset(Game.all())
    return {"status" : "ok", "data" : response}

#delete coach
@app.delete("/games/{id}")
async def delete_game(id: int, user: user_pydantic = Depends(get_current_user)):
    game = await Game.get(id = id)
    owner = await game.owner
    game.delete()
    return {"status" : "ok"}


register_tortoise(
    app,
    db_url="sqlite://database.sqlite3",
    modules={"models" : ["models"]},
    generate_schemas=True,
    add_exception_handlers=True
)