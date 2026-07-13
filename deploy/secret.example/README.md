# Secret files

The back-end reads its secrets from plain files in `back-end/secret/`
(resolved by `config/config.py`). That directory is git-ignored.

## Setup

Copy this template directory to the real location and fill in the values:

```sh
cp -r deploy/secret.example back-end/secret
```

Then edit `back-end/secret/`:

- **db_url_production** — the connection string the app uses (APP_CONFIG=production).
  Host is the compose service name `db`. The password must match
  `POSTGRES_PASSWORD` in `.env`.
- **private_key** — generate a real 256-bit key; do not ship the placeholder:
  ```sh
  python back-end/www/gen_key.py back-end/secret/private_key confirm
  ```
- **unsplash_access_key_production** — required for the `/photos/random` endpoint.
- **google_signin_client_id_production** — unused on kind.io (anonymous-only),
  but must remain a non-empty file.

## Why all eight files are required

`config/config.py` reads every environment's secret files at import time
(Config, ProductionConfig, and TestingConfig class bodies all run on import),
so all files must exist and be non-empty even though production only uses the
`_production` values. The `_staging` and `_testing` files can stay as harmless
placeholders (db_url_testing is only used when running the test suite).
