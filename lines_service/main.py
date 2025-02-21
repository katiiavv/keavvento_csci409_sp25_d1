from fastapi import FastAPI, Depends, HTTPException, status
from auth import get_current_user
from auth import User
import httpx

app = FastAPI()

API_KEY = "28e54b79f81240b8ab16950ae66c3eca"
ENDPOINT_URL = "https://api-v3.mbta.com/"

async def get_all_lines():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{ENDPOINT_URL}/lines?api_key={API_KEY}")
        response.raise_for_status()
        return response.json()

@app.get("/lines")
async def get_lines(lines=Depends(get_all_lines), current_user: User = Depends(get_current_user)):
    lines_list = [
        {
            "id": line["id"],
            "text_color": line["attributes"]["text_color"],
            "short_name": line["attributes"]["short_name"],
            "long_name": line["attributes"]["long_name"],
            "color": line["attributes"]["color"],
        }
        for line in lines["data"]
    ]
    return {"lines": lines_list}

async def get_line_by_id(line_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{ENDPOINT_URL}/lines/{line_id}?api_key={API_KEY}")
        response.raise_for_status()
        return response.json()

@app.get("/lines/{line_id}")
async def get_line(line_id: str, lines=Depends(get_line_by_id)):
    line_data = lines["data"]
    return {
        "id" : line_data["id"],
        "text_color": line_data["attributes"]["text_color"],
        "short_name": line_data["attributes"]["short_name"],
        "long_name": line_data["attributes"]["long_name"],
        "color": line_data["attributes"]["color"],
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
    uvicorn.run(app, host="0.0.0.0", port=8003)