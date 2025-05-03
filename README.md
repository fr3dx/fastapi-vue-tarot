Implementing Postgres

Note:

Add .env with the following contents:
# Container
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
# Backend
DB_HOST=
DB_PORT=
DB_NAME=
DB_USER=
DB_PASSWORD=


CREATE TABLE card_descriptions (
    id SERIAL PRIMARY KEY,
    key VARCHAR(255) UNIQUE NOT NULL,
    description TEXT NOT NULL
);

INSERT INTO card_descriptions (key, description) VALUES
('empress', 'A kreativitás és termékenység kártyája.'),
('fool', 'A kezdetek és új lehetőségek jelképe.'),
('magician', 'A hatalom és képességek kártyája.');


pip install asyncpg
