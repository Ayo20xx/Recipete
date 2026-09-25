from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter()

router.post("/register")
async def registration():
    pass