# Connection Conventions

## Supported env keys

The runner checks these URL keys first:

- `DATABASE_URL`
- `DATABASEURL`
- `DB_URL`
- `DB_DSN`
- `POSTGRES_URL`
- `POSTGRESQL_URL`
- `MYSQL_URL`
- `SQLITE_URL`

If none exist, it falls back to component keys:

- Host: `DB_HOST`, `DATABASE_HOST`, `PGHOST`, `MYSQL_HOST`
- Port: `DB_PORT`, `DATABASE_PORT`, `PGPORT`, `MYSQL_PORT`
- User: `DB_USER`, `DB_USERNAME`, `PGUSER`, `MYSQL_USER`
- Password: `DB_PASSWORD`, `DB_PASS`, `PGPASSWORD`, `MYSQL_PASSWORD`
- Database name: `DB_NAME`, `DB_DATABASE`, `PGDATABASE`, `MYSQL_DATABASE`
- Dialect or engine hint: `DB_DIALECT`, `DB_ENGINE`, `DB_TYPE`, `DATABASE_TYPE`

## Driver normalization

The runner normalizes common URLs before handing them to SQLAlchemy:

- `postgres://...` -> `postgresql+psycopg://...`
- `postgresql://...` -> `postgresql+psycopg://...`
- `mysql://...` -> `mysql+pymysql://...`

SQLite URLs pass through unchanged.

## Installed Python packages

The runner bootstraps these packages into the project interpreter when needed:

- `SQLAlchemy`
- `python-dotenv`
- `sqlparse`
- `psycopg[binary]`
- `PyMySQL`

## Notes

- The repository root `.env` is the default source of truth.
- The runner prints only metadata about the connection target. It does not echo secrets.
- For write statements, review the SQL carefully before executing against a live database.
