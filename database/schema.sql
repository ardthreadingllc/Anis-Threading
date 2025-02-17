-- ============================
-- Customers Table
-- ============================
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT NOT NULL UNIQUE,
    email TEXT UNIQUE
);

-- ============================
-- Services Table (Preloaded)
-- ============================
CREATE TABLE IF NOT EXISTS services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

-- ============================
-- Combo Types Table
-- ============================
CREATE TABLE IF NOT EXISTS combo_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    total_uses INTEGER NOT NULL
);

-- ============================
-- Combo Services Mapping Table
-- ============================
CREATE TABLE IF NOT EXISTS combo_services (
    combo_type_id INTEGER NOT NULL,
    service_id INTEGER NOT NULL,
    PRIMARY KEY (combo_type_id, service_id),
    FOREIGN KEY (combo_type_id) REFERENCES combo_types (id) ON DELETE CASCADE,
    FOREIGN KEY (service_id) REFERENCES services (id) ON DELETE CASCADE
);

-- ============================
-- Combos Table
-- ============================
CREATE TABLE IF NOT EXISTS combos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    combo_type_id INTEGER NOT NULL,
    remaining_uses INTEGER NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers (id) ON DELETE CASCADE,
    FOREIGN KEY (combo_type_id) REFERENCES combo_types (id) ON DELETE CASCADE
);

-- ============================
-- Appointments Table
-- ============================
CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    service_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    combo_id INTEGER,
    FOREIGN KEY (customer_id) REFERENCES customers (id) ON DELETE CASCADE,
    FOREIGN KEY (service_id) REFERENCES services (id) ON DELETE CASCADE,
    FOREIGN KEY (combo_id) REFERENCES combos (id) ON DELETE SET NULL
);

-- ============================
-- Indexes for Optimization
-- ============================
CREATE INDEX IF NOT EXISTS idx_customers_phone ON customers (phone);
CREATE INDEX IF NOT EXISTS idx_combos_customer_id ON combos (customer_id);
CREATE INDEX IF NOT EXISTS idx_appointments_customer_id ON appointments (customer_id);
CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments (date);
CREATE INDEX IF NOT EXISTS idx_services_name ON services (name);

-- ============================
-- Preload Services Data
-- ============================
INSERT OR IGNORE INTO services (name) VALUES
('Eyebrow Threading'), ('Lip Threading'), ('Chin Threading'), ('Forehead Threading'),
('Sideburns Threading'), ('Cheeks Threading'), ('Full Face Threading'),
('Ear Waxing'), ('Nose Waxing'), ('Full Leg Waxing'), ('Half Leg Waxing'),
('Full Arm Waxing'), ('Half Arm Waxing'), ('Under Arm Waxing'),
('Bikini Waxing'), ('Brazilian Waxing'), ('Stomach Waxing'), ('Back Waxing'),
('Full Body Waxing'), ('Express Facial'), ('Acne Facial'), ('Shahnaz Gold Facial'),
('Anis Signature Facial'), ('Ayurveda Haldi Chandan Facial'), ('Microdermabrasion Facial'),
('Hydra Facial'), ('Radio Frequency Treatment'), ('Teen Clean Facial'),
('Herbal Pearl Glow Facial'), ('Classic Soothing Regular Facial');

-- ============================
-- Preload Combo Types Data
-- ============================
INSERT OR IGNORE INTO combo_types (name, total_uses) VALUES
('Eyebrow Threading Combo', 5),
('Lip or Chin or Forehead Threading Combo', 5),
('Sideburns or Cheeks Threading Combo', 5),
('Full Face Threading Combo', 5),
('Ear or Nose Waxing Combo', 5),
('Full Leg Waxing Combo', 5),
('Half Leg Waxing Combo', 5),
('Full Arm Waxing Combo', 5),
('Half Arm Waxing Combo', 5),
('Under Arm Waxing Combo', 5),
('Bikini Waxing Combo', 5),
('Brazilian Waxing Combo', 5),
('Stomach Waxing Combo', 5),
('Back Waxing Combo', 5),
('Full Body Waxing Combo', 5),
('Express Facial Combo', 5),
('Acne Facial Combo', 5),
('Shahnaz Gold Facial Combo', 5),
('Anis Signature Facial Combo', 5),
('Ayurveda Haldi Chandan Facial Combo', 5),
('Microdermabrasion Facial Combo', 5),
('Hydra Facial Combo', 5),
('Radio Frequency Treatment Combo', 5),
('Teen Clean Facial Combo', 5),
('Herbal Pearl Glow Facial Combo', 5),
('Classic Soothing Regular Facial Combo', 5);

-- ============================
-- Preload Combo Services Mapping
-- ============================
INSERT OR IGNORE INTO combo_services (combo_type_id, service_id) VALUES
(1, 1),  -- Eyebrow Threading Combo → Eyebrow Threading
(2, 2), (2, 3), (2, 4),  -- Lip, Chin, Forehead Threading Combo
(3, 5), (3, 6),  -- Sideburns or Cheeks Threading Combo
(4, 7),  -- Full Face Threading Combo
(5, 8), (5, 9),  -- Ear or Nose Waxing Combo
(6, 10),  -- Full Leg Waxing Combo
(7, 11),  -- Half Leg Waxing Combo
(8, 12),  -- Full Arm Waxing Combo
(9, 13),  -- Half Arm Waxing Combo
(10, 14),  -- Under Arm Waxing Combo
(11, 15),  -- Bikini Waxing Combo
(12, 16),  -- Brazilian Waxing Combo
(13, 17),  -- Stomach Waxing Combo
(14, 18),  -- Back Waxing Combo
(15, 19),  -- Full Body Waxing Combo
(16, 20), (17, 21), (18, 22), (19, 23), (20, 24), (21, 25), (22, 26),
(23, 27), (24, 28), (25, 29), (26, 30);  -- Facial Services
