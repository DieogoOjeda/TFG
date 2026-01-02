// static/js/adminSanciones.js
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
        <h2>Sanciones</h2>
        <div class="panel__controls">
          <input id="sanctions-search-email" class="input" type="email"
            placeholder="Buscar por email (ej: user@alumnos.upm.es)" />
          <button id="sanctions-refresh" class="btn">Recargar</button>
        </div>
      </div>

      <div id="sanctions-status" class="status" style="margin: 10px 0;"></div>

      <div class="table-wrap">
        <table class="table" id="sanctions-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Usuario</th>
              <th>Email</th>
              <th>Book ID</th>
              <th>Copy ID</th>
              <th>Días</th>
              <th>Creada</th>
            </tr>
          </thead>
          <tbody id="sanctions-tbody">
            <tr><td colspan="6">Cargando…</td></tr>
          </tbody>
        </table>
      </div>
    </section>
  `;
}

function setStatus(msg, type = "info") {
  const el = document.querySelector("#sanctions-status");
  if (!el) return;
  el.textContent = msg || "";
  el.dataset.type = type;
}

function renderTable(rows) {
  const tbody = document.querySelector("#sanctions-tbody");
  if (!tbody) return;

  if (!rows || rows.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6">No hay sanciones.</td></tr>`;
    return;
  }

  tbody.innerHTML = rows
    .map((s) => {
      return `
        <tr>
          <td>${escapeHtml(s.id ?? "—")}</td>
          <td>${escapeHtml(s.user_name)}</td>
          <td>${escapeHtml(s.user_email)}</td>
          <td>${escapeHtml(s.book_id ?? "—")}</td>
          <td>${escapeHtml(s.copy_id ?? "—")}</td>
          <td>${escapeHtml(s.days ?? "—")}</td>
          <td>${escapeHtml(formatDate(s.created_at))}</td>
        </tr>
      `;
    })
    .join("");
}

async function loadSanctions(email = "") {
  const qs = email ? `?email=${encodeURIComponent(email)}` : "";
  // tu router es @router.get("/") con prefix /sanctions -> /sanctions/?email=...
  return await apiGet(`/sanctions/${qs}`);
}

async function loadAndRender(email = "") {
  try {
    setStatus("Cargando sanciones…", "info");
    const sanctions = await loadSanctions(email);
    const rows = Array.isArray(sanctions) ? sanctions : [];
    renderTable(rows);
    setStatus(`${rows.length} sanción(es)`, "ok");
  } catch (e) {
    console.error(e);
    renderTable([]);
    setStatus("Error cargando sanciones (¿token/rol LIBRARIAN?).", "error");
  }
}

// ✅ Igual estilo que adminPrestamos/adminCatalogo:
export function renderAdminSanciones() {
  const container = document.getElementById("contenido-admin");
  if (!container) return;

  renderUI(container);

  const searchInput = document.querySelector("#sanctions-search-email");
  const refreshBtn = document.querySelector("#sanctions-refresh");

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
