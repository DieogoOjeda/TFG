// static/js/userCatalog.js
import { apiGet } from "./api.js";

export async function renderUserCatalogo() {
  const container = document.getElementById("contenido-usuario");
  if (!container) return;

  container.innerHTML = `
    <h3>Catálogo</h3>
    <div class="card">
      <p>Cargando libros...</p>
    </div>
  `;

  try {
    const books = await apiGet("/books");

    if (!books.length) {
      container.innerHTML = `
        <h3>Catálogo</h3>
        <div class="card"><p>No hay libros disponibles.</p></div>
      `;
      return;
    }

    const rows = books
      .map(
        (b) => `
        <tr>
          <td>${b.id}</td>
          <td>${escapeHtml(b.title)}</td>
          <td>${escapeHtml(b.authors)}</td>
          <td>${b.isbn ? escapeHtml(b.isbn) : ""}</td>
          <td>${b.copies ? b.copies.length : 0}</td>
        </tr>
      `
      )
      .join("");

    container.innerHTML = `
      <h3>Catálogo</h3>
      <div class="card">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Título</th>
              <th>Autores</th>
              <th>ISBN</th>
              <th>Ejemplares</th>
            </tr>
          </thead>
          <tbody>
            ${rows}
          </tbody>
        </table>
      </div>
    `;
  } catch (err) {
    console.error("Error cargando catálogo de usuario", err);
    container.innerHTML = `
      <h3>Catálogo</h3>
      <div class="card"><p>Error cargando catálogo. Revisa la consola.</p></div>
    `;
  }
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}
