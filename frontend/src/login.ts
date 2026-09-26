import { showGame } from "./game";
import { postRequest } from "./apiHelper";

export function showLogin() {

    const app = document.querySelector<HTMLDivElement>("#app")!;

    app.innerHTML = `
        <h1>Login</h1>

        <input
            id="username"
            type="text"
            placeholder="Username"
        >

        <button id="login">
            Login
        </button>
    `;

    const username =
        document.querySelector<HTMLInputElement>("#username")!;

    const button =
        document.querySelector<HTMLButtonElement>("#login")!;

    button.addEventListener("click", async () => {

        const name = username.value.trim();

        if (!name) {
            return;
        }

        await postRequest("/login", {username: username.value})

        showGame();
    });
}