CREATE TABLE users (
    id BIGINT PRIMARY KEY,
    last_claim DATE NOT NULL,
    claim_streak INT NOT NULL,
    balance BIGINT NOT NULL,
    inventory_capacity BIGINT NOT NULL
);

CREATE TABLE skins (
    id BIGSERIAL PRIMARY KEY,
    owner_id BIGINT NOT NULL,
    name TEXT NOT NULL,
    float FLOAT NOT NULL,
    FOREIGN KEY (owner_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE INDEX idx_skins_owner_id ON skins (owner_id);
CREATE INDEX idx_skins_owner_id_name ON skins (owner_id, name);

CREATE TABLE stickers (
    id BIGSERIAL PRIMARY KEY,
    owner_id BIGINT NOT NULL,
    name TEXT NOT NULL,
    FOREIGN KEY (owner_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE INDEX idx_stickers_owner_id ON stickers (owner_id);
CREATE INDEX idx_stickers_owner_id_name ON stickers (owner_id, name)

