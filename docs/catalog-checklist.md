# Catalog and Training – Todo List (version 2, checked against the UI; built)

Ordered work list for **categories** (in `apps/catalog`) and **trainings** (in the new `apps/training` app): sessions,
curriculum, search and filters, the institute portal and the admin review. Follow it top to bottom: each milestone is its
own commit, with `python manage.py check`, `makemigrations --check --dry-run` and the full test suite green before you
move on. Notion copy: "Catalog – Todo List (C0–C6)" under the System Design Review page.

Version 2 (2026-10-05) replaces version 1 after two things: your code changes (a separate `training` app, and
`django.contrib.postgres` installed), and a check of the three UI prototypes in `design/` (decoded; they share one data
file and the portal's create-training form is the real list of inputs). Where the UI and version 1 disagreed, the plan below
follows the UI unless the PRD or a decision you already made says otherwise.

## Status (2026-10-05): built

- **All milestones C0 to C6 are built** on the sixteen defaults below ("use the defaults", 2026-10-05). `check` and
  `makemigrations --check` are clean; the whole suite passes (266 tests: users 26, catalog 36, institutes 132,
  training 72). Swagger generates without errors.
- **Migrations are generated, not applied:** `catalog/0004` (category icon and hue), `institutes/0002`
  (`InstituteLocation.map_url`) and a regenerated `training/0001_initial`. Review them, then run `python manage.py migrate`,
  `load_categories`, and add the daily `expire_trainings` schedule.
- This file is now a record of the plan. Where the code differs from a snippet, the code wins; the differences are listed
  in "Built differently from the snippets" at the end.

## What the UI check found

| Area | Version 1 | The UI says | Now |
|---|---|---|---|
| Levels | Beginner, Intermediate, Advanced, All levels | Filter chips and the portal select have exactly **Beginner, Intermediate, Advanced** | Three levels; `ALL_LEVELS` removed |
| Duration | number + unit (hours, days, weeks, months) | Free text such as "6 weeks"; the portal parses day, week or month and stores a `weeks` number (month = 4.3 weeks, at least 1); the hub filter is **Under 1 month (under 4 weeks), 1 to 3 months (4 to 12), 3 months or more (13+)** | Units days, weeks, months (no hours); a derived `duration_weeks`; filter `duration=short, mid, long` |
| Schedule | dated sessions (date, start, end) | **Start date, end date, one daily start and end time, class days (Sun to Sat)**; the detail page shows "Class days" and "Class time" | A session is a weekly slot: `class_days` plus times. No per-date sessions |
| Statuses | Draft, Submitted, Approved, Changes requested, Rejected, Unpublished, Cancelled, Completed | Draft, **Pending Review**, Approved, Rejected, Changes Requested, **Expired**. The admin settings page has "Auto-expire trainings after end date" and "New and edited trainings stay hidden until approved" | `Expired` set automatically replaces manual `Completed`; editing an approved training sends it back to review by itself (no separate "withdraw") |
| Description | one `overview` | **Short description** (160 characters, on the cards, required) and **Detailed description** | `short_description` and `overview` |
| Skills | none | "Skills covered", comma separated, shown as chips, **searchable** | `skills` list, in the search |
| Category | a training belongs to a sub-category | The portal asks for a **Category** (required) and a free-text Subcategory; the admin manages 13 flat categories with an **icon and a colour hue**; the hub filters by category | Managed two-level tree is kept (PRD, System Design), a training may use a category **or** a sub-category; `icon` and `hue` added; starter data comes from the UI |
| Contact | none | Contact person, phone, email on every training (person and phone required) | Optional `contact_person`, `contact_phone`, `contact_email` on the training |
| Map | none | "Google Map location" link next to the address | `map_url` on `InstituteLocation` (institutes app) |
| Search | title, institute, category, overview, modules | Title, category, subcategory, **skills**, institute name, **location**, short description | The search vector covers all of those, prefix match |
| Sort | `ordering` published, start, fee | Relevance (title match, then featured, then views), Newest, Upcoming (start date), Price low to high, Price high to low | Same fields; `featured` and `views` are left for later (admin and analytics) |
| Fee filter | min and max | A maximum-fee slider (5,000 to 60,000) | `fee_max` (and `fee_min`) |
| Seats | optional, empty means unlimited | "Maximum participants"; the UI uses 20 when empty and always shows "N seats left" | Optional, empty means unlimited, the frontend shows "Open"; **confirm** |
| Modes | PHYSICAL, ONLINE, HYBRID | Physical, Online, Hybrid | Match |
| Fee | NPR | "NPR 18,500" | Match |
| Public visibility | approved training of approved institute | `isPublic` is exactly that | Match |
| Institute types | your seven types | Labels differ ("Private Training Institute", "Vocational School", "NGO / INGO") | Your list stays; align the frontend labels |

Not in this list but seen in the UI: the institute registration form has a **registration number** (required), a contact
person and mobile, and the hub mentions a PAN/VAT document; `Institute` has none of those. Reviews and ratings, FAQs, SMS
alerts and the "featured" flag are out of scope here.

## Decisions this list assumes

Defaults for everything the UI or the PRD did not settle; confirm them (or change a row) before the milestone in the last
column. Rows that changed after the UI check are marked **changed**.

| # | Decision | Default used | Milestone |
|---|---|---|---|
| 1 | Categories (**changed**) | Two levels, managed by admins with `manage_categories`. A training may use a **category or a sub-category**. Starter data is the UI's 13 categories and their sub-categories, with `icon` and `hue` | C1 |
| 2 | Levels (**decided**) | `BEGINNER`, `INTERMEDIATE`, `ADVANCED` | C2 |
| 3 | Duration (**changed**) | Number plus unit (days, weeks, months), derived `duration_weeks`, filter `short`, `mid`, `long` | C2, C4 |
| 4 | Schedule (**changed**) | Training has start and end date; each session is a weekly slot (class days and times); at least one slot is needed to submit | C2, C3 |
| 5 | Editing (**changed**) | `DRAFT`, `CHANGES_REQUESTED` and `REJECTED` are saved as they are and the institute submits when ready. Editing an `APPROVED` or `UNPUBLISHED` training sends it straight back to review (hidden until approved). `SUBMITTED` cannot be edited, but can be withdrawn to `DRAFT` | C3 |
| 6 | Expiry (**changed**) | A daily job sets `EXPIRED` on `APPROVED` and `UNPUBLISHED` trainings whose `end_date` has passed; there is no manual "complete". `UNPUBLISHED` and `CANCELLED` stay (PRD) | C3 |
| 7 | Who can create and submit | Only an `APPROVED` institute can create, submit, republish or edit an approved training | C3 |
| 8 | Needed to submit (**changed**) | short description, level, duration, fee (0 allowed), start and end date, at least one weekly slot, a location unless online, start date not in the past. Overview, contact, skills and registration deadline are optional | C3 |
| 9 | Seats | Optional; empty means unlimited. The "available" filter waits for `enquiries` | C2 |
| 10 | Search (**changed**) | Full-text, `simple` configuration, prefix match over title, institute, category and sub-category, skills, short description, overview, municipality and district, module titles | C3, C4 |
| 11 | Public visibility | `APPROVED` training of an `APPROVED` institute; an expired, cancelled or unpublished training is not listed | C4 |
| 12 | Cover image | Own endpoint (multipart), jpg or png, 5 MB | C5 |
| 13 | Deleting | Only a `DRAFT` | C5 |
| 14 | Sorting | `ordering=published_at, start_date, fee_npr` (either direction); with `search`, best match first. UI "Newest" is `-published_at`, "Upcoming" is `start_date` | C4 |
| 15 | Contact | Optional on the training; the public page falls back to the institute's contact phone and email | C2, C4 |
| 16 | Map link | `map_url` on `InstituteLocation` | C2 |

Already decided elsewhere: modes `PHYSICAL`, `ONLINE`, `HYBRID`; a training is held at exactly one location of its own
institute; one fee in NPR; all times are Nepal time; certification is free text; a training's location must belong to the
same institute (checked in the service, because Django 5.2 has no composite foreign keys).

State machine (rows 5 and 6). Moves to `APPROVED`, `CHANGES_REQUESTED` and `REJECTED` are admin actions; the rest are the
institute's, or the system's for `EXPIRED`:

```
DRAFT              -> SUBMITTED
SUBMITTED          -> APPROVED | CHANGES_REQUESTED | REJECTED (admin) | DRAFT (institute withdraws)
CHANGES_REQUESTED  -> SUBMITTED
REJECTED           -> SUBMITTED
APPROVED           -> UNPUBLISHED | CANCELLED | EXPIRED (system) | SUBMITTED (an edit)
UNPUBLISHED        -> APPROVED (republish) | CANCELLED | EXPIRED (system) | SUBMITTED (an edit)
CANCELLED, EXPIRED are final
```

Labels for the frontend: Pending Review is `SUBMITTED`; Draft, Approved, Rejected, Changes Requested and Expired are the
same words. Unpublished and Cancelled have no UI yet.

---

## C0 – Review fixes and housekeeping

- [x] Branch created (`feature/catalog-app`).
- [x] Confirm the sixteen decisions above (or reply "use the defaults").
- [x] Fix the category task path. `apps/catalog/services.py::update_category` queues `apps.catalog.tasks.refresh_category_trainings`,
  which does not exist and, with the split, belongs to the training app. Nothing tests it yet, so the failure would be silent:

  ```python
  # apps/catalog/services.py, in update_category
  transaction.on_commit(lambda: async_task(
      "apps.training.tasks.refresh_category_trainings", category.pk, save=False))
  ```

- [x] Small clean-ups from the review: `AdminCategoryFilter.Meta.fields` is a **set** (`{"parent", "is_active"}`), use a tuple
  (a set has no stable order, the same reason `MunicipalityType.CHOICES` had to be a tuple); rename the cache key to
  `"catalog:category-tree:v1"` (it is `catalog:catalog-tree:v1`); delete the stub `apps/training/views.py`; add a full stop to
  the first error message in `_check_parent` (the second has one).
- [x] `django.contrib.postgres` is now installed. It is harmless (one small query per new database connection), it makes
  `ArrayField` available (used for `class_days` and `skills`), and it makes `CLAUDE.md` and version 1 wrong where they said it
  stays out. Docs are updated in C6.
- [x] Move the shared test helpers. `apps/catalog/tests/helpers.py` imports `apps.training.models` and calls
  `services.refresh_search_vector` from `apps.catalog.services`, which will not have it. Keep `make_category` there; put
  `approved_institute` and `make_training` in `apps/training/tests/helpers.py` (C2).

## C1 – Categories (mostly done)

- [x] Constants, model, migration `0003` (applied), signals, services, public tree API, admin API and URLs.
- [x] Add `icon` and `hue` (the hub draws every category tile with a Remix icon and a colour). Edit the model and make a new
  migration (`0003` is already applied, so this is `0004`):

  ```python
  # apps/catalog/models.py, in Category
  icon = models.CharField(max_length=50, blank=True)                       # a Remix icon name, e.g. "ri-cup-line"
  hue = models.PositiveSmallIntegerField(null=True, blank=True)            # 0 to 360, the tile colour

  # in Category.Meta.constraints
  models.CheckConstraint(condition=models.Q(hue__isnull=True) | models.Q(hue__lte=360),
                         name="catalog_category_hue_range"),
  ```

  Add `"icon"` and `"hue"` to `AdminCategorySerializer.Meta.fields` and to the `.values(...)` call in `build_category_tree`.

- [x] Starter data. It is the UI's own list, not the PRD examples: 13 categories with their icon and hue, and the
  sub-categories that the UI's sample trainings use. Create `apps/catalog/data/categories.json`:

  ```json
  [
    {"name": "IT & Computer", "icon": "ri-computer-line", "hue": 235, "children": ["Web development", "Office skills", "Data"]},
    {"name": "Digital Marketing", "icon": "ri-megaphone-line", "hue": 300, "children": ["Social media"]},
    {"name": "Accounting & Finance", "icon": "ri-calculator-line", "hue": 155, "children": ["Accounting software", "Taxation"]},
    {"name": "Hospitality", "icon": "ri-cup-line", "hue": 50, "children": ["Coffee & Barista", "Hotel operations", "Culinary"]},
    {"name": "Beauty & Wellness", "icon": "ri-sparkling-2-line", "hue": 350, "children": ["Makeup"]},
    {"name": "Language Training", "icon": "ri-translate-2", "hue": 270, "children": ["English tests", "Japanese"]},
    {"name": "Professional Skills", "icon": "ri-briefcase-4-line", "hue": 205, "children": ["Excel", "Soft skills"]},
    {"name": "Technical & Vocational", "icon": "ri-tools-line", "hue": 75, "children": ["Equipment maintenance", "Electrical"]},
    {"name": "Healthcare", "icon": "ri-heart-pulse-line", "hue": 20, "children": ["Caregiving"]},
    {"name": "Driving & Automobile", "icon": "ri-steering-2-line", "hue": 110, "children": ["Car driving", "Scooter & bike"]},
    {"name": "Graphic Design", "icon": "ri-palette-line", "hue": 325, "children": ["Graphic design", "UI/UX"]},
    {"name": "Entrepreneurship", "icon": "ri-lightbulb-flash-line", "hue": 90, "children": ["Startup basics"]},
    {"name": "Other Skills", "icon": "ri-apps-2-line", "hue": 250, "children": []}
  ]
  ```

  "Other Skills" has no sub-categories, which is why a training may use a top-level category (decision 1). Admins add more
  sub-categories through the admin API. The command, `apps/catalog/management/commands/load_categories.py`; it never
  re-activates a retired category and never overwrites an icon or hue that an admin changed:

  ```python
  import json
  from pathlib import Path

  from django.core.management.base import BaseCommand
  from django.db import transaction

  from apps.catalog.models import Category

  DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "categories.json"


  class Command(BaseCommand):
      help = "Load the starter categories (the UI's list). Safe to run twice."

      @transaction.atomic
      def handle(self, *args, **options):
          for entry in json.loads(DATA_FILE.read_text(encoding="utf-8")):
              top, _ = Category.objects.get_or_create(
                  name=entry["name"], parent=None, defaults={"icon": entry["icon"], "hue": entry["hue"]})
              for child in entry["children"]:
                  Category.objects.get_or_create(name=child, parent=top)
          self.stdout.write(self.style.SUCCESS(f"Categories: {Category.objects.count()}"))
  ```

- [x] Read-only admin for `Category` in `apps/catalog/admin.py` (same pattern as `Location`: no add, change or delete).
- [x] Tests, `apps/catalog/tests/test_categories.py`:
  - Constraints: a duplicate top-level name (any case) is rejected; the same name twice under one parent is rejected; the same name under two parents is allowed; a category cannot be its own parent; a hue above 360 is rejected.
  - Services: a sub-category under a sub-category is refused; a category with children cannot become a sub-category; moving a sub-category to another top-level works; renaming or moving queues the refresh task (patch `apps.catalog.services.async_task` and use `captureOnCommitCallbacks`; assert the path is `apps.training.tasks.refresh_category_trainings`).
  - Tree API: public, hides inactive categories and the children of an inactive parent, includes `icon` and `hue`, is cached (`assertNumQueries(0)` on the second call) and cleared by a save.
  - Admin API: anonymous 401, institute staff 403, an admin without `manage_categories` 403, with it 200; create, rename, move and deactivate; a duplicate name (any case) gives 400; no DELETE (405).
  - Seed command: run twice gives 13 top-level categories and 22 sub-categories; a retired category stays retired; an edited icon is kept.
- [x] **C1 done when:** the suite is green, and `python manage.py load_categories` then `GET /api/v1/categories/` shows the tree.

## C2 – Training data layer (`apps/training`)

- [x] App created, installed (`apps.training` in `LOCAL_APPS`), models written, migration generated.
- [x] Constants. Version 1 put them in `apps/catalog/constants.py`; with a separate app they belong in the training app
  (the migration does not mention them, so moving is free). Create `apps/training/constants.py` and delete the training
  parts from `apps/catalog/constants.py` (keep `LocationLevel`, `MunicipalityType` and the two cache keys there):

  ```python
  class TrainingMode:
      PHYSICAL, ONLINE, HYBRID = "PHYSICAL", "ONLINE", "HYBRID"
      CHOICES = ((PHYSICAL, "Physical"), (ONLINE, "Online"), (HYBRID, "Hybrid"))


  class TrainingLevel:
      BEGINNER, INTERMEDIATE, ADVANCED = "BEGINNER", "INTERMEDIATE", "ADVANCED"      # exactly the UI's three
      CHOICES = ((BEGINNER, "Beginner"), (INTERMEDIATE, "Intermediate"), (ADVANCED, "Advanced"))


  class DurationUnit:
      DAYS, WEEKS, MONTHS = "DAYS", "WEEKS", "MONTHS"
      CHOICES = ((DAYS, "Days"), (WEEKS, "Weeks"), (MONTHS, "Months"))


  class WeekDay:
      """Nepal's week starts on Sunday, like the UI's day picker."""
      SUN, MON, TUE, WED, THU, FRI, SAT = "SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"
      ORDER = (SUN, MON, TUE, WED, THU, FRI, SAT)
      CHOICES = ((SUN, "Sun"), (MON, "Mon"), (TUE, "Tue"), (WED, "Wed"), (THU, "Thu"), (FRI, "Fri"), (SAT, "Sat"))


  class TrainingStatus:
      DRAFT = "DRAFT"
      SUBMITTED = "SUBMITTED"                       # "Pending Review" in the UI
      APPROVED = "APPROVED"
      CHANGES_REQUESTED = "CHANGES_REQUESTED"
      REJECTED = "REJECTED"
      UNPUBLISHED = "UNPUBLISHED"
      CANCELLED = "CANCELLED"
      EXPIRED = "EXPIRED"                           # set by a daily job once end_date has passed

      CHOICES = (
          (DRAFT, "Draft"), (SUBMITTED, "Pending review"), (APPROVED, "Approved"),
          (CHANGES_REQUESTED, "Changes requested"), (REJECTED, "Rejected"),
          (UNPUBLISHED, "Unpublished"), (CANCELLED, "Cancelled"), (EXPIRED, "Expired"),
      )
      TRANSITIONS = {
          DRAFT: {SUBMITTED},
          SUBMITTED: {APPROVED, CHANGES_REQUESTED, REJECTED, DRAFT},
          CHANGES_REQUESTED: {SUBMITTED},
          REJECTED: {SUBMITTED},
          APPROVED: {UNPUBLISHED, CANCELLED, EXPIRED, SUBMITTED},
          UNPUBLISHED: {APPROVED, CANCELLED, EXPIRED, SUBMITTED},
          CANCELLED: set(),
          EXPIRED: set(),
      }
      EDITABLE = {DRAFT, CHANGES_REQUESTED, REJECTED}     # saved as is; the institute submits when ready
      REVIEWED_EDIT = {APPROVED, UNPUBLISHED}             # an edit goes straight back to review
      REASON_REQUIRED = {CHANGES_REQUESTED, REJECTED}
      FINISHED = {CANCELLED, EXPIRED}


  SEARCH_CONFIG = "simple"          # no stemming: safe for English and romanised Nepali words
  ```

- [x] Replace `apps/training/models.py`. Changes from what you wrote: `short_description`, `skills`, the contact fields,
  `duration_weeks`; levels and duration units from the UI; a session is a weekly slot; constraint and index names use the
  app's own prefix (index names must be 30 characters or fewer):

  ```python
  from django.contrib.postgres.fields import ArrayField
  from django.contrib.postgres.indexes import GinIndex
  from django.contrib.postgres.search import SearchVectorField
  from django.db import models

  from apps.catalog.models import Category
  from apps.common.models import BaseModel, SlugModel
  from apps.common.utils.helpers import get_upload_path
  from apps.common.validators import validate_phone_number
  from apps.institutes.models import Institute, InstituteLocation
  from apps.institutes.validators import validate_image_file
  from apps.training.constants import (
      DurationUnit, TrainingLevel, TrainingMode, TrainingStatus, WeekDay,
  )


  class Training(BaseModel, SlugModel):
      institute = models.ForeignKey(Institute, on_delete=models.PROTECT, related_name="trainings")
      category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="trainings")   # category or sub-category
      title = models.CharField(max_length=255)
      short_description = models.CharField(max_length=160, blank=True)       # shown on cards; required to submit
      overview = models.TextField(blank=True)                                # the detailed description
      mode = models.CharField(max_length=10, choices=TrainingMode.CHOICES)
      level = models.CharField(max_length=15, choices=TrainingLevel.CHOICES, blank=True)
      duration_value = models.PositiveSmallIntegerField(null=True, blank=True)
      duration_unit = models.CharField(max_length=10, choices=DurationUnit.CHOICES, blank=True)
      duration_weeks = models.PositiveSmallIntegerField(null=True, blank=True, editable=False)   # derived; the duration filter uses it
      fee_npr = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)      # 0 means free
      seats = models.PositiveIntegerField(null=True, blank=True)                                  # empty = unlimited
      start_date = models.DateField(null=True, blank=True)                                        # Nepal time
      end_date = models.DateField(null=True, blank=True)
      registration_deadline = models.DateField(null=True, blank=True)
      institute_location = models.ForeignKey(InstituteLocation, null=True, blank=True,
                                             on_delete=models.PROTECT, related_name="trainings")
      eligibility = models.TextField(blank=True)
      certification = models.CharField(max_length=255, blank=True)                                # free text
      skills = ArrayField(models.CharField(max_length=60), blank=True, default=list)              # "Skills covered"
      contact_person = models.CharField(max_length=150, blank=True)
      contact_phone = models.CharField(max_length=25, blank=True, validators=[validate_phone_number])
      contact_email = models.EmailField(blank=True)
      cover_image = models.ImageField(upload_to=get_upload_path, blank=True, validators=[validate_image_file])
      status = models.CharField(max_length=20, choices=TrainingStatus.CHOICES, default=TrainingStatus.DRAFT)
      review_feedback = models.TextField(blank=True)
      published_at = models.DateTimeField(null=True, blank=True)                                  # first approval
      search_vector = SearchVectorField(null=True, editable=False)

      class Meta:
          constraints = [
              # drafts may be incomplete, so only "online has no location" is a database rule;
              # "physical and hybrid need a location" is checked when submitting
              models.CheckConstraint(
                  condition=~models.Q(mode=TrainingMode.ONLINE, institute_location__isnull=False),
                  name="training_online_has_no_location"),
              models.CheckConstraint(
                  condition=models.Q(start_date__isnull=True) | models.Q(end_date__isnull=True)
                  | models.Q(end_date__gte=models.F("start_date")),
                  name="training_dates_ordered"),
              models.CheckConstraint(
                  condition=models.Q(registration_deadline__isnull=True) | models.Q(start_date__isnull=True)
                  | models.Q(registration_deadline__lte=models.F("start_date")),
                  name="training_deadline_before_start"),
              models.CheckConstraint(
                  condition=models.Q(fee_npr__isnull=True) | models.Q(fee_npr__gte=0),
                  name="training_fee_not_negative"),
              models.CheckConstraint(
                  condition=models.Q(seats__isnull=True) | models.Q(seats__gt=0),
                  name="training_seats_positive"),
              models.CheckConstraint(
                  condition=models.Q(duration_value__isnull=True) | models.Q(duration_value__gt=0),
                  name="training_duration_positive"),
              models.CheckConstraint(
                  condition=models.Q(duration_value__isnull=True) | ~models.Q(duration_unit=""),
                  name="training_duration_has_unit"),
          ]
          indexes = [
              models.Index(fields=["start_date"], condition=models.Q(status=TrainingStatus.APPROVED),
                           name="training_start_pub_idx"),
              models.Index(fields=["-published_at"], condition=models.Q(status=TrainingStatus.APPROVED),
                           name="training_published_idx"),
              models.Index(fields=["institute", "status"], name="training_inst_status_idx"),
              models.Index(fields=["category", "status"], name="training_cat_status_idx"),
              GinIndex(fields=["search_vector"], name="training_search_gin"),
          ]

      def __str__(self):
          return self.title


  class TrainingSession(BaseModel):
      """A weekly class slot: the days it runs on and the time of day (Nepal time, online included).
      A training may have several, for example a morning and an evening batch."""
      training = models.ForeignKey(Training, on_delete=models.CASCADE, related_name="sessions")
      class_days = ArrayField(models.CharField(max_length=3, choices=WeekDay.CHOICES), size=7)
      start_time = models.TimeField()
      end_time = models.TimeField()

      class Meta:
          constraints = [
              models.CheckConstraint(condition=models.Q(end_time__gt=models.F("start_time")),
                                     name="training_session_ends_after_start"),
          ]


  class TrainingModule(BaseModel):
      """One entry of the curriculum."""
      training = models.ForeignKey(Training, on_delete=models.CASCADE, related_name="modules")
      title = models.CharField(max_length=255)
      description = models.TextField(blank=True)
      position = models.PositiveSmallIntegerField(default=0)

      class Meta:
          indexes = [models.Index(fields=["training", "position"], name="training_module_pos_idx")]


  class LearningOutcome(BaseModel):
      training = models.ForeignKey(Training, on_delete=models.CASCADE, related_name="outcomes")
      text = models.CharField(max_length=300)
      position = models.PositiveSmallIntegerField(default=0)

      class Meta:
          indexes = [models.Index(fields=["training", "position"], name="training_outcome_pos_idx")]
  ```

- [x] Regenerate the migration (it is not applied and not committed, so this is safe): delete
  `apps/training/migrations/0001_initial.py`, run `python manage.py makemigrations training`, read it, then `migrate`.
  If you had already applied it on a database, use `migrate training zero` first, then delete and regenerate.
- [x] Institutes follow-up, the map link (decision 16). In `apps/institutes/models.py`, class `InstituteLocation`:
  `map_url = models.URLField(blank=True)`; add `"map_url"` to `InstituteLocationSerializer.Meta.fields`, to the public
  location dictionaries in `PublicInstituteListSerializer.get_location` and `PublicInstituteDetailSerializer.get_locations`,
  run `makemigrations institutes`, and add one test that a location saves and returns its link.
- [x] Read-only admin for `Training` in `apps/training/admin.py`; no inlines.
- [x] Test helpers, `apps/training/tests/helpers.py`. They reuse the institutes helpers and use `timezone.localdate()`,
  never `date.today()`:

  ```python
  from datetime import time, timedelta
  from decimal import Decimal

  from django.utils import timezone

  from apps.institutes.constants import InstituteStatus
  from apps.institutes.tests.helpers import (  # noqa: F401  (re-exported for the training tests)
      PASSWORD, TempMediaMixin, User, add_location, count_queries, make_institute, make_municipality,
      png, reset_throttles,
  )
  from apps.training import services
  from apps.training.constants import TrainingStatus
  from apps.training.models import Training, TrainingSession
  from apps.catalog.tests.helpers import make_category   # noqa: F401


  def approved_institute(name="Alpha Institute", email="owner@example.com"):
      institute, owner = make_institute(name=name, email=email, status=InstituteStatus.APPROVED)
      location = add_location(institute, make_municipality(), is_main=True)
      return institute, owner, location


  def make_training(institute, *, category=None, location=None, status=TrainingStatus.APPROVED, **overrides):
      today = timezone.localdate()
      fields = dict(
          title="Python Bootcamp", short_description="Learn Python from scratch", overview="A detailed description",
          mode="ONLINE", level="BEGINNER", duration_value=8, duration_unit="WEEKS", duration_weeks=8,
          fee_npr=Decimal("5000"), skills=["Python", "Git"],
          start_date=today + timedelta(days=30), end_date=today + timedelta(days=90),
          registration_deadline=today + timedelta(days=20), status=status,
          published_at=timezone.now() if status == TrainingStatus.APPROVED else None,
      )
      if location is not None:
          fields["mode"] = "PHYSICAL"           # a located training is physical unless the test says otherwise
      fields.update(overrides)
      training = Training.objects.create(
          institute=institute, category=category or make_category(), institute_location=location, **fields)
      TrainingSession.objects.create(
          training=training, class_days=["SUN", "MON", "TUE"], start_time=time(7, 0), end_time=time(9, 0))
      services.refresh_search_vector(training)
      return training
  ```

- [x] Constraint tests, `apps/training/tests/test_models.py`: online with a location is rejected; end before start; deadline after
  start; negative fee; zero seats; zero duration; a duration with no unit; a session that ends before it starts; a draft with only
  the required fields saves fine; `class_days` rejects an unknown day.
- [x] **C2 done when:** `check` and `makemigrations --check` are clean, the constraint tests pass, the whole suite passes.

## C3 – Services (rules, workflow, search, expiry)

- [x] `apps/training/services.py`, part 1: derived values, the search vector and the checks. Verified on your database:
  `SearchVector(Value(text), config="simple")` builds a vector without joins.

  ```python
  from django.contrib.postgres.search import SearchVector
  from django.core.exceptions import ValidationError
  from django.db import transaction
  from django.db.models import Value
  from django.utils import timezone

  from apps.institutes.constants import InstituteStatus
  from apps.institutes.models import Institute
  from apps.training.constants import SEARCH_CONFIG, DurationUnit, TrainingMode, TrainingStatus
  from apps.training.models import LearningOutcome, Training, TrainingModule, TrainingSession

  WEEKS_PER_UNIT = {DurationUnit.DAYS: 1 / 7, DurationUnit.WEEKS: 1, DurationUnit.MONTHS: 4.3}   # the portal's own rule


  def duration_in_weeks(value, unit):
      if not value or unit not in WEEKS_PER_UNIT:
          return None
      return max(1, int(value * WEEKS_PER_UNIT[unit] + 0.5))            # half up, like the portal's Math.round


  def _build_search_vector(training):
      category = training.category
      category_names = " ".join(filter(None, [category.parent.name if category.parent_id else "", category.name]))
      place = training.institute_location
      place_names = f"{place.location.name} {place.location.district.name}" if place else ""
      return (
          SearchVector(Value(training.title), weight="A", config=SEARCH_CONFIG)
          + SearchVector(Value(f"{training.institute.name} {category_names} {' '.join(training.skills)}"),
                         weight="B", config=SEARCH_CONFIG)
          + SearchVector(Value(f"{training.short_description} {training.overview} {place_names}"),
                         weight="C", config=SEARCH_CONFIG)
          + SearchVector(Value(" ".join(training.modules.values_list("title", flat=True))),
                         weight="D", config=SEARCH_CONFIG)
      )


  def refresh_search_vector(training):
      Training.objects.filter(pk=training.pk).update(search_vector=_build_search_vector(training))


  def refresh_search_vectors(queryset):
      for training in queryset.select_related(
              "institute", "category__parent", "institute_location__location__district").iterator():
          refresh_search_vector(training)


  def _require_approved_institute(institute):
      if not Institute.objects.filter(pk=institute.pk, status=InstituteStatus.APPROVED).exists():
          raise ValidationError("Only an approved institute can do this.")


  def _check_category(category):
      if not category.is_active or (category.parent_id and not category.parent.is_active):
          raise ValidationError({"category": "This category is not available."})


  def _check_location(institute, mode, location):
      if mode == TrainingMode.ONLINE:
          if location is not None:
              raise ValidationError({"institute_location": "An online training has no location."})
          return
      if location is not None and (location.institute_id != institute.pk or not location.is_active):
          raise ValidationError({"institute_location": "Choose one of your active locations."})


  def _check_dates(start, end, deadline):
      errors = {}
      if start and end and end < start:
          errors["end_date"] = "The end date cannot be before the start date."
      if deadline and start and deadline > start:
          errors["registration_deadline"] = "The registration deadline cannot be after the start date."
      if errors:
          raise ValidationError(errors)


  def _check_sessions(sessions):
      for s in sessions:
          days = s["class_days"]
          if not days or len(set(days)) != len(days):
              raise ValidationError({"sessions": "Choose at least one class day, each day once."})
          if s["end_time"] <= s["start_time"]:
              raise ValidationError({"sessions": "A session must end after it starts."})


  def _replace_children(training, sessions, modules, outcomes):
      """None leaves a list alone; a list (even an empty one) replaces it."""
      if sessions is not None:
          training.sessions.all().delete()
          TrainingSession.objects.bulk_create([TrainingSession(training=training, **s) for s in sessions])
      if modules is not None:
          training.modules.all().delete()
          TrainingModule.objects.bulk_create(
              [TrainingModule(training=training, position=i, **m) for i, m in enumerate(modules)])
      if outcomes is not None:
          training.outcomes.all().delete()
          LearningOutcome.objects.bulk_create(
              [LearningOutcome(training=training, position=i, **o) for i, o in enumerate(outcomes)])
  ```

- [x] Part 2: workflow. `only_from` is what keeps every action honest: the transition table alone would let an admin "approve"
  an unpublished training, because `UNPUBLISHED` also lists `APPROVED`. Every move runs under a row lock:

  ```python
  def _transition(training, to, *, only_from=None, reason="", check=None):
      """Caller must be inside transaction.atomic()."""
      training = (Training.objects.select_for_update()
                  .select_related("institute", "institute_location").get(pk=training.pk))
      if only_from is not None and training.status not in only_from:
          raise ValidationError(f"A {training.status.lower()} training cannot do this.")
      if to not in TrainingStatus.TRANSITIONS[training.status]:
          raise ValidationError(f"Cannot move from {training.status} to {to}.")
      if to in TrainingStatus.REASON_REQUIRED and not reason.strip():
          raise ValidationError({"reason": "A reason is required."})
      if check:
          check(training)
      training.status = to
      if to in TrainingStatus.REASON_REQUIRED:
          training.review_feedback = reason
      elif to == TrainingStatus.APPROVED:
          training.review_feedback = ""
      training.save(update_fields=["status", "review_feedback", "modified_at"])
      return training


  def _ready_for_submission(training):
      errors = {}
      required = {"short_description": training.short_description, "level": training.level,
                  "duration_value": training.duration_value, "duration_unit": training.duration_unit,
                  "fee_npr": training.fee_npr, "start_date": training.start_date, "end_date": training.end_date}
      for name, value in required.items():
          if value in (None, ""):
              errors[name] = "This is required before submitting."
      if training.mode != TrainingMode.ONLINE:
          if training.institute_location_id is None:
              errors["institute_location"] = "Choose where the training is held."
          elif not training.institute_location.is_active:
              errors["institute_location"] = "The selected location is no longer active."
      if not training.sessions.exists():
          errors["sessions"] = "Add at least one class day and time."
      if training.start_date and training.start_date < timezone.localdate():
          errors["start_date"] = "The start date is in the past."
      if errors:
          raise ValidationError(errors)


  # institute actions

  @transaction.atomic
  def submit(training, *, by):
      _require_approved_institute(training.institute)
      return _transition(training, TrainingStatus.SUBMITTED, check=_ready_for_submission,
                         only_from={TrainingStatus.DRAFT, TrainingStatus.CHANGES_REQUESTED, TrainingStatus.REJECTED})


  @transaction.atomic
  def withdraw(training, *, by):
      """Take a submitted training back to DRAFT while it waits for review."""
      return _transition(training, TrainingStatus.DRAFT, only_from={TrainingStatus.SUBMITTED})


  @transaction.atomic
  def unpublish(training, *, by):
      return _transition(training, TrainingStatus.UNPUBLISHED, only_from={TrainingStatus.APPROVED})


  @transaction.atomic
  def republish(training, *, by):
      _require_approved_institute(training.institute)
      return _transition(training, TrainingStatus.APPROVED, only_from={TrainingStatus.UNPUBLISHED})


  @transaction.atomic
  def cancel(training, *, by):
      # TODO(notify): people who sent an enquiry (once enquiries exist)
      return _transition(training, TrainingStatus.CANCELLED,
                         only_from={TrainingStatus.APPROVED, TrainingStatus.UNPUBLISHED})


  # admin actions (a training that waits for review)

  @transaction.atomic
  def approve(training, *, by):
      training = _transition(training, TrainingStatus.APPROVED, only_from={TrainingStatus.SUBMITTED})
      if training.published_at is None:
          training.published_at = timezone.now()
          training.save(update_fields=["published_at", "modified_at"])
      # TODO(audit) + TODO(notify): the institute
      return training


  @transaction.atomic
  def request_changes(training, *, by, reason):
      return _transition(training, TrainingStatus.CHANGES_REQUESTED, reason=reason,
                         only_from={TrainingStatus.SUBMITTED})


  @transaction.atomic
  def reject(training, *, by, reason):
      return _transition(training, TrainingStatus.REJECTED, reason=reason, only_from={TrainingStatus.SUBMITTED})


  # the system

  def expire_trainings(today=None):
      """Set EXPIRED on every live training whose end date has passed. One statement, safe to run often."""
      today = today or timezone.localdate()
      return Training.objects.filter(
          status__in=(TrainingStatus.APPROVED, TrainingStatus.UNPUBLISHED), end_date__lt=today,
      ).update(status=TrainingStatus.EXPIRED, modified_at=timezone.now())
  ```

- [x] Part 3: create, edit (with the review rule), cover and delete:

  ```python
  @transaction.atomic
  def create_training(institute, *, sessions=None, modules=None, outcomes=None, **fields):
      _require_approved_institute(institute)
      _check_category(fields["category"])
      _check_location(institute, fields["mode"], fields.get("institute_location"))
      _check_dates(fields.get("start_date"), fields.get("end_date"), fields.get("registration_deadline"))
      if sessions is not None:
          _check_sessions(sessions)
      fields["duration_weeks"] = duration_in_weeks(fields.get("duration_value"), fields.get("duration_unit"))
      training = Training.objects.create(institute=institute, **fields)
      _replace_children(training, sessions, modules, outcomes)
      refresh_search_vector(training)
      return training


  @transaction.atomic
  def update_training(training, *, sessions=None, modules=None, outcomes=None, **fields):
      """DRAFT, CHANGES_REQUESTED and REJECTED are saved as they are. APPROVED and UNPUBLISHED go straight back
      to review (hidden until approved), and the edit is refused if the result is not ready to submit."""
      training = (Training.objects.select_for_update()
                  .select_related("institute", "category__parent").get(pk=training.pk))
      back_to_review = training.status in TrainingStatus.REVIEWED_EDIT
      if training.status not in TrainingStatus.EDITABLE and not back_to_review:
          raise ValidationError(f"A {training.status.lower()} training cannot be edited.")
      mode = fields.get("mode", training.mode)
      if mode == TrainingMode.ONLINE and "institute_location" not in fields:
          fields["institute_location"] = None               # switching to online clears the location
      _check_category(fields.get("category", training.category))
      _check_location(training.institute, mode, fields.get("institute_location", training.institute_location))
      _check_dates(fields.get("start_date", training.start_date), fields.get("end_date", training.end_date),
                   fields.get("registration_deadline", training.registration_deadline))
      if sessions is not None:
          _check_sessions(sessions)
      if "duration_value" in fields or "duration_unit" in fields:
          fields["duration_weeks"] = duration_in_weeks(
              fields.get("duration_value", training.duration_value), fields.get("duration_unit", training.duration_unit))
      for name, value in fields.items():
          setattr(training, name, value)
      training.save(update_fields=[*fields, "modified_at"])
      _replace_children(training, sessions, modules, outcomes)
      refresh_search_vector(training)
      if back_to_review:
          _require_approved_institute(training.institute)
          training = _transition(training, TrainingStatus.SUBMITTED, check=_ready_for_submission)
      return training


  @transaction.atomic
  def set_cover(training, image):
      training = Training.objects.select_for_update().get(pk=training.pk)
      if training.status not in TrainingStatus.EDITABLE:
          raise ValidationError("The cover can only change while the training is a draft or being revised.")
      training.cover_image = image
      training.save(update_fields=["cover_image", "modified_at"])
      return training


  @transaction.atomic
  def delete_training(training):
      training = Training.objects.select_for_update().get(pk=training.pk)
      if training.status != TrainingStatus.DRAFT:
          raise ValidationError("Only a draft can be deleted. Cancel the training instead.")
      training.delete()
  ```

  A failed check in `_transition` rolls the whole edit back, because everything runs in one transaction.

- [x] Tasks and the daily expiry job. `apps/training/tasks.py`:

  ```python
  from django.db.models import Q

  from apps.training import services
  from apps.training.models import Training


  def refresh_institute_trainings(institute_id):
      services.refresh_search_vectors(Training.objects.filter(institute_id=institute_id))


  def refresh_category_trainings(category_id):
      services.refresh_search_vectors(
          Training.objects.filter(Q(category_id=category_id) | Q(category__parent_id=category_id)))


  def refresh_location_trainings(institute_location_id):
      services.refresh_search_vectors(Training.objects.filter(institute_location_id=institute_location_id))


  def expire_trainings():
      return services.expire_trainings()
  ```

  and the command, `apps/training/management/commands/expire_trainings.py` (run it by hand or from cron):

  ```python
  from django.core.management.base import BaseCommand

  from apps.training import services


  class Command(BaseCommand):
      help = "Set EXPIRED on trainings whose end date has passed. Safe to run any time."

      def handle(self, *args, **options):
          self.stdout.write(self.style.SUCCESS(f"Expired {services.expire_trainings()} training(s)"))
  ```

  To run it daily without cron, add a `Schedule` in the Django admin (Django Q, Scheduled tasks): function
  `apps.training.tasks.expire_trainings`, schedule type Daily. `qcluster` must be running.

- [x] Keep the search vector fresh. In `apps/institutes/services.py`:

  ```python
  # new function; use it from the profile serializer
  @transaction.atomic
  def update_profile(institute, **fields):
      institute = Institute.objects.select_for_update().get(pk=institute.pk)
      renamed = "name" in fields and fields["name"] != institute.name
      for name, value in fields.items():
          setattr(institute, name, value)
      institute.save(update_fields=[*fields, "modified_at"])
      if renamed:
          transaction.on_commit(lambda: async_task(
              "apps.training.tasks.refresh_institute_trainings", institute.pk, save=False))
      return institute


  # in update_location, after the save
  if "location" in fields:
      transaction.on_commit(lambda: async_task(
          "apps.training.tasks.refresh_location_trainings", instance.pk, save=False))
  ```

  ```python
  # apps/institutes/api/v1/serializers.py, in InstituteProfileSerializer (add)
  def update(self, instance, validated_data):
      return services.update_profile(instance, **validated_data)
  ```

- [x] Finish the old `TODO(catalog)` in `deactivate_location` (`apps/institutes/services.py`): a location that a live training uses
  cannot be retired:

  ```python
  from apps.training.constants import TrainingStatus     # constants only, so there is no import cycle

  # inside deactivate_location, before the update:
  if location.trainings.exclude(status__in=TrainingStatus.FINISHED).exists():
      raise ValidationError("Move or cancel the trainings held at this location first.")
  ```

- [x] Tests, `apps/training/tests/test_services.py`:
  - State machine: every pair of statuses through `_transition` (allowed ones work, all others raise); every action refuses a status outside its `only_from` (for example `approve` on `UNPUBLISHED`, `submit` on `APPROVED`); a reason is required for changes-requested and reject; approving sets `published_at` once and clears the feedback; rejecting stores it; withdrawing keeps it.
  - Create: an unapproved institute, an inactive category, a sub-category of an inactive parent, another institute's location, an inactive location, an online training with a location, end before start and a deadline after the start are all refused; a top-level category and a sub-category are both accepted; `duration_weeks` is derived (6 weeks gives 6, 2 months gives 9, 3 months gives 13, 1 month gives 4, 10 days gives 1).
  - Edit: `DRAFT`, `CHANGES_REQUESTED` and `REJECTED` keep their status; an edit of `APPROVED` or `UNPUBLISHED` moves to `SUBMITTED`, and is refused (nothing saved) when the result is not ready; `SUBMITTED`, `CANCELLED` and `EXPIRED` cannot be edited; switching to online clears the location; changing the unit recomputes the weeks.
  - Children: sessions, modules and outcomes are replaced as a set; `None` keeps them, `[]` empties them; an empty or repeated `class_days`, and a session ending before it starts, are refused; positions follow the list order.
  - Submit: every missing field is reported at once; a physical training needs a location; no session and a start date in the past are refused; a free training (fee 0) is accepted; a suspended or pending institute is refused.
  - Workflow: unpublish then republish needs no review; withdraw only from `SUBMITTED`; cancel is final; a suspended institute cannot republish.
  - Expiry: an `APPROVED` or `UNPUBLISHED` training past its end date becomes `EXPIRED`; one ending today does not; drafts and cancelled trainings are untouched; a second run changes nothing; the command prints the count.
  - Search vector: found by a title prefix; by a skill; by the short description; by the municipality; by the institute's new name after `update_profile` (with the queued task run); by the new category name after a rename or a move; by a module title.
  - `deactivate_location` is refused while a live training uses it, and allowed once the training is cancelled or expired.
- [x] **C3 done when:** the services tests pass and the suite is green.

## C4 – Public API: list, detail, search and filters

- [x] Wire the URLs. Prefixes live only in `apps/api/v1/urls.py`; the `institute/` include from `institutes` has no `trainings/`
  route, so that one is reached by falling through (keep it after). `admin/` now has three includes, which is fine because
  their routes differ:

  ```python
  path("trainings/", include("apps.training.api.v1.urls.trainings")),
  path("institute/trainings/", include("apps.training.api.v1.urls.portal")),       # C5
  path("admin/", include("apps.training.api.v1.urls.admin")),                      # C5
  ```

  Create the package: `apps/training/api/__init__.py`, `api/v1/__init__.py`, `api/v1/urls/__init__.py` and the modules below.

- [x] Public serializers, `apps/training/api/v1/serializers.py`:

  ```python
  from rest_framework import serializers

  from apps.common.serializers import DynamicFieldsModelSerializer
  from apps.training.constants import WeekDay
  from apps.training.models import Training


  def format_class_days(days):
      """['SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI'] gives 'Sun – Fri'; a gap gives 'Sun, Tue, Thu'."""
      labels = dict(WeekDay.CHOICES)
      indexes = sorted(WeekDay.ORDER.index(d) for d in set(days))
      if len(indexes) > 2 and indexes == list(range(indexes[0], indexes[-1] + 1)):
          return f"{labels[WeekDay.ORDER[indexes[0]]]} – {labels[WeekDay.ORDER[indexes[-1]]]}"
      return ", ".join(labels[WeekDay.ORDER[i]] for i in indexes)


  class PublicTrainingListSerializer(DynamicFieldsModelSerializer):
      duration = serializers.SerializerMethodField()
      institute = serializers.SerializerMethodField()
      category = serializers.SerializerMethodField()
      location = serializers.SerializerMethodField()

      class Meta:
          model = Training
          fields = ("id", "slug", "title", "short_description", "mode", "level", "duration", "fee_npr",
                    "start_date", "end_date", "registration_deadline", "cover_image", "skills",
                    "institute", "category", "location", "published_at")

      def get_duration(self, obj):
          unit = obj.duration_unit.lower()
          return {"value": obj.duration_value, "unit": obj.duration_unit, "weeks": obj.duration_weeks,
                  "text": f"{obj.duration_value} {unit[:-1] if obj.duration_value == 1 else unit}"}

      def get_institute(self, obj):
          return {"slug": obj.institute.slug, "name": obj.institute.name,
                  "logo": obj.institute.logo.url if obj.institute.logo else None}

      def get_category(self, obj):
          parent = obj.category.parent
          return {"id": obj.category.id, "name": obj.category.name,
                  "parent": {"id": parent.id, "name": parent.name} if parent else None}

      def get_location(self, obj):
          place = obj.institute_location
          if place is None:
              return None                                                  # online
          return {"municipality": place.location.name, "district": place.location.district.name,
                  "province": place.location.province.name, "address": place.address, "map_url": place.map_url}


  class PublicTrainingDetailSerializer(PublicTrainingListSerializer):
      schedule = serializers.SerializerMethodField()
      modules = serializers.SerializerMethodField()
      outcomes = serializers.SerializerMethodField()
      contact = serializers.SerializerMethodField()

      class Meta(PublicTrainingListSerializer.Meta):
          fields = PublicTrainingListSerializer.Meta.fields + (
              "overview", "eligibility", "certification", "seats", "schedule", "modules", "outcomes", "contact")

      def get_schedule(self, obj):
          return [{"class_days": s.class_days, "class_days_text": format_class_days(s.class_days),
                   "start_time": s.start_time, "end_time": s.end_time} for s in obj.sessions.all()]

      def get_modules(self, obj):
          return [{"title": m.title, "description": m.description} for m in obj.modules.all()]

      def get_outcomes(self, obj):
          return [o.text for o in obj.outcomes.all()]

      def get_contact(self, obj):
          return {"person": obj.contact_person,
                  "phone": obj.contact_phone or obj.institute.contact_phone,      # falls back to the institute
                  "email": obj.contact_email or obj.institute.contact_email}
  ```

- [x] Filters and search, `apps/training/api/v1/filters.py`. Prefix search turns every word into `word:*` after stripping everything
  that is not a letter or digit, so user input can never break the query. An online training has no location, so a location filter
  excludes it. The duration buckets are the hub's own: under 4 weeks, 4 to 12, 13 or more. `registration_open` is derived: the
  deadline has not passed, or there is no deadline and the training has not started:

  ```python
  import re

  import django_filters
  from django.contrib.postgres.search import SearchQuery, SearchRank
  from django.db.models import F, Q
  from django.utils import timezone

  from apps.training.constants import SEARCH_CONFIG
  from apps.training.models import Training

  DURATION_BUCKETS = {"short": Q(duration_weeks__lt=4), "mid": Q(duration_weeks__gte=4, duration_weeks__lt=13),
                      "long": Q(duration_weeks__gte=13)}


  def prefix_query(text):
      words = re.findall(r"[^\W_]+", text.lower())[:8]
      return " & ".join(f"{word}:*" for word in words)


  class TrainingFilter(django_filters.FilterSet):
      category = django_filters.NumberFilter(method="filter_category")           # a category or any of its sub-categories
      sub_category = django_filters.NumberFilter(field_name="category_id")
      province = django_filters.NumberFilter(field_name="institute_location__location__province_id")
      district = django_filters.NumberFilter(field_name="institute_location__location__district_id")
      municipality = django_filters.NumberFilter(field_name="institute_location__location_id")
      fee_min = django_filters.NumberFilter(field_name="fee_npr", lookup_expr="gte")
      fee_max = django_filters.NumberFilter(field_name="fee_npr", lookup_expr="lte")
      start_from = django_filters.DateFilter(field_name="start_date", lookup_expr="gte")
      start_to = django_filters.DateFilter(field_name="start_date", lookup_expr="lte")
      duration = django_filters.ChoiceFilter(choices=[(k, k) for k in DURATION_BUCKETS], method="filter_duration")
      duration_weeks_min = django_filters.NumberFilter(field_name="duration_weeks", lookup_expr="gte")
      duration_weeks_max = django_filters.NumberFilter(field_name="duration_weeks", lookup_expr="lte")
      institute = django_filters.CharFilter(field_name="institute__slug")
      registration_open = django_filters.BooleanFilter(method="filter_registration_open")
      search = django_filters.CharFilter(method="filter_search")

      class Meta:
          model = Training
          fields = ("mode", "level")

      def filter_category(self, queryset, name, value):
          return queryset.filter(Q(category_id=value) | Q(category__parent_id=value))

      def filter_duration(self, queryset, name, value):
          return queryset.filter(DURATION_BUCKETS[value])

      def filter_registration_open(self, queryset, name, value):
          if not value:
              return queryset
          today = timezone.localdate()
          return queryset.filter(Q(registration_deadline__gte=today)
                                 | Q(registration_deadline__isnull=True, start_date__gte=today))

      def filter_search(self, queryset, name, value):
          query = prefix_query(value)
          if not query:
              return queryset
          search_query = SearchQuery(query, config=SEARCH_CONFIG, search_type="raw")
          return (queryset.filter(search_vector=search_query)
                  .annotate(rank=SearchRank(F("search_vector"), search_query))
                  .order_by("-rank", "-published_at", "-pk"))
  ```

- [x] Public viewset and URLs, `apps/training/api/v1/views.py`. The list needs no prefetch (cards show no schedule); the
  detail loads its children with three prefetches. Sort mapping for the UI: Newest is `-published_at`, Upcoming is `start_date`,
  Price is `fee_npr` or `-fee_npr`; Relevance is the default when `search` is set:

  ```python
  from django.db.models import Prefetch
  from django_filters.rest_framework import DjangoFilterBackend
  from rest_framework.filters import OrderingFilter

  from apps.common.viewsets import ReadOnlyViewSet
  from apps.institutes.constants import InstituteStatus
  from apps.training.api.v1.filters import TrainingFilter
  from apps.training.api.v1.serializers import PublicTrainingDetailSerializer, PublicTrainingListSerializer
  from apps.training.constants import TrainingStatus
  from apps.training.models import LearningOutcome, Training, TrainingModule, TrainingSession


  class PublicTrainingViewSet(ReadOnlyViewSet):
      permission_classes = []                     # public
      lookup_field = "slug"
      filter_backends = (DjangoFilterBackend, OrderingFilter)
      filterset_class = TrainingFilter
      ordering_fields = ("published_at", "start_date", "fee_npr")

      def get_serializer_class(self):
          return PublicTrainingDetailSerializer if self.action == "retrieve" else PublicTrainingListSerializer

      def get_queryset(self):
          queryset = (
              Training.objects.filter(status=TrainingStatus.APPROVED, institute__status=InstituteStatus.APPROVED)
              .select_related("institute", "category__parent",
                              "institute_location__location__district", "institute_location__location__province")
          )
          if self.action == "retrieve":
              return queryset.prefetch_related(
                  Prefetch("sessions", queryset=TrainingSession.objects.order_by("start_time", "pk")),
                  Prefetch("modules", queryset=TrainingModule.objects.order_by("position", "pk")),
                  Prefetch("outcomes", queryset=LearningOutcome.objects.order_by("position", "pk")))
          return queryset.order_by("-published_at", "-pk")
  ```

  ```python
  # apps/training/api/v1/urls/trainings.py
  from rest_framework import routers

  from apps.training.api.v1 import views

  app_name = "trainings"
  router = routers.SimpleRouter()
  router.register("", views.PublicTrainingViewSet, basename="training")
  urlpatterns = router.urls
  ```

- [x] Tests, `apps/training/tests/test_api_public.py`:
  - Visibility: only `APPROVED` trainings of `APPROVED` institutes; every other status is hidden (including `EXPIRED`, `UNPUBLISHED`, `CANCELLED`), and so is a training of a suspended institute; the detail of a hidden training is a 404.
  - Filters, one test each: `category` (a top-level id finds its sub-categories' trainings), `sub_category`, `mode`, `level`, `province`, `district`, `municipality` (online trainings excluded), `fee_min` and `fee_max`, `start_from` and `start_to`, `duration` (each bucket, including the edges: 1 month is `mid`, 3 months is `long`), `duration_weeks_min` and `duration_weeks_max`, `institute`, `registration_open`.
  - Search: a whole word, a prefix (`pyth`), two prefixes (`pyth boot`), a skill, the institute name, the category and sub-category names, the municipality, the short description, a module title; no match gives an empty list; punctuation and SQL-looking input are harmless; best match first when no `ordering` is given.
  - Ordering: `ordering=start_date`, `-fee_npr`, `-published_at`; the default is newest published first.
  - Detail: the schedule shows each slot with its days text (`Sun – Fri`) and times; modules and outcomes in position order; the card of the institute; the location with district, province and map link; the contact falls back to the institute's phone and email.
  - Query counts: the list costs the same number of queries for 1 and for 15 trainings, and the detail is constant (use `count_queries`, and start from one row).
  - Writes are 405.
- [x] **C4 done when:** the suite is green, and filtering and prefix search work from Swagger at `/api/root/`.

## C5 – Institute portal and admin review

- [x] Portal serializers, appended to `apps/training/api/v1/serializers.py` (add `Q`, `serializers`, `validate_image_file`, the models
  and `services` imports). A nested list replaces the whole list and leaving it out keeps it. The cover image has its own endpoint,
  because nested lists and files do not mix in one multipart request:

  ```python
  class TrainingSessionSerializer(serializers.ModelSerializer):
      class Meta:
          model = TrainingSession
          fields = ("class_days", "start_time", "end_time")


  class TrainingModuleSerializer(serializers.ModelSerializer):
      class Meta:
          model = TrainingModule
          fields = ("title", "description")


  class LearningOutcomeSerializer(serializers.ModelSerializer):
      class Meta:
          model = LearningOutcome
          fields = ("text",)


  class OwnLocationField(serializers.PrimaryKeyRelatedField):
      """Only the caller's own active locations are valid; anything else reads as an unknown id."""

      def get_queryset(self):
          institute_id = self.context["request"].user.membership.institute_id
          return InstituteLocation.objects.filter(institute_id=institute_id, is_active=True)


  class PortalTrainingSerializer(DynamicFieldsModelSerializer):
      category = serializers.PrimaryKeyRelatedField(
          queryset=Category.objects.filter(is_active=True).filter(Q(parent__isnull=True) | Q(parent__is_active=True)))
      institute_location = OwnLocationField(required=False, allow_null=True)
      sessions = TrainingSessionSerializer(many=True, required=False)
      modules = TrainingModuleSerializer(many=True, required=False)
      outcomes = LearningOutcomeSerializer(many=True, required=False)

      class Meta:
          model = Training
          fields = ("id", "slug", "title", "category", "short_description", "overview", "mode", "level",
                    "duration_value", "duration_unit", "duration_weeks", "fee_npr", "seats", "start_date", "end_date",
                    "registration_deadline", "institute_location", "eligibility", "certification", "skills",
                    "contact_person", "contact_phone", "contact_email", "cover_image", "status", "review_feedback",
                    "sessions", "modules", "outcomes", "created_at")
          read_only_fields = ("id", "slug", "duration_weeks", "cover_image", "status", "review_feedback", "created_at")

      def _children(self, data):
          return {key: data.pop(key, None) for key in ("sessions", "modules", "outcomes")}

      def create(self, validated_data):
          children = self._children(validated_data)
          return services.create_training(self.request.user.membership.institute, **children, **validated_data)

      def update(self, instance, validated_data):
          children = self._children(validated_data)
          return services.update_training(instance, **children, **validated_data)


  class PortalTrainingListSerializer(DynamicFieldsModelSerializer):
      category_name = serializers.CharField(source="category.name", read_only=True)
      municipality = serializers.SerializerMethodField()

      class Meta:
          model = Training
          fields = ("id", "slug", "title", "status", "review_feedback", "category_name", "mode", "fee_npr",
                    "start_date", "end_date", "municipality", "created_at")

      def get_municipality(self, obj):
          return obj.institute_location.location.name if obj.institute_location_id else None


  class CoverSerializer(serializers.Serializer):
      cover_image = serializers.ImageField(validators=[validate_image_file])
  ```

- [x] Portal viewset and URLs, `apps/training/api/v1/views.py`. Staff of the institute can do everything here; other institutes'
  rows are a 404. A `PATCH` on an approved training sends it back to review (decision 5):

  ```python
  class PortalTrainingViewSet(InstituteScopedMixin, CustomModelViewSet):
      permission_classes = [IsInstituteMember]
      lookup_value_regex = r"[0-9]+"
      http_method_names = ["get", "post", "patch", "delete", "head", "options"]
      filter_backends = (DjangoFilterBackend,)
      filterset_fields = ("status",)
      queryset = (Training.objects.select_related("category__parent", "institute_location__location")
                  .order_by("-created_at", "-pk"))

      def get_serializer_class(self):
          return PortalTrainingListSerializer if self.action == "list" else PortalTrainingSerializer

      def get_queryset(self):
          queryset = super().get_queryset()                   # scoped to the caller's institute
          if self.action == "list":
              return queryset
          return queryset.prefetch_related(
              Prefetch("sessions", queryset=TrainingSession.objects.order_by("start_time", "pk")),
              Prefetch("modules", queryset=TrainingModule.objects.order_by("position", "pk")),
              Prefetch("outcomes", queryset=LearningOutcome.objects.order_by("position", "pk")))

      def perform_destroy(self, instance):
          services.delete_training(instance)

      def _move(self, service):
          training = service(self.get_object(), by=self.request.user)
          fresh = self.get_queryset().get(pk=training.pk)      # reload with the children prefetched
          return Response(self.get_serializer(fresh).data)

      @action(detail=True, methods=["post"])
      def submit(self, request, pk=None):
          return self._move(services.submit)

      @action(detail=True, methods=["post"])
      def withdraw(self, request, pk=None):
          return self._move(services.withdraw)

      @action(detail=True, methods=["post"])
      def unpublish(self, request, pk=None):
          return self._move(services.unpublish)

      @action(detail=True, methods=["post"])
      def republish(self, request, pk=None):
          return self._move(services.republish)

      @action(detail=True, methods=["post"])
      def cancel(self, request, pk=None):
          return self._move(services.cancel)

      @action(detail=True, methods=["post"], parser_classes=[MultiPartParser, FormParser])
      def cover(self, request, pk=None):
          serializer = CoverSerializer(data=request.data)
          serializer.is_valid(raise_exception=True)
          training = services.set_cover(self.get_object(), serializer.validated_data["cover_image"])
          return Response(self.get_serializer(self.get_queryset().get(pk=training.pk)).data)
  ```

  ```python
  # apps/training/api/v1/urls/portal.py
  from rest_framework import routers

  from apps.training.api.v1 import views

  app_name = "training_portal"
  router = routers.SimpleRouter()
  router.register("", views.PortalTrainingViewSet, basename="portal-training")
  urlpatterns = router.urls
  ```

- [x] Admin review API (`users.manage_trainings`), appended to the same files. A reviewer lists with `?status=SUBMITTED`; the list
  serializer already shows the feedback column:

  ```python
  # serializers.py
  class AdminTrainingSerializer(PortalTrainingSerializer):
      """Read-only view of a whole training for the reviewer."""
      institute = serializers.SerializerMethodField()
      category = serializers.SerializerMethodField()
      institute_location = serializers.SerializerMethodField()

      class Meta(PortalTrainingSerializer.Meta):
          fields = PortalTrainingSerializer.Meta.fields + ("institute", "published_at")
          read_only_fields = fields

      def get_institute(self, obj):
          return {"id": obj.institute_id, "name": obj.institute.name, "status": obj.institute.status}

      def get_category(self, obj):
          parent = obj.category.parent
          return {"id": obj.category_id, "name": obj.category.name, "parent": parent.name if parent else None}

      def get_institute_location(self, obj):
          place = obj.institute_location
          return None if place is None else {"id": place.id, "municipality": place.location.name, "address": place.address}


  class TrainingReasonSerializer(serializers.Serializer):
      reason = serializers.CharField()
  ```

  ```python
  # views.py
  class AdminTrainingViewSet(ReadOnlyViewSet):
      permission_classes = [HasPlatformPermission]
      required_permission = "users.manage_trainings"
      lookup_value_regex = r"[0-9]+"
      filter_backends = (DjangoFilterBackend, SearchFilter)
      filterset_fields = ("status", "mode")
      search_fields = ("title", "institute__name")
      queryset = (Training.objects.select_related("institute", "category__parent", "institute_location__location")
                  .order_by("-created_at", "-pk"))

      def get_serializer_class(self):
          return PortalTrainingListSerializer if self.action == "list" else AdminTrainingSerializer

      def get_queryset(self):
          queryset = super().get_queryset()
          if self.action == "list":
              return queryset
          return queryset.prefetch_related("sessions", "modules", "outcomes")

      def _review(self, request, service, *, with_reason):
          kwargs = {}
          if with_reason:
              serializer = TrainingReasonSerializer(data=request.data)
              serializer.is_valid(raise_exception=True)
              kwargs["reason"] = serializer.validated_data["reason"]
          training = service(self.get_object(), by=request.user, **kwargs)
          return Response(self.get_serializer(self.get_queryset().get(pk=training.pk)).data)

      @action(detail=True, methods=["post"])
      def approve(self, request, pk=None):
          return self._review(request, services.approve, with_reason=False)

      @action(detail=True, methods=["post"], url_path="request-changes")
      def request_changes(self, request, pk=None):
          return self._review(request, services.request_changes, with_reason=True)

      @action(detail=True, methods=["post"])
      def reject(self, request, pk=None):
          return self._review(request, services.reject, with_reason=True)
  ```

  ```python
  # apps/training/api/v1/urls/admin.py
  from rest_framework import routers

  from apps.training.api.v1 import views

  app_name = "training_admin"
  router = routers.SimpleRouter()
  router.register("trainings", views.AdminTrainingViewSet, basename="admin-training")
  urlpatterns = router.urls
  ```

- [x] Imports the new view code needs: `MultiPartParser`, `FormParser` (`rest_framework.parsers`), `SearchFilter` (`rest_framework.filters`),
  `Response` and `action`, `CustomModelViewSet` (`apps.common.viewsets`), `InstituteScopedMixin` and `IsInstituteMember`
  (`apps.institutes.permissions`), `HasPlatformPermission` (`apps.users.permissions`), and `services` (`apps.training`).
- [x] Tests, `apps/training/tests/test_api_portal.py` and `test_api_admin.py`:
  - Portal permissions for every endpoint: anonymous 401, an admin 403, institute staff 200, staff of institute B gets a 404 on institute A's training.
  - Create with nested sessions (class days and times), modules and outcomes in one request; the response shows them in order; `status`, `slug` and `duration_weeks` in the payload are ignored; another institute's location, an inactive location, an inactive category and a pending institute are 400; a top-level category is accepted.
  - Edit: PATCH while `DRAFT` works; omitting `sessions` keeps them, `[]` empties them; PATCH on an `APPROVED` training moves it to `SUBMITTED` (and it disappears from the public list), and is a 400 with nothing saved when the result would be incomplete; PATCH on `SUBMITTED`, `CANCELLED` and `EXPIRED` is 400; PUT is 405.
  - Cover: multipart upload works while editable; a `.exe`, a file over 5 MB and a non-image give 400; it is refused once submitted or approved.
  - The whole lifecycle through the API: create, submit (a missing field gives a 400 listing every problem), an admin requests changes (reason shown to the institute), edit, resubmit, an admin approves, it is public, the institute edits it (hidden again), an admin approves again, the institute unpublishes (gone from the public list), republishes, cancels.
  - Delete: works for a draft, 400 otherwise.
  - Admin: anonymous 401, institute staff 403, an admin without `manage_trainings` 403, with it 200; the list filters on `status`; approve, request-changes and reject return the new status; request-changes and reject without a reason are 400; approving a `DRAFT` or an `UNPUBLISHED` training is 400.
  - Query counts stay constant for the portal list and the admin list.
- [x] **C5 done when:** the suite is green, and the lifecycle works by hand with Postman against `runserver`.

## C6 – Docs and wrap-up

- [x] `CLAUDE.md`: the `training` app in Layout (Training, TrainingSession as a weekly slot, modules, outcomes, `services.py`,
  `tasks.py`, `expire_trainings`); `catalog` now holds locations and categories; the new endpoints and prefixes; the
  `load_categories` and `expire_trainings` commands; the tests line; `django.contrib.postgres` is installed (ArrayField, search);
  and these landmines: trainings feed a search vector kept by services, so never write `Training` rows directly or use
  `QuerySet.update()` on content; content is editable only as described in decision 5 and an edit of an approved training
  hides it until re-approved; `expire_trainings` must be scheduled (Django Q schedule, daily) or the expiry never happens; the
  category tree is cached and `update()` skips the signals.
- [x] `docs/System Design.md`: Training and Category as built (the fields above), the decisions table rows (the sixteen), the final
  state machine and labels, the endpoint table (section 3.6), build step 4 progress, and the answered questions removed from
  section 8 (category depth, completion and cancellation, editing an approved training, duration, training levels, search scope).
  Change the "multiple sessions" wording to weekly slots, and add the UI findings to the PRD mapping if you keep one.
- [x] `README.md`: `load_categories` and the daily expiry in setup, and the new endpoint tables.
- [x] Notion review page: the diagram for trainings, and section 19.
- [x] Definition of done: `check` clean; `makemigrations --check --dry-run` clean; all tests pass; no hand-edited migrations; docs updated in the same change.

## Known limits and follow-ups (not in this list)

- The **availability filter** (seats minus converted enquiries above zero) and the "N seats left" figure need the `enquiries` app. The UI shows seats left on every card and defaults an empty `seats` to 20; here an empty value means unlimited, so the frontend must show "Open".
- **`featured` and `views`.** The UI's Relevance sort ranks title matches first, then featured trainings, then by views. A featured flag (admin) and a view counter (analytics) are not built; until then relevance is the search rank.
- **Institute registration fields** the UI asks for and `Institute` lacks: registration number (required), contact person, mobile. A separate change to `institutes`.
- **Instructor name** search: there is no such field and the UI has none either.
- No notification to enquirers on cancellation, no audit log and no notifications to the institute on a decision (`TODO(notify)`, `TODO(audit)` markers, as in `institutes`).
- Search uses the `simple` configuration: no stemming. It matches word prefixes, not text in the middle of a word (the UI's own search matched anywhere in a word).
- A bulk fix with `QuerySet.update()` does not refresh search vectors or clear the tree cache; use the services.
- Reviews and ratings, FAQs and SMS alerts shown in the UI are out of scope.

## Built differently from the snippets

- `TrainingStatus.LIVE` (`APPROVED`, `UNPUBLISHED`) is used by `cancel` and the expiry job; `WEEKS_PER_UNIT` lives on
  `DurationUnit` in `apps/training/constants.py`.
- `TrainingSession`, `TrainingModule` and `LearningOutcome` have a default `Meta.ordering` (start time, position), so a
  plain `prefetch_related("sessions", "modules", "outcomes")` and the create / update responses come back in order.
- An extra index `training_status_end_idx` (`status`, `end_date`) serves the daily expiry job. No separate index on
  `TrainingSession.training`: the foreign key already has one.
- Row locks use `select_for_update(of=("self",))`: Postgres refuses `FOR UPDATE` on the nullable side of the outer join
  that `select_related("institute_location")` creates. `create_training` also locks the institute row, so a suspension
  that runs at the same time is seen.
- `refresh_search_vector` re-reads the training with its related rows (one query) before the update, so callers can pass
  any instance; `refresh_search_vectors` walks primary keys.
- `institute/trainings/` is declared before `institute/` in `apps/api/v1/urls.py` instead of relying on fall-through.
- The admin detail serializer is its own class (`AdminTrainingSerializer`, read-only) rather than a subclass of the portal
  serializer; the admin list adds `institute_name`; the admin list also filters on `institute` (id).
- `CoverSerializer` and `TrainingReasonSerializer` extend `DynamicFieldsSerializer`, because `BaseViewSet.get_serializer`
  passes `fields=` / `exclude_fields=`, which a plain `Serializer` rejects (Swagger generation failed on it). The portal
  viewset returns `CoverSerializer` from `get_serializer_class` for the `cover` action.
- `map_url` is also accepted for locations given at registration.
- Postgres does not enforce an `ArrayField`'s `size`, so a bad `class_days` list is caught by the serializer (unknown day)
  and the service (empty or repeated day), not by the database.
- Tests are in `apps/training/tests/` as `test_models.py`, `test_services.py`, `test_api_public.py` and
  `test_api_portal_admin.py`; `apps/catalog/tests/test_categories.py` covers categories.
- Found while building: `apps/users/permissions.py` used `Role` without importing it (`IsInstituteStaff` would have raised
  `NameError`); fixed.
