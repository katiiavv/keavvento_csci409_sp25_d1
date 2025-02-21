from fastapi import FastAPI, Depends, HTTPException, status
from auth import get_current_user
from auth import User
import httpx
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from auth import authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token

app = FastAPI()

API_KEY = "28e54b79f81240b8ab16950ae66c3eca"
ENDPOINT_URL = "https://api-v3.mbta.com/"

async def get_all_alerts(route: str = None, stop: str = None):
    params = {}
    if route:
        params["filter[route]"] = route
    if stop:
        params["filter[stop]"] = stop

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{ENDPOINT_URL}/alerts?api_key={API_KEY}", params=params)
        response.raise_for_status()
        return response.json()

@app.get("/alerts")
async def read_alerts(route: str = None, stop: str = None, alerts=Depends(get_all_alerts), current_user: User = Depends(get_current_user)):
    return alerts

async def get_alert_by_id(alert_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{ENDPOINT_URL}/alerts/{alert_id}?api_key={API_KEY}")
        response.raise_for_status()
        return response.json()

@app.get("/alerts/{alert_id}")
async def read_alert(alert_id: str, alerts: Depends(get_alert_by_id)):
    return alerts

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)

