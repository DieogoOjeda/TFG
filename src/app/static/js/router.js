// static/js/router.js
import { getCurrentUser, logout as authLogout } from "./auth.js";

// Referencias a elementos del DOM
const viewLogin = document.getElementById("view-login");
const appLayout = document.getElementById("app-layout");

const viewUser = document.getElementById("view-user");
const viewAdmin = document.getElementById("view-admin");

const userNameSpan = document.getElementById("user-name");
const adminNameSpan = document.getElementById("admin-name");
const sidebarRole = document.getElementById("sidebar-role");
const dashboardTitle = document.getElementById("dashboard-title");

const btnUsuarios = document.getElementById("btn-usuarios");
const btnLogout = document.getElementById("btn-logout");

// -------- Helpers internos --------

function safeDisplay(el, value) {
  if (el) el.style.display = value;
}

function hideAll() {
  safeDisplay(viewLogin, "none");
  safeDisplay(appLayout, "none");
  safeDisplay(viewUser, "none");
  safeDisplay(viewAdmin, "none");
}

// -------- Vistas públicas --------

export function showLoginView() {
  hideAll();
  safeDisplay(viewLogin, "flex");
  if (dashboardTitle) dashboardTitle.textContent = "Iniciar sesión";
  if (sidebarRole) sidebarRole.textContent = "";
  if (userNameSpan) userNameSpan.textContent = "";
  if (adminNameSpan) adminNameSpan.textContent = "";
}

export function showUserDashboard() {
  const user = getCurrentUser();

  hideAll();
  safeDisplay(appLayout, "flex");
  safeDisplay(viewUser, "flex");

  if (btnUsuarios) btnUsuarios.style.display = "none"; // usuario normal no ve "Usuarios"
  if (userNameSpan) userNameSpan.textContent = user?.full_name ?? "";
  if (adminNameSpan) adminNameSpan.textContent = "";
  if (sidebarRole) sidebarRole.textContent = "Usuario";
  if (dashboardTitle) dashboardTitle.textContent = "Panel de usuario";
}

export function showAdminDashboard() {
  const user = getCurrentUser();

  hideAll();
  safeDisplay(appLayout, "flex");
  safeDisplay(viewAdmin, "flex");

  if (btnUsuarios) btnUsuarios.style.display = "block"; // bibliotecario sí ve "Usuarios"
  if (adminNameSpan) adminNameSpan.textContent = user?.full_name ?? "";
  if (userNameSpan) userNameSpan.textContent = "";
  if (sidebarRole) sidebarRole.textContent = "Bibliotecario";
  if (dashboardTitle) dashboardTitle.textContent = "Panel de bibliotecario";
}

// -------- Inicialización (logout) --------

export function initRouter() {
  if (btnLogout) {
    btnLogout.addEventListener("click", () => {
      authLogout();
      showLoginView();
    });
  }
}
