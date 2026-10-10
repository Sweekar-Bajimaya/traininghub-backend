# TrainingHub — Backend System Design (DRAFT v0.6)

Sources: `docs/Training for Merojob (PRD).md`, `design/` (Training Hub, Institute Portal, Admin Console).
Where the PRD and the design prototypes disagree, the decisions in this document win.
Items marked **[OPEN]** are unresolved; nothing marked OPEN has been assumed.
The design is expected to change as open questions (section 8) are answered during development.
The reviewed design with class diagrams per subsystem is in the Notion page "TrainingHub Backend – System Design Review".

## 1. Decisions made

| Topic | Decision |
| :---- | :---- |
| Stack | Django 5.2 + DRF, PostgreSQL, Next.js frontend (separate project) |
| Learner interaction (MVP) | Anonymous **Enquiry** (name, phone, optional email, message, preferred time; an `ENQUIRY` or an `INTEREST`). No learner login |
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
| Frontend calls the API | Directly from the **browser** (may change). Needs a CORS allow-list; throttling can key on client IP (proxy headers must be configured); the `X-Device-Token` header (see "My enquiries") is in the CORS allow-list |
| Notifications | Email (SMTP) at MVP. SMS not planned. A new enquiry sends no alert yet (decided 2026-10-10); the portal shows the new count from `institute/enquiries/summary/` |
| Async jobs / cache | django-q2 + Redis (Redis broker) |
| Files | Local `media/` now, S3 later. Use Django's storage API only; no hard-coded paths |
| Abuse protection | DRF rate limiting on public submit endpoints. The enquiry form has **no captcha for now** (decided 2026-10-10): 10 a hour per client IP and 3 a day per phone number, plus one open enquiry per phone number and training. `RECAPTCHA_SECRET_KEY` exists in settings but nothing verifies it yet |
| Training mode | `PHYSICAL`, `ONLINE`, `HYBRID` |
| Reviews & ratings | **Out of MVP** (needs learner login). `reviews` app deferred |
| "My enquiries" | Tracked by a device token: a random UUID4 the browser makes and sends in the `X-Device-Token` header (a missing, malformed or non-v4 token is a 400). Lost if browser data is cleared. A device sees its enquiries for **90 days**, with a plain-language status and never the phone number or notes. Revisit when learner login is added |
| Location data | The team keeps the Nepal location data itself and documents where it came from. The files are in `apps/common/data/` (`provinces.json` 7, `districts.json` 77, `cities.json` 752 local governments; checked: no orphan parents, no duplicate `(district, name)`). Loaded with a `load_locations` management command, not a fixture |
| Enquiry statuses | The portal's seven: `NEW`, `CONTACTED`, `FOLLOW_UP`, `INTERESTED`, `CONVERTED`, `NOT_INTERESTED`, `CLOSED`. Any status can move to any other; institute staff and the owner both change them. Only `CONVERTED` is guarded, by the seats (see Seats) |
| Location | Managed list of Nepal provinces / districts / **municipalities**. The third level is called Municipality in code and UI and includes rural municipalities. Names are kept exactly as they appear in the data (no normalising of "Province" / "Pradesh") |
| API URL prefixes | Every prefix is declared in `apps/api/v1/urls.py`, one include per resource group (`user/`, `locations/`, `categories/`, `trainings/`, `institutes/` public, `institute/trainings/` and `institute/` portal, `admin/` console); an app's URL module is relative to its prefix. `admin/` is a single include of `apps/control_panel` |
| Institute re-application | A rejected institute can re-apply for verification (`REJECTED` → `PENDING`) |
| Institute visibility | Only `APPROVED` institutes, and their approved trainings, appear on the public site. Pending, info-requested, rejected and suspended institutes are not visible |
| Institute type | A fixed list, required at registration: Private Training Affiliated, CTEVT Affiliated, Vocational Training, Language School, Company, NGO/INGO, Government |
| Institute profile | The institute's own details are columns on `Institute` (name, type, registration number, established year, description, logo). The required contact person, the optional CEO profile and the social links are small tables of their own (`InstituteContact`, `InstituteCEO`, `InstituteSocialLink`), edited through their own portal endpoints, as is the gallery. Not a generic items table |
| Institute registration | One JSON request creates the institute (`PENDING`), its owner, its contact person and at least one location. The owner's email and password are the institute's login, and the email must be verified first with a one-time code (next row). The owner can log in at once and uploads verification documents afterwards. Approval needs at least one active location and one document |
| One-time codes (OTP) | Six digits from `secrets`, valid 5 minutes, kept only in the Redis cache (never in the database or in a queued task's arguments). One code per address per 60 seconds; 5 wrong guesses lock a code; a right code does not count as a guess. A code is bound to its purpose (`password_reset`, `institute_registration`) and its address, which is lower-cased. Sent by email through a django-q task that gets only the address and reads the code when it runs (needs `qcluster`). Registration checks the code before it writes anything and uses it up in the same transaction |
| Verification documents | pdf, jpg or png, max 5 MB, stored privately (never a URL), streamed only to the owning institute and to admins with `manage_institutes`. Which documents are required is not enforced beyond "at least one" |
| Staff powers | Staff do everything except manage staff and invitations (owner only). No ownership transfer. Removing staff deactivates the account and revokes its refresh tokens |
| Suspended institutes | Staff keep their accounts and can log in; the institute is hidden from the public site |
| Staff invitations | Valid 7 days; email sent with Django `send_mail`, queued with django-q2 after commit (needs `qcluster`); only a sha256 hash of the token is stored; the full `notifications` app comes later |
| Institute name | Not unique; the slug is |
| Pricing | Single fee, NPR only. Discounts may come later |
| Time zone | All trainings in NPT (`Asia/Kathmandu`), including online |
| Certification | Free-text field managed by the institute |
| Search | PostgreSQL full-text search, `simple` configuration (no stemming), word-prefix match over title, institute, category and sub-category, skills, short description, overview, municipality and district, module titles. Best match first unless `ordering` is given |
| Categories | Two levels (category, sub-category), managed by admins with `manage_categories`, with an icon and a colour hue. A training uses a category **or** a sub-category. Starter data is the UI's 13 categories (`load_categories`) |
| Training levels | `BEGINNER`, `INTERMEDIATE`, `ADVANCED` (the UI's three) |
| Training duration | A number plus a unit (days, weeks, months); the service derives `duration_weeks` (a month is 4.3 weeks, at least 1). Filter buckets as in the UI: under 4 weeks, 4 to 12, 13 or more |
| Training schedule | Start and end date plus one or more **weekly class slots** (class days Sun to Sat, start and end time); at least one slot is needed to submit |
| Training statuses | `DRAFT`, `SUBMITTED` (UI "Pending Review"), `APPROVED`, `CHANGES_REQUESTED`, `REJECTED`, `UNPUBLISHED`, `CANCELLED`, `EXPIRED`. Only an `APPROVED` institute creates, submits or republishes |
| Editing a training | `DRAFT`, `CHANGES_REQUESTED`, `REJECTED` are saved as they are and submitted when ready. Editing an `APPROVED` or `UNPUBLISHED` training sends it straight back to `SUBMITTED` (hidden until re-approved); the edit is refused if the result is not ready to submit. A submitted training can be withdrawn to `DRAFT`. Only a `DRAFT` can be deleted |
| Training expiry | A daily job (`expire_trainings`) sets `EXPIRED` on `APPROVED` / `UNPUBLISHED` trainings whose `end_date` has passed. No manual "complete" |
| Training contact | Optional contact person, phone and email per training; the public page falls back to the institute's phone and email |
| Seats | Optional; empty means unlimited |
| Merojob SSO / integration | On hold |
| Deployment | Docker, to be set up after development starts |

## 2. Apps (Django)

| App | Responsibility | State |
| :---- | :---- | :---- |
| `common` | BaseModel, SlugModel, shared serializers / viewsets / validators; reference data: Location (managed Nepal list) and Category (two-level tree), with their loaders and public APIs | built |
| `users` | User, roles, permissions, auth endpoints, the services behind the admin team (its API is in `control_panel`) | in progress |
| `control_panel` | The admin API, one place for every admin task, served under `admin/`: admin team, category admin, institute and training review. No models; it calls the other apps' services. Flat `api/v1/` (one `serializers.py`, `views.py`, `urls.py`, `filters.py`) until it grows | built |
| `institutes` | Institute, locations, staff membership and invitations, verification documents, contact person / CEO / social links, gallery, status workflow | built (on defaults, see section 8) |
| `training` | Training, weekly sessions, curriculum modules, learning outcomes, search, review workflow, expiry | built (on defaults, see section 1) |
| `enquiries` | Enquiry, internal notes, status changes with the seat guard, device tracking ("My enquiries"), public submit and portal APIs | built (on defaults, see section 3.7) |
| `notifications` | In-app notifications + email dispatch (django-q2 tasks) | planned |
| `analytics` | View counters, enquiry stats for dashboards | planned |
| `api` | Versioned URL routing (`/api/v1/`) | exists |
| `reviews` | Deferred (post-MVP) | deferred |

Phase 2: `applications` (reuses Training capacity fields), `learners`.

## 3. Core entities (first pass)

- **User**: email (login, unique case-insensitively), UUID `username`, full_name, phone_number (optional, unique), gender, profile_picture, role, `is_active` (account status). `first_name` / `last_name` are removed.
- **Institute**: name, type, established year, description, logo, status (`PENDING`, `APPROVED`, `REJECTED`, `INFO_REQUESTED`, `SUSPENDED`), status_reason, `registration_number` (required, not checked for uniqueness). `registered_at` is `created_at`. A gallery table holds the images.
- **InstituteContact**: institute (one-to-one, required at registration), contact person, phone, email. **InstituteCEO**: institute (one-to-one, optional), name, message, photo, LinkedIn URL. **InstituteSocialLink**: institute, platform (Facebook, LinkedIn, X, Instagram, YouTube, website, other), url, label; a platform may be added once per institute, `other` any number of times.
- **InstituteLocation**: institute, location (managed Nepal list), address, optional contact phone and `map_url` (Google Maps link), `is_main` (at most one main office per institute), is_active.
- **InstituteMember**: user (unique: one institute per user), institute, role (`OWNER`, `STAFF`). One `OWNER` per institute (derived, to confirm).
- **InstituteInvitation**: institute, email, role, token, status, expires_at (owner invites staff; the invite email is sent via `notifications`).
- **InstituteDocument**: institute, name, file, status (pending / verified / rejected).
- **Category**: name, parent (sub-category; two levels, checked in the service), icon (Remix icon name), hue (0 to 360), is_active. Names are unique among siblings, ignoring case.
- **Location**: province / district / municipality hierarchy (managed list): one table with `level`, `parent`, a `code` (id from the source data), `type` for municipalities (metropolitan, sub-metropolitan, municipality, rural municipality), `is_active`, and denormalised `province` / `district` set in one place.
- **Training** (`apps/training`): institute, category (a category or a sub-category), title, short description (160 characters, on the cards), mode (`PHYSICAL`, `ONLINE`, `HYBRID`), level, duration value and unit plus derived `duration_weeks`, fee (NPR, 0 = free), seats (empty = unlimited), start / end date, registration deadline, `institute_location` (nullable FK to one of the same institute's locations; empty for `ONLINE`, required to submit `PHYSICAL` / `HYBRID`), cover image, status, review feedback, `published_at` (first approval), `search_vector` (GIN index, kept by the services). Drafts may be incomplete; check constraints cover online-without-location, date order, deadline before start, non-negative fee, positive seats and duration, and a unit with every duration.
- **TrainingDetail** (one-to-one with a training, created with it): overview (the detailed description), eligibility, certification (text), skills (list). **TrainingContact** (one-to-one, created with it): contact person / phone / email, all optional. The API shows both as flat fields on the training (`overview`, `skills`, `contact_person`, ...); only the tables are split.
- **TrainingSession**: a weekly slot (class days, start / end time, NPT); a training may have several (for example a morning and an evening batch). **TrainingModule** (curriculum: title, description), **LearningOutcome** (text); both come back in the order they were sent (ordered by pk, no position column).
- **Enquiry** (`apps/enquiries`): training and institute (both `PROTECT`; the institute is copied from the training by the service so the portal can scope on it), name, phone (ten digits, no country code, a 96 / 97 / 98 mobile number), email (optional), message (up to 2000 characters), `type` (`ENQUIRY`, `INTEREST`), `preferred_time` (optional: `MORNING`, `DAY`, `EVENING`, `WEEKEND`), status, `device_token` (UUID). "My enquiries" returns only a device's enquiries from the last 90 days; older ones stay visible to the institute. Check constraints cover the status, type, preferred time and phone format; a partial unique index allows one *open* (`NEW`, `CONTACTED`, `FOLLOW_UP`, `INTERESTED`) enquiry per phone number and training. There is no preferred-location field (dropped 2026-10-10).
- **EnquiryNote**: enquiry, author (null if the user is deleted), text. Internal: only the institute's team sees notes.
- **Notification**: recipient user, type, body, read_at.
- **Proposed (derived, to confirm)**: `AuditLog` (actor, action, target, changes; append-only), `TrainingViewDaily` (training, day, views).
- **Seats**: `available_seats = seats - count(CONVERTED enquiries)`. A training with no `seats` value is unlimited. Converting an enquiry is rejected once converted enquiries reach `seats`, with the training row locked.

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
| `POST auth/otp/send/` | public | Emails a one-time code to an address that has an account (password reset). Throttled (`otp`, per submitted email). `429` with `Retry-After` inside the 60-second cooldown; `400` for an unknown address |
| `POST auth/otp/verify/` | public | Checks `{email, otp}` without using the code up. `400` for a wrong or expired code, `429` after 5 wrong guesses. Nothing consumes a verified password-reset code yet |
| `GET/PATCH me/` | authenticated | Own profile. `email` and `role` are read-only |
| `PUT me/password/` | authenticated | Old password required; Django password validators applied |
| `admin/users/admins/` (CRUD) | `manage_admins` | Create / edit admins, set the initial password and the permissions granted. Role forced to `ADMIN`. Implemented in `apps/control_panel` |
| `PATCH users/{id}/status/` | `manage_account_status` | Suspend / activate. Not yourself, never the Super Admin; only the Super Admin may change an admin's status. Suspending revokes the user's refresh tokens |

Implemented in `apps/users`, except the admins CRUD (`apps/control_panel`). `admins/` has no DELETE (suspend instead); `PATCH admin/users/admins/{id}/` edits name, phone, gender, picture and the granted permissions, but not `email` or `password`. Changing your own password revokes your refresh tokens, and the new password must differ from the old one. Throttling uses the `login`, `token_refresh` and `otp` scopes.

### 3.3 Institute locations

- A location is picked from the managed `Location` list (province → district → municipality) and given an address, so an institute can run trainings in several cities.
- A training points to one `InstituteLocation` of its own institute (validated in the model / serializer). Online trainings have none.
- Public location filtering uses the training's location (city, district or province). The institute card in the design (city, province) is derived from its main office.
- A location cannot be deactivated while a training that is not cancelled or expired uses it. Changing a location's municipality refreshes the search vectors of the trainings held there (queued task).

### 3.4 Engineering conventions (the `users` app already follows them)

- Each app gets `services.py` (business rules, transactions, state changes) and `selectors.py` (read queries with `select_related` / `prefetch_related`). Views and serializers stay thin; status changes go only through services.
- State machines (institute, training) are one allowed-transitions table each; illegal moves raise a validation error. Enquiry statuses are the exception: any status moves to any other, and only seats guard `CONVERTED`.
- Workflow actions run in `transaction.atomic()` with `select_for_update()`; emails are queued with `transaction.on_commit`.
- Invariants are also database constraints: one Super Admin, one main active location per institute, one owner per institute, training mode / location check, case-insensitive unique email.
- List endpoints avoid N+1 queries (query-count tests); public lists use cursor pagination; Redis caches only reference data and short-lived facets.
- Views use DRF generics / the `common` mixin viewsets; logic sits in serializer `create()` / `update()` calling the service.
- A database `IntegrityError` that slips past validation returns 409, not 500.

### 3.5 Institutes API (built)

| Endpoint | Who | Notes |
| :---- | :---- | :---- |
| `POST institute/register/send-otp/` | public | Body `{email}`: the address that will be the owner's login. Emails a six-digit code to that address only (not the CEO or the contact person). Throttled (`register_otp`, 5/hour per address); `429` with `Retry-After` inside the 60-second cooldown; `400` if a user already has the address |
| `POST institute/register/verify-otp/` | public | Optional: checks `{email, otp}` so the form can confirm the address before it is submitted. Does not use the code up. Throttled (`register_otp_verify`, 30/hour per address) |
| `POST institute/register/` | public | Throttled (`institute_register`, 5/hour). Needs `owner` (`email`, `password`, `confirm_password`, optional `phone_number`; the email is the institute's login and `confirm_password` must equal `password`), `otp` (the code sent to `owner.email` by `send-otp/`), `contact` and at least one location. Checks the code first, then creates the institute (`PENDING`), its owner, contact and locations in one transaction and uses the code up; a failed registration keeps the code. `status`, `role` and `slug` in the payload are ignored |
| `POST institute/invitations/accept/` | public | Throttled (`invitation_accept`, 10/hour). Creates a staff account from a valid, unexpired, unused token |
| `GET institutes/`, `institutes/{slug}/` | public | `APPROVED` only; filter `type`, search `name`; constant number of queries (four for the detail); the detail also shows the contact person, CEO, social links, every active location and the gallery, but never the owner's login; the card shows the main location with district and province |
| `GET, PATCH institute/profile/`, `POST institute/resubmit/` | institute staff | `PATCH` edits the institute's own columns only (name, type, description, established year, logo); `registration_number`, `status` and `slug` are read-only and the nested contact, CEO and social links cannot be written here. Renaming queues a search refresh of the institute's trainings. `resubmit` moves `INFO_REQUESTED` or `REJECTED` back to `PENDING` |
| `GET, PUT, PATCH institute/contact/` | institute staff | The contact person; `PUT` needs every field. `404` if the institute has none (registration always creates one) |
| `GET, PUT, DELETE institute/ceo/` | institute staff | `PUT` creates or updates, through `services.save_ceo` (serialised per institute); an omitted photo stays. `404` until one exists |
| `institute/social-links/` (list, create, patch, delete) | institute staff | A platform once per institute (`other` repeats); another institute's link is a 404 |
| `institute/locations/` (list, create, patch) and `.../{id}/set-main/`, `.../deactivate/` | institute staff | Only active municipalities; the first location is main; the main one cannot be deactivated |
| `institute/documents/` (list, upload) and `.../{id}/download/` | institute staff | Multipart; the response never contains the file path; downloads are streamed after a membership check |
| `institute/gallery/` (list, create, patch, delete) and `.../reorder/` | institute staff | Public images; reorder takes every id exactly once |
| `institute/staff/` (list, delete), `institute/invitations/` (list, create, delete) | owner only | Removing staff deactivates the account and revokes its refresh tokens; the invitation token is never returned |
| `admin/institutes/` and `.../{id}/{approve,reject,request-info,suspend,reinstate}/` | `users.manage_institutes` | Reject, request-info and suspend need a reason; approve needs one active location and one document |
| `admin/institutes/{id}/documents/{doc}/` (PATCH) and `.../download/` | `users.manage_institutes` | Document review: `VERIFIED` or `REJECTED` |

The `admin/institutes/` endpoints are implemented in `apps/control_panel`. Rows of another institute return 404. Verification documents live under `PRIVATE_MEDIA_ROOT`, outside `MEDIA_ROOT`, and never get a URL. Invitation tokens are stored as a sha256 hash only. Renaming an institute queues a refresh of its trainings' search vectors.

### 3.6 Categories and trainings API (built)

| Endpoint | Who | Notes |
| :---- | :---- | :---- |
| `GET categories/` | public | Category > sub-category tree with icon and hue; active only; cached in Redis until a category changes |
| `admin/categories/` (list, create, retrieve, patch) | `users.manage_categories` | No DELETE (deactivate with `is_active`); filters `parent`, `is_active`, search `name`; renaming or moving queues a search refresh of its trainings |
| `GET trainings/`, `trainings/{slug}/` | public | `APPROVED` trainings of `APPROVED` institutes. Filters `category` (includes its sub-categories), `sub_category`, `mode`, `level`, `province`, `district`, `municipality`, `fee_min` / `fee_max`, `start_from` / `start_to`, `duration` (`short`, `mid`, `long`), `duration_weeks_min` / `_max`, `institute` (slug), `registration_open`, `search`; `ordering` on `published_at`, `start_date`, `fee_npr`. Constant number of queries |
| `institute/trainings/` (list, create, retrieve, patch, delete) | institute staff | Nested `sessions`, `modules`, `outcomes` in one JSON body (a list replaces the whole list; leave it out to keep it). Filter `status`. Actions `submit/`, `withdraw/`, `unpublish/`, `republish/`, `cancel/`, `cover/` (multipart, jpg or png, 5 MB, only while editable) |
| `admin/trainings/` (list, retrieve) and `.../{id}/{approve,request-changes,reject}/` | `users.manage_trainings` | Review queue with `?status=SUBMITTED`; filters `status`, `mode`, `institute`, search title and institute name. Request-changes and reject need a reason; only a `SUBMITTED` training can be reviewed |

The `admin/categories/` and `admin/trainings/` endpoints are implemented in `apps/control_panel`; the services they call stay in `common` and `training`.

### 3.7 Enquiries API (built)

| Endpoint | Who | Notes |
| :---- | :---- | :---- |
| `POST enquiries/` | public (no account) | Needs header `X-Device-Token` (a random UUID4) and body `training` (slug), `name` (2+ characters), `phone` (a 96 / 97 / 98 mobile number; spaces, dashes and `+977` are accepted and stripped), optional `email`, `message`, `type` (`ENQUIRY` default, or `INTEREST`), `preferred_time`. Throttled: `enquiry` scope (10/hour per client IP) and 3 per phone number per day, both `429` with `Retry-After`. `400` when the training is not an approved one of an approved institute, when registration has closed or the seats are full (a plain enquiry only), or when the phone number already has an open enquiry for that training. The answer is the visitor's view (`id`, `type`, `training`, `institute_name`, `status_label`, `created_at`); the status, institute and device token cannot be set |
| `GET enquiries/my/` | public (header) | The enquiries of this device from the last 90 days, newest first, paginated (`limit` / `offset`). Same fields as the answer above: never the phone, email, message or notes |
| `GET institute/enquiries/` | institute staff (owner or staff) | Newest first, paginated (the UI asks for 25 at a time); filters `status`, `training`, `q` (name, phone or email, anywhere in the text). Constant number of queries |
| `GET, PATCH institute/enquiries/{id}/` | institute staff | The detail adds `message`, `preferred_time`, `modified_at` and the `notes` (newest first, with the author's name, or email if none). `PATCH` takes only `status`, moves any status to any other, and is refused with `400` for `CONVERTED` when the training's converted enquiries already reach its `seats`, or for a status that would make a second open enquiry of one phone number for one training. No PUT or DELETE |
| `GET, POST institute/enquiries/{id}/notes/` | institute staff | Internal notes (up to 2000 characters), all of them in one list; the author is the caller |
| `GET institute/enquiries/summary/` | institute staff | `total`, `new`, `unique_phones` and `by_status` (every status, zeros included) in one query. The `training` and `q` filters apply, so the tab counts follow them; call it without filters for the sidebar badge, and leave `status` out |

Another institute's enquiry or note is a 404. Enquiries are written only through `apps/enquiries/services.py`: `submit_enquiry` (rules, per-phone allowance, one open enquiry per phone and training, the unique index as the final judge) and `change_status` (locks the enquiry, then the training for `CONVERTED`, so two staff cannot take the last seat). The per-phone counter lives in Redis under `enquiry_phone_<phone>` for 24 hours. A training that has enquiries cannot be deleted (`delete_training` says so; the foreign key is `PROTECT`).

## 4. Key workflows

1. **Institute onboarding**: request a code for the login email (`register/send-otp/`) → register (one JSON request: institute, owner with that email and the code, contact, at least one location; the owner can log in right away) → upload verification documents in the portal → `PENDING` → admin approves / rejects / requests more info / suspends → email to the institute. A rejected institute can re-apply (`REJECTED` → `PENDING`) after updating its details. Only `APPROVED` institutes are visible publicly.
2. **Training lifecycle**: institute drafts → submits (`SUBMITTED`, can withdraw) → admin approves / requests changes / rejects (with a reason) → `APPROVED` (public) → an edit sends it back to review; the institute can unpublish / republish (no review) or cancel; a daily job expires it after `end_date`. `CANCELLED` and `EXPIRED` are final.
3. **Enquiry**: public submit (throttled per IP and per phone number, no captcha yet) → the institute sees it in the portal (no email yet; the sidebar count comes from `summary/`) → staff change the status and add internal notes → admin conversion stats (not built). The visitor's device sees it under "My enquiries" for 90 days. A plain enquiry is refused once registration has closed or the seats are full; an `INTEREST` ("tell me about the next batch") is still accepted.
3a. **Staff invitation**: institute owner invites by email → invitee accepts and sets a password → becomes `INSTITUTE_STAFF` of that institute.
4. **Discovery**: prefix full-text search + filters (category, sub-category, mode, level, location, fee, start date, duration, registration open, institute) using PostgreSQL full-text search and django-filter. The availability filter waits for `enquiries`.

## 5. API surface (v1, sketch)

- **Public**: `GET trainings`, `trainings/{slug}`, `categories`, `locations`, `institutes`, `institutes/{slug}`, `POST enquiries/`, `GET enquiries/my/` (by device token, last 90 days); built, see 3.7.
- **Built (institutes):** see section 3.5 for `institutes/`, `institute/` and `admin/institutes/`.
- **Built (categories and trainings):** see section 3.6.
- **Built:** `GET locations/` (filters `level`, `parent`, `province`, `district`; `search` on name; only active rows; one query, unpaginated, about 850 rows), `GET locations/{id}/`, `GET locations/tree/` (province > district > municipality, cached in Redis until a location changes).
- **Institute**: auth, profile + documents + gallery + locations, staff invitations, CRUD trainings, submit for review, enquiries list / status / notes / summary (built, see 3.7), dashboard stats (weekly trend, by training: not built; page views wait for `analytics`).
- **Admin**: institute review actions, training review actions, categories and locations CRUD, enquiries monitor / export, admin team, platform settings.

## 6. Non-functional

- DRF throttling by scope, backed by Redis; no captcha is verified yet. Because the browser calls the API directly, throttling keys on client IP (and the enquiry service also limits each phone number, with a Redis counter); the deployment proxy must pass the real client IP. If Redis is down the throttle and the phone counter raise, so an enquiry fails with a 500 (it fails closed).
- One-time codes, their attempt counters and cooldowns live in the Redis cache with a 5-minute expiry; the OTP throttles are keyed on the submitted email, not on the client IP. The email is sent by a django-q task, so OTP mail is delivered only while `qcluster` runs, and `qcluster` does not reload code: restart it after a deploy.
- Caching: the location and category trees are cached in Redis with no expiry and cleared when a `Location` / `Category` is saved or deleted (and by `load_locations`). `QuerySet.update()` skips the signals.
- Scheduled job: `apps.training.tasks.expire_trainings` must run daily (a django-q `Schedule`, or `manage.py expire_trainings` from cron), with `qcluster` running for the queued search refreshes.
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
2b. [x] One-time codes by email: `users` services / tasks / `auth/otp/` endpoints, and email verification at institute registration (`register/send-otp/`, `register/verify-otp/`, the code goes with `owner.email` in `register/`).
3. [x] `institutes`: models and constraints, services, public / admin / portal APIs (132 tests). The decisions it was built on were confirmed on 2026-10-02.
4. [x] `catalog` (locations, categories) and `training` (trainings, weekly sessions, curriculum, search and filters, institute portal, admin review, expiry): built from `docs/catalog-checklist.md` on its defaults (confirmed 2026-10-05). The whole suite is 266 tests (users 26, catalog 36, institutes 132, training 72).
5. [x] `enquiries`: models and constraints, services, public submit and "My enquiries", portal list / detail / status / notes / summary (built 2026-10-10 on the decisions in the log). No email alert and no captcha yet. 89 tests; the whole suite is 444.
5a. [ ] `notifications`, `analytics`, the admin enquiries monitor (`users.manage_enquiries`), and the availability filter / "seats left" on public trainings.
6. [ ] Search, filters and public API polish.
7. [ ] Docker.

## 8. Open questions

1. **Enquiry retention**: after 90 days an enquiry disappears from the visitor's "My enquiries". Today the institute keeps every enquiry and nothing deletes old ones. Keep it that way, or delete old enquiries too?
2. **Browser auth storage**: where does the frontend keep the access and refresh tokens (memory, `localStorage`, or an httpOnly cookie)? This affects security and CORS settings.
3. **Search**: the PRD lists "Instructor Name" but there is no instructor field (the UI has none either). Add a text field on `Training` or drop it?
4. **Enquirers and cancellation**: are people who sent an enquiry told when a training is cancelled? (`TODO(notify)` in `training/services.py`.)
5. **Notifications**: which events notify whom (in-app and email)? A new enquiry sends nothing today (decided 2026-10-10), and the enquirer is never emailed.
6. **Reports**: which provider "Reports" / "Sessions" dashboard items belong to the MVP ("Participants" is phase 2)?
7. **PRD wording**: the Problem Statement and some user stories describe the later phase, and the "Training Instructors" list repeats the Learner list. Treat as phase 2 / ignore?
8. **Privacy**: retention, consent and export rules for enquirer name / phone.
9. **Admin password reset**: the Super Admin sets an admin's initial password, but nothing resets it later (`PATCH admin/users/admins/{id}/` rejects `password`). Add an endpoint, or the "set your own password" email with `notifications`?
10. **Admin site access**: rename `/admin/`, restrict it at the proxy, or add 2FA before production?
11. **Locations at runtime**: may admins with `manage_categories` edit locations through an API, or does only `load_locations` write them? Until then the admin site is read-only and the loader is the only writer.
12. **Editing an approved institute**: today an institute's staff can change the profile of an `APPROVED` institute without re-review (an edited training does go back to review). Should some fields (name, type) need re-approval?
13. **Public contact details**: the institute detail page shows the contact person's name, phone and email, and the CEO profile (a comment in `PublicInstituteDetailSerializer` shows how to hide the name). Keep all of it public? And should `registration_number` be unique or validated?
14. **Featured and views**: the UI's relevance sort uses a featured flag and view counts; neither exists yet.
15. **Password reset**: `auth/otp/send/` and `auth/otp/verify/` exist, but no endpoint takes a verified code and sets a new password. Build it (`consume_otp` is ready), and should it also cover admins (see 9)?

## 9. Decision log (answered questions)

- Reviews: skipped for now; needs login first. Hybrid mode: included. "My enquiries": browser-stored token accepted. Enquiry statuses: first `NEW` / `CONTACTED` / `CONVERTED` / `CLOSED`, replaced by the portal's seven on 2026-10-10 (see the last entry).
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
- Categories and trainings built (2026-10-05): the UI prototypes were decoded and compared with the plan; the sixteen defaults in `docs/catalog-checklist.md` (version 2) were confirmed ("use the defaults"). Trainings live in their own `training` app; `django.contrib.postgres` is installed. Answered: category depth (two levels, a training may use either), levels (three), duration (value + unit, derived weeks), schedule (weekly slots), completion (automatic `EXPIRED`), editing an approved training (back to review), unlimited seats (empty = unlimited), search configuration (`simple`, prefix).
- `catalog` merged into `common` (2026-10-07): one installed app (label `common`) now holds the shared base classes and the reference data (`Location`, `Category`), so earlier entries and `docs/*-checklist.md` that say `catalog` mean `apps/common`. Tables are `common_location` / `common_category`, the cache keys are `common:location-tree:v1` / `common:category-tree:v1`, and the API URLs did not change. Rule: `common` holds base classes and reference data that several apps point to; anything with its own workflow gets its own app. The migrations of `common`, `institutes` and `training` were regenerated from scratch (no production data yet), so a database built before this change has to be recreated.
- Locations are required at registration (2026-10-07): `POST institute/register/` answers 400 when `locations` is missing or empty, so every new institute starts with at least one location. This replaces the 2026-10-02 default of optional locations at registration; approval still needs at least one active location and one document. The serializer enforces it; `services.register` itself accepts none.
- Email verification at institute registration (2026-10-08): the institute's login is `owner.email` with `owner.password`, so that is the address verified; `Institute` has no separate email column. `POST institute/register/send-otp/` emails the code to it, and `POST institute/register/` takes the code as `otp`. The send endpoint refuses an address a user already has. Assumed defaults, easy to change in `apps/users/constants.py`: six digits, 5 minutes, 60-second resend, 5 wrong guesses. The send / verify endpoints answer 200 (not 201); too many requests is a 429 from `TooManyRequests`, which the exception handler maps. `POST institute/register/` lost its `AllowAny`, `authentication_classes = []` and `institute_register` throttle in an earlier refactor, so it answered 401; they are back.
- Institute profile split (2026-10-08, built in the registration refactor): registration now takes a required `registration_number` and contact person (name, phone, email), plus an optional CEO and social links; the contact, CEO and social links live in their own tables with portal endpoints (see 3.5). This answers the old question about the UI's registration number, contact person and mobile. A follow-up repaired what that refactor broke: `PATCH institute/profile/` crashed (`update_profile` had a new signature) and lost the search refresh on rename, the public detail returned location ids instead of objects, `save_ceo` was never called, and tests still used removed columns.
- Control panel (2026-10-10): every admin endpoint lives in `apps/control_panel` under `admin/`, so admin work has one home and its permissions, serializers and views are read in one place. It has no models and calls the services of `users`, `common`, `institutes` and `training`, which keep the rules. Its `api/v1/` is deliberately flat (one `serializers.py`, `views.py`, `urls.py` and `filters.py`) until it grows. The admin-team CRUD moved from `user/admins/` to `admin/users/admins/`; the old path was dropped without an alias. URLs of the category, institute and training admin endpoints did not change. `users/{id}/status/` (suspend) is still in `users`.
- Enquiries (2026-10-10), decided from the Institute Portal's Enquiries screen before building `apps/enquiries`: (1) the status set is the UI's seven and any status moves to any other; institute staff and the owner both change them, and an admin only reads (the admin monitor is not built); (2) the UI's `type` is kept (`ENQUIRY` / `INTEREST`): an interest is always accepted for a published training, a plain enquiry is refused when seats are full or registration has closed (`registration_open`: the deadline has not passed, or there is no deadline and the training has not started); (3) the preferred location is dropped, the preferred time (`MORNING`, `DAY`, `EVENING`, `WEEKEND`) is kept; (4) internal notes are a table of their own, and a status change adds no automatic note; (5) no email alert for a new enquiry and no captcha for now; the limits are the `enquiry` throttle scope (10 an hour per IP), 3 a day per phone number and one open enquiry per phone number and training; (6) "My enquiries" uses a client-made UUID4 in `X-Device-Token`, answers with a plain-language status label and never the phone, notes or the institute's internal status (`NOT_INTERESTED` reads as "Closed"); (7) the portal dashboard gets `summary/` now, while the weekly trend, per-training counts and page views wait; (8) all enquiries are kept (no deletion job); (9) the submit fails closed if Redis is down. Built: 3.7. Two touches in `training`: `registration_open_q` is now the one definition of "registration open" (the public filter and enquiries share it), and `delete_training` refuses a draft that has enquiries, since the institute keeps them.
