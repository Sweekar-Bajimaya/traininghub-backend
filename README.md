# TrainingHub Backend

Django + DRF backend for **TrainingHub**, a Merojob training marketplace. Verified institutes publish
trainings (physical, online or hybrid), admins review them, and visitors browse and send enquiries
without an account. The frontend is a separate Next.js project.

## Docs

| File                                                                               | What it is                                                    |
| ---------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| [docs/Training for Merojob (PRD).md](docs/Training%20for%20Merojob%20%28PRD%29.md) | Product requirements                                          |
| [docs/System Design.md](docs/System%20Design.md)                                   | Architecture, decisions made, open questions                  |
| [CLAUDE.md](CLAUDE.md)                                                             | Conventions, commands and landmines (read this before coding) |

## Stack

Python 3.12, Django 5.2, DRF, simplejwt (RS256), PostgreSQL, Redis (cache, throttling, django-q2 broker).

## Setup

You need Python 3.12, PostgreSQL and Redis running locally.

```sh
# 1. virtual environment and dependencies
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements/dev.txt

# 2. local settings (gitignored): copy, then edit the DATABASES block
cp config/settings/env.sample.py config/settings/env.py

# 3. create an empty PostgreSQL database with the name/user/password you put in env.py

# 4. JWT signing keys (gitignored, once per checkout)
python manage.py generate_rsa_keys

# 5. database and first user
python manage.py migrate
python manage.py load_locations       # Nepal provinces / districts / municipalities
python manage.py load_categories      # the 13 starter training categories
python manage.py createsuperuser      # creates the one and only Super Admin

# 6. run
python manage.py runserver
```

Check it works: open `http://localhost:8000/api/root/` (Swagger UI, only when `DEBUG=True`). The root `http://localhost:8000/` returns 404 on purpose.

Optional settings are environment variables with defaults: `REDIS_URL` (`redis://localhost:6379/0`),
`EMAIL_*`, `DEFAULT_FROM_EMAIL`, `RECAPTCHA_SECRET_KEY`, `FRONTEND_BASE_URL` (`http://localhost:3000`, used in
staff invitation links).

Institute verification documents are stored in `private_media/` in the project root (created on first upload,
gitignored, never served by URL). Staff invitation emails are sent by the background worker, so run
`python manage.py qcluster` (needs Redis); with the default console email backend the email appears in that terminal.
The worker also refreshes training search data after an institute, category or location is renamed.

Trainings expire after their end date only if `expire_trainings` runs daily: in the Django admin, add a Django Q
"Scheduled task" for `apps.training.tasks.expire_trainings` with schedule type Daily (or run
`python manage.py expire_trainings` from cron).

## Everyday commands

| Task                    | Command                                                                          |
| ----------------------- | -------------------------------------------------------------------------------- |
| Run tests               | `python manage.py test`                                                          |
| Check before committing | `python manage.py check` and `python manage.py makemigrations --check --dry-run` |
| Create migrations       | `python manage.py makemigrations` then `python manage.py migrate`                |
| Background worker       | `python manage.py qcluster`                                                      |
| Reload location data    | `python manage.py load_locations` (safe to re-run)                               |
| Load starter categories | `python manage.py load_categories` (safe to re-run)                              |
| Expire past trainings   | `python manage.py expire_trainings` (safe to re-run)                             |

Tests create their own test database, so the PostgreSQL user needs permission to create databases.
Redis must be running (throttling uses it).

## Project layout

```
config/       settings (base.py + your local env.py), urls, exception handler
apps/
  api/v1/     mounts each app's URLs under /api/v1/
  common/     base models, base viewsets, shared serializers and validators; Nepal locations (province / district /
              municipality) and training categories, with their loaders and APIs
  users/      User model, roles and permissions, JWT auth, admin management
  training/   trainings, weekly class slots, curriculum, search; public, portal and admin review APIs
  institutes/ institutes, staff and invitations, documents, locations, gallery; public, portal and admin APIs
docs/         PRD and system design
design/       UI prototypes (bundled HTML, decode before searching)
```

Planned apps: `enquiries`, `notifications`, `analytics`.

## Users API (`/api/v1/user/`)

| Endpoint                                            | Who                                                     |
| --------------------------------------------------- | ------------------------------------------------------- |
| `POST auth/login/`, `auth/refresh/`, `auth/logout/` | public (login and refresh are throttled)                |
| `GET, PATCH me/` and `PUT me/password/`             | any logged-in user                                      |
| `admins/` (list, create, retrieve, update)          | Super Admin only                                        |
| `PATCH users/{id}/status/`                          | `manage_account_status` permission (suspend / activate) |

There is no public user registration. Admins are created by the Super Admin; institute owners are created by
institute registration (below). Roles: `SUPER_ADMIN` (exactly one), `ADMIN`, `INSTITUTE_STAFF`.

## Locations API (`/api/v1/locations/`)

| Endpoint | What it returns |
| --- | --- |
| `GET /` | active locations; filter with `level`, `parent`, `province`, `district`, search with `search` |
| `GET {id}/` | one location |
| `GET tree/` | province > district > municipality tree (cached) |

All are public and read-only. Example for a district dropdown: `GET /api/v1/locations/?level=DISTRICT&parent=<province id>`.

## Institutes API

| Prefix | Who | What |
| --- | --- | --- |
| `/api/v1/institutes/` | public | approved institutes: list (filter `type`, search `search`) and `{slug}/` |
| `/api/v1/institute/register/` | public | register an institute and its owner (JSON); then log in and upload documents |
| `/api/v1/institute/invitations/accept/` | public | accept a staff invitation with the emailed token |
| `/api/v1/institute/` `profile/`, `resubmit/`, `locations/`, `documents/`, `gallery/` | institute staff | manage the institute; another institute's rows are a 404 |
| `/api/v1/institute/` `staff/`, `invitations/` | owner only | list or remove staff; invite, list or revoke invitations |
| `/api/v1/admin/institutes/` | `manage_institutes` | review: `approve`, `reject`, `request-info`, `suspend`, `reinstate`; document review and download |

An institute becomes public only when an admin approves it, which needs at least one active location and one document.

## Categories and trainings API

| Prefix | Who | What |
| --- | --- | --- |
| `/api/v1/categories/` | public | category > sub-category tree (cached), with icon and hue |
| `/api/v1/admin/categories/` | `manage_categories` | list, create, rename, move, deactivate (no delete) |
| `/api/v1/trainings/` | public | approved trainings: list and `{slug}/`; filters `category`, `sub_category`, `mode`, `level`, `province`, `district`, `municipality`, `fee_min`, `fee_max`, `start_from`, `start_to`, `duration` (`short`, `mid`, `long`), `institute`, `registration_open`; `search`; `ordering` (`published_at`, `start_date`, `fee_npr`) |
| `/api/v1/institute/trainings/` | institute staff | create and edit (with `sessions`, `modules`, `outcomes`), `submit`, `withdraw`, `unpublish`, `republish`, `cancel`, `cover`; delete a draft |
| `/api/v1/admin/trainings/` | `manage_trainings` | review queue (`?status=SUBMITTED`): `approve`, `request-changes`, `reject` |

A training starts as `DRAFT`, becomes `SUBMITTED` (shown as "Pending Review") when the institute submits it, and is
public once an admin approves it. Editing an approved training sends it back to review.

## Working on the code

- Business rules go in the app's `services.py`; views and serializers stay thin and use DRF generics.
- Avoid N+1 queries (`select_related` / `prefetch_related`) and lock rows (`select_for_update`) before
  check-then-write inside `transaction.atomic()`.
- Do not hand-edit existing migrations; regenerate with `makemigrations`.
- Never commit `config/settings/env.py`, `keys/`, `*.pem` or `media/`.
- Times are Nepal time (`Asia/Kathmandu`); use `timezone.localdate()` / `localtime()`, not `.date()` on `timezone.now()`.
- Change `CLAUDE.md` and `docs/System Design.md` in the same change as the code they describe.
- The Django admin site (`/admin/`) shows users read-only; manage users through the API.

## Known gaps

- `ATTACHMENT_MAX_UPLOAD_SIZE` is not defined yet, so image uploads (profile picture) fail until it is added.
