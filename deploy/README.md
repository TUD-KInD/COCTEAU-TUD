# Deploying Periscope to https://kind.io.tudelft.nl/periscope

This directory contains the Docker deployment for the Periscope public
engagement tool. The stack runs three containers behind the host's existing
nginx reverse proxy:

| Service | Image            | Role                                                   |
|---------|------------------|--------------------------------------------------------|
| `db`    | postgres:13      | Database (data in the named volume `db-data`)          |
| `api`   | built locally    | Flask app served by uWSGI, mounted at `/periscope/api` |
| `web`   | built locally    | nginx serving the front-end + proxying the API         |

Only `web` publishes a port, bound to `127.0.0.1:8080`. The host nginx proxies
`https://kind.io.tudelft.nl/periscope/` to it. The `/periscope` path prefix is
preserved end-to-end (never stripped), which keeps Flask's routes and generated
URLs correct.

---

## Prerequisites (on the server)

- Docker Engine + the Compose plugin.
- The repository checked out.
- The production SQL dump file (plain-format `pg_dump`).
- Sudo access to edit and reload the host nginx.

---

## 1. Configure secrets

The back-end reads plain-file secrets from `back-end/secret/` (git-ignored).

```sh
cp -r deploy/secret.example back-end/secret
```

Then edit `back-end/secret/`:

- **db_url_production** — set the DB password (host stays `db`, database and user
  stay `public_engagement_tool`).
- **private_key** — generate a real key (do NOT ship the placeholder):
  ```sh
  python3 back-end/www/gen_key.py back-end/secret/private_key confirm
  ```
- **unsplash_access_key_production** — required for the `/photos/random` endpoint.
- The `_staging` / `_testing` files may stay as placeholders (they must be
  non-empty; config.py reads every profile's files at import time).

> Google Sign-In is intentionally disabled on this host (anonymous-only), so
> `google_signin_client_id_*` can stay as placeholders.

## 2. Set the database password

```sh
cp .env.example .env
# edit .env: POSTGRES_PASSWORD must match the password in db_url_production
```

## 3. Restore the database

Place the plain-SQL dump in `deploy/db-init/`. It runs automatically the first
time the `db` volume is initialized (empty volume only):

```sh
cp /path/to/public_engagement_tool_production_2026.sql deploy/db-init/
```

The dump's schema is already at the app's Alembic head (`fc9e28ea6036`), so no
`flask db upgrade` is needed. If you ever start from a fresh DB with no dump,
run migrations instead:

```sh
docker compose exec api flask db upgrade
```

## 4. Build and start the stack

```sh
docker compose up -d --build
docker compose ps          # db should be "healthy"; api and web "Up"
```

Verify internally (before exposing publicly):

```sh
curl -s http://127.0.0.1:8080/periscope/api/      # -> Hello, World!
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8080/periscope/
```

## 5. Wire up the host nginx

Add the two location blocks from `deploy/host-nginx-periscope.conf` into the
existing `server { listen 443 ssl; server_name kind.io.tudelft.nl; ... }` block,
then:

```sh
sudo nginx -t && sudo systemctl reload nginx
```

## 6. Verify publicly

```sh
curl -s https://kind.io.tudelft.nl/periscope/api/     # -> Hello, World!
```

Then in a browser open `https://kind.io.tudelft.nl/periscope/`:

- The page loads; the browser console shows API calls to `/periscope/api/...`.
- "Continue as guest" works (anonymous login issues a JWT).
- Existing topics/scenarios/visions appear (restored data).
- Enumeration is blocked: `curl https://kind.io.tudelft.nl/periscope/api/vision/?user_id=1`
  returns 400 (not data).

---

## Running the tests (optional)

```sh
docker compose exec db createdb -U public_engagement_tool public_engagement_tool_test
docker compose exec api sh -c 'cd tests && python run_all_tests.py'
```

## Updating the app

```sh
git pull
docker compose up -d --build        # rebuilds api/web; db volume is untouched
```

## Common operations

```sh
docker compose logs -f api          # tail app logs
docker compose restart api          # restart just the API
docker compose stop                 # stop everything (keeps data)
docker compose down                 # remove containers (keeps the db volume)
docker compose down -v              # ALSO delete the database volume (data loss!)
```

## Notes / gotchas

- **Do not commit** `back-end/secret/`, `.env`, or the `.sql` dump — all are
  git-ignored. Keep the dump access-controlled; it contains real user data.
- The pinned dependency stack requires **Python 3.9** (handled by the Dockerfile).
- A new `private_key` invalidates previously issued user JWTs (fine for a fresh
  deployment; users just get a new anonymous token).
- To enable Google Sign-In later: add a `kind.io.tudelft.nl` client-ID branch in
  `front-end/js/account.js` and add `https://kind.io.tudelft.nl` to the OAuth
  client's authorized JavaScript origins.
