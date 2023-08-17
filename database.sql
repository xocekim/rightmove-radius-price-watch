DROP TABLE IF EXISTS property;
DROP TABLE IF EXISTS history;

CREATE TABLE property (
  id INTEGER PRIMARY KEY,
  price CURRENCY,
  address TEXT,
  type TEXT,
  agent TEXT,
  first_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
  last_seen DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  property_id INTEGER,
  price CURRENCY,
  address TEXT,
  type TEXT,
  agent TEXT,
  changed_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE TRIGGER update_trigger UPDATE OF price, address, type, agent ON property
WHEN old.price IS DISTINCT FROM new.price OR old.address IS DISTINCT FROM new.address OR old.type IS DISTINCT FROM new.type OR old.agent IS DISTINCT FROM new.agent
BEGIN
  INSERT INTO history (property_id, price, address, type, agent) VALUES (old.id, old.price, old.address, old.type, old.agent);
END;

-- INSERT INTO property (id, price, address, type, agent) VALUES (1234, '75000', '1234 Main St', 'Detached', 'John Doe') ON CONFLICT(id) DO UPDATE SET price=excluded.price, address=excluded.address, type=excluded.type, agent=excluded.agent, last_seen=CURRENT_TIMESTAMP;