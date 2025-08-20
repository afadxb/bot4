-- SQLite schema for core tables
CREATE TABLE IF NOT EXISTS signal_log (
    id INTEGER PRIMARY KEY,
    symbol TEXT NOT NULL,
    score REAL NOT NULL,
    timestamp DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS position (
    id INTEGER PRIMARY KEY,
    symbol TEXT NOT NULL,
    qty INTEGER NOT NULL,
    entry_price REAL NOT NULL,
    state TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS order_log (
    id INTEGER PRIMARY KEY,
    symbol TEXT NOT NULL,
    side TEXT NOT NULL,
    price REAL NOT NULL,
    timestamp DATETIME NOT NULL
);
