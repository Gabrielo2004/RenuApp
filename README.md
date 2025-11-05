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

## Guía de instalación y ejecución (paso a paso)

### 0) Requisitos
- Python 3.10 o 3.11 (recomendado). Verifica con:
  ```bash
  python --version
  ```
- Git opcional (para resolver dependencias desde GitHub si lo necesitas).

### 1) Crear y activar un entorno virtual
- Windows (PowerShell):
  ```powershell
  cd "C:\Users\Gabrielo\Desktop\Proyectos\RenuApp"
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
  Si PowerShell bloquea el script, ejecuta una vez y vuelve a activar:
  ```powershell
  Set-ExecutionPolicy -Scope CurrentUser RemoteSigned -Force
  .\venv\Scripts\Activate.ps1
  ```

- Windows (CMD):
  ```cmd
  python -m venv venv
  .\venv\Scripts\activate.bat
  ```

- macOS / Linux:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 2) Actualizar herramientas de instalación
```bash
python -m pip install --upgrade pip setuptools wheel
```

### 3) Instalar dependencias
- Kivy (base) y utilidades:
  ```bash
  pip install "kivy[base]" pillow
  ```

- KivyMD (desde la rama principal, requerido por esta app):
  ```bash
  pip install https://github.com/kivymd/KivyMD/archive/master.zip
  ```

### 4) Ejecutar el proyecto
```bash
python main.py
```

Al primer arranque se crea e inicializa la base `app/renu.db` con datos de ejemplo (tips, materiales, desafíos), y se sincronizan imágenes desde `assets/images`.

### 5) Conectarse a la base de datos (SQLite) con Database Client
1. Asegúrate de haber corrido la app una vez para que se genere `app/renu.db`.
2. En VS Code instala estas extensiones:
   - "Database Client" (autor: cweijan)
   - "SQLite" (para explorar archivos SQLite)
3. Abre la vista "Database Client" en la barra lateral. Crea una nueva conexión:
   - Tipo: SQLite
   - File / Archivo: selecciona `app/renu.db` dentro del proyecto
   - Test / Connect
4. Explora tablas y ejecuta consultas de verificación, por ejemplo:
   ```sql
   SELECT name FROM sqlite_master WHERE type = 'table';
   SELECT COUNT(*) AS tips FROM tips;
   SELECT COUNT(*) AS challenges FROM challenges;
   ```

### 6) Comandos útiles
- Desactivar el entorno virtual:
  ```bash
  deactivate
  ```
- Actualizar KivyMD (si lo necesitas en el futuro):
  ```bash
  pip install --upgrade https://github.com/kivymd/KivyMD/archive/master.zip
  ```

### 7) Solución de problemas
- No se activa el entorno en PowerShell:
  ```powershell
  Set-ExecutionPolicy -Scope CurrentUser RemoteSigned -Force
  .\venv\Scripts\Activate.ps1
  ```
- Error al instalar Kivy en Windows:
  - Verifica Python 3.10/3.11.
  - Asegúrate de haber actualizado `pip`, `setuptools` y `wheel`.
  - Cierra y reabre la terminal tras instalar Python o agregarlo al PATH.
- La app no crea la base de datos:
  - Ejecuta `python main.py` desde la raíz del proyecto (donde está `main.py`).
  - Confirma permisos de escritura en la carpeta `app/`.

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

## IA Utilizadas
- Cursor IDE para construcción de codigo y desarrollo más rapido.
- ChatGPT para consultas

