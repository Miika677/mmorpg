export function showGame() {

    const app = document.querySelector<HTMLDivElement>("#app")!;

    app.innerHTML = `
        <h1 id="player">-</h1>
        <button id="dc">remove all connections</button>

        <canvas id="game"></canvas>

        <ul id="chat"></ul>

        <input
            id="message"
            type="text"
            placeholder="Message..."
        >

        <button id="send">
            Send
        </button>
    `;


    const canvas =
        document.querySelector<HTMLCanvasElement>("#game")!;

    const dc = document.querySelector<HTMLButtonElement>("#dc")!;
    dc.addEventListener("click", disconnect);

    const ctx = canvas.getContext("2d")!;

    canvas.width = 800;
    canvas.height = 600;


    const players: Record<string, Player> = {};


    const socket = new WebSocket(
        "ws://localhost:8000/ws"
    );


    socket.onopen = () => {
        console.log("Connected!");
    };


    socket.onmessage = (event) => {

        const message = JSON.parse(event.data);

        if (message.type === "login") {

            players[message.username] = {
                username: message.username,
                x: message.x,
                y: message.y
            };

            document.querySelector("#player")!.textContent =
                "PLAYER: " + message.username;

            draw();
        }


        if (message.type === "player_joined") {

            players[message.username] = {
                username: message.username,
                x: message.x,
                y: message.y
            };

            draw();
        }


        if (message.type === "player_position") {

            players[message.username] = {
                username: message.username,
                x: message.x,
                y: message.y
            };

            draw();
        }


        if (message.type === "player_left") {

            delete players[message.username];

            draw();
        }
    };

    function disconnect() {

        socket.send(JSON.stringify({
            type: "dc"
        }));
    }


    function move(dx: number, dy: number) {

        if (socket.readyState !== WebSocket.OPEN) {
        return;
    }


        socket.send(JSON.stringify({
            type: "move",
            dx,
            dy
        }));
    }


    document.addEventListener("keydown", (event) => {

        switch (event.key.toLowerCase()) {

            case "w":
                move(0, -10);
                break;

            case "s":
                move(0, 10);
                break;

            case "a":
                move(-10, 0);
                break;

            case "d":
                move(10, 0);
                break;
        }
    });


    function draw() {

        ctx.clearRect(
            0,
            0,
            canvas.width,
            canvas.height
        );


        for (const username in players) {

            const player = players[username];

            ctx.fillStyle = "red";

            ctx.fillRect(
                player.x,
                player.y,
                32,
                32
            );


            ctx.fillStyle = "black";

            ctx.font = "14px Arial";

            ctx.fillText(
                player.username,
                player.x,
                player.y - 5
            );
        }
    }
}


interface Player {
    username: string;
    x: number;
    y: number;
}