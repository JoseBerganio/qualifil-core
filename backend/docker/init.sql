# QUALIFIL backend — pgvector bootstrap script.
# Mounted by docker-compose.yml into /docker-entrypoint-initdb.d/ so the
# PostgreSQL 18 + pgvector extension is ready when the database initializes.
CREATE EXTENSION IF NOT EXISTS vector;
