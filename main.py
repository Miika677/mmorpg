from fastapi import FastAPI, WebSocket
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

connections = {}
players = {}


@app.get("/")
async def index():
    return FileResponse("frontend/index.html")


@app.post("/login")
async def login(data: dict):
    username = data["username"]

    players[username] = {
        "username": username,
        "x": 100,
        "y": 100,
    }

    response = JSONResponse({"status" : "ok"}, status_code=200)
    response.set_cookie("username", username)

    return response

async def broadcast(message):
    for ws in connections.values():
        await ws.send_json(message)


@app.websocket("/ws")
async def websocket(ws: WebSocket):
    username = ws.cookies.get("username")

    print("username:", username)

    if not username or username not in players:
        await ws.close()
        print("closed early")
        return

    await ws.accept()

    connections[username] = ws

    try:
        # Send all existing players to the new player
        for player in players.values():
            await ws.send_json({
                "type": "login",
                "username": player["username"],
                "x": player["x"],
                "y": player["y"],
            })

        # Tell everyone else that this player joined
        await broadcast({
            "type": "player_joined",
            "username": username,
            "x": players[username]["x"],
            "y": players[username]["y"],
        })

        while True:
            message = await ws.receive_json()

            if message["type"] == "move":

                players[username]["x"] += message["dx"]
                players[username]["y"] += message["dy"]

                await broadcast({
                    "type": "player_position",
                    "username": username,
                    "x": players[username]["x"],
                    "y": players[username]["y"],
                })

            if message["type"] == "dc":
                for connection in list(connections):
                    if connection != username:
                        await connections[connection].close()



    except Exception as e:
        print("WebSocket error:", e)

    finally:
        connections.pop(username, None)

        # Remove player from game
        players.pop(username, None)

        # Tell everyone this player left
        await broadcast({
            "type": "player_left",
            "username": username,
        })