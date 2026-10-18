# FastAPI_2 Project Recap

_Updated 12 October 2026. This report reflects a static workspace audit. The API was not started against PostgreSQL because importing `app.main` currently performs schema-creation DDL._

## 1. Executive Summary

This project is now an early-stage FastAPI REST API for posts with user registration and JWT-based bearer authentication. It has progressed beyond the original single-file CRUD exercise: HTTP endpoints are split into post, user, and authentication routers; passwords are bcrypt-hashed; and authenticated callers can list, create, update, and delete posts.

The application remains a small, synchronous Python/PostgreSQL service. It does not yet have a frontend, migrations, tests, documented setup, reproducible dependency metadata, container configuration, or Git history in this workspace.

| Layer | Technology detected locally | Role |
| --- | --- | --- |
| Runtime | Python 3.13.7 | Local virtual environment in `f_api2/` |
| HTTP / ASGI | FastAPI 0.139.0, Uvicorn 0.50.0 | API and development server |
| Validation | Pydantic 2.13.4, email-validator 2.3.0 | Request and response schemas |
| Persistence | SQLAlchemy 1.4.23, psycopg2-binary 2.9.12 | PostgreSQL ORM and driver |
| Authentication | PyJWT 2.15.1, python-multipart 0.0.32 | Access-token creation/validation and OAuth2 form login |
| Password security | Passlib 1.7.4, bcrypt 4.3.0 | Password hashing and verification |

### Changes since the 30 August recap

- The flat post routes were moved out of `app/main.py` into `app/routers/posts.py`.
- `app/routers/users.py`, `app/routers/auth.py`, `app/utils.py`, and `app/oauth2.py` were added.
- A `User` database model and user-oriented Pydantic schemas were added.
- Public user registration, user retrieval, and `/login` endpoints were added.
- Login verifies a bcrypt password hash and issues an expiring JWT bearer token.
- Post list, creation, update, and deletion now require that token; response models were added for posts and users.
- The original database configuration, import-time `create_all()`, lack of migrations/tests/docs, and hard-coded database credential remain unresolved. A hard-coded JWT signing key is now an additional security concern.

## 2. Architecture Map

```text
Uvicorn (expected command: uvicorn app.main:app --reload)
    |
    v
app/main.py
    |- imports ORM models and database engine
    |- calls Base.metadata.create_all() during import
    |- creates FastAPI application
    |- includes posts, users, and auth routers
    |
    +--> app/routers/posts.py
    |      |- post CRUD through SQLAlchemy sessions
    |      `- bearer-token dependency for list/create/update/delete
    |
    +--> app/routers/users.py
    |      |- registration
    |      `- user retrieval
    |
    +--> app/routers/auth.py
           `- OAuth2 password-form login and JWT issuance

app/oauth2.py <--- PyJWT token creation and bearer-token verification
app/utils.py  <--- Passlib/bcrypt hash and verify helpers
app/schemas.py <--- request and response contracts
app/models.py  <--- Post_table and User ORM mappings
app/database.py <--- PostgreSQL engine, session factory, declarative Base
                         |
                         v
                    PostgreSQL: posts and users tables
```

| Path | Current responsibility |
| --- | --- |
| [app/main.py](app/main.py) | Application bootstrap, import-time schema creation, router registration, and `GET /`. |
| [app/routers/posts.py](app/routers/posts.py) | Post CRUD routes and selected bearer-token protection. |
| [app/routers/users.py](app/routers/users.py) | User registration and user lookup. |
| [app/routers/auth.py](app/routers/auth.py) | Form-based login and access-token response. |
| [app/oauth2.py](app/oauth2.py) | Creates 30-minute HS256 JWTs and exposes `get_current_user`. |
| [app/utils.py](app/utils.py) | Hashes and verifies passwords with bcrypt. |
| [app/models.py](app/models.py) | Maps `posts` and the newly added `users` table. |
| [app/schemas.py](app/schemas.py) | Post, user, and token input/output models. |
| [app/database.py](app/database.py) | PostgreSQL URL, SQLAlchemy engine, `SessionLocal`, and `get_db`. |
| [Test_PostgreSQL_file.sql](Test_PostgreSQL_file.sql) | Unused SQL practice file for an unrelated `Products` table. |
| [Error_log.txt](Error_log.txt) | Historical startup error; it is not evidence of a current live failure. |

## 3. Entry Point & State

The importable ASGI entry point remains `app.main:app`. The likely local command is:

```powershell
.\f_api2\Scripts\uvicorn.exe app.main:app --reload
```

Starting the application currently follows this sequence:

1. Import the database module, ORM mappings, routers, and authentication utilities.
2. Build a PostgreSQL engine from the source-controlled connection URL.
3. Run `Base.metadata.create_all(bind=engine)` before the FastAPI object is created.
4. Register post, user, and authentication routers.
5. Open and close one SQLAlchemy session per request through `Depends(get_db)`.

Because of step 3, a reachable PostgreSQL instance is required even to import the app. Startup can create the `posts` and `users` tables, but it cannot safely manage schema changes. The older error log records a malformed `"<localhost"` hostname; current source uses `localhost`, so that error appears historical and must be retested rather than assumed fixed.

### Current API surface

The declared trailing slashes below are significant; FastAPI may redirect a slash-less request.

| Method | Route | Authentication | Current behavior |
| --- | --- | --- | --- |
| `GET` | `/` | Public | Returns a greeting. |
| `GET` | `/posts/` | Bearer token | Lists all posts. |
| `POST` | `/posts/` | Bearer token | Creates a post and returns HTTP 201. |
| `GET` | `/posts/{id}` | Public | Retrieves a post or returns 404. |
| `PUT` | `/posts/{id}` | Bearer token | Fully replaces a post or returns 404. |
| `DELETE` | `/posts/{id}` | Bearer token | Deletes a post or returns 404/204. |
| `POST` | `/users/` | Public | Creates a user with a bcrypt-hashed password. |
| `GET` | `/users/{id}` | Public | Returns user details without the password. |
| `POST` | `/login` | Public | Accepts OAuth2 form fields (`username` carries the email) and returns a bearer token. |

### Verification performed for this update

- All current Python source files parsed successfully.
- A local PyJWT creation/decode round trip passed.
- Password hashing and verification passed, although Passlib logged a bcrypt-version compatibility traceback described below.
- `pip check` reported no broken installed requirements.
- The app itself and API routes were not exercised against a live database, so database-backed behavior remains unverified.

## 4. Incomplete / Broken Tracks

No explicit `TODO`, `FIXME`, `pass`, `NotImplemented`, or empty route handler was found. The main unfinished work is operational hardening and completing the authorization design.

| Priority | Track | Evidence and impact |
| --- | --- | --- |
| Blocker | Secrets and configuration | The PostgreSQL credential in `app/database.py` and JWT signing key in `app/oauth2.py` are hard-coded in source. Rotate both secrets, move them to environment-backed configuration, and provide an `.env.example` without values. |
| Blocker | Database lifecycle | `app/main.py` still runs `create_all()` during import. This makes PostgreSQL availability a startup requirement and provides no safe migration path for either table or the category enum. |
| High | Authorization model | Tokens prove that a caller is authenticated, but posts have no `owner_id`/user foreign key and no ownership check. Any valid token can currently update or delete any post. `GET /posts/{id}` is public while the other post operations are protected; make that policy intentional. |
| High | Security cleanup | `create_posts` prints the token-derived data to stdout. The token dependency returns `TokenData`, although parameters name and annotate it as `user_id: int`. JWT secret rotation, revocation/refresh policy, and verifying that the token's user still exists are not implemented. |
| High | Reproducible delivery and tests | There is still no `README`, `requirements.txt`, `pyproject.toml`, lockfile, `.env.example`, Docker/Compose config, root `.gitignore`, Git repository, or application test suite. Pytest and Alembic are not installed. |
| Medium | User-management edge cases | Database uniqueness failures for duplicate username/email are not translated into a controlled HTTP response. The `UserLogin` schema is unused because login uses `OAuth2PasswordRequestForm`. |
| Medium | Response/API contract | `PostRes` now controls post serialization, but it omits the post `id`, making client-side post identification awkward. Create and full-update share the same model; pagination, filtering, partial updates, and explicit error response contracts are absent. |
| Medium | Password-library compatibility | The installed Passlib/bcrypt pair successfully hashed and verified a password, but Passlib emitted an `AttributeError` while reading bcrypt's removed version metadata. Pin or upgrade to a tested compatible combination before treating the auth path as production-ready. |
| Low | Legacy/tutorial cleanup | Commented raw-psycopg2 implementations and unused imports remain in `main.py`, `posts.py`, and `oauth2.py`. The active implementation is SQLAlchemy plus PyJWT; archive or remove the superseded approach. |

### Current strengths

- Routes are now separated by domain instead of all living in `main.py`.
- Passwords are hashed before persistence and omitted from user responses.
- JWTs include an expiry and invalid tokens are rejected by the bearer dependency.
- Response models now protect user and post output shape, even though `PostRes` needs an `id`.
- The local environment contains the packages needed for email validation and OAuth2 form parsing.

## 5. Re-entry Plan

Follow this order to turn the new authentication work into a dependable baseline.

1. **Capture the current state in version control.** Initialize Git, add a root `.gitignore` for `f_api2`, `__pycache__`, `.env`, logs, and editor files, then make a baseline commit. Keep the current recap as the handoff record.
2. **Make the environment reproducible.** Replace the preserved virtual environment as the dependency source of truth with a pinned `requirements.txt` or `pyproject.toml`/lockfile. Include the newly required authentication, email-validation, and form-parsing packages.
3. **Move and rotate secrets.** Rotate the exposed database credential and JWT key. Load configuration from environment variables, validate it at startup, and add a safe `.env.example` plus setup documentation.
4. **Establish a migration baseline.** Provision or verify PostgreSQL deliberately, introduce Alembic, create migrations for `posts`, `users`, and the enum, then remove import-time `create_all()` once migrations own schema lifecycle.
5. **Finish the authorization design.** Decide which routes are public, add a post owner foreign key, set it from the authenticated user during creation, and enforce ownership for reads/updates/deletes as appropriate. Remove the debug `print` and give dependency values accurate names/types.
6. **Stabilize user and API contracts.** Add duplicate-user handling, make `PostRes` include `id`, split create/update/patch schemas as needed, and document the form-encoded `/login` request shape and error responses.
7. **Resolve the password-library warning.** Choose and pin a tested password hashing dependency combination, then confirm password registration/login works without the Passlib/bcrypt compatibility traceback.
8. **Add automated tests before adding more features.** Cover registration, duplicate users, login failures, valid/expired/invalid tokens, protected versus public routes, ownership checks, CRUD behavior, 404s, response models, and migration/database isolation.
9. **Document the runnable project.** Add a README with prerequisites, environment variables, database/migration commands, the Uvicorn command, authentication examples, endpoint usage, and the test command.

Completing steps 1-5 will make the current code safe to run and evolve. Steps 6-9 will turn the router/auth expansion into a maintainable API foundation.
