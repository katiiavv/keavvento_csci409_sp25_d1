from fastapi import FastAPI, Depends, HTTPException, status
from auth import get_current_user
from auth import User
import httpx

app = FastAPI()

API_KEY = "28e54b79f81240b8ab16950ae66c3eca"
ENDPOINT_URL = "https://api-v3.mbta.com/"

async def get_all_routes():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{ENDPOINT_URL}/routes?api_key={API_KEY}")
        response.raise_for_status()
        return response.json()

@app.get("/routes")
async def get_routes(routes=Depends(get_all_routes), current_user: User = Depends(get_current_user)):

    routes_list = [
        {
            "id": route["id"],
            "type": route["type"],
            "color": route["attributes"]["color"],
            "text_color": route["attributes"]["text_color"],
            "description": route["attributes"]["description"],
            "long_name": route["attributes"]["long_name"],
        }
        for route in routes["data"]
    ]
    return {"routes": routes_list}
async def get_route_by_id(route_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{ENDPOINT_URL}/routes/{route_id}?api_key={API_KEY}")
        response.raise_for_status()
        return response.json()

@app.get("/routes/{route_id}")
async def get_route(route_id: str, route=Depends(get_route_by_id)):
    route_data = route["data"]
    return {
        "id": route_data["id"],
        "type": route_data["type"],
        "color": route_data["attributes"]["color"],
        "text_color": route_data["attributes"]["text_color"],
        "description": route_data["attributes"]["description"],
        "long_name": route_data["attributes"]["long_name"],
    }


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
    uvicorn.run(app, host="0.0.0.0", port=8001)
