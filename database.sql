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

CREATE VIEW v_price_history AS
SELECT '<a target="_blank" href="https://www.rightmove.co.uk/properties/' || p.id || '">link</a>' AS link, 
        PRINTF("£%,d", p.price) AS price, 
        PRINTF("£%,d", h.price) AS old_price, 
        PRINTF("%+,d", p.price - h.price) AS price_change,
        p.address, 
        p.type, 
        h.changed_at
    FROM history AS h
    LEFT JOIN property AS p ON p.id = h.property_id
    ORDER BY changed_at DESC;

CREATE VIEW v_new_properties_7days AS
SELECT '<a target="_blank" href="https://www.rightmove.co.uk/properties/' || p.id || '">link</a>' AS link, 
        PRINTF("£%,d", p.price) AS price,
        p.address,
        p.type,
        p.agent,
        p.first_seen
    FROM property AS p
    WHERE first_seen BETWEEN DATETIME('now', '-7 days') AND DATETIME('now')
    ORDER BY first_seen DESC;

CREATE TRIGGER update_trigger UPDATE OF price, address, type, agent ON property
WHEN old.price IS NOT new.price OR old.address IS NOT new.address OR old.type IS NOT new.type OR old.agent IS NOT new.agent
BEGIN
  INSERT INTO history (property_id, price, address, type, agent) VALUES (old.id, old.price, old.address, old.type, old.agent);
END;

-- INSERT INTO property (id, price, address, type, agent) VALUES (1234, '75000', '1234 Main St', 'Detached', 'John Doe') ON CONFLICT(id) DO UPDATE SET price=excluded.price, address=excluded.address, type=excluded.type, agent=excluded.agent, last_seen=CURRENT_TIMESTAMP;
