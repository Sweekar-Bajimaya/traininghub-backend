# Enquiries: what was built and what needs changes

Written 2026-10-10 on branch `feature/enquiry-management`, after the `apps/enquiries` app was built from the
Institute Portal's Enquiries screen. A record of the work, not of the code: where they differ, the code wins.
The decisions behind it are in the last entry of the decision log in `docs/System Design.md`; the endpoint tables are
in its section 3.7.

Updated 2026-11-02: the device token, the `X-Device-Token` header and the visitor's "My enquiries" list were removed.
This file describes the app without them; the decision is the last entry of the log in `docs/System Design.md`.

## 1. In short

- **Built:** a visitor sends an enquiry or an interest without an account; the institute's staff and owner list,
  search, filter and open enquiries, change the status, add internal notes and read the counts. The visitor has no
  identity after the submit and no list of their own.
- **Tested:** 82 tests in `apps/enquiries`, and the whole suite is 516 tests, all passing (`python manage.py test`).
- **Not built:** email or in-app alerts, captcha, the admin enquiries monitor, dashboard analytics, and "seats left" on
  public trainings (section 5).
- **Before it works end to end:** run `python manage.py migrate` (a database built before 2026-11-02 has to roll the
  app back first, section 4.1).

## 2. What was built

### 2.1 Data (`apps/enquiries/models.py`)

| Model | Fields | Rules in the database |
| :---- | :---- | :---- |
| `Enquiry` | `training` and `institute` (both `PROTECT`; the institute is copied from the training), `name`, `phone` (ten digits, no country code), `email` (optional), `message` (up to 2000), `type`, `preferred_time` (optional), `status`, `created_at`, `modified_at` | Check constraints on status, type, preferred time and phone format (`^9[678][0-9]{8}$`). A partial unique index: one **open** enquiry per phone number and training. Indexes for the portal list and the seat count |
| `EnquiryNote` | `enquiry`, `author` (null if the user is deleted), `text` (up to 2000), `created_at` | Text cannot be blank; ordered newest first |

- Statuses: `NEW`, `CONTACTED`, `FOLLOW_UP`, `INTERESTED`, `CONVERTED`, `NOT_INTERESTED`, `CLOSED`. "Open" means
  `NEW`, `CONTACTED`, `FOLLOW_UP` or `INTERESTED`.
- Types: `ENQUIRY`, `INTEREST`. Preferred time: `MORNING`, `DAY`, `EVENING`, `WEEKEND`.
- There is no preferred-location field and no status history.

### 2.2 Rules (`apps/enquiries/services.py`)

**Submitting** (`submit_enquiry`)

1. The training must be `APPROVED` and its institute `APPROVED`. An unknown, draft or unpublished slug gives the same
   400 ("This training is not accepting enquiries.").
2. An `INTEREST` is accepted whenever rule 1 holds.
3. A plain `ENQUIRY` is also refused when registration has closed (the deadline has passed, or there is no deadline and the
   training has started) or the seats are full (`seats` is set and `CONVERTED` enquiries have reached it). The 400
   message ends "You can still show interest."
4. A phone number with an open enquiry for the same training is refused, for either type.
5. A phone number may send 3 enquiries a day (a Redis counter; refused enquiries do not use it). Over that is a 429 with
   `Retry-After`.
6. The unique index decides if two submits arrive at the same moment.

**Changing the status** (`change_status`): any status to any other. Moving to `CONVERTED` is refused when the
training's converted enquiries already reach `seats`; the training row is locked first (enquiry, then training, always in
that order) so two staff cannot take the last seat. Moving a closed enquiry back to an open status is refused if that
phone number already has another open one for the training. Moving out of `CONVERTED` frees the seat.

### 2.3 API (all under `/api/v1/`)

| Endpoint | Who | What it does |
| :---- | :---- | :---- |
| `POST enquiries/` | public | Body: `training` (slug), `name` (2+ characters), `phone`, optional `email`, `message`, `type`, `preferred_time`. No header is needed. Answers 201 with the visitor's view |
| `GET institute/enquiries/` | staff, owner | Newest first, `limit` / `offset`; filters `status`, `training`, `q` (name, phone or email, anywhere in the text) |
| `GET, PATCH institute/enquiries/{id}/` | staff, owner | Detail with notes; `PATCH` accepts only `status` |
| `GET, POST institute/enquiries/{id}/notes/` | staff, owner | Internal notes, newest first, all in one list |
| `GET institute/enquiries/summary/` | staff, owner | `total`, `new`, `unique_phones`, `by_status` (every status, zeros included); the `training` and `q` filters apply |

Another institute's enquiry is a 404. An admin account gets 403 on the portal endpoints. No PUT or DELETE.

Response shapes (from the tests):

```jsonc
// POST enquiries/ -> 201
{ "id": 12, "type": "ENQUIRY",
  "training": { "id": 5, "slug": "python-bootcamp", "title": "Python Bootcamp" },
  "institute_name": "Alpha Institute", "status_label": "Sent to institute", "created_at": "2026-10-10T14:05:00+05:45" }

// GET institute/enquiries/ -> results[]
{ "id", "name", "phone", "email", "type", "status", "training", "training_title", "created_at" }

// GET, PATCH institute/enquiries/{id}/
{ "id", "name", "phone", "email", "message", "type", "preferred_time", "status", "training", "training_title",
  "notes": [ { "id", "text", "author", "created_at" } ], "created_at", "modified_at" }

// GET institute/enquiries/summary/
{ "total": 3, "new": 1, "unique_phones": 2, "by_status": { "NEW": 1, "CONTACTED": 0, "...": 0 } }
```

The visitor never receives the phone number, email, message, notes or the raw status. `status_label` is the prototype's
wording: `NEW` "Sent to institute", `CONTACTED` "Institute contacted you", `FOLLOW_UP` "Institute will follow up",
`INTERESTED` "Marked interested", `CONVERTED` "Enrolled", `NOT_INTERESTED` and `CLOSED` both "Closed". A new enquiry is
always `NEW`, so the only label the API sends today is "Sent to institute".

Errors the frontend should expect: field errors as `{"phone": ["Enter a 10-digit mobile number starting with 96, 97 or
98."]}`; the three business refusals (closed, full, duplicate) as `{"non_field_errors": ["..."]}`; throttling as 429 with
`Retry-After`.

### 2.4 Changes outside the new app

| File | Change |
| :---- | :---- |
| `config/settings/base.py` | `apps.enquiries` installed |
| `apps/api/v1/urls.py` | Prefixes `enquiries/` and `institute/enquiries/` |
| `apps/training/services.py` | New `registration_open_q()`, the one definition of "registration open"; `delete_training` refuses a draft that has enquiries (the institute keeps them) |
| `apps/training/api/v1/filters.py` | The public `registration_open` filter now uses `registration_open_q()` (same behaviour) |
| `CLAUDE.md`, `docs/System Design.md` | Updated in the same change, as the repo rules require |

### 2.5 Tests (`apps/enquiries/tests/`)

Constraints; the submit rules; free status moves and the seat guard, including a two-thread test that only one of two
simultaneous conversions takes the last seat; the phone allowance and the IP throttle; that a stray device token is ignored
and `enquiries/my/` is gone; the access matrix (anonymous 401, admin 403, other institute 404); filters and search; notes; the summary; and
query counts that stay constant as lists and notes grow.

## 3. Where the build differs from the prototype

| Prototype | Build | Why |
| :---- | :---- | :---- |
| "Preferred location" in the modal, drawer and admin data model | Dropped | Decided 2026-10-10 |
| Status change adds "Status changed to X" to the notes | Not added | Decided 2026-10-10: notes only; the status change leaves no history |
| Alerts by in-app, email and SMS | None yet | Decided 2026-10-10: no email for now |
| Captcha | None | Decided 2026-10-10: not for now |
| Phone check `^9[678]\d{8}$` with the message "97 or 98" | Same pattern; the message says "96, 97 or 98" | The pattern already allowed 96 |
| `+977` stripped from the start of any number | Stripped only when ten digits remain | Otherwise a real number starting 977 is cut short |
| Visitor sees the raw status colour and label | Visitor sees `status_label` only | `NOT_INTERESTED` must not show the institute's verdict |
| "My enquiries" for the visitor on the same browser, kept 90 days (PRD) | Not built; no device token | Decided 2026-11-02: not needed |

## 4. What needs changes

### 4.1 Before it works end to end

- [ ] **Run `python manage.py migrate`** on every database. The migration is `apps/enquiries/migrations/0001_initial.py`.
- [ ] **A database that applied `0001` before 2026-11-02 must roll the app back first.** That migration was rewritten in
      place to drop `device_token`, so the old table keeps a NOT NULL `device_token` column and every submit fails. Run
      `python manage.py migrate enquiries zero` (this deletes every enquiry), then `migrate`. A fresh database is fine.
- [ ] **The deployment proxy must pass the real client IP**, or the 10-an-hour limit counts every visitor together.
- [ ] **Redis must be up.** The throttle and the phone counter need it; if it is down, a submit fails with a 500.
- [ ] `qcluster` is **not** needed for enquiries (they queue nothing).

### 4.2 Frontend changes against the prototype

- Send the training's **slug**, not its id, when submitting. Send no `X-Device-Token`, and drop the "My enquiries" screen:
  `enquiries/my/` is a 404 now. The answer to the `POST` is the visitor's only receipt.
- Send enum values, not labels: `ENQUIRY` / `INTEREST`, `MORNING` / `DAY` / `EVENING` / `WEEKEND`, and the seven status
  values (`FOLLOW_UP`, `NOT_INTERESTED`, ...). Show the labels in the UI.
- Remove the preferred-location field. Show the validation text that says 96, 97 or 98.
- Ids are integers (the prototype's are `enq-4000`). The portal list does not return an institute id (it is always the
  caller's own), so the drawer's "Institute ID" row has no source.
- Phone numbers come back as ten digits: add `+977` for the `tel:` and `sms:` links, as the prototype does.
- Field names are snake_case: `training_title`, `created_at`. A note's `author` is a name, an email if the user has no
  name, or `null` for a note whose author was deleted (show "Former staff" or nothing).
- "Show more (N left)": use `limit` / `offset` (the default page is 10, so ask for 25) and `count` for what is left.
- Tabs and the sidebar badge: call `summary/` with the search and training filters for the tab counts, and without any
  filter for the badge (`new`). Leave `status` out of that call. The dashboard's "Interested users" is `unique_phones`;
  the conversion rate is `by_status.CONVERTED / total`, worked out in the browser.
- The drawer's automatic "Status changed" note will not appear; either drop it or show the status change another way.
- When a plain enquiry is refused as closed or full, the message says so; offer "Show interest" as the next step.
- Dates are ISO timestamps in Nepal time (`+05:45`).

### 4.3 Backend work not done

| Item | What is missing | Depends on |
| :---- | :---- | :---- |
| Admin enquiries monitor | `admin/enquiries/` in `control_panel` (`users.manage_enquiries`), with the Admin Console's filters (institute, training, category, date, status) and an export. Its "Location" filter and column have no data now that preferred location is dropped; the training's location could replace it | Undecided: read-only or editing, and what the location column shows |
| New-enquiry alerts | Email to the institute, in-app notification, SMS (the prototype shows all three). The enquiry service has no hook for it yet | The `notifications` app and open question 5 |
| Dashboard analytics | Enquiries per week (12 weeks), counts by training, conversion by institute, page views, response rate on the public institute page | The `analytics` app; page views need view counting (open question 14) |
| "Seats left" and the availability filter | `seats` minus `CONVERTED` enquiries on public trainings, and the filter in `trainings/` | Touches the public training serializers and filters |
| Cancelled trainings | Tell people who enquired when a training is cancelled (`TODO(notify)` in `training/services.py`) | Open question 4 and `notifications` |
| Audit trail | Who changed a status and when. `change_status` takes `by` and does nothing with it (`TODO(audit)`) | The planned audit log |
| Captcha | `RECAPTCHA_SECRET_KEY` is in settings but nothing verifies a token, and no HTTP client is pinned in `requirements/base.txt` (`requests` arrives only through `requests-oauthlib`) | A decision to turn it on |

### 4.4 Risks and limits to know about

- **Spam:** without a captcha, one address can send 10 enquiries an hour with a different phone number each time. If you
  need more, add the captcha or lower the rate.
- **A frontend that calls from its own server** would put every visitor behind one IP, so the `enquiry` throttle would limit
  them all together. The IP throttle suits the browser-direct setup in CLAUDE.md; revisit it if that changes.
- **Phone numbers sit in Redis** (`enquiry_phone_<phone>`) for up to 24 hours as part of the per-phone counter.
- **The seat check on submit does not lock the training**, so one extra enquiry can slip in beside the last seat. An
  enquiry does not take a seat; only `CONVERTED` does, and that is locked.
- **Search** uses `icontains` on name, phone and email, with no trigram index. It is fine for one institute's volume; look
  at it again if an institute reaches tens of thousands of enquiries.
- **Notes are not paginated.** A few per enquiry is expected.
- **Nothing deletes old enquiries.** The institute keeps all of them (open question 1).
- **An admin cannot read enquiries through the API yet**, only through the read-only Django admin site.

### 4.5 Questions still open (numbers as in `docs/System Design.md`, section 8)

1. Keep every enquiry indefinitely, or delete old ones?
4. Tell enquirers when a training is cancelled?
5. Which events notify whom; is the enquirer ever emailed?
8. Privacy: retention, consent and export rules for the visitor's name and phone.
14. The featured flag and view counts behind the relevance sort (also needed for page-view analytics).

## 5. How to check it

```bash
source .venv/bin/activate
python manage.py migrate
python manage.py test apps.enquiries      # 82 tests
python manage.py test                     # the whole suite, 516 tests
python manage.py check && python manage.py makemigrations --check --dry-run
DEBUG=true python manage.py show_urls | grep enquir     # the routes
```

With `DEBUG=true` the swagger page is at `/api/root/` and lists `/enquiries/` and the
`/institute/enquiries/` routes.

Files: `apps/enquiries/` (`models.py`, `constants.py`, `services.py`, `validators.py`, `admin.py`,
`api/v1/{serializers,views,filters,urls/}`, `migrations/0001_initial.py`, `tests/`).
