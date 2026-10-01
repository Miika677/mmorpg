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
        "chunk": {
            "x" : 0,
            "y" : 0
        }
    }

    response = JSONResponse({"status" : "ok"}, status_code=200)
    response.set_cookie("username", username)

    return response

def chunk_check(username : str, x : int, y : int):
    player = players[username]
    chunk = player["chunk"]

    if player["x"] > 800:
        player["x"] = 0
        chunk["x"] += 1

        print(str(chunk["x"]) + " " + username.capitalize())

    if player["x"] < 0:
        if chunk["x"] > 0:
            player["x"] = 800
            chunk["x"] -= 1

        print(str(chunk["x"]) + " " + username.capitalize())

    if player["y"] > 600:
        player["y"] = 0
        chunk["y"] += 1

        print(str(chunk["y"]) + " " + username.capitalize())

    if player["y"] < 0:
        if chunk["y"] > 0:
            player["y"] = 600
            chunk["y"] -= 1

        print(str(chunk["y"]) + " " + username.capitalize())
    

async def broadcast(message):
    for ws in connections.values():
        await ws.send_json(message)

async def chunkcast(message, x_input,y_input):
    for username, ws in connections.items():
        if (
        players[username]["chunk"]["x"] == x_input
        and players[username]["chunk"]["y"] == y_input
        ):
            await ws.send_json(message)


@app.websocket("/ws")
async def websocket(ws: WebSocket):
    username = ws.cookies.get("username")

    print("username:", username)

    #if player not logged in close connection
    if not username or username not in players:
        await ws.close()
        print("closed early")
        return

    await ws.accept()

    #add to WS dict
    connections[username] = ws

    try:
        # Send all existing players to the new player
        for player in players.values():
            await chunkcast({
                "type": "login",
                "username": player["username"],
                "x": player["x"],
                "y": player["y"],
            }, players[username]["chunk"]["x"], players[username]["chunk"]["y"])

            

        # Tell everyone else that this player joined
        await chunkcast({
            "type": "player_joined",
            "username": username,
            "x": players[username]["x"],
            "y": players[username]["y"],
        }, players[username]["chunk"]["x"], players[username]["chunk"]["y"])

        #RECEIVE ACTION
        while True:
            message = await ws.receive_json()

            #movement
            if message["type"] == "move":

                direction = message["direction"]

                if direction == "north":
                    players[username]["y"] -= 5
                elif direction == "south":
                    players[username]["y"] += 5
                elif direction == "west":
                    players[username]["x"] -= 5
                elif direction == "east":
                    players[username]["x"] += 5

                chunk_check(username, players[username]["chunk"]["x"], players[username]["chunk"]["y"])

                await chunkcast({
                    "type": "player_position",
                    "username": username,
                    "x": players[username]["x"],
                    "y": players[username]["y"],
                }, players[username]["chunk"]["x"], players[username]["chunk"]["y"])


            #experimental dc thing
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