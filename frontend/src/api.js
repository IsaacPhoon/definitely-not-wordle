const BASE_URL = "http://localhost:8000";

function getToken() {
  return localStorage.getItem("token");
}

function setToken(token) {
  localStorage.setItem("token", token);
}

function clearToken() {
  localStorage.removeItem("token");
}

async function request(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...options.headers };
  const token = getToken();
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  const res = await fetch(`${BASE_URL}${path}`, { ...options, headers });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const err = new Error(body.detail || `Request failed: ${res.status}`);
    err.status = res.status;
    throw err;
  }
  return res.json();
}

export async function register(email, password) {
  const data = await request("/auth/register", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  setToken(data.access_token);
  return data;
}

export async function login(email, password) {
  const data = await request("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  setToken(data.access_token);
  return data;
}

export function logout() {
  clearToken();
}

export function isAuthenticated() {
  return !!getToken();
}

export async function createGame() {
  return request("/games", { method: "POST" });
}

export async function getGame(gameId) {
  return request(`/games/${gameId}`);
}

export async function getGuesses(gameId) {
  return request(`/games/${gameId}/guesses`);
}

export async function submitGuess(gameId, word) {
  return request(`/games/${gameId}/guess`, {
    method: "POST",
    body: JSON.stringify({ word }),
  });
}

export async function getStats() {
  return request("/users/me/stats");
}
