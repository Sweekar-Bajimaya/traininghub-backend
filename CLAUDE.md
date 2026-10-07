# traininghub-backend

Django + DRF backend for **TrainingHub**, a Merojob training marketplace. Verified institutes publish
trainings (physical / online / hybrid); admins review them; visitors browse and send enquiries without
an account. The frontend is a separate Next.js project.

## Source of truth

- `docs/Training for Merojob (PRD).md` - product requirements.
- `docs/System Design.md` - architecture and every decision made so far, plus open questions.
  Read it before designing anything; where the PRD and the design prototypes disagree, the decisions
  in System Design.md win.
- `docs/institutes-checklist.md` - the work list `institutes` was built from (decisions assumed, milestones, snippets);
  mirrored in Notion. A record of the plan, not of the code: where they differ, the code wins.
- `docs/catalog-checklist.md` - the work list categories (built as the `catalog` app, since merged into `common`) and
  trainings (`training`) were built from: the
  sixteen decisions, a comparison with the UI, milestones C0 to C6, snippets; mirrored in Notion. A record of the plan,
  like the one above: where they differ, the code wins.
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
- PostgreSQL (`django.contrib.postgres` is installed: `ArrayField`, full-text search). Redis for cache and the django-q2
  broker. SMTP email. Google reCAPTCHA (planned).
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
  Locations are a managed Nepal province/district/municipality list. Search is PostgreSQL full-text (`simple`
  configuration, word-prefix match).
- Trainings (`apps/training/constants.py`): levels `BEGINNER` / `INTERMEDIATE` / `ADVANCED`; duration is a value plus a
  unit (days, weeks, months) and the service derives `duration_weeks`; the schedule is a start / end date plus weekly
  class slots (`TrainingSession.class_days` and times). A training uses a category or a sub-category (two levels).
  Statuses `DRAFT` → `SUBMITTED` → `APPROVED` / `CHANGES_REQUESTED` / `REJECTED`; then `UNPUBLISHED`, `CANCELLED`, and
  `EXPIRED` (set by a daily job after `end_date`). Editing an `APPROVED` / `UNPUBLISHED` training sends it back to
  `SUBMITTED`; only a `DRAFT` can be deleted; only an `APPROVED` institute creates, submits or republishes. Empty
  `seats` means unlimited.
- Institute types (fixed list): Private Training Affiliated, CTEVT Affiliated, Vocational Training, Language School,
  Company, NGO/INGO, Government.
- Institute status workflow: `PENDING` → `APPROVED` / `REJECTED` / `INFO_REQUESTED`; a rejected institute can re-apply
  (`REJECTED` → `PENDING`). Only `APPROVED` institutes are visible publicly. Registration is JSON only (institute, owner,
  at least one location); the owner then logs in (even while `PENDING`) and uploads verification documents. Approval needs at
  least one active location and one document. A suspended institute's staff keep their accounts.
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
  api/v1/urls.py          declares every URL prefix: `user/`, `locations/`, `categories/`, `trainings/`, `institutes/`,
                          `institute/trainings/`, `institute/`, `admin/` (one include per resource group;
                          `admin/` is included once per app)
  common/                 the one shared app (installed, label `common`): base classes and reference data.
                          `models/`: `base.py` (`BaseModel` created_at/modified_at, `SlugModel`), `location.py`,
                          `category.py`; `BaseViewSet` + mixin viewsets, DynamicFields serializers,
                          validators, `utils/` (plain helpers, no models).
                          `Location` (province / district / municipality in one table, denormalised
                          `province` / `district`), management command `load_locations` (data in
                          `common/data/`: provinces.json, districts.json, cities.json), public read-only API
                          under `locations/` (list with filters, detail, cached `tree/`); `Category` (two-level
                          tree, `services.py`), public cached tree under `categories/`, admin API under
                          `admin/categories/` (`users.manage_categories`, no DELETE); starter categories in
                          `common/data/categories.json`, loaded by `load_categories`; `signals.py` clears the
                          tree caches
  users/                  custom User (email login), roles/permissions, JWT auth, `services.py` (admin
                          create/update, suspend, password change), API under `user/` (auth/, me/,
                          admins/, users/{id}/status/), management command `generate_rsa_keys`
  training/               `Training`, `TrainingSession` (weekly slot), `TrainingModule`, `LearningOutcome`;
                          `services.py` (create / edit with the review rule, workflow, search vector, expiry),
                          `tasks.py` (search refreshes, `expire_trainings`), management command `expire_trainings`;
                          APIs: public `trainings/` (filters, prefix search, ordering), portal `institute/trainings/`
                          (nested sessions / modules / outcomes, submit, withdraw, unpublish, republish, cancel,
                          cover), admin `admin/trainings/` (approve, request-changes, reject)
  institutes/             Institute, members, invitations, documents, locations, gallery; `services.py` (status
                          workflow, registration, locations, documents, gallery, staff invitations), `tasks.py`
                          (invitation email), private `storage.py`; APIs: public `institutes/`, portal `institute/`
                          (register, profile, locations, documents, gallery, staff, invitations, resubmit), admin
                          `admin/institutes/` (review actions, document review and download)
docs/  design/            see "Source of truth"
```

Planned apps (not created yet): `enquiries`, `notifications`, `analytics`; later `applications`,
`learners`, `reviews`.
Each app follows `models.py`, `admin.py`, `migrations/`, `api/v1/{serializers,views,urls}.py`
(`apps/users/api/v1/urls/users.py` and the modules in `apps/common/api/v1/urls/`, `apps/institutes/api/v1/urls/` and
`apps/training/api/v1/urls/` are the package form: one module per URL group; `apps/common/models/` likewise has one
module per model group, its `__init__.py` imports them all so every model registers, and callers import by module path,
e.g. `apps.common.models.location`).

## Commands

Run through the venv (`source .venv/bin/activate`, or prefix `.venv/bin/python`).

| task | command |
|---|---|
| install | `pip install -r requirements/dev.txt` |
| JWT keys (once per checkout) | `python manage.py generate_rsa_keys` (writes `keys/`, gitignored) |
| check | `python manage.py check` |
| migrate | `python manage.py makemigrations` then `python manage.py migrate` |
| load locations | `python manage.py load_locations` (upserts from `apps/common/data/`; safe to re-run, never re-activates a retired location) |
| load categories | `python manage.py load_categories` (the UI's 13 categories and 22 sub-categories from `apps/common/data/categories.json`; only creates missing rows, never re-activates or overwrites an admin's change) |
| expire trainings | `python manage.py expire_trainings` (sets `EXPIRED` after `end_date`; safe any time). Schedule it daily: Django admin > Django Q > Scheduled tasks, function `apps.training.tasks.expire_trainings` |
| dev server | `python manage.py runserver` |
| task worker | `python manage.py qcluster` (needs Redis); without it, staff invitation emails and search-vector refreshes (institute rename, category rename or move, location change) stay queued |
| tests | `python manage.py test` - `apps/users/tests.py` (User constraints, users API) `apps/common/tests/` (Location and Category constraints, loaders, locations and categories API), `apps/institutes/tests/` (constraints, services, public / admin / portal API, end-to-end journey) and `apps/training/tests/` (constraints, services and workflow, search, public / portal / admin API, lifecycle, query counts); needs Postgres where the test DB can be created, and Redis for throttling and the tree caches |
| lint / typecheck | unverified - pylint is in dev.txt but there is no config |

## Conventions

- Models extend `apps.common.models.base.BaseModel`; add `SlugModel` (same module) for public-URL objects (needs `name`
  or `title`). Import `Location` and `Category` from `apps.common.models.location` / `.category`.
- `common` holds base classes and reference data that several apps point to (today the locations and categories).
  Anything with its own workflow (enquiries, notifications, analytics) gets its own app. `common/models/`,
  `constants.py`, `utils/` and `validators.py` never import another domain app (every app imports them, so it would be a
  cycle); only `common/api/` and `common/tests/` reach into `users` and `institutes`.
- Viewsets extend `apps.common.viewsets.BaseViewSet`. Per-action permissions go in `permission_class_mapper`
  (`{"create": [...]}`); an empty list means public. Plural `permission_classes` elsewhere - the singular
  is silently ignored by DRF.
- Serializers extend `DynamicFieldsModelSerializer`; `Meta.create_only_fields` makes model fields read-only on
  update (declared fields such as `password` are not affected). Serializers read the request from `self.request`.
- Views are DRF generics (`RetrieveUpdateAPIView`, `UpdateAPIView`, the `apps.common.viewsets` mixins) with only
  attributes set; no hand-written `post()` / `patch()`. Business rules and state changes live in each app's
  `services.py` (`transaction.atomic()`, `select_for_update()` before check-then-write), called from serializer
  `create()` / `update()`. Admin lists use `prefetch_related` and a deterministic `order_by(..., "-pk")`.
- URL prefixes live only in `apps/api/v1/urls.py`; an app's URL module is relative to its prefix. A router
  registered with an empty prefix must be a `SimpleRouter` (`DefaultRouter` adds a root view at `""`).
- Filter on a foreign key with `NumberFilter(field_name="<fk>_id")`, not django-filter's default
  `ModelChoiceFilter`, which runs an extra query per request to check that the row exists.
- Institute-scoped views mix in `InstituteScopedMixin` and use `IsInstituteMember` / `IsInstituteOwner`
  (`apps/institutes/permissions.py`): the queryset is filtered to the caller's institute, so another institute's row is a
  404, not a 403. Staff can do everything except manage staff and invitations (owner only).
- Read settings with `from django.conf import settings`, never `from config import settings` (the raw module ignores
  `override_settings`). In tests clear throttles with `cache.delete_pattern("throttle_*")`, never `cache.clear()`: the
  same Redis database holds the django-q broker.
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
- **The location and category trees are cached in Redis with no expiry** (`common:location-tree:v1`,
  `common:category-tree:v1`). `post_save` / `post_delete` (and `load_locations`) clear them; `QuerySet.update()` and
  `bulk_update()` do not, so delete the key yourself after those.
- **Trainings carry a stored search vector.** Write them through `apps/training/services.py` (it rebuilds the vector and
  `duration_weeks`); a direct `create()` / `update()` leaves search stale. Renaming an institute, renaming or moving a
  category and changing a location's municipality refresh the affected trainings through queued tasks, so they need
  `qcluster`.
- **Expiry only happens if `expire_trainings` is scheduled** (daily); otherwise past trainings stay `APPROVED` and
  public.
- **`select_for_update()` with a nullable `select_related`** fails in Postgres ("FOR UPDATE cannot be applied to the
  nullable side of an outer join"); the training services lock with `of=("self",)`.
- An `InstituteLocation` cannot be deactivated while a training that is not `CANCELLED` / `EXPIRED` uses it.
- **Verification documents are private.** They are stored under `PRIVATE_MEDIA_ROOT` (`private_media/` in the project
  root, gitignored; note `BASE_DIR` is `config/`, so it is `BASE_DIR.parent`), `PrivateStorage` raises on `.url`, and
  they are only served by `private_file_response` after a permission check. `InstituteDocument` is deliberately not
  registered in the admin site. Upload validators check extension and size only (`INSTITUTE_UPLOAD_MAX_BYTES`, 5 MB).
- **Staff invitation tokens** are stored as a sha256 hash only; the raw token goes into the queued email task with
  `save=False`, so django-q does not keep it in its results table. The link uses `FRONTEND_BASE_URL`.
- `validate_attachment` reads `settings.ATTACHMENT_MAX_UPLOAD_SIZE`, which is not defined yet; image
  uploads raise `AttributeError` until it is added to `base.py`.

## Open decisions (also in System Design.md)

- Do institutes keep enquiries after the 90-day "My enquiries" window?
- Where the frontend stores access/refresh tokens (memory, `localStorage`, httpOnly cookie).
- How an admin's password is reset (the API only lets the Super Admin set the initial password).
- Whether `/admin/` is renamed or restricted at the proxy before production (it is on the default path, no 2FA).
- The team still has to document where the location data came from.
- Who edits Nepal locations at runtime (today only `load_locations` writes them; the admin site is read-only).
- Whether enquirers are told when a training is cancelled, and whether "Instructor name" search is needed.
- The UI's registration number / contact fields on `Institute`, and the featured flag / view counts for relevance sort.

## Verification

- `python manage.py check` and `python manage.py makemigrations --check --dry-run` before committing.
- Swagger UI at `/api/root/` and Redoc at `/redoc/` - only mounted when `DEBUG=True`. The site root `/` has no route (404).
- Every package under `apps/` needs an `__init__.py`, or test discovery silently finds zero tests.
