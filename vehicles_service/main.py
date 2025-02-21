from fastapi import FastAPI, Depends, HTTPException, status
from auth import get_current_user
from auth import User
import httpx


app = FastAPI()

API_KEY = "28e54b79f81240b8ab16950ae66c3eca"
ENDPOINT_URL = "https://api-v3.mbta.com/"

async def get_vehicles(route: str = None, revenue: bool = None):
    params = {}
    if route:
        params["filter[route]"] = route
    if revenue is not None:
        params["filter[revenue]"] = str(revenue).lower()

        async with httpx.AsyncClient() as client:
            response = await client.get(f"{ENDPOINT_URL}/vehicles?api_key={API_KEY}", params=params)
            response.raise_for_status()
            response = response.json()

@app.get("/vehicles")
async def read_vehicles(route: str = None, revenue: bool = None, vehicles=Depends(get_vehicles), current_user: User = Depends(get_current_user)):
    return vehicles

async def get_vehicle_by_id(vehicle_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{ENDPOINT_URL}/vehicles/{vehicle_id}?api_key={API_KEY}")
        response.raise_for_status()
        response = response.json()

@app.get("/vehicles/{vehicle_id}")
async def read_vehicle(vehicle_id: str, vehicle=Depends(get_vehicle_by_id)):
    return vehicle


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
    uvicorn.run(app, host="0.0.0.0", port=8004)
