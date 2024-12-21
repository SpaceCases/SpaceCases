CREATE TABLE users (
    id BIGINT PRIMARY KEY,
    last_claim DATE NOT NULL,
    claim_streak INT NOT NULL,
    balance BIGINT NOT NULL,
    inventory_capacity BIGINT NOT NULL
);

CREATE TABLE skins (
    owner_id BIGINT NOT NULL,
    name TEXT NOT NULL,
    floats REAL[] NOT NULL,
    PRIMARY KEY (owner_id, name),
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE stickers (
    owner_id BIGINT NOT NULL,
    name TEXT NOT NULL,
    count BIGINT NOT NULL,
    PRIMARY KEY (owner_id, name),
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
);
