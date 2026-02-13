from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/signup")
def signup():
    # TODO: implement signup
    return {"message": "Signup endpoint - to be implemented"}


@router.post("/login")
def login():
    # TODO: implement login
    return {"message": "Login endpoint - to be implemented"}
