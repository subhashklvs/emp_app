-- ================================================
--  Employee Management System — SQLite Schema
--  Auto-created on first run via init_db()
--  Manual: sqlite3 company.db < schema.sql
-- ================================================

CREATE TABLE IF NOT EXISTS users (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS employee (
    eid     INTEGER PRIMARY KEY AUTOINCREMENT,
    ename   TEXT NOT NULL,
    edept   TEXT NOT NULL,
    esalary REAL NOT NULL,
    ephone  TEXT NOT NULL
);
