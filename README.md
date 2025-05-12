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

SELECT * FROM card_descriptions

pip install asyncpg

Remove Python cache
Get-ChildItem -Path . -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force

Oauth:
pip install authlib 

CREATE TABLE users (
    id SERIAL PRIMARY KEY,  -- PostgreSQL esetén
    facebook_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    email VARCHAR(255),
    last_draw_date DATE,  -- vagy TIMESTAMP, ha pontos idő is kell
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

show tables:
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public';

OR



DB migration:
pip install alembic

FB new app:
http://localhost:8000/api/auth/facebook/callback


Oauth:
pip install google-auth google-auth-oauthlib

https://developers.google.com/oauthplayground/

Test token:
curl -X POST http://localhost:8000/api/auth/google \
  -H "Content-Type: application/json" \
  -d '{"token": "IDE_ÍRD_BE_AZ_ID_TOKEN-T"}'


npm install jwt-decode

npm install axios

pip install PyJWT


TODO: implemet Authorization: Bearer token auth

UPDATE users SET last_draw_date = NULL WHERE id = 1;

mc alias set localhost http://localhost:9000 minioaccesskey miniosecretkey

docker pull bitnami/python:3.13.3-debian-12-r11
docker pull bitnami/node:24.0.1-debian-12-r1
docker pull bitnami/nginx:1.28.0-debian-12-r0




