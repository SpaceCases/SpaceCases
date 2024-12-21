CREATE TABLE users (
    id bigint PRIMARY KEY,
    last_claim date NOT NULL,
    claim_streak int NOT NULL,
    balance bigint NOT NULL,
    inventory_capacity bigint NOT NULL
);

CREATE TABLE skins (
    owner_id bigint NOT NULL,
    name text NOT NULL,
    floats real[] NOT NULL,
    PRIMARY KEY (owner_id, name),
    FOREIGN KEY (owner_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE stickers (
    owner_id bigint NOT NULL,
    name text NOT NULL,
    count bigint NOT NULL,
    PRIMARY KEY (owner_id, name),
    FOREIGN KEY (owner_id) REFERENCES users (id) ON DELETE CASCADE
);

