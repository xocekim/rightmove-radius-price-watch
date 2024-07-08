DROP TABLE IF EXISTS property;
DROP TABLE IF EXISTS history;

CREATE TABLE property (
  id INTEGER PRIMARY KEY,
  price CURRENCY,
  address TEXT,
  type TEXT,
  agent TEXT,
  img TEXT,
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
  img TEXT,
  changed_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE VIEW v_price_history AS 
SELECT
    p.id AS property_id,
    p.price AS property_price,
    p.address AS property_address,
    p.type AS property_type,
    p.agent AS property_agent,
    p.img AS property_img,
    p.first_seen AS property_first_seen,
    p.last_seen AS property_last_seen,
    h.id AS history_id,
    h.price AS history_price,
    h.address AS history_address,
    h.type AS history_type,
    h.agent AS history_agent,
    h.img AS history_img,
    h.changed_at AS history_changed_at
FROM
    history h
LEFT JOIN
    property p ON h.property_id = p.id;


CREATE TRIGGER update_trigger UPDATE OF price, address, type, agent ON property
WHEN old.price IS NOT new.price OR old.address IS NOT new.address OR old.type IS NOT new.type OR old.agent IS NOT new.agent OR old.img IS NOT new.img
BEGIN
  INSERT INTO history (property_id, price, address, type, agent, img) VALUES (old.id, old.price, old.address, old.type, old.agent, old.img);
END;

