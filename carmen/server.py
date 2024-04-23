from fastapi import FastAPI
from pydantic import BaseModel

import carmen_backend

HOST = "0.0.0.0"
PORT = 8000

class TravelParam(BaseModel):
    case_id: str
    city: str

app = FastAPI()

@app.post("/new_game", summary="Starts a new game")
def new_game():
    return carmen_backend.new_game()

@app.get("/get_destinations", summary="Gets the next set of destinations", description="Gets the possible destinations to travel to next to solve the case specified by case_id")
def get_destinations(case_id: str):
    return carmen_backend.get_destinations(case_id)

@app.get("/get_clues", summary="Get clues for the next destination to travel to", description="Get clues for the next destination to travel to in the case specified by case_id")
def get_clues(case_id: str):
    return carmen_backend.get_clues(case_id)


@app.post("/travel", summary="Travel to the specified destination", description="Travel to the specified destination to solve the case for a given case_id")
def travel(param: TravelParam):
    return carmen_backend.travel(param.case_id, param.city)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=HOST, port=PORT)
