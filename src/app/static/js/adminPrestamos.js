// static/js/adminPrestamos.js
import { apiGet, apiPost } from "./api.js";

let loansCache = [];
let loansTbody = null;

// ======== PUNTO DE ENTRADA ========

export function renderAdminPrestamos() {
  const container = document.getElementById("contenido-admin");
  if (!container) return;

  container.innerHTML = `
    <h3>Gestión de préstamos</h3>

    <!-- BUSCADOR POR EMAIL -->
    <div class="card">
      <h4>Buscar préstamos por email de usuario</h4>
      <input
        type="text"
        id="loan-search-email"
        placeholder="Ej: diego@alumnos.upm.es"
      />
      <button id="btn-search-loans">Buscar</button>
      <button id="btn-clear-loans">Limpiar</button>
    </div>

    <!-- LISTA DE PRÉSTAMOS -->
    <div class="card">
      <h4>Préstamos (ordenados por fecha de fin)</h4>
      <table id="tabla-prestamos" border="1" cellpadding="4">
        <thead>
          <tr>
            <th>ID</th>
            <th>Usuario</th>
            <th>Email</th>
            <th>Libro</th>
            <th>Ejemplar</th>
            <th>Fecha fin</th>
            <th>Estado</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <!-- filas aquí -->
        </tbody>
      </table>
    </div>
  `;

  loansTbody = document.querySelector("#tabla-prestamos tbody");

  const btnSearch = document.getElementById("btn-search-loans");
  const btnClear = document.getElementById("btn-clear-loans");

  btnSearch.addEventListener("click", handleSearchLoans);
  btnClear.addEventListener("click", handleClearLoans);
  loansTbody.addEventListener("click", handleLoansTableClick);

  loadAllLoansAdmin();
}

// ======== CARGA Y ORDENACIÓN ========

async function loadAllLoansAdmin() {
  try {
    const loans = await apiGet("/loans");

    // Guardamos en caché y ordenamos por fecha de fin (due_date ascendente)
    loansCache = [...loans].sort((a, b) => {
      const da = a.due_date ? new Date(a.due_date) : new Date(0);
      const db = b.due_date ? new Date(b.due_date) : new Date(0);
      return da - db;
    });

    renderLoansTable(loansCache);
  } catch (err) {
    console.error("Error cargando préstamos", err);
    if (loansTbody) {
      loansTbody.innerHTML = `
        <tr><td colspan="8">Error cargando préstamos. Revisa la consola.</td></tr>
      `;
    }
  }
}

// ======== BUSCADOR POR EMAIL (CLIENTE) ========

function handleSearchLoans() {
  const input = document.getElementById("loan-search-email");
  if (!input) return;

  const query = input.value.trim().toLowerCase();
  if (!query) {
    renderLoansTable(loansCache);
    return;
  }

  const filtered = loansCache.filter((loan) => {
    const email =
      (loan.user && loan.user.email) ||
      loan.user_email ||
      ""; // intentamos varias formas

    return email.toLowerCase().includes(query);
  });

  renderLoansTable(filtered);
}

function handleClearLoans() {
  const input = document.getElementById("loan-search-email");
  if (input) input.value = "";
  renderLoansTable(loansCache);
}

// ======== RENDER TABLA ========

function renderLoansTable(loans) {
  if (!loansTbody) return;
  loansTbody.innerHTML = "";

  if (!loans || loans.length === 0) {
    const tr = document.createElement("tr");
    const td = document.createElement("td");
    td.colSpan = 8;
    td.textContent = "No hay préstamos.";
    tr.appendChild(td);
    loansTbody.appendChild(tr);
    return;
  }

  loans.forEach((loan) => {
    const tr = document.createElement("tr");

    const userName =
      (loan.user && (loan.user.full_name || loan.user.email)) ||
      loan.user_full_name ||
      "Desconocido";

    const userEmail =
      (loan.user && loan.user.email) ||
      loan.user_email ||
      "";

    const bookTitle =
      loan.book_title ||
      (loan.copy && loan.copy.book && loan.copy.book.title) ||
      "Desconocido";

    const copyBarcode =
      loan.copy_barcode ||
      (loan.copy && loan.copy.barcode) ||
      "";

    const dueDateStr = loan.due_date
      ? new Date(loan.due_date).toLocaleDateString("es-ES")
      : "-";

    const status = loan.status || "";

    tr.innerHTML = `
      <td>${loan.id}</td>
      <td>${escapeHtml(userName)}</td>
      <td>${escapeHtml(userEmail)}</td>
      <td>${escapeHtml(bookTitle)}</td>
      <td>${escapeHtml(copyBarcode)}</td>
      <td>${dueDateStr}</td>
      <td>${escapeHtml(status)}</td>
      <td>
        <button class="btn-devolver" data-id="${loan.id}">Devolver</button>
        <button class="btn-prolongar" data-id="${loan.id}">Prolongar</button>
        <button class="btn-sancionar" data-id="${loan.id}">Sancionar</button>
      </td>
    `;

    loansTbody.appendChild(tr);
  });
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

// ======== GESTOR DE BOTONES EN CADA FILA ========

async function handleLoansTableClick(event) {
  const btn = event.target.closest("button");
  if (!btn) return;

  const loanIdAttr = btn.getAttribute("data-id");
  if (!loanIdAttr) return;

  const loanId = parseInt(loanIdAttr, 10);
  const loan = loansCache.find((l) => l.id === loanId);
  if (!loan) {
    alert("No se ha encontrado el préstamo en memoria.");
    return;
  }

  if (btn.classList.contains("btn-devolver")) {
    await devolverPrestamo(loan);
  } else if (btn.classList.contains("btn-prolongar")) {
    await prolongarPrestamo(loan);
  } else if (btn.classList.contains("btn-sancionar")) {
    await sancionarPrestamo(loan);
  }
}

// ======== ACCIÓN: DEVOLVER PRÉSTAMO ========

async function devolverPrestamo(loan) {
  const confirmMsg =
    `Vas a marcar como DEVUELTO el préstamo ${loan.id}.\n\n` +
    `Ejemplar: ${
      loan.copy_barcode ||
      (loan.copy && loan.copy.barcode) ||
      "desconocido"
    }\n` +
    `¿Seguro que quieres continuar?`;

  const ok = confirm(confirmMsg);
  if (!ok) return;

  try {
    // Asumimos endpoint: POST /loans/{id}/return
    await apiPost(`/loans/${loan.id}/return`, {});

    alert("Préstamo devuelto correctamente.");
    await loadAllLoansAdmin();
  } catch (err) {
    console.error("Error devolviendo préstamo", err);
    alert("Error devolviendo préstamo. Revisa la consola.");
  }
}

// ======== ACCIÓN: PROLONGAR PRÉSTAMO ========

async function prolongarPrestamo(loan) {
  const input = prompt(
    "¿Cuántos días quieres prolongar el préstamo?\n(Ejemplo: 7)"
  );
  if (!input) return;

  const extraDays = parseInt(input, 10);
  if (Number.isNaN(extraDays) || extraDays <= 0) {
    alert("Número de días no válido.");
    return;
  }

  try {
    // Asumimos endpoint: POST /loans/{id}/renew con { extra_days }
    await apiPost(`/loans/${loan.id}/renew`, {
      extra_days: extraDays,
    });

    alert("Préstamo prolongado correctamente.");
    await loadAllLoansAdmin();
  } catch (err) {
    console.error("Error prolongando préstamo", err);
    alert("Error prolongando préstamo. Revisa la consola.");
  }
}

// ======== ACCIÓN: SANCIONAR PRÉSTAMO ========

async function sancionarPrestamo(loan) {
  const input = prompt(
    "¿Cuántos días de sanción quieres aplicar a este préstamo?"
  );
  if (!input) return;

  const days = parseInt(input, 10);
  if (Number.isNaN(days) || days <= 0) {
    alert("Número de días no válido.");
    return;
  }

  try {
    // Asumimos que el préstamo incluye user_id y copy_id
    // y que el endpoint de sanciones es POST /sanctions
    await apiPost("/sanctions/", {
      user_id: loan.user_id,
      book_id: loan.book_id,
      copy_id: loan.copy_id,
      days: days,
    });

    alert("Sanción creada correctamente.");
  } catch (err) {
    console.error("Error creando sanción", err);
    alert("Error creando sanción. Revisa la consola.");
  }
}
