from fastapi import FastAPI, Depends
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
async def read_vehicles(route: str = None, revenue: bool = None, vehicles=Depends(get_vehicles)):
    return vehicles

async def get_vehicle_by_id(vehicle_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{ENDPOINT_URL}/vehicles/{vehicle_id}?api_key={API_KEY}")
        response.raise_for_status()
        response = response.json()

@app.get("/vehicles/{vehicle_id}")
async def read_vehicle(vehicle_id: str, vehicle=Depends(get_vehicle_by_id)):
    return vehicle

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
