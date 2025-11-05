## Modelo Relacional — Renü (SQLite)

Alineado con el ERD aportado en `diagrams/ERD Gabriel Ramirez Renü.drawio` y con el esquema de `app/services/storage.py`/`data/schema.sql`.

### Tabla: `recycling_points`
- id INTEGER PRIMARY KEY
- name TEXT NOT NULL
- address TEXT
- lat REAL NOT NULL
- lon REAL NOT NULL
- hours TEXT
- is_open INTEGER DEFAULT 1
- notes TEXT

Cardinalidad:
- `recycling_points` 1 — N `point_materials` (cada punto acepta varios materiales)

Índices:
- PK implícito en `id`.

---

### Tabla: `materials`
- id INTEGER PRIMARY KEY
- name TEXT NOT NULL UNIQUE

Cardinalidad:
- `materials` 1 — N `point_materials`

Índices:
- PK implícito en `id`.
- UNIQUE en `name`.

---

### Tabla: `point_materials` (puente M:N)
- point_id INTEGER NOT NULL REFERENCES `recycling_points`(id) ON DELETE CASCADE
- material_id INTEGER NOT NULL REFERENCES `materials`(id) ON DELETE CASCADE
- PRIMARY KEY (point_id, material_id)

Cardinalidad:
- `recycling_points` 1 — N `point_materials` N — 1 `materials` (resuelve M:N)

Índices:
- PK compuesta (point_id, material_id) — index implícito.

---

### Tabla: `tips`
- id INTEGER PRIMARY KEY
- title TEXT NOT NULL
- body TEXT
- image TEXT
- category TEXT
- difficulty TEXT
- impact TEXT
- is_featured INTEGER DEFAULT 0

Cardinalidad:
- Independiente (usada para carrusel/destacados).

Índices:
- PK implícito en `id`.
- (Opcional) `CREATE INDEX IF NOT EXISTS tips_is_featured_idx ON tips(is_featured);`

---

### Tabla: `challenges`
- id INTEGER PRIMARY KEY
- title TEXT NOT NULL
- description TEXT
- period TEXT NOT NULL   -- ('daily'|'weekly'|'once')
- target INTEGER NOT NULL
- unit TEXT NOT NULL
- points_reward INTEGER DEFAULT 0
- is_weekly INTEGER DEFAULT 0

Cardinalidad:
- `challenges` 1 — 1 `challenge_progress`

Índices:
- PK implícito en `id`.
- (Opcional) `CREATE INDEX IF NOT EXISTS challenges_weekly_idx ON challenges(is_weekly);`

---

### Tabla: `challenge_progress`
- challenge_id INTEGER PRIMARY KEY REFERENCES `challenges`(id) ON DELETE CASCADE
- progress INTEGER NOT NULL DEFAULT 0
- last_updated TEXT

Cardinalidad:
- 1 — 1 con `challenges` (misma PK como FK).

Índices:
- PK implícito en `challenge_id`.

---

### Tablas de soporte (implementación)
Estas tablas pueden no estar dibujadas en el ERD, pero existen en la implementación para cubrir autenticación y KV local:

#### Tabla: `users`
- id INTEGER PRIMARY KEY
- username TEXT NOT NULL UNIQUE
- email TEXT
- password_hash TEXT NOT NULL
- salt TEXT NOT NULL
- created_at TEXT DEFAULT CURRENT_TIMESTAMP

Uso: autenticación (login/registro) y sesión persistida.

#### Tabla: `settings`
- key TEXT PRIMARY KEY
- value TEXT

Uso: par clave-valor; aquí se persiste `current_user_id` para mantener sesión iniciada.

---

### Observaciones de diseño
- Se usa SQLite con `PRAGMA foreign_keys = ON`.
- Booleanos representados como INTEGER (0/1) por compatibilidad SQLite.
- M:N resuelta con `point_materials` (PK compuesta + FKs con ON DELETE CASCADE).
- `users`/`settings` se consideran soporte de implementación (no necesariamente reflejados en el ERD conceptual).
