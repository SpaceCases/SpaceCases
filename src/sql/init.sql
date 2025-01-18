CREATE TABLE users (
    id BIGINT PRIMARY KEY,
    last_claim DATE NOT NULL,
    claim_streak INT NOT NULL,
    balance BIGINT NOT NULL,
    inventory_capacity BIGINT NOT NULL
);

CREATE TYPE item_type AS ENUM ('skin', 'sticker');

CREATE TABLE items (
    id BIGSERIAL PRIMARY KEY,
    owner_id BIGINT NOT NULL,
    type item_type NOT NULL,
    name TEXT NOT NULL,
    details JSONB NOT NULL,
    FOREIGN KEY (owner_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE INDEX idx_items_owner_id ON items (owner_id);
