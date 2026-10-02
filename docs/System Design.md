# TrainingHub — Backend System Design (DRAFT v0.5)

Sources: `docs/Training for Merojob (PRD).md`, `design/` (Training Hub, Institute Portal, Admin Console).
Where the PRD and the design prototypes disagree, the decisions in this document win.
Items marked **[OPEN]** are unresolved; nothing marked OPEN has been assumed.
The design is expected to change as open questions (section 8) are answered during development.
The reviewed design with class diagrams per subsystem is in the Notion page "TrainingHub Backend – System Design Review".

## 1. Decisions made

| Topic | Decision |
| :---- | :---- |
| Stack | Django 5.2 + DRF, PostgreSQL, Next.js frontend (separate project) |
| Learner interaction (MVP) | Anonymous **Enquiry** (name, phone, optional email). No learner login |
| Learner interaction (phase 2) | **Application** (approve / reject / capacity). Schema must allow adding it without a rewrite |
| Who logs in | Institute staff and admins only |
| Providers | Verified **Institutes** only (no individual instructors) |
| Institute users | An Institute has many staff users (owner + staff). The owner can invite more staff after registration |
| Staff membership | A staff user belongs to **one institute only** (unique `InstituteMember.user`) |
| Training location | A physical / hybrid training is held at **exactly one** of its institute's locations |
| Availability | A training is available while `seats` minus its `CONVERTED` enquiries is above zero. An institute-maintained seat count may be added later |
| Institute locations | An institute can have **several locations**; each physical / hybrid training is held at one of them (see 3.3) |
| Roles | `SUPER_ADMIN` (exactly one), `ADMIN`, `INSTITUTE_STAFF` |
| Admin permissions | A Super Admin can do everything and grants admins limited rights per area (see 3.1) |
| Auth | Own accounts, email + password. JWT via simplejwt, RS256 with a key pair (`manage.py generate_rsa_keys`), Bearer header. Suspended accounts (`is_active=False`) are rejected at the authentication layer |
| Public user registration | None. Institute owners are created by institute registration; admins are created by the Super Admin, who sets the initial password. A "set your own password" email to the new admin comes later, with `notifications` |
| Frontend calls the API | Directly from the **browser** (may change). Needs a CORS allow-list; throttling can key on client IP (proxy headers must be configured); reCAPTCHA token comes from the browser |
| Notifications | Email (SMTP) at MVP. SMS not planned |
| Async jobs / cache | django-q2 + Redis (Redis broker) |
| Files | Local `media/` now, S3 later. Use Django's storage API only; no hard-coded paths |
| Abuse protection | Google reCAPTCHA (verified server-side) + DRF rate limiting on public submit endpoints |
| Training mode | `PHYSICAL`, `ONLINE`, `HYBRID` |
| Reviews & ratings | **Out of MVP** (needs learner login). `reviews` app deferred |
| "My enquiries" | Tracked by a browser-stored device token; lost if browser data is cleared. A device sees its enquiries for **90 days**. Revisit when learner login is added |
| Location data | The team keeps the Nepal location data itself and documents where it came from. The files are in `apps/catalog/data/` (`provinces.json` 7, `districts.json` 77, `cities.json` 752 local governments; checked: no orphan parents, no duplicate `(district, name)`). Loaded with a `load_locations` management command, not a fixture |
| Enquiry statuses | `NEW`, `CONTACTED`, `CONVERTED`, `CLOSED`. Kept easy to change later |
| Location | Managed list of Nepal provinces / districts / **municipalities**. The third level is called Municipality in code and UI and includes rural municipalities. Names are kept exactly as they appear in the data (no normalising of "Province" / "Pradesh") |
| API URL prefixes | Every prefix is declared in `apps/api/v1/urls.py`, one include per resource group (`user/`, `locations/`, `institutes/` public, `institute/` portal, `admin/` console); an app's URL module is relative to its prefix |
| Institute re-application | A rejected institute can re-apply for verification (`REJECTED` → `PENDING`) |
| Institute visibility | Only `APPROVED` institutes, and their approved trainings, appear on the public site. Pending, info-requested, rejected and suspended institutes are not visible |
| Institute type | A fixed list, required at registration: Private Training Affiliated, CTEVT Affiliated, Vocational Training, Language School, Company, NGO/INGO, Government |
| Institute profile | Plain columns on `Institute` (option A), not a generic items table. The gallery is a small separate table |
| Institute registration | One JSON request creates the institute (`PENDING`), its owner and optional locations. The owner can log in at once and uploads verification documents afterwards. Approval needs at least one active location and one document |
| Verification documents | pdf, jpg or png, max 5 MB, stored privately (never a URL), streamed only to the owning institute and to admins with `manage_institutes`. Which documents are required is not enforced beyond "at least one" |
| Staff powers | Staff do everything except manage staff and invitations (owner only). No ownership transfer. Removing staff deactivates the account and revokes its refresh tokens |
| Suspended institutes | Staff keep their accounts and can log in; the institute is hidden from the public site |
| Staff invitations | Valid 7 days; email sent with Django `send_mail`, queued with django-q2 after commit (needs `qcluster`); only a sha256 hash of the token is stored; the full `notifications` app comes later |
| Institute name | Not unique; the slug is |
| Pricing | Single fee, NPR only. Discounts may come later |
| Time zone | All trainings in NPT (`Asia/Kathmandu`), including online. Multiple sessions allowed |
| Certification | Free-text field managed by the institute |
| Search | PostgreSQL full-text search |
| Merojob SSO / integration | On hold |
| Deployment | Docker, to be set up after development starts |

## 2. Apps (Django)

| App | Responsibility | State |
| :---- | :---- | :---- |
| `common` | BaseModel, SlugModel, shared serializers / viewsets / validators | exists |
| `users` | User, roles, permissions, auth endpoints, admin team | in progress |
| `institutes` | Institute, locations, staff membership and invitations, verification documents, profile columns, gallery, status workflow | built (on defaults, see section 8) |
| `catalog` | Category (tree), Location (managed Nepal list), Training, sessions, curriculum modules, learning outcomes | in progress: `Location`, its loader and API are built |
| `enquiries` | Enquiry, status workflow, device tracking | planned |
| `notifications` | In-app notifications + email dispatch (django-q2 tasks) | planned |
| `analytics` | View counters, enquiry stats for dashboards | planned |
| `api` | Versioned URL routing (`/api/v1/`) | exists |
| `reviews` | Deferred (post-MVP) | deferred |

Phase 2: `applications` (reuses Training capacity fields), `learners`.

## 3. Core entities (first pass)

- **User**: email (login, unique case-insensitively), UUID `username`, full_name, phone_number (optional, unique), gender, profile_picture, role, `is_active` (account status). `first_name` / `last_name` are removed.
- **Institute**: name, type, established year, description, logo, status (`PENDING`, `APPROVED`, `REJECTED`, `INFO_REQUESTED`, `SUSPENDED`), status_reason, profile columns (about, CEO name and message, website, contact email / phone, social links; exact list to be confirmed). `registered_at` is `created_at`. A gallery table holds the images.
- **InstituteLocation**: institute, location (managed Nepal list), address, optional contact phone / map label, `is_main` (at most one main office per institute), is_active.
- **InstituteMember**: user (unique: one institute per user), institute, role (`OWNER`, `STAFF`). One `OWNER` per institute (derived, to confirm).
- **InstituteInvitation**: institute, email, role, token, status, expires_at (owner invites staff; the invite email is sent via `notifications`).
- **InstituteDocument**: institute, name, file, status (pending / verified / rejected).
- **Category**: name, parent (sub-category), is_active.
- **Location**: province / district / municipality hierarchy (managed list): one table with `level`, `parent`, a `code` (id from the source data), `type` for municipalities (metropolitan, sub-metropolitan, municipality, rural municipality), `is_active`, and denormalised `province` / `district` set in one place.
- **Training**: institute, category, title, short description / overview, mode (`PHYSICAL`, `ONLINE`, `HYBRID`), level, duration, fee (NPR), seats, start / end date, registration deadline, `institute_location` (nullable FK to one of the same institute's locations; empty for `ONLINE`, required for `PHYSICAL` / `HYBRID`), eligibility, certification (text), cover image, status (`DRAFT`, `SUBMITTED`, `APPROVED`, `CHANGES_REQUESTED`, `REJECTED`, `UNPUBLISHED`, `CANCELLED`, `COMPLETED`), review feedback.
- **TrainingModule** (curriculum), **LearningOutcome**, **TrainingSession** (date, start / end time, NPT).
- **Enquiry**: training, name, phone, email (optional), message, status, device_token, created_at. "My enquiries" returns only a device's enquiries from the last 90 days; older ones stay visible to the institute.
- **Notification**: recipient user, type, body, read_at.
- **Proposed (derived, to confirm)**: `AuditLog` (actor, action, target, changes; append-only), `TrainingViewDaily` (training, day, views).
- **Seats**: `available_seats = seats - count(CONVERTED enquiries)`. A training with no `seats` value is treated as unlimited (assumption, to confirm). Converting an enquiry is rejected once converted enquiries reach `seats`, with the training row locked.

All models extend `BaseModel`. Public listings return only `APPROVED` trainings of `APPROVED` institutes.

### 3.1 Users, roles and permissions

- There is exactly **one Super Admin**: `is_superuser=True`, passes every permission check, created with `createsuperuser` (which sets `role=SUPER_ADMIN`). No API creates another one; the database enforces it with a unique constraint on `role = SUPER_ADMIN`.
- An **Admin** has `role=ADMIN`, `is_staff=True`, and only the permissions the Super Admin granted. The Super Admin sets the initial password when creating the admin. Permissions are Django permissions declared on `User.Meta.permissions` and checked with `has_perm`:

| Permission | Allows |
| :---- | :---- |
| `users.manage_enquiries` | Monitor and handle enquiries |
| `users.manage_account_status` | Activate / suspend accounts |
| `users.manage_institutes` | Review institutes (approve, reject, request info, suspend) |
| `users.manage_trainings` | Review trainings (approve, request changes, reject) |
| `users.manage_categories` | Manage categories and locations |
| `users.manage_admins` | Create / edit admins and their permissions. **Not grantable**: Super Admin only |

- **Institute staff** have `role=INSTITUTE_STAFF` and can only touch their own institute's data (object-level ownership checks).
- An admin or staff user is never created from client-supplied `role` or `is_staff`; the role is set by the server.
- `User.save()` derives `is_superuser` (role `SUPER_ADMIN`) and `is_staff` (role `SUPER_ADMIN` or `ADMIN`) from `role`; check constraints reject any other combination.
- `is_platform_admin` is true for superusers and for roles `SUPER_ADMIN` / `ADMIN`.
- Suspending an account sets `is_active=False` and also blacklists that user's outstanding refresh tokens.

### 3.2 Users API (`/api/v1/user/`)

| Endpoint | Who | Notes |
| :---- | :---- | :---- |
| `POST auth/login/` | public | Throttled (`login` scope). Returns access, refresh and the user's profile |
| `POST auth/refresh/` | public | Throttled (`token_refresh` scope) |
| `POST auth/logout/` | authenticated | Blacklists the refresh token |
| `GET/PATCH me/` | authenticated | Own profile. `email` and `role` are read-only |
| `PUT me/password/` | authenticated | Old password required; Django password validators applied |
| `admins/` (CRUD) | `manage_admins` | Create / edit admins, set the initial password and the permissions granted. Role forced to `ADMIN` |
| `PATCH users/{id}/status/` | `manage_account_status` | Suspend / activate. Not yourself, never the Super Admin; only the Super Admin may change an admin's status. Suspending revokes the user's refresh tokens |

Implemented in `apps/users`. `admins/` has no DELETE (suspend instead); `PATCH admins/{id}/` edits name, phone, gender, picture and the granted permissions, but not `email` or `password`. Changing your own password revokes your refresh tokens, and the new password must differ from the old one. Throttling uses the `login` and `token_refresh` scopes.

### 3.3 Institute locations

- A location is picked from the managed `Location` list (province → district → municipality) and given an address, so an institute can run trainings in several cities.
- A training points to one `InstituteLocation` of its own institute (validated in the model / serializer). Online trainings have none.
- Public location filtering uses the training's location (city, district or province). The institute card in the design (city, province) is derived from its main office.
- Deactivating or deleting a location must not silently orphan trainings that use it.

### 3.4 Engineering conventions (the `users` app already follows them)

- Each app gets `services.py` (business rules, transactions, state changes) and `selectors.py` (read queries with `select_related` / `prefetch_related`). Views and serializers stay thin; status changes go only through services.
- State machines (institute, training, enquiry) are one allowed-transitions table each; illegal moves raise a validation error.
- Workflow actions run in `transaction.atomic()` with `select_for_update()`; emails are queued with `transaction.on_commit`.
- Invariants are also database constraints: one Super Admin, one main active location per institute, one owner per institute, training mode / location check, case-insensitive unique email.
- List endpoints avoid N+1 queries (query-count tests); public lists use cursor pagination; Redis caches only reference data and short-lived facets.
- Views use DRF generics / the `common` mixin viewsets; logic sits in serializer `create()` / `update()` calling the service.
- A database `IntegrityError` that slips past validation returns 409, not 500.

### 3.5 Institutes API (built)

| Endpoint | Who | Notes |
| :---- | :---- | :---- |
| `POST institute/register/` | public | Throttled (`institute_register`, 5/hour). Creates the institute (`PENDING`), its owner and optional locations in one transaction. `status`, `role` and `slug` in the payload are ignored |
| `POST institute/invitations/accept/` | public | Throttled (`invitation_accept`, 10/hour). Creates a staff account from a valid, unexpired, unused token |
| `GET institutes/`, `institutes/{slug}/` | public | `APPROVED` only; filter `type`, search `name`; constant number of queries; the card shows the main location with district and province |
| `GET, PATCH institute/profile/`, `POST institute/resubmit/` | institute staff | `resubmit` moves `INFO_REQUESTED` or `REJECTED` back to `PENDING` |
| `institute/locations/` (list, create, patch) and `.../{id}/set-main/`, `.../deactivate/` | institute staff | Only active municipalities; the first location is main; the main one cannot be deactivated |
| `institute/documents/` (list, upload) and `.../{id}/download/` | institute staff | Multipart; the response never contains the file path; downloads are streamed after a membership check |
| `institute/gallery/` (list, create, patch, delete) and `.../reorder/` | institute staff | Public images; reorder takes every id exactly once |
| `institute/staff/` (list, delete), `institute/invitations/` (list, create, delete) | owner only | Removing staff deactivates the account and revokes its refresh tokens; the invitation token is never returned |
| `admin/institutes/` and `.../{id}/{approve,reject,request-info,suspend,reinstate}/` | `users.manage_institutes` | Reject, request-info and suspend need a reason; approve needs one active location and one document |
| `admin/institutes/{id}/documents/{doc}/` (PATCH) and `.../download/` | `users.manage_institutes` | Document review: `VERIFIED` or `REJECTED` |

Rows of another institute return 404. Verification documents live under `PRIVATE_MEDIA_ROOT`, outside `MEDIA_ROOT`, and never get a URL. Invitation tokens are stored as a sha256 hash only.

## 4. Key workflows

1. **Institute onboarding**: register (one JSON request: institute, owner, optional locations; the owner can log in right away) → upload verification documents in the portal → `PENDING` → admin approves / rejects / requests more info / suspends → email to the institute. A rejected institute can re-apply (`REJECTED` → `PENDING`) after updating its details. Only `APPROVED` institutes are visible publicly.
2. **Training lifecycle**: institute drafts → submits → admin approves / requests changes / rejects → published (public) → unpublish / cancel / complete.
3. **Enquiry**: public submit (captcha + throttle) → institute notified (email + dashboard) → institute updates status → admin sees conversion stats. The visitor's device sees it under "My enquiries" for 90 days.
3a. **Staff invitation**: institute owner invites by email → invitee accepts and sets a password → becomes `INSTITUTE_STAFF` of that institute.
4. **Discovery**: search (title, institute, keywords) + filters (category, sub-category, mode, location, price, start date, duration, availability, institute) using PostgreSQL full-text search and django-filter.

## 5. API surface (v1, sketch)

- **Public**: `GET trainings`, `trainings/{slug}`, `categories`, `locations`, `institutes`, `institutes/{slug}`, `POST enquiries`, `GET my-enquiries` (by device token, last 90 days).
- **Built (institutes):** see section 3.5 for `institutes/`, `institute/` and `admin/institutes/`.
- **Built:** `GET locations/` (filters `level`, `parent`, `province`, `district`; `search` on name; only active rows; one query, unpaginated, about 850 rows), `GET locations/{id}/`, `GET locations/tree/` (province > district > municipality, cached in Redis until a location changes).
- **Institute**: auth, profile + documents + gallery + locations, staff invitations, CRUD trainings, submit for review, enquiries list / update, dashboard stats.
- **Admin**: institute review actions, training review actions, categories and locations CRUD, enquiries monitor / export, admin team, platform settings.

## 6. Non-functional

- DRF throttling by scope, backed by Redis; captcha verification server-side. Because the browser calls the API directly, throttling can key on client IP (and phone for enquiries); the deployment proxy must pass the real client IP.
- Caching: the location tree is cached in Redis with no expiry and cleared when a `Location` is saved or deleted, and by `load_locations`.
- CORS is an explicit allow-list of frontend origins (not allow-all) outside development.
- Tokens live in the browser, so keep access tokens short-lived and decide where the refresh token is stored (open question).
- Permissions by role + Django permissions + object ownership.
- Audit log for admin actions (the design says "Activity is logged"). Not built yet; `users/services.py` has TODO markers where it will be called.
- Django admin site: users are read-only there, because edits would skip the services (token revocation, role rules). `/admin/` is still on the default path with no 2FA; restrict it before production.
- Swagger via drf-yasg (debug only). Settings split (`base` / `env`), secrets from `env.py` and environment variables.
- Cleaned repo hygiene: `.gitignore` covers `.venv`, `__pycache__`, `media/`, `keys/`, `*.pem`, `config/settings/env.py`.

## 7. Build order

1. [x] Repo hygiene, settings (Redis cache + django-q2, SMTP, reCAPTCHA setting, throttle scopes), exception handler, JWT auth class.
2. [x] `users`: model, manager, permission classes, services, serializers, views and URLs, migration, tests. The Django admin site for users is read-only.
2a. [x] `users` hardening: single Super Admin constraint, case-insensitive unique email, `blank=True` on `phone_number`.
3. [x] `institutes`: models and constraints, services, public / admin / portal APIs and 131 tests (the whole suite is 174). The decisions it was built on were confirmed on 2026-10-02.
4. [ ] `catalog`: `Location` model, the `load_locations` loader and the public locations API are **done** (built before `institutes`, which depends on them). Categories, trainings and sessions are still to do.
5. [ ] `enquiries`, `notifications`, `analytics`.
6. [ ] Search, filters and public API polish.
7. [ ] Docker.

## 8. Open questions

1. **Enquiry retention**: after 90 days an enquiry disappears from the visitor's "My enquiries". Does the institute keep it indefinitely, or should old enquiries be deleted too?
2. **Browser auth storage**: where does the frontend keep the access and refresh tokens (memory, `localStorage`, or an httpOnly cookie)? This affects security and CORS settings.
3. **Completion / cancellation**: set manually by the institute, or does the system complete a training after `end_date`? Are enquirers told about a cancellation?
4. **Category depth**: strictly two levels or arbitrary? Only admins with `manage_categories` create them?
5. **Enquiry status moves**: free or forward-only? Who changes them: institute staff only, or admins with `manage_enquiries` too?
6. **Enquiries after the deadline**: allowed after the registration deadline or the start date?
7. **Search**: the PRD lists "Instructor Name" but there is no instructor field. Add a text field on `Training` or drop it? Full-text language configuration (English, `simple`, Nepali script)?
8. **Redis outage**: should throttled / captcha-protected enquiry submit fail closed or open?
9. **Editing an approved training**: does it need re-review, or only for some fields (fee, dates)?
10. **Training levels**: the fixed values for training `level` are still needed.
11. **Duration**: independent field or computed from sessions / dates? Filtering needs a numeric unit.
12. **Notifications**: which events notify whom (in-app and email)? Is the enquirer ever emailed?
13. **Reports**: which provider "Reports" / "Sessions" dashboard items belong to the MVP ("Participants" is phase 2)?
14. **PRD wording**: the Problem Statement and some user stories describe the later phase, and the "Training Instructors" list repeats the Learner list. Treat as phase 2 / ignore?
15. **Privacy**: retention, consent and export rules for enquirer name / phone.
16. **Unlimited seats**: confirm that a training without a `seats` value counts as always available.
17. **Admin password reset**: the Super Admin sets an admin's initial password, but nothing resets it later (`PATCH admins/{id}/` rejects `password`). Add an endpoint, or the "set your own password" email with `notifications`?
18. **Admin site access**: rename `/admin/`, restrict it at the proxy, or add 2FA before production?
19. **Locations at runtime**: may admins with `manage_categories` edit locations through an API, or does only `load_locations` write them? Until then the admin site is read-only and the loader is the only writer.
20. **Editing an approved institute**: today an institute's staff can change the profile of an `APPROVED` institute without re-review (as for trainings, question 9). Should some fields (name, type) need re-approval?

## 9. Decision log (answered questions)

- Reviews: skipped for now; needs login first. Hybrid mode: included. "My enquiries": browser-stored token accepted. Enquiry statuses: `NEW` / `CONTACTED` / `CONVERTED` / `CLOSED`, changeable later.
- Admin roles: Super Admin does everything and grants limited permissions (e.g. handling enquiries, account status) to other users.
- Location: managed Nepal list. Price: single fee in NPR. Search: PostgreSQL full-text. Time: NPT everywhere, multiple sessions. Certification: text field.
- Merojob integration: on hold. Email: SMTP. Captcha: reCAPTCHA. Deployment: Docker, later.
- Learner model: enquiry now, application in phase 2. Auth: only institutes and admins log in. Providers: institutes only, with multiple staff users. Services: email, Redis + django-q2, local media (S3 later). Abuse protection: captcha + rate limiting. Stale `authentication.py` from another project: rewritten for TrainingHub.
- Admin creation: the Super Admin sets the initial password; a "set your own password" email is sent later with `notifications`. There is exactly one Super Admin. Institute owners can invite more staff. The frontend calls the API from the browser (may change). "My enquiries" is kept 90 days per device. The Nepal location list already exists. An institute can have several locations and trainings are held at one of them.
- Answered (review of the Notion design page, 2026-10-01): a training is held at **exactly one** institute location. A staff member belongs to **one institute only** (unique `InstituteMember.user`). The "availability" filter means **seats minus `CONVERTED` enquiries is above zero** (option b, confirmed); an institute-maintained seat count (option c) may be added later. The Nepal location file will be provided by the team. Many remaining questions will be answered during development, so expect the design to change.
- Users API (2026-10-01): admin management is Super Admin only and admins are suspended, not deleted. Only the Super Admin may change an admin's status (our assumption, kept). The user admin site is read-only; the API and services are the only way to change users. `me/password/` is `PUT`.
- Institutes and locations (2026-10-02): the third location level is **Municipality**, and names stay as in the data. The team keeps the location data and documents its source. The institute type is a fixed list the team will provide. The institute profile uses plain columns (option A). A rejected institute can re-apply (`REJECTED` → `PENDING`); only `APPROVED` institutes are publicly visible.
- Institute types and location data (2026-10-02): the seven institute types are fixed (see the decisions table). The location data files are in `apps/catalog/data/`; the empty `catalog` app is scaffolded and installed, its models and loader are not written yet.
- Locations built (2026-10-02): one `Location` table, loaded by `load_locations` (7 provinces, 77 districts, 752 municipalities), public read-only API under `locations/`. URL prefixes are declared only in `apps/api/v1/urls.py`.
- Institutes built (2026-10-02): models and constraints, services, public / admin / portal APIs, 131 tests. The nine defaults it was built on (staff powers, suspended staff login, locations at registration, documents, invitation email and expiry, unique name, profile columns, URL split) were confirmed on 2026-10-02 by ticking "Confirm the nine decisions" in the Notion work list; they are in the decisions table above.
