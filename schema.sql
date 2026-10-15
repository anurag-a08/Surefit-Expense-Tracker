
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT,
    address TEXT,
    joining_date TEXT NOT NULL,
    plan_name TEXT NOT NULL,
    monthly_fee REAL NOT NULL CHECK (monthly_fee >= 0),
    membership_start TEXT NOT NULL,
    membership_end TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER NOT NULL,
    amount REAL NOT NULL CHECK (amount > 0),
    payment_date TEXT NOT NULL,
    payment_method TEXT NOT NULL,
    notes TEXT,
    FOREIGN KEY (member_id)
        REFERENCES members(id)
        ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_members_end
ON members(membership_end);

CREATE INDEX IF NOT EXISTS idx_payments_member
ON payments(member_id);

ALTER TABLE members ADD COLUMN amount_due REAL DEFAULT 0;