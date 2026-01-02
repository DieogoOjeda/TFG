// static/js/auth.js
import { apiPost, apiGet, setAuthToken } from "./api.js";

let currentUser = null;

export function getCurrentUser() {
  return currentUser;
}

export async function login(email, password) {
  // 1) pedir token
  const data = await apiPost("/auth/login", { email, password });
  setAuthToken(data.access_token);

  // 2) pedir /auth/me para conocer el usuario
  currentUser = await apiGet("/auth/me");
  return currentUser;
}

export async function loadSession() {
  try {
    currentUser = await apiGet("/auth/me");
    return currentUser;
  } catch {
    // token inválido o caducado
    setAuthToken(null);
    currentUser = null;
    return null;
  }
}

export function logout() {
  setAuthToken(null);
  currentUser = null;
}
