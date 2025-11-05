# Plan de implementación — Renü

## Mapping funcionalidad ↔ tablas/archivos

| Funcionalidad/Pantalla | Tablas/Archivos | Descripción |
|---|---|---|
| Mapa de reciclaje | `recycling_points`, `materials`, `point_materials` | Listado de puntos, materiales aceptados y relación M:N. |
| Consejos eco | `tips` | Listado/destacados, imágenes y metadatos (categoría, dificultad, impacto). |
| Desafío semanal | `challenges`, `challenge_progress` | Obtiene desafío semanal y actualiza progreso. |
| Autenticación | `users`, `settings` | Login/registro y sesión persistente. |
| Configuración | `settings` | KV simple para flags locales. |
| Seed inicial | `data/schema.sql`, `app/services/seed.py` | Crea datos base y sincroniza imágenes. |

## Tareas (stories/tickets)

1. Definir ERD inicial (hecho)
   - Resultado: `diagrams/erd.drawio`, `diagrams/erd.svg`.
   - Responsable: Gabriel
   - Estimado: S

2. Documentar modelo relacional (hecho)
   - Resultado: `diagrams/relational_model.md`.
   - Responsable: Gabriel
   - Estimado: S

3. Exportar esquema SQL (hecho)
   - Resultado: `data/schema.sql`.
   - Responsable: Gabriel
   - Estimado: XS

4. Repositorios de lectura (tips/challenges) (existente)
   - Archivos: `app/services/repositories/*.py`
   - Aceptación: retorna datos coherentes con DB

5. Progreso de desafíos (existente)
   - Método: `ChallengesRepository.increment_progress`
   - Aceptación: incrementa y persiste `challenge_progress`

6. Autenticación real (hecho)
   - Tabla `users` + sesión en `settings.current_user_id`
   - Aceptación: login persiste sesión; logout la limpia

7. (Opcional futuro) Favoritos por usuario
   - Diseñar `favorite_points` / `favorite_tips` con `user_id`
   - Aceptación: crear/eliminar para el usuario autenticado

8. Índices de rendimiento (opcional según volumen)
   - `tips(is_featured)`, `challenges(is_weekly)`
   - Aceptación: tiempos de consulta mejoran en listados

## Criterios de aceptación (MVP)
- Al iniciar la app:
  - Se crea `app/renu.db` si no existe (con FKs activas).
  - `seed.py` inserta materiales, tips e inicializa desafío semanal.
- Pantalla Consejos:
  - Muestra hasta 5 destacados (`is_featured = 1`) con imagen si existe.
- Pantalla Desafíos:
  - Muestra desafío semanal y permite incrementar el progreso.
- Pantalla Mapa:
  - Puede listar puntos y materiales aceptados.

## Riesgos / decisiones
- `favorites` polimórfico: simplicidad vs. integridad referencial; validado en capa de aplicación.
- Booleanos como INTEGER por compatibilidad con SQLite.
- Futuro: normalizar categorías de tips si crece el uso.
