PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    email TEXT,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS recycling_points (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    address TEXT,
    lat REAL NOT NULL,
    lon REAL NOT NULL,
    hours TEXT,
    is_open INTEGER DEFAULT 1,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS materials (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS point_materials (
    point_id INTEGER NOT NULL,
    material_id INTEGER NOT NULL,
    PRIMARY KEY (point_id, material_id),
    FOREIGN KEY (point_id) REFERENCES recycling_points(id) ON DELETE CASCADE,
    FOREIGN KEY (material_id) REFERENCES materials(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tips (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    body TEXT,
    image TEXT,
    category TEXT,
    difficulty TEXT,
    impact TEXT,
    is_featured INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS challenges (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    period TEXT NOT NULL,          -- 'daily'|'weekly'|'once'
    target INTEGER NOT NULL,
    unit TEXT NOT NULL,            -- e.g., 'items'
    points_reward INTEGER DEFAULT 0,
    is_weekly INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS challenge_progress (
    challenge_id INTEGER PRIMARY KEY,
    progress INTEGER NOT NULL DEFAULT 0,
    last_updated TEXT,
    FOREIGN KEY (challenge_id) REFERENCES challenges(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
);
