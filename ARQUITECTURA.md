# 🏗️ Arquitectura del Proyecto Renü

## 📁 Estructura Visual de Directorios

```
RenuApp/
│
├── 📄 main.py                          # Punto de entrada de la aplicación
│
├── 📁 app/                             # Módulo principal de la aplicación
│   ├── __init__.py
│   ├── main.py                         # Clase RenuApp (MDApp) - Navegación y configuración
│   ├── theme.py                        # Configuración de tema y estilos KivyMD
│   ├── renu.db                         # Base de datos SQLite (generada automáticamente)
│   │
│   ├── 📁 screens/                     # Pantallas de la aplicación (Vista)
│   │   ├── home.py                     # Pantalla de inicio (carrusel, desafío semanal)
│   │   ├── map.py                      # Pantalla de mapa de puntos de reciclaje
│   │   ├── tips.py                     # Pantalla de consejos ecológicos
│   │   ├── challenges.py               # Pantalla de desafíos y progreso
│   │   └── auth.py                     # Pantallas de login y registro
│   │
│   └── 📁 services/                    # Lógica de negocio y acceso a datos
│       ├── __init__.py
│       ├── storage.py                  # Servicio de base de datos SQLite (StorageService)
│       ├── seed.py                     # Población inicial de datos (seed_if_empty)
│       │
│       └── 📁 repositories/            # Patrón Repository - Acceso a datos por entidad
│           ├── __init__.py
│           ├── users.py                # UserRepository - Autenticación y usuarios
│           ├── challenges.py           # ChallengesRepository - Desafíos y progreso
│           ├── tips.py                 # TipsRepository - Consejos ecológicos
│           └── points.py               # PointsRepository - Puntos de reciclaje
│
├── 📁 assets/                          # Recursos estáticos
│   ├── 📁 images/                      # Imágenes de la aplicación
│   │   ├── Renü logo.png
│   │   ├── ecologico1.jpg
│   │   ├── ecologico2.jpg
│   │   ├── reciclar.jpg
│   │   ├── reciclar1.jpg
│   │   └── reciclar2.jpg
│   │
│   └── 📁 kv/                          # Archivos de diseño Kivy (UI)
│       ├── styles.kv                   # Estilos compartidos
│       ├── home.kv                     # Layout de pantalla de inicio
│       ├── map.kv                      # Layout de pantalla de mapa
│       ├── tips.kv                     # Layout de pantalla de consejos
│       ├── challenges.kv               # Layout de pantalla de desafíos
│       └── auth.kv                     # Layout de login/registro
│
├── 📁 data/                            # Datos y esquemas
│   └── schema.sql                      # Esquema SQL de la base de datos
│
├── 📁 diagrams/                        # Diagramas de diseño
│   ├── ERD Gabriel Ramirez Renü.drawio # Diagrama entidad-relación (Draw.io)
│   ├── ERD Renü.png                    # Imagen del ERD
│   └── relational_model.md             # Modelo relacional en texto
│
├── 📁 tests/                           # Pruebas unitarias
│   ├── conftest.py                     # Configuración de pytest
│   ├── test_auth_screen.py             # Tests de autenticación
│   ├── test_challenges.py              # Tests de desafíos
│   ├── test_points.py                  # Tests de puntos de reciclaje
│   └── test_users.py                   # Tests de usuarios
│
├── 📁 cache/                           # Cache de Kivy (generado automáticamente)
│
├── 📁 venv/                            # Entorno virtual de Python
│
└── 📄 README.md                        # Documentación principal del proyecto
```

## 🔄 Flujo de Arquitectura

### **Capa de Presentación (UI)**
```
┌─────────────────────────────────────────┐
│         KivyMD Screens                  │
│  (home, map, tips, challenges, auth)    │
│                                         │
│  ┌──────────┐  ┌──────────┐            │
│  │  .py     │  │  .kv     │            │
│  │ (lógica) │  │ (layout) │            │
│  └──────────┘  └──────────┘            │
└─────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│         RenuApp (main.py)                │
│  - ScreenManager                         │
│  - Navegación                            │
│  - Repositorios (inyectados)             │
└─────────────────────────────────────────┘
```

### **Capa de Lógica de Negocio**
```
┌─────────────────────────────────────────┐
│         Repositories                     │
│  ┌──────────────┐  ┌──────────────┐    │
│  │ UsersRepo    │  │ ChallengesRepo│    │
│  │ TipsRepo     │  │ PointsRepo    │    │
│  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│         StorageService                   │
│  - Conexión SQLite                       │
│  - Ejecución de queries                  │
│  - Transacciones                         │
└─────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│         SQLite Database                  │
│  (app/renu.db)                           │
│  - users, challenges, tips,              │
│    recycling_points, materials, etc.     │
└─────────────────────────────────────────┘
```

## 📊 Patrones Arquitectónicos Implementados

### 1. **MVC (Model-View-Controller)**
- **Model**: Repositories + StorageService + SQLite
- **View**: Screens (.py) + Layouts (.kv)
- **Controller**: RenuApp (main.py) coordina la navegación

### 2. **Repository Pattern**
- Cada entidad tiene su repositorio:
  - `UsersRepository`: Gestión de usuarios y autenticación
  - `ChallengesRepository`: Desafíos y progreso
  - `TipsRepository`: Consejos ecológicos
  - `PointsRepository`: Puntos de reciclaje

### 3. **Service Layer**
- `StorageService`: Abstracción de acceso a datos
- `seed.py`: Inicialización de datos

## 🔗 Dependencias entre Módulos

```
main.py
  └──> app/main.py (RenuApp)
        ├──> app/theme.py
        ├──> app/services/storage.py
        ├──> app/services/seed.py
        ├──> app/services/repositories/*
        └──> app/screens/*
              ├──> app/services/repositories/* (inyectados)
              └──> assets/kv/* (layouts)
```

## 📦 Responsabilidades por Capa

### **app/main.py (RenuApp)**
- ✅ Inicialización de la aplicación
- ✅ Configuración de tema
- ✅ Gestión de navegación (ScreenManager)
- ✅ Inyección de dependencias (repositorios)
- ✅ Control de sesión de usuario
- ✅ Gestión de barra de navegación inferior

### **app/screens/** (Vista)
- ✅ Lógica de presentación
- ✅ Interacción con el usuario
- ✅ Actualización de UI
- ✅ Delegación de operaciones a repositorios

### **app/services/repositories/** (Modelo)
- ✅ Acceso a datos por entidad
- ✅ Consultas SQL específicas
- ✅ Transformación de datos
- ✅ Validaciones de negocio

### **app/services/storage.py** (Acceso a Datos)
- ✅ Conexión a SQLite
- ✅ Ejecución de queries
- ✅ Gestión de transacciones
- ✅ Inicialización del esquema

### **assets/kv/** (Layout)
- ✅ Definición de estructura visual
- ✅ Estilos y temas
- ✅ Binding de propiedades

## 🗄️ Base de Datos

### **Tablas Principales**
- `users`: Usuarios y autenticación (PBKDF2)
- `challenges`: Desafíos (diarios, semanales, únicos)
- `challenge_progress`: Progreso de usuarios en desafíos
- `tips`: Consejos ecológicos
- `recycling_points`: Puntos de reciclaje
- `materials`: Materiales reciclables
- `point_materials`: Relación muchos-a-muchos (puntos ↔ materiales)
- `settings`: Configuración y sesión actual

### **Archivo de Esquema**
- `data/schema.sql`: Definición completa del esquema

## 🎨 Recursos y Assets

### **Imágenes**
- Logo de la aplicación
- Imágenes para el carrusel de inicio
- Sincronización automática desde `assets/images/`

### **Layouts Kivy**
- Separación de lógica (.py) y presentación (.kv)
- Estilos compartidos en `styles.kv`
- Layouts específicos por pantalla

## 🧪 Testing

### **Estructura de Tests**
- `tests/conftest.py`: Fixtures compartidos
- Tests por módulo: `test_*.py`
- Configuración en `pytest.ini`

## 🚀 Flujo de Inicialización

```
1. main.py ejecuta RenuApp().run()
   │
2. RenuApp.build()
   │
   ├──> setup_theme()
   ├──> Builder.load_file() (carga .kv)
   ├──> StorageService.initialize_database()
   ├──> seed_if_empty() (población inicial)
   ├──> sync_tip_images() (sincronización)
   ├──> Creación de repositorios
   ├──> Creación de screens
   └──> Verificación de sesión → login o home
```

## 📝 Notas de Diseño

- **Separación de responsabilidades**: Cada capa tiene una responsabilidad clara
- **Inyección de dependencias**: Repositorios inyectados en la app y screens
- **Idempotencia**: Seed solo se ejecuta si las tablas están vacías
- **Persistencia local**: SQLite para almacenamiento offline
- **UI declarativa**: Kivy KV para layouts, Python para lógica

