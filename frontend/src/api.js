const BASE_URL = "http://localhost:8000";

function getToken() {
  return localStorage.getItem("token") || sessionStorage.getItem("token");
}

function setToken(token, guest = false) {
  if (guest) {
    sessionStorage.setItem("token", token);
  } else {
    localStorage.setItem("token", token);
  }
}

function clearToken() {
  localStorage.removeItem("token");
  sessionStorage.removeItem("token");
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

export async function register(username, password) {
  const data = await request("/auth/register", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
  setToken(data.access_token, false);
  return data;
}

export async function login(username, password) {
  const data = await request("/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
  setToken(data.access_token, false);
  return data;
}

export async function loginAsGuest() {
  const data = await request("/auth/guest", { method: "POST" });
  setToken(data.access_token, true);
  return data;
}

export function logout() {
  clearToken();
}

export function isAuthenticated() {
  return !!getToken();
}

export function isGuest() {
  return !!sessionStorage.getItem("token") && !localStorage.getItem("token");
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
