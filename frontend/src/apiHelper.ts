const API_URL = "http://localhost:8000";

export async function getRequest(endpoint : string) {
    const res = await fetch(`${API_URL}${endpoint}`, {
        credentials: "include"
    });

    return await res.json();
}

export async function postRequest(endpoint : string, data : object) {
    const res = await fetch(`${API_URL}${endpoint}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        credentials: "include",
        body: JSON.stringify(data)
    });

    return await res.json();
}