from tortoise import Model, fields
from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator


class User(Model):
    id = fields.IntField(pk = True, index = True)
    username = fields.CharField(max_length = 20, null = False, unique = True)
    email = fields.CharField(max_length=100, null = False, unique = True)
    password = fields.CharField(max_length = 100, null = False)
    verified = fields.BooleanField(default = True)

class Game(Model):
    id = fields.IntField(pk = True, index = True)
    game_name = fields.CharField(max_length=100, null=False, unique = True)
    logo = fields.CharField(max_length=100, null=False, default = "default.jpg")

class Coach(Model):
    id = fields.IntField(pk = True, index = True)
    name = fields.CharField(max_length=200, null = False, index = True)
    price = fields.DecimalField(max_digits=12, decimal_places=0)
    coach_image = fields.CharField(max_length=200, null = False, default = 'coachDefault.jpg')
    mmr = fields.IntField(max_digits=99999)
    game = fields.ForeignKeyField("models.Game", related_name="coaches")



user_pydantic = pydantic_model_creator(User, name="User", exclude=("verified", ))
user_pydanticIn = pydantic_model_creator(User, name= "UserIn", exclude_readonly=True, exclude=("verified", ))
user_pydanticOut = pydantic_model_creator(User, name= "UserOut", exclude=("password", ))

game_pydantic = pydantic_model_creator(Game, name="Game")
game_pydanticIn = pydantic_model_creator(Game, name="GameIn", exclude=("id"))

coach_pydantic = pydantic_model_creator(Coach, name="Coach")
coach_pydanticIn = pydantic_model_creator(Coach, name="CoachIn", exclude=("id"))