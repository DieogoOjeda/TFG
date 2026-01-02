// static/js/main.js
import { login, loadSession, getCurrentUser } from "./auth.js";
import { showLoginView, showUserDashboard, showAdminDashboard, initRouter } from "./router.js";
import { renderAdminCatalogo } from "./adminCatalog.js";
import { renderUserCatalogo } from "./userCatalog.js";
import { renderAdminPrestamos } from "./adminPrestamos.js";
// ❌ NO import estático de adminSanciones.js para no romper login si falla

function setupLoginForm() {
  const form = document.getElementById("login-form");
  const loginError = document.getElementById("login-error");

  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (loginError) {
      loginError.style.display = "none";
      loginError.textContent = "";
    }

    const email = document.getElementById("login-email").value;
    const password = document.getElementById("login-password").value;

    try {
      await login(email, password);
      const user = getCurrentUser();

      if (!user) throw new Error("No se pudo obtener el usuario actual");

      if (user.role === "librarian") showAdminDashboard();
      else showUserDashboard();
    } catch (err) {
      console.error("Error al iniciar sesión:", err);
      if (loginError) {
        loginError.textContent = "Usuario o contraseña incorrectos.";
        loginError.style.display = "block";
      }
    }
  });
}

function setupNavbarButtons() {
  window.showCatalogo = async () => {
    const user = getCurrentUser();
    if (!user) return;

    if (user.role === "librarian") {
      showAdminDashboard();
      renderAdminCatalogo();
    } else {
      showUserDashboard();
      renderUserCatalogo();
    }
  };

  window.showReservas = async () => {
    const user = getCurrentUser();
    if (!user) return;

    const title = document.getElementById("dashboard-title");
    if (title) title.textContent = "Reservas";

    if (user.role === "librarian") {
      showAdminDashboard();

      // Import dinámico: no rompe login si hay errores en adminReservas.js
      const mod = await import("./adminReservas.js");
      mod.renderAdminReservas();
    } else {
      showUserDashboard();

      const container = document.getElementById("contenido-usuario");
      if (!container) return;

      container.innerHTML = `
        <div class="card">
          <h3>Mis reservas</h3>
          <p>TODO: vista de reservas de usuario (pendiente de conectar con la API).</p>
        </div>
      `;
    }
  S};

  window.showPrestamos = () => {
    const user = getCurrentUser();
    if (!user) return;

    if (user.role === "librarian") {
      showAdminDashboard();
      renderAdminPrestamos();
    } else {
      showUserDashboard();
      // TODO: vista préstamos usuario
    }
  };

  // ✅ Ahora Sanciones para ADMIN se renderiza igual que adminPrestamos/adminCatalogo
  window.showSanciones = async () => {
    const user = getCurrentUser();
    if (!user) return;

    const title = document.getElementById("dashboard-title");
    if (title) title.textContent = "Sanciones";

    if (user.role === "librarian") {
      showAdminDashboard();

      // Import dinámico: no rompe login si sanciones tiene un error
      const mod = await import("./adminSanciones.js");
      mod.renderAdminSanciones();
    } else {
      showUserDashboard();

      const container = document.getElementById("contenido-usuario");
      if (!container) return;

      container.innerHTML = `
        <div class="card">
          <h3>Mis sanciones</h3>
          <p>TODO: vista de sanciones de usuario (pendiente de conectar con la API).</p>
        </div>
      `;
    }
  };

  window.showInicio = () => {
    const user = getCurrentUser();
    if (!user) return;

    if (user.role === "librarian") {
      showAdminDashboard();
      const container = document.getElementById("contenido-admin");
      if (container) {
        container.innerHTML = `
          <div class="card"><h3>Inicio bibliotecario</h3><p>Aquí puedes ver un resumen de la actividad de la biblioteca.</p></div>
        `;
      }
    } else {
      showUserDashboard();
      const container = document.getElementById("contenido-usuario");
      if (container) {
        container.innerHTML = `
          <div class="card"><h3>Inicio usuario</h3><p>Bienvenido a la biblioteca. Usa el menú de la izquierda para navegar.</p></div>
        `;
      }
    }
  };

  window.showUsuarios = () => {
    const user = getCurrentUser();
    if (!user || user.role !== "librarian") return;
    console.log("TODO: gestión de usuarios para bibliotecario");
  };
}

document.addEventListener("DOMContentLoaded", async () => {
  setupLoginForm();
  setupNavbarButtons();
  initRouter();

  const user = await loadSession();
  if (!user) {
    showLoginView();
  } else {
    if (user.role === "librarian") showAdminDashboard();
    else showUserDashboard();
  }
});
