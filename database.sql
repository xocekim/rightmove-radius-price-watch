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
  col TEXT,
  old TEXT,
  new TEXT,
  ts DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(property_id) REFERENCES property(id)
);

CREATE TRIGGER price_update_trigger UPDATE OF price ON property
BEGIN
  INSERT INTO history (property_id, col, old, new) VALUES (old.id, 'PRICE', old.price, new.price);
END;

CREATE TRIGGER address_update_trigger UPDATE OF address ON property
BEGIN
  INSERT INTO history (property_id, col, old, new) VALUES (old.id, 'ADDRESS', old.address, new.address);
END;

CREATE TRIGGER type_update_trigger UPDATE OF type ON property
BEGIN
  INSERT INTO history (property_id, col, old, new) VALUES (old.id, 'TYPE', old.type, new.type);
END;

CREATE TRIGGER agent_update_trigger UPDATE OF agent ON property
BEGIN
  INSERT INTO history (property_id, col, old, new) VALUES (old.id, 'AGENT', old.agent, new.agent);
END;

-- INSERT INTO property (id, price, address, type, agent) VALUES (1234, '75000', '1234 Main St', 'Detached', 'John Doe') ON CONFLICT(id) DO UPDATE SET price=excluded.price, address=excluded.address, type=excluded.type, agent=excluded.agent, last_seen=CURRENT_TIMESTAMP;