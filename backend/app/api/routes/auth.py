from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.crud import get_user_by_email
from app.core.security import verify_password, create_access_token

router = APIRouter(tags=["auth"])

@router.post("/login")
async def login(db: AsyncSession = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    
    user = await get_user_by_email(db=db, email=form_data.username)
    
    if not user or not verify_password(plain_password=form_data.password, hashed_password=user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token = create_access_token(data={"sub": user.email})
    
    return {"access_token": access_token, "token_type": "bearer"}

# We use OAuth2PasswordRequestForm because the global OAuth2 standard requires 
# login credentials to be sent as an HTML Form (application/x-www-form-urlencoded) 
# with specific fields ('username' and 'password'). 
# If we used a Pydantic schema like UserCreate, FastAPI would expect a JSON body 
# (application/json) instead, which breaks the OAuth2 specification and stops 
# built-in frontend tools like Swagger UI from working.