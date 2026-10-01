# traininghub-backend

Django + DRF backend for **TrainingHub**, a Merojob training marketplace. Verified institutes publish
trainings (physical / online / hybrid); admins review them; visitors browse and send enquiries without
an account. The frontend is a separate Next.js project.

## Source of truth

- `docs/Training for Merojob (PRD).md` - product requirements.
- `docs/System Design.md` - architecture and every decision made so far, plus open questions.
  Read it before designing anything; where the PRD and the design prototypes disagree, the decisions
  in System Design.md win.
- `design/*.html` - three UI prototypes (Training Hub, Institute Portal, Admin Console). Each is a
  bundled single file: the screens live in a base64/gzip `__bundler/template` + `__bundler/manifest`
  script, so grepping the HTML for UI text finds nothing - decode it first.

## Keeping this file current

This file and `docs/System Design.md` must change in the **same change** as the code they describe.
Update them when you add, remove or rename: an app, a model or workflow, an endpoint group, a setting or
environment variable, a dependency, a management command, or when a decision in System Design.md changes
or an open question gets answered. Rules:

- Only write what exists in the repo now. Unbuilt work goes under "Planned" and moves out when built.
- Verify a command or path before listing it. If it can't be verified, write "unverified".
- Delete lines that stop being true instead of leaving them.
- Don't record transient state (a half-done refactor, a bug being fixed right now).

## Stack

- Python 3.12 (`.venv`), Django 5.2, DRF 3.16, `djangorestframework-simplejwt` 5.5 (RS256),
  `django-filter`, `django-cors-headers`, `drf-yasg`, `django-q2`, `django-redis`, `django-allauth`
  (installed, not in `INSTALLED_APPS`), Pillow, Argon2 password hashing - `requirements/base.txt`.
- Dev extras in `requirements/dev.txt`: debug toolbar, django-extensions, ipdb, ipython, fabric3, pylint.
- PostgreSQL. Redis for cache and the django-q2 broker. SMTP email. Google reCAPTCHA (planned).
- Files: local `media/` now, S3 later - use Django's storage API, never hard-code paths.

## Product decisions that shape the code

- No learner accounts. Only **institute staff** and **admins** log in. Visitors submit anonymous
  **Enquiries** (captcha + rate limiting); "My enquiries" is tracked by a browser-stored device token and
  shows the last 90 days.
- Learner **Applications** (approve/reject/capacity) are phase 2 - keep the schema open to them.
- Providers are verified **Institutes** only; an Institute has several staff users (owner + staff; the owner
  can invite more) and **several locations** - a physical/hybrid training is held at one of its own locations.
- Roles: `SUPER_ADMIN` (exactly one), `ADMIN`, `INSTITUTE_STAFF` (`apps/users/constants.py::Role`).
  The Super Admin sets a new admin's initial password. A Super Admin grants
  admins limited rights via Django permissions on `User.Meta.permissions` (`users.manage_*`), checked with
  `has_perm`. `GRANTABLE_PERMISSIONS` excludes `manage_admins`.
- Training mode: `PHYSICAL`, `ONLINE`, `HYBRID`. Single fee, NPR only. All times are NPT, online included.
  Locations are a managed Nepal province/district/city list. Search is PostgreSQL full-text.
- Reviews & ratings are out of the MVP.
- The Next.js app calls this API directly from the browser (may change): CORS allow-list, throttling can key
  on client IP.

## Layout

```
config/
  settings/__init__.py    `from .base import *` then `from .env import *`
  settings/base.py        shared settings; reads secrets/toggles from os.environ
  settings/env.sample.py  template -> copy to env.py (gitignored): DB, SECRET_KEY, JWT key loading
  exception_handlers.py   maps Django ValidationError -> 400 and database IntegrityError -> 409
  urls.py                 admin/, api/v1/ -> apps.api.v1.urls; swagger/redoc/debug toolbar only if DEBUG
apps/
  api/v1/urls.py          mounts each app's URLs (currently `user/`)
  common/                 BaseModel (created_at/modified_at), SlugModel, BaseViewSet, DynamicFields
                          serializers, validators, helpers
  users/                  custom User (email login), roles/permissions, JWT auth, `services.py` (admin
                          create/update, suspend, password change), API under `user/` (auth/, me/,
                          admins/, users/{id}/status/), management command `generate_rsa_keys`
docs/  design/            see "Source of truth"
```

Planned apps (not created yet): `institutes`, `catalog` (categories, locations, trainings, sessions),
`enquiries`, `notifications`, `analytics`; later `applications`, `learners`, `reviews`.
Each app follows `models.py`, `admin.py`, `migrations/`, `api/v1/{serializers,views,urls}.py`
(`apps/users/api/v1/urls/users.py` is a package form of the same idea).

## Commands

Run through the venv (`source .venv/bin/activate`, or prefix `.venv/bin/python`).

| task | command |
|---|---|
| install | `pip install -r requirements/dev.txt` |
| JWT keys (once per checkout) | `python manage.py generate_rsa_keys` (writes `keys/`, gitignored) |
| check | `python manage.py check` |
| migrate | `python manage.py makemigrations` then `python manage.py migrate` |
| dev server | `python manage.py runserver` |
| task worker | `python manage.py qcluster` (needs Redis) |
| tests | `python manage.py test` - `apps/users/tests.py` covers the User constraints and the users API (needs Postgres where the test DB can be created, and Redis for throttling) |
| lint / typecheck | unverified - pylint is in dev.txt but there is no config |

## Conventions

- Models extend `apps.common.models.BaseModel`; add `SlugModel` for public-URL objects (needs `name` or `title`).
- Viewsets extend `apps.common.viewsets.BaseViewSet`. Per-action permissions go in `permission_class_mapper`
  (`{"create": [...]}`); an empty list means public. Plural `permission_classes` elsewhere - the singular
  is silently ignored by DRF.
- Serializers extend `DynamicFieldsModelSerializer`; `Meta.create_only_fields` makes model fields read-only on
  update (declared fields such as `password` are not affected). Serializers read the request from `self.request`.
- Views are DRF generics (`RetrieveUpdateAPIView`, `UpdateAPIView`, the `apps.common.viewsets` mixins) with only
  attributes set; no hand-written `post()` / `patch()`. Business rules and state changes live in each app's
  `services.py` (`transaction.atomic()`, `select_for_update()` before check-then-write), called from serializer
  `create()` / `update()`. Admin lists use `prefetch_related` and a deterministic `order_by(..., "-pk")`.
- Project skills `backend-best-practices` and `drf-generics` are in `.claude/skills/` (that folder is gitignored,
  so they are local to this checkout).
- Public vs authenticated: `ActiveAccountJWTAuthentication` (default auth class) treats a deactivated
  user's token as anonymous on public views and rejects it elsewhere. Suspending = `is_active=False`.
- Public listings return only `APPROVED` trainings of `APPROVED` institutes.
- Throttle by scope (`throttle_scope` on the view); rates are in `REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]`.

## Do not touch

- `config/settings/env.py`, `keys/`, `*.pem`, `media/` - gitignored; never commit credentials or keys.
- Existing `migrations/0*.py` - regenerate with `makemigrations`, don't hand-edit.

## Landmines

- **`config/settings/env.py` is gitignored.** A fresh clone won't boot until `env.sample.py` is copied
  to `env.py` and filled in. `DEBUG` is read from the environment in `base.py`, so it must be set before
  `base.py` is imported (`env.py` does this with `os.environ.setdefault`), otherwise debug toolbar is
  missing from `INSTALLED_APPS`/`MIDDLEWARE`.
- **JWT keys are mandatory.** Settings raise `ImproperlyConfigured` if `keys/private_key.pem` or
  `public_key.pem` is missing. Regenerating with `--force` logs everyone out.
- **`USE_TZ = True`, `TIME_ZONE = "Asia/Kathmandu"`.** Never call `.date()` or `.time()` on
  `timezone.now()` (gives the UTC day); use `timezone.localdate()` / `localtime()`.
- **Redis must be running** for `CACHES` (django-redis), throttling and `qcluster`.
  The default `REDIS_URL` is `redis://localhost:6379/0`.
- **User constraints live in the database**: a partial unique index allows one `SUPER_ADMIN`, email is unique on `Lower(email)`,
  `User.save()` stores a blank `phone_number` as NULL (it is unique) and derives `is_superuser` / `is_staff` from `role`
  (check constraints back this up), so never set those flags directly. Migration `0002` also moves `username` from a
  CharField to a UUID, so apply it to a database with existing users only after checking that data.
- **`User.username` is a UUID and `first_name`/`last_name` are removed**; login is by email, looked up
  case-insensitively. Django's stock `UserAdmin` references the removed fields, so `apps/users/admin.py` is a
  **read-only** `ModelAdmin` (no add / change / delete, password hidden). Manage users through the API or the
  service functions, never the admin site, which would skip token revocation and the role rules.
- `validate_attachment` reads `settings.ATTACHMENT_MAX_UPLOAD_SIZE`, which is not defined yet; image
  uploads raise `AttributeError` until it is added to `base.py`.

## Open decisions (also in System Design.md)

- Do institutes keep enquiries after the 90-day "My enquiries" window?
- Where the frontend stores access/refresh tokens (memory, `localStorage`, httpOnly cookie).
- Limits for invited institute staff; ownership transfer.
- How an admin's password is reset (the API only lets the Super Admin set the initial password).
- Whether `/admin/` is renamed or restricted at the proxy before production (it is on the default path, no 2FA).
- The Nepal location dataset will be provided by the team; format and repo location still to be agreed.

## Verification

- `python manage.py check` and `python manage.py makemigrations --check --dry-run` before committing.
- Swagger UI at `/api/root/` and Redoc at `/redoc/` - only mounted when `DEBUG=True`. The site root `/` has no route (404).
- Every package under `apps/` needs an `__init__.py`, or test discovery silently finds zero tests.
