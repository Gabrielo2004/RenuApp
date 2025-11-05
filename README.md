# Renü — App de sustentabilidad (Kivy + SQLite)

Proyecto móvil que promueve hábitos de reciclaje y sustentabilidad. Incluye mapa de puntos de reciclaje, consejos eco, y desafíos con progreso.

## Integrantes y roles
- Gabriel Ramírez
  - Líder/Coordinador
  - Analista de datos / modelador ER
  - Implementador Kivy / persistencia
  - Redactor de documentación / QA
  - Presentador

## Alcance y datos relevantes
- Pantallas principales: Inicio, Mapa, Consejos, Desafíos, Login/Registro.
- Entidades clave: `recycling_points`, `materials`, `point_materials`, `tips`, `challenges`, `challenge_progress`, `users`, `settings`.
- Volumen esperado (MVP):
  - Puntos de reciclaje: 20–200
  - Materiales: 3–20
  - Consejos: 5–100
  - Desafíos: 1–20
- Operaciones principales (CRUD):
  - Lectura: listados de puntos, materiales, consejos y desafíos; progreso del desafío
  - Escritura: progreso de desafío; seed inicial; futuros favoritos

## Persistencia elegida
- SQLite (valorada para apps y volúmenes mayores).
  - Archivo: `app/renu.db`
  - Inicialización en: `app/services/storage.py`
  - Esquema exportado en: `data/schema.sql`
  - Autenticación: tabla `users` con hash PBKDF2 y sesión persistida en `settings.current_user_id`.

### Seed y datos iniciales
- Se ejecuta en `app/services/seed.py` al inicio de la app.
- Inserta SÓLO si las tablas están vacías ("if empty").
  - `materials`: valores base.
  - `tips`: 5 consejos iniciales; luego sincroniza imágenes desde `assets/images` y marca destacados.
  - `challenges`: crea el desafío semanal (y algunos diarios si hay pocos).
  - `recycling_points` + `point_materials`: crea 3 puntos ejemplo y vincula materiales si no hay datos.
- Por eso NO se elimina el seed: sirve para bootstrap y es idempotente (no duplica registros existentes).

## Diagramas (ERD y modelo relacional)
- Editable: `diagrams/ERD Gabriel Ramirez Renü.drawio` (principal) y `diagrams/erd.drawio` (alternativo)
- Modelo relacional: `diagrams/relational_model.md` (alineado al ERD principal)

## Cómo ejecutar (desarrollo)
1. Requisitos: Python 3.10+, Kivy/KivyMD.
2. Ejecutar:
   ```bash
   python -m pip install kivy kivymd
   python -m pip install pillow
   python main.py
   ```
3. La primera ejecución crea e inicializa `app/renu.db` con datos de prueba (tips, materiales, desafíos).

## Ejemplo de acceso a persistencia (sqlite3)
El proyecto usa un servicio delgado (`StorageService`) que envuelve `sqlite3` y activa FKs:
```python
from app.services.storage import StorageService

storage = StorageService()
storage.initialize_database()
rows = storage.fetchall("SELECT id, title FROM tips WHERE is_featured = 1 LIMIT ?", (5,))
```
Repositorios de ejemplo:
- `app/services/repositories/tips.py`
- `app/services/repositories/challenges.py`
- `app/services/repositories/points.py`
- `app/services/repositories/users.py`

## Estructura relevante
- `app/main.py`: arranque de la app y navegación
- `app/services/storage.py`: conexión SQLite y creación de tablas
- `app/services/seed.py`: población de datos y sincronización de imágenes
- `assets/kv/*.kv`: layouts de pantallas
- `diagrams/*`: ERD y documentación de datos
- `data/schema.sql`: script SQL del esquema

## Notas de diseño
- Campos booleanos como `is_featured`, `is_weekly` e `is_open` se representan como INTEGER (0/1) por compatibilidad con SQLite.
