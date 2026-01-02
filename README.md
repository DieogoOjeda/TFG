# 📚 Biblioteca – API Backend

API REST para la gestión de una biblioteca universitaria desarrollada con **FastAPI**, **SQLAlchemy** y **SQLite**, con **testeo automatizado completo** mediante **pytest**.

El sistema gestiona:
- Usuarios (estudiantes y bibliotecarios)
- Libros y copias
- Préstamos
- Reservas
- Sanciones
- Autenticación JWT con control de roles

---

## 🧱 Arquitectura del proyecto

biblioteca/
└── src/
├── app/
│ ├── main.py
│ ├── core/
│ ├── models/
│ ├── schemas/
│ ├── routers/
│ ├── services/
│ └── utils/
├── tests/
│ ├── conftest.py
│ ├── test_auth.py
│ ├── test_books.py
│ ├── test_loans.py
│ ├── test_reservations.py
│ ├── test_sanctions.py
│ └── test_users.py
└── pytest.ini

---

## 🚀 Puesta en marcha
### 1️⃣ Crear y activar entorno virtual
#### Windows
```powershell
python -m venv venv
.\venv\Scripts\activate
#### Linux/MacOS
python3 -m venv venv
source venv/bin/activate

### 2️⃣ Instalar dependencias
pip install -r requirements.txt 
Si no funciona requirements intalar al menos: pip install fastapi uvicorn sqlalchemy pytest pytest-cov httpx

### 3️⃣ Ejecutar API
desde src/:
uvicorn app.main:app --reload

Swagger UI: 👉 http://127.0.0.1:8000/docs
OpenAPI JSON: 👉 http://127.0.0.1:8000/openapi.json

🔮 Trabajo futuro (roadmap)


 Notificaciones automáticas de reservas

 Documentación OpenAPI ampliada





