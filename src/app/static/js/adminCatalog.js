// static/js/adminCatalog.js
import { apiGet, apiPost, apiPut, apiDelete } from "./api.js";

let adminBooksTbody = null;

// ======== PUNTO DE ENTRADA ========

export function renderAdminCatalogo() {
  const container = document.getElementById("contenido-admin");
  if (!container) return;

  container.innerHTML = `
    <h3>Catálogo – Bibliotecario</h3>

    <!-- FORMULARIO ALTA LIBRO -->
    <div class="card">
      <h4>Crear nuevo libro</h4>
      <form id="form-create-book">
        <div>
          <label>Título</label>
          <input type="text" id="book-title" required />
        </div>
        <div>
          <label>Autores</label>
          <input type="text" id="book-authors" required />
        </div>
        <div>
          <label>ISBN</label>
          <input type="text" id="book-isbn" />
        </div>
        <div>
          <label>Edición</label>
          <input type="text" id="book-edition" />
        </div>
        <div>
          <label>Materia</label>
          <input type="text" id="book-subject" />
        </div>
        <div>
          <label>Código de barras del primer ejemplar</label>
          <input type="text" id="book-barcode" required />
        </div>
        <div>
          <label>¿Es referencia?</label>
          <input type="checkbox" id="book-is-reference" />
        </div>
        <button type="submit">Crear libro</button>
      </form>
      <p id="create-book-msg" style="color: green;"></p>
    </div>

    <!-- BUSCADOR -->
    <div class="card">
      <h4>Buscar libros</h4>
      <input type="text" id="search-query" placeholder="Título, autor, ISBN..." />
      <button id="btn-search-books">Buscar</button>
      <button id="btn-search-clear">Limpiar</button>
    </div>

    <!-- RESULTADOS -->
    <div class="card">
      <h4>Resultados</h4>
      <table id="tabla-libros" border="1" cellpadding="4">
        <thead>
          <tr>
            <th>ID</th>
            <th>Título</th>
            <th>Autores</th>
            <th>ISBN</th>
            <th>Ejemplares</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <!-- filas aquí -->
        </tbody>
      </table>
    </div>
  `;

  // Referencias
  const form = document.getElementById("form-create-book");
  const btnSearch = document.getElementById("btn-search-books");
  const btnSearchClear = document.getElementById("btn-search-clear");
  adminBooksTbody = document.querySelector("#tabla-libros tbody");

  // Listeners
  form.addEventListener("submit", handleCreateBook);
  btnSearch.addEventListener("click", handleSearchBooks);
  btnSearchClear.addEventListener("click", handleSearchClear);

  // Delegado para acciones de la tabla
  adminBooksTbody.addEventListener("click", handleBooksTableClick);

  // Carga inicial
  loadAllBooksForAdmin();
}

// ======== CREAR LIBRO ========

async function handleCreateBook(event) {
  event.preventDefault();
  const msg = document.getElementById("create-book-msg");
  if (msg) {
    msg.textContent = "";
    msg.style.color = "green";
  }

  const title = document.getElementById("book-title").value.trim();
  const authors = document.getElementById("book-authors").value.trim();
  const isbn = document.getElementById("book-isbn").value.trim() || null;
  const edition = document.getElementById("book-edition").value.trim() || null;
  const subject = document.getElementById("book-subject").value.trim() || null;
  const barcode = document.getElementById("book-barcode").value.trim();
  const isRef = document.getElementById("book-is-reference").checked;

  if (!title || !authors || !barcode) {
    if (msg) {
      msg.style.color = "red";
      msg.textContent = "Título, autores y código de barras son obligatorios.";
    }
    return;
  }

  try {
    await apiPost("/books", {
      title,
      authors,
      isbn,
      edition,
      subject,
      access_level: "general",
      first_copy_barcode: barcode,
      first_copy_is_reference: isRef,
    });

    if (msg) {
      msg.style.color = "green";
      msg.textContent = "Libro creado correctamente.";
    }

    event.target.reset();
    await loadAllBooksForAdmin();
  } catch (err) {
    console.error("Error creando libro", err);
    if (msg) {
      msg.style.color = "red";
      msg.textContent = "Error creando libro. Revisa la consola.";
    }
  }
}

// ======== LISTADO / BÚSQUEDA ========

async function loadAllBooksForAdmin() {
  try {
    const books = await apiGet("/books");
    renderBooksTable(books);
  } catch (err) {
    console.error("Error cargando libros", err);
  }
}

async function handleSearchBooks() {
  const q = document.getElementById("search-query").value.trim();
  if (!q) {
    return loadAllBooksForAdmin();
  }

  try {
    const books = await apiGet(`/books/search?q=${encodeURIComponent(q)}`);
    renderBooksTable(books);
  } catch (err) {
    console.error("Error buscando libros", err);
  }
}

function handleSearchClear() {
  const input = document.getElementById("search-query");
  input.value = "";
  loadAllBooksForAdmin();
}

function renderBooksTable(books) {
  if (!adminBooksTbody) return;
  adminBooksTbody.innerHTML = "";

  if (!books || books.length === 0) {
    const tr = document.createElement("tr");
    const td = document.createElement("td");
    td.colSpan = 6;
    td.textContent = "No hay libros.";
    tr.appendChild(td);
    adminBooksTbody.appendChild(tr);
    return;
  }

  books.forEach((book) => {
    const tr = document.createElement("tr");
    const copiesCount = book.copies ? book.copies.length : 0;

    tr.innerHTML = `
      <td>${book.id}</td>
      <td>${escapeHtml(book.title)}</td>
      <td>${escapeHtml(book.authors)}</td>
      <td>${book.isbn ? escapeHtml(book.isbn) : ""}</td>
      <td>${copiesCount}</td>
      <td>
        <button class="btn-addcopy" data-id="${book.id}">Añadir copia</button>
        <button class="btn-delcopy" data-id="${book.id}">Eliminar copia</button>
        <button class="btn-prestar" data-id="${book.id}">Crear préstamo</button>
        <button class="btn-reservar" data-id="${book.id}">Crear reserva</button>
        <button class="btn-editar" data-id="${book.id}">Editar</button>
        <button class="btn-borrar" data-id="${book.id}">Eliminar libro</button>
      </td>
    `;

    adminBooksTbody.appendChild(tr);
  });
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

// ======== ACCIONES EN LA TABLA ========

async function handleBooksTableClick(event) {
  const btn = event.target.closest("button");
  if (!btn) return;

  const bookId = btn.getAttribute("data-id");
  if (!bookId) return;

  if (btn.classList.contains("btn-addcopy")) {
    await agregarCopia(bookId);
  } else if (btn.classList.contains("btn-delcopy")) {
    await eliminarCopia(bookId);
  } else if (btn.classList.contains("btn-prestar")) {
    await crearPrestamoParaUsuario(bookId);
  } else if (btn.classList.contains("btn-reservar")) {
    await crearReservaParaUsuario(bookId);
  } else if (btn.classList.contains("btn-editar")) {
    await editarLibroPrompt(bookId);
  } else if (btn.classList.contains("btn-borrar")) {
    await borrarLibro(bookId);
  }
}

// ======== AÑADIR COPIA (con último barcode en el mensaje) ========

async function agregarCopia(bookId) {
  try {
    // 1) Pedimos el libro para saber sus copias
    const book = await apiGet(`/books/${bookId}`);

    let lastBarcodeText = "ninguno (será la primera copia)";
    if (book.copies && book.copies.length > 0) {
      const lastCopy = book.copies[book.copies.length - 1];
      if (lastCopy && lastCopy.barcode) {
        lastBarcodeText = lastCopy.barcode;
      }
    }

    // 2) Prompt mostrando el último código usado
    const barcode = prompt(
      `Código de barras de la nueva copia.\n` +
      `Último código usado para este libro: ${lastBarcodeText}\n\n` +
      `Introduce el nuevo código:`
    );

    if (!barcode) return;

    const esReferencia = confirm("¿Esta copia será de referencia (no prestable)?");

    await apiPost(`/books/${bookId}/copies`, {
      barcode: barcode.trim(),
      is_reference: esReferencia,
    });

    alert("Copia añadida correctamente.");
    await loadAllBooksForAdmin();
  } catch (err) {
    console.error("Error añadiendo copia", err);
    alert("Error añadiendo copia. Revisa la consola.");
  }
}

// ======== ELIMINAR COPIA (lista de barcodes) ========

async function eliminarCopia(bookId) {
  try {
    const book = await apiGet(`/books/${bookId}`);

    if (!book.copies || book.copies.length === 0) {
      alert("Este libro no tiene copias para eliminar.");
      return;
    }

    // Construimos lista numerada de barcodes
    const lines = book.copies.map((copy, idx) => {
      const tipo = copy.is_reference ? " (referencia)" : "";
      return `${idx + 1}. ${copy.barcode}${tipo}`;
    });

    const msg =
      "Selecciona la copia que quieres eliminar:\n\n" +
      lines.join("\n") +
      "\n\nIntroduce el número de la copia a eliminar:";

    const input = prompt(msg);
    if (!input) return;

    const index = parseInt(input, 10);
    if (Number.isNaN(index) || index < 1 || index > book.copies.length) {
      alert("Número no válido.");
      return;
    }

    const selectedCopy = book.copies[index - 1];

    const seguro = confirm(
      `Vas a eliminar la copia con código de barras: ${selectedCopy.barcode}\n\n¿Estás seguro?`
    );
    if (!seguro) return;

    // Llamamos al endpoint de borrado de copia
    await apiDelete(`/books/${bookId}/copies/${selectedCopy.id}`);

    alert("Copia eliminada correctamente.");
    await loadAllBooksForAdmin();
  } catch (err) {
    console.error("Error eliminando copia", err);
    alert("Error eliminando copia. Revisa la consola.");
  }
}

// ======== CREAR PRÉSTAMO PARA USUARIO (POR EMAIL) ========

async function crearPrestamoParaUsuario(bookId) {
  const email = prompt("Email del usuario para el que quieres crear el préstamo:");
  if (!email) return;

  const emailTrimmed = email.trim();
  if (!emailTrimmed) {
    alert("Email no válido.");
    return;
  }

  try {
    // 1) Buscar usuario por email
    const user = await apiGet(`/users/by-email/${encodeURIComponent(emailTrimmed)}`);

    if (!user || !user.id) {
      alert("No se encontró un usuario con ese email.");
      return;
    }

    // 2) Obtener copias del libro
    const book = await apiGet(`/books/${bookId}`);

    if (!book.copies || book.copies.length === 0) {
      alert("Este libro no tiene ejemplares para prestar.");
      return;
    }

    // (Opcional) filtrar solo copias disponibles si en el JSON te llega el status
    const availableCopies = book.copies.filter(
      (c) => c.status === "available" || c.status === "AVAILABLE"
    );
    const copiesToShow = availableCopies.length > 0 ? availableCopies : book.copies;
    const usingAvailableOnly = availableCopies.length > 0;

    // 3) Construir lista numerada de copias
    const lines = copiesToShow.map((copy, idx) => {
      const refText = copy.is_reference ? " (referencia)" : "";
      const statusText = copy.status ? ` [${copy.status}]` : "";
      return `${idx + 1}. ${copy.barcode}${refText}${statusText}`;
    });

    const msg =
      (usingAvailableOnly
        ? "Selecciona el ejemplar (copia) que quieres prestar (solo disponibles):\n\n"
        : "No se ha podido determinar disponibilidad, elige un ejemplar:\n\n") +
      lines.join("\n") +
      "\n\nIntroduce el número de la copia a prestar:";

    const input = prompt(msg);
    if (!input) return;

    const index = parseInt(input, 10);
    if (Number.isNaN(index) || index < 1 || index > copiesToShow.length) {
      alert("Número no válido.");
      return;
    }

    const selectedCopy = copiesToShow[index - 1];

    // 4) Confirmación
    const seguro = confirm(
      `Vas a crear un préstamo del ejemplar con código de barras: ${selectedCopy.barcode}\n` +
      `para el usuario: ${user.full_name || user.email}\n\n¿Estás seguro?`
    );
    if (!seguro) return;

    // 5) Crear préstamo por copy_id
    await apiPost("/loans", {
      user_id: user.id,
      copy_id: selectedCopy.id,
    });

    alert("Préstamo creado correctamente.");
  } catch (err) {
    console.error("Error creando préstamo", err);
    alert("Error creando préstamo. Revisa la consola.");
  }
}

// ======== CREAR RESERVA PARA USUARIO (POR EMAIL) ========
// Requiere backend: POST /reservations/ con body { user_id, book_id }
async function crearReservaParaUsuario(bookId) {
  const email = prompt("Email del usuario para el que quieres crear la reserva:");
  if (!email) return;

  const emailTrimmed = email.trim();
  if (!emailTrimmed) {
    alert("Email no válido.");
    return;
  }

  try {
    // 1) Buscar usuario por email
    const user = await apiGet(`/users/by-email/${encodeURIComponent(emailTrimmed)}`);
    if (!user || !user.id) {
      alert("No se encontró un usuario con ese email.");
      return;
    }

    // 2) Confirmación
    const seguro = confirm(
      `Vas a crear una RESERVA del libro ${bookId}\n` +
      `para el usuario: ${user.full_name || user.email}\n\n¿Estás seguro?`
    );
    if (!seguro) return;

    // 3) Crear reserva por book_id (el backend debe validar si procede)
    await apiPost("/reservations/", {
      user_id: user.id,
      book_id: Number(bookId),
    });

    alert("Reserva creada correctamente.");
  } catch (err) {
    console.error("Error creando reserva", err);

    // FastAPI suele devolver JSON en err.message; mostramos algo útil
    const msg = String(err?.message || "");
    if (msg.includes("Hay copias disponibles")) {
      alert("No se puede reservar: hay copias disponibles para préstamo.");
    } else if (msg.includes("no admite reservas")) {
      alert("No se puede reservar: material de referencia.");
    } else if (msg.includes("Ya tienes una reserva activa")) {
      alert("El usuario ya tiene una reserva activa para este título.");
    } else {
      alert("Error creando reserva. Revisa la consola.");
    }
  }
}


// ======== EDITAR LIBRO ========

async function editarLibroPrompt(bookId) {
  try {
    const book = await apiGet(`/books/${bookId}`);

    const nuevoTitulo = prompt("Nuevo título:", book.title);
    if (nuevoTitulo === null) return;

    const nuevosAutores = prompt("Nuevos autores:", book.authors);
    if (nuevosAutores === null) return;

    await apiPut(`/books/${bookId}`, {
      title: nuevoTitulo,
      authors: nuevosAutores,
    });

    alert("Libro actualizado.");
    await loadAllBooksForAdmin();
  } catch (err) {
    console.error("Error editando libro", err);
    alert("Error editando libro. Revisa la consola.");
  }
}

// ======== BORRAR LIBRO ========

async function borrarLibro(bookId) {
  const seguro = confirm(`¿Seguro que quieres eliminar el libro ${bookId}?`);
  if (!seguro) return;

  try {
    await apiDelete(`/books/${bookId}`);
    alert("Libro eliminado.");
    await loadAllBooksForAdmin();
  } catch (err) {
    console.error("Error borrando libro", err);
    alert("Error borrando libro. Revisa la consola.");
  }
}
