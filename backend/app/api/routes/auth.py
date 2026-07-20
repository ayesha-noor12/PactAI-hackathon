import json
import os

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
USER_FILE = os.path.join(BASE_DIR, "storage", "users.json")


class SignupRequest(BaseModel):
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


def load_users():

    if not os.path.exists(USER_FILE):
        return []

    with open(USER_FILE, "r") as f:
        return json.load(f)


def save_users(users):

    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)


@router.post("/signup")
def signup(data: SignupRequest):

    users = load_users()

    for user in users:

        if user["email"] == data.email:
            raise HTTPException(
                status_code=400,
                detail="Email already exists."
            )

    users.append({

        "name": data.name,
        "email": data.email,
        "password": data.password

    })

    save_users(users)

    return {

        "message": "Signup successful."

    }


@router.post("/login")
def login(data: LoginRequest):

    users = load_users()

    for user in users:

        if (
            user["email"] == data.email
            and user["password"] == data.password
        ):

            return {

                "message": "Login successful.",

                "user": {

                    "name": user["name"],

                    "email": user["email"]

                }

            }

    raise HTTPException(

        status_code=401,

        detail="Invalid email or password."

    )