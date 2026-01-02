// static/js/adminReservas.js
import { apiGet } from "./api.js";

function escapeHtml(str) {
  return String(str ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function formatDate(value) {
  if (!value) return "—";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return String(value);
  return d.toLocaleString();
}

function normalizeEmail(email) {
  return String(email ?? "").trim().toLowerCase();
}

function debounce(fn, wait) {
  let t = null;
  return (...args) => {
    if (t) clearTimeout(t);
    t = setTimeout(() => fn(...args), wait);
  };
}

function renderUI(container) {
  container.innerHTML = `
    <section class="panel">
      <div class="panel__header">
        <h2>Reservas</h2>
        <div class="panel__controls">
          <input id="reservations-search-email" class="input" type="email"
            placeholder="Buscar por email (ej: user@alumnos.upm.es)" />
          <button id="reservations-refresh" class="btn">Recargar</button>
        </div>
      </div>

      <div id="reservations-status" class="status" style="margin: 10px 0;"></div>

      <div class="table-wrap">
        <table class="table" id="reservations-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>User ID</th>
              <th>Book ID</th>
              <th>Copy ID</th>
              <th>Estado</th>
              <th>Creada</th>
            </tr>
          </thead>
          <tbody id="reservations-tbody">
            <tr><td colspan="6">Cargando…</td></tr>
          </tbody>
        </table>
      </div>

      <p style="margin-top:8px; font-size: 0.9em; opacity:.8;">
        Nota: si quieres ver el <b>email</b> en la tabla, añade <code>user_email</code> a <code>ReservationRead</code>.
      </p>
    </section>
  `;
}

function setStatus(msg, type = "info") {
  const el = document.querySelector("#reservations-status");
  if (!el) return;
  el.textContent = msg || "";
  el.dataset.type = type;
}

function renderTable(rows) {
  const tbody = document.querySelector("#reservations-tbody");
  if (!tbody) return;

  if (!rows || rows.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6">No hay reservas.</td></tr>`;
    return;
  }

  tbody.innerHTML = rows
    .map((r) => {
      // Intenta soportar nombres típicos de campos
      const id = r.id ?? "—";
      const userId = r.user_id ?? "—";
      const bookId = r.book_id ?? "—";
      const copyId = r.copy_id ?? r.book_copy_id ?? "—";
      const status = r.status ?? r.state ?? "—";
      const created = r.created_at ?? r.createdAt ?? r.reserved_at ?? null;

      return `
        <tr>
          <td>${escapeHtml(id)}</td>
          <td>${escapeHtml(userId)}</td>
          <td>${escapeHtml(bookId)}</td>
          <td>${escapeHtml(copyId)}</td>
          <td>${escapeHtml(status)}</td>
          <td>${escapeHtml(formatDate(created))}</td>
        </tr>
      `;
    })
    .join("");
}

async function loadReservations(email = "") {
  // Backend recomendado:
  // GET /reservations/        -> todas (admin)
  // GET /reservations/?email= -> filtrar por email
  const qs = email ? `?email=${encodeURIComponent(email)}` : "";
  return await apiGet(`/reservations/${qs}`);
}

async function loadAndRender(email = "") {
  try {
    setStatus("Cargando reservas…", "info");
    const reservations = await loadReservations(email);
    const rows = Array.isArray(reservations) ? reservations : [];
    renderTable(rows);
    setStatus(`${rows.length} reserva(s)`, "ok");
  } catch (e) {
    console.error(e);
    renderTable([]);
    setStatus("Error cargando reservas (¿endpoint /reservations/?email=... existe? ¿token/rol?).", "error");
  }
}

// ✅ Igual estilo que adminPrestamos/adminCatalogo:
export function renderAdminReservas() {
  const container = document.getElementById("contenido-admin");
  if (!container) return;

  renderUI(container);

  const searchInput = document.querySelector("#reservations-search-email");
  const refreshBtn = document.querySelector("#reservations-refresh");

  const doSearch = debounce(async () => {
    const email = normalizeEmail(searchInput.value);
    await loadAndRender(email);
  }, 300);

  searchInput.addEventListener("input", doSearch);
  refreshBtn.addEventListener("click", async () => {
    const email = normalizeEmail(searchInput.value);
    await loadAndRender(email);
  });

  loadAndRender("");
}
