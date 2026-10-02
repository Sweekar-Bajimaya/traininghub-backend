# Institutes App – Build Checklist

Todo list for the `institutes` app with code snippets. Section 1 (the `catalog` locations) is **built**; everything else is snippets still to apply.
They follow `docs/System Design.md` and the project skills (services for writes, DRF generics, locking, no N+1).
Items marked **BLOCKER** need a decision first. Tick items off as you go.
Updated 2026-10-02 with the findings from the other project's location catalog (section 1). Notion copy: "Institutes App – Build Checklist" under the System Design Review page.

## Status and next steps (2026-10-02)

**Built and tested** (43 tests pass): `users` (26 tests), `common`, and the `catalog` locations (17 tests). The locations are
loaded on the dev database (7 provinces, 77 districts, 752 municipalities) and served at `/api/v1/locations/`.
**Not committed yet:** the `catalog` app and the doc changes since the last commit.

**Next: the `institutes` app**, in four milestones. Each one is its own commit, with `check`,
`makemigrations --check` and the full test suite green.

| Milestone | Contents | Blocked by (section 0) |
|---|---|---|
| M1 Data layer | settings, `.gitignore`, `LOCAL_APPS`, constants, models (with profile columns and gallery), migration, read-only admin, constraint tests | unique name, profile columns, required documents |
| M2 Services | status workflow, registration, locations, invitations, staff removal, documents; service and concurrency tests | staff powers, suspended staff login, locations at registration, invitation expiry |
| M3 Public and admin API | registration, public list and detail, admin review actions, document review and download; permission and query-count tests | URL convention |
| M4 Portal API | profile, gallery, locations, documents, staff, invitations and accepting them | invitation email delivery |

Then update the docs listed in section 10.

## 0. Decisions and blockers (resolve first)

- [x] **Location level name:** decided, `MUNICIPALITY`, shown as "Municipality" in the UI.
- [x] **Province names:** decided, keep them exactly as in the data (no normalising). Assumption: this is how the answer "keep it in province while having in data" was read.
- [ ] **Nepali names.** `name_ne` and alternative spellings are empty in the source. Recommendation: leave them out until the content exists.
- [ ] **Who edits locations at runtime.** `users.manage_categories` covers "categories and locations". Admin API CRUD, or only the loader?
- [x] **Location data files:** copied into `apps/catalog/data/` and checked (7 / 77 / 752, no orphan parents, no duplicate
  `(district, name)`, 22 municipality names repeat across districts). The file names stay as they are (`provinces.json`,
  `districts.json`, `cities.json`, which holds the municipalities); no rename. The team documents the source. Remaining task:
  delete the unused `local_government.py` from that folder.
- [x] **Institute `type` values:** decided, seven fixed types (snippet in section 3). Assumption: `type` is required at registration.
- [x] **Profile fields:** decided, option A (plain columns on `Institute`, section 7). Still to confirm: the exact column list.
- [x] **Rejected institute:** decided, it can re-apply (`REJECTED` → `PENDING`). Assumption: it re-applies on the same institute record and account, after updating its details and documents. Only `APPROVED` institutes are publicly visible.
- [ ] **Suspended institute staff** (Q12): snippets let them log in but not publish. Confirm.
- [ ] **Staff powers** (Q4): invited staff can do everything except remove the owner or invite staff; only the owner invites. Confirm or give limits.
- [ ] **Locations at registration**: must an institute give at least one location when registering (diagram says 1..*)?
  The checklist enforces at least one active location before **approval**, not at registration. Confirm.
- [ ] **Required documents**, file types and size limit. `ATTACHMENT_MAX_UPLOAD_SIZE` is still undefined (deliberate),
  so document upload needs a size rule of its own.
- [ ] **Invitation expiry**: snippets assume 7 days. Confirm.
- [ ] **Invitation email delivery:** there is no `notifications` app yet, so nothing can send the invite token.
  Recommendation: send it now with Django's `send_mail`, queued with django-q2 after the transaction commits; build the
  full `notifications` app (in-app + templates) later. Alternative: build `notifications` first.
- [ ] **Unique institute name?** Not stated, so not enforced. Slug is unique.
- [ ] **URL convention** (`institutes/`, `institute/`, `admin/` by audience): proposed, not yet adopted.

## 1. Prerequisite: the `catalog` app with `Location`

`InstituteLocation` points at the managed location list, which the design places in `catalog`. Build a minimal `catalog`
(locations only) first, otherwise `institutes` cannot migrate.

### What we take from the other project's catalog

- Same idea: Province, then District, then local government (municipality or rural municipality). 7 provinces, 77 districts,
  752 local governments; 22 municipality names repeat across districts, so the district must be shown next to the name.
- **Avoid its problems:** denormalised ancestor columns that nothing keeps consistent; fixed primary keys copied from the JSON
  with no sequence reset; the rural / urban category thrown away; no active flag; a loader doing one query per row with no
  tests; a separate marketing `City` table and a free-text `Location` that overlap the real hierarchy.
- **Our choices:** one `Location` table; a `code` column holds the source id (unique per level) and the database assigns
  primary keys; `type` kept for municipalities; `is_active`; ancestors derived in exactly one place; check constraints on the
  shape; a bulk, idempotent loader with a test.

### Tasks

- [x] **Built (2026-10-02):** `apps/catalog/` with `constants.py`, the `Location` model, `load_locations`, signals that clear
  the tree cache, a read-only admin, the public API under `/api/v1/locations/` and 17 tests (all passing, 43 in the whole
  suite). The snippets below are what was applied, with these fixes: `MunicipalityType.CHOICES` is a tuple (a set gave an
  unstable order), the constraint names are spelled `catalog_` (migration `0002`), the list filters `is_active=True`,
  foreign-key filters are `NumberFilter`s on `*_id` (no extra query), and the URLs are a package mounted at `locations/`
  with a `SimpleRouter`.
- [x] Run on the dev database: `migrate catalog` (`0002` applied) and `load_locations` (7 / 77 / 752 rows).
- [x] Constants and model:

  ```python
  # apps/catalog/constants.py
  class LocationLevel:
      PROVINCE, DISTRICT, MUNICIPALITY = "PROVINCE", "DISTRICT", "MUNICIPALITY"
      CHOICES = ((PROVINCE, "Province"), (DISTRICT, "District"), (MUNICIPALITY, "Municipality"))


  class MunicipalityType:
      METROPOLITAN, SUB_METROPOLITAN = "METROPOLITAN", "SUB_METROPOLITAN"
      MUNICIPALITY, RURAL_MUNICIPALITY = "MUNICIPALITY", "RURAL_MUNICIPALITY"
      CHOICES = (
          (METROPOLITAN, "Metropolitan city"), (SUB_METROPOLITAN, "Sub-metropolitan city"),
          (MUNICIPALITY, "Municipality"), (RURAL_MUNICIPALITY, "Rural municipality"),
      )


  # apps/catalog/models.py
  class Location(BaseModel):
      code = models.PositiveIntegerField()              # id from the source file, NOT the primary key
      name = models.CharField(max_length=255)
      level = models.CharField(max_length=12, choices=LocationLevel.CHOICES)
      type = models.CharField(max_length=20, choices=MunicipalityType.CHOICES, blank=True)
      parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.PROTECT, related_name="children")
      # denormalised ancestors: a province or district filter is one indexed equality
      province = models.ForeignKey("self", null=True, blank=True, on_delete=models.PROTECT, related_name="+")
      district = models.ForeignKey("self", null=True, blank=True, on_delete=models.PROTECT, related_name="+")
      is_active = models.BooleanField(default=True)

      class Meta:
          constraints = [
              models.UniqueConstraint(fields=["level", "code"], name="catalog_location_level_code_uniq"),
              models.UniqueConstraint(fields=["parent", "name"], name="catalog_location_parent_name_uniq"),
              models.CheckConstraint(name="catalog_location_level_shape", condition=(
                  models.Q(level="PROVINCE", parent__isnull=True, province__isnull=True, district__isnull=True)
                  | models.Q(level="DISTRICT", parent__isnull=False, province__isnull=False, district__isnull=True)
                  | models.Q(level="MUNICIPALITY", parent__isnull=False, province__isnull=False, district__isnull=False)
              )),
          ]
          indexes = [
              models.Index(fields=["level", "parent"], name="catalog_location_level_idx"),
              models.Index(fields=["province"], name="catalog_location_province_idx"),
              models.Index(fields=["district"], name="catalog_location_district_idx"),
          ]

      def __str__(self):
          return self.name

      def save(self, *args, **kwargs):
          # The single place that derives the ancestor columns; the loader sets the same values in bulk.
          if self.level == LocationLevel.DISTRICT:
              self.province_id = self.parent_id
          elif self.level == LocationLevel.MUNICIPALITY:
              self.district_id = self.parent_id
              self.province_id = self.parent.province_id
          super().save(*args, **kwargs)
  ```

- [x] Loader `python manage.py load_locations`: three bulk upserts, parents resolved from dictionaries built once, each JSON
  file read once, idempotent:

  ```python
  # apps/catalog/management/commands/load_locations.py (core part)
  TYPE_MAP = {
      "Metropolitan City": "METROPOLITAN", "Sub-Metropolitan City": "SUB_METROPOLITAN",
      "Municipality": "MUNICIPALITY", "Rural Municipality": "RURAL_MUNICIPALITY",
      "Gaunpalika": "RURAL_MUNICIPALITY",       # 2 rows; Gaunpalika = rural municipality
  }

  @transaction.atomic
  def handle(self, *args, **options):
      read = lambda name: json.loads((DATA_DIR / name).read_text(encoding="utf-8"))

      self._upsert([dict(code=p["id"], name=p["name"].strip(), level="PROVINCE")
                    for p in read("provinces.json")])
      province = dict(Location.objects.filter(level="PROVINCE").values_list("code", "pk"))

      self._upsert([dict(code=d["id"], name=d["name"].strip(), level="DISTRICT",
                         parent_id=province[d["province"]], province_id=province[d["province"]])
                    for d in read("districts.json")])
      district = {c: (pk, prov) for c, pk, prov in
                  Location.objects.filter(level="DISTRICT").values_list("code", "pk", "province_id")}

      self._upsert([dict(code=m["id"], name=m["name"].strip(), level="MUNICIPALITY",
                         type=TYPE_MAP[m["category"]],
                         parent_id=district[m["district"]][0], district_id=district[m["district"]][0],
                         province_id=district[m["district"]][1])
                    for m in read("cities.json")])

  def _upsert(self, rows):
      Location.objects.bulk_create(
          [Location(**r) for r in rows], update_conflicts=True,
          unique_fields=["level", "code"],
          update_fields=["name", "type", "parent", "province", "district"],
      )
  ```

- [x] Loader test: run the command twice and assert 7 provinces, 77 districts and 752 municipalities; assert every
  municipality's `province_id` equals its district's `province_id`; assert the second run changes nothing.
- [x] Location API (read-only, public): `parent_id` filter and a name search for the dependent selects, plus **one cached
  tree endpoint** (about 850 small rows) invalidated on admin write. Use `select_related("parent")` on lists so showing the
  district next to a repeated municipality name costs no extra queries.
- [x] Read-only admin for `Location` (same pattern as `users`).
- [x] Migrations generated: `0001_initial` (applied) and `0002_fix_choices_and_constraint_names`.

## 2. Settings and scaffold for `institutes`

- [ ] Settings (new, so document them):

  ```python
  # config/settings/base.py
  PRIVATE_MEDIA_ROOT = BASE_DIR / "private_media"       # gitignored; swap for a private S3 bucket later
  INSTITUTE_INVITATION_TTL_DAYS = 7                     # assumption, see section 0

  REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"].update({
      "institute_register": "5/hour",
      "invitation_accept": "10/hour",
  })
  ```

- [ ] Add `"apps.institutes"` to `LOCAL_APPS` and `private_media/` to `.gitignore`.
- [ ] Create `apps/institutes/` with `__init__.py`, `apps.py`, `models.py`, `constants.py`, `services.py`, `storage.py`,
  `permissions.py`, `admin.py`, `tests/__init__.py`, `api/v1/{__init__,serializers,views}.py` and
  `api/v1/urls/{__init__,public,portal,admin}.py`. Every package needs an `__init__.py` or tests are silently skipped.
- [ ] Mount the URLs. Prefixes live only in `apps/api/v1/urls.py` (decided, as for `locations/`); the audience split itself is still a proposal
  (public / `institute/` portal / `admin/`):

  ```python
  # apps/api/v1/urls.py
  urlpatterns = [
      path("user/", include("apps.users.api.v1.urls.users")),
      path("institutes/", include("apps.institutes.api.v1.urls.public")),
      path("institute/", include("apps.institutes.api.v1.urls.portal")),
      path("admin/", include("apps.institutes.api.v1.urls.admin")),
  ]
  ```

## 3. Constants and state machine

- [ ] `apps/institutes/constants.py`, in the style of `users/constants.py`:

  ```python
  class InstituteStatus:
      PENDING = "PENDING"
      APPROVED = "APPROVED"
      REJECTED = "REJECTED"
      INFO_REQUESTED = "INFO_REQUESTED"
      SUSPENDED = "SUSPENDED"

      CHOICES = (
          (PENDING, "Pending"), (APPROVED, "Approved"), (REJECTED, "Rejected"),
          (INFO_REQUESTED, "Info requested"), (SUSPENDED, "Suspended"),
      )
      # Allowed moves. A rejected institute can re-apply (REJECTED -> PENDING).
      TRANSITIONS = {
          PENDING: {APPROVED, REJECTED, INFO_REQUESTED},
          INFO_REQUESTED: {PENDING},
          APPROVED: {SUSPENDED},
          SUSPENDED: {APPROVED},
          REJECTED: {PENDING},
      }
      REASON_REQUIRED = {REJECTED, INFO_REQUESTED, SUSPENDED}


  class MemberRole:
      OWNER = "OWNER"
      STAFF = "STAFF"
      CHOICES = ((OWNER, "Owner"), (STAFF, "Staff"))


  class DocumentStatus:
      PENDING, VERIFIED, REJECTED = "PENDING", "VERIFIED", "REJECTED"
      CHOICES = ((PENDING, "Pending"), (VERIFIED, "Verified"), (REJECTED, "Rejected"))


  class InvitationStatus:
      PENDING, ACCEPTED, REVOKED = "PENDING", "ACCEPTED", "REVOKED"
      CHOICES = ((PENDING, "Pending"), (ACCEPTED, "Accepted"), (REVOKED, "Revoked"))


  class InstituteType:
      PRIVATE_TRAINING_AFFILIATED = "PRIVATE_TRAINING_AFFILIATED"
      CTEVT_AFFILIATED = "CTEVT_AFFILIATED"
      VOCATIONAL_TRAINING = "VOCATIONAL_TRAINING"
      LANGUAGE_SCHOOL = "LANGUAGE_SCHOOL"
      COMPANY = "COMPANY"
      NGO_INGO = "NGO_INGO"
      GOVERNMENT = "GOVERNMENT"

      CHOICES = (
          (PRIVATE_TRAINING_AFFILIATED, "Private Training Affiliated"),
          (CTEVT_AFFILIATED, "CTEVT Affiliated"),
          (VOCATIONAL_TRAINING, "Vocational Training"),
          (LANGUAGE_SCHOOL, "Language School"),
          (COMPANY, "Company"),
          (NGO_INGO, "NGO/INGO"),
          (GOVERNMENT, "Government"),
      )
  ```

## 4. Models and migration

- [ ] Private storage for documents (never under public `media/`):

  ```python
  # apps/institutes/storage.py
  from django.conf import settings
  from django.core.files.storage import FileSystemStorage


  def private_storage():
      return FileSystemStorage(location=settings.PRIVATE_MEDIA_ROOT)
  ```

- [ ] Models. `registered_at` from the design is covered by `BaseModel.created_at`, so it is not added.

  ```python
  # apps/institutes/models.py
  from django.conf import settings
  from django.db import models
  from django.db.models.functions import Lower

  from apps.common.models import BaseModel, SlugModel
  from apps.common.utils.helpers import get_upload_path
  from apps.common.validators import validate_phone_number
  from apps.institutes.constants import (
      DocumentStatus, InstituteStatus, InstituteType, InvitationStatus, MemberRole,
  )
  from apps.institutes.storage import private_storage


  class Institute(BaseModel, SlugModel):
      name = models.CharField(max_length=255)
      type = models.CharField(max_length=30, choices=InstituteType.CHOICES)   # fixed list, required
      established_year = models.PositiveSmallIntegerField(null=True, blank=True)
      description = models.TextField(blank=True)
      logo = models.ImageField(upload_to=get_upload_path, blank=True)
      status = models.CharField(max_length=20, choices=InstituteStatus.CHOICES,
                                default=InstituteStatus.PENDING)
      status_reason = models.TextField(blank=True)

      class Meta:
          indexes = [models.Index(fields=["status"], name="institutes_status_idx")]

      def __str__(self):
          return self.name


  class InstituteMember(BaseModel):
      # OneToOne = a staff user belongs to ONE institute only (Q6), unique at the DB level.
      user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                  related_name="membership")
      institute = models.ForeignKey(Institute, on_delete=models.CASCADE, related_name="members")
      role = models.CharField(max_length=10, choices=MemberRole.CHOICES)

      class Meta:
          constraints = [
              models.UniqueConstraint(
                  fields=["institute"], condition=models.Q(role=MemberRole.OWNER),
                  name="institutes_one_owner_per_institute",
              ),
          ]


  class InstituteInvitation(BaseModel):
      institute = models.ForeignKey(Institute, on_delete=models.CASCADE, related_name="invitations")
      email = models.EmailField()
      role = models.CharField(max_length=10, choices=MemberRole.CHOICES, default=MemberRole.STAFF)
      token_hash = models.CharField(max_length=64, unique=True)   # sha256 of the emailed token
      status = models.CharField(max_length=10, choices=InvitationStatus.CHOICES,
                                default=InvitationStatus.PENDING)
      expires_at = models.DateTimeField()
      invited_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL,
                                     related_name="+")

      class Meta:
          constraints = [
              # one pending invitation per (institute, email), case-insensitive
              models.UniqueConstraint(
                  Lower("email"), "institute", condition=models.Q(status=InvitationStatus.PENDING),
                  name="institutes_one_pending_invite",
              ),
          ]
          indexes = [models.Index(fields=["expires_at"], name="institutes_invite_expiry_idx")]


  class InstituteDocument(BaseModel):
      institute = models.ForeignKey(Institute, on_delete=models.CASCADE, related_name="documents")
      name = models.CharField(max_length=150)
      file = models.FileField(upload_to=get_upload_path, storage=private_storage)
      status = models.CharField(max_length=10, choices=DocumentStatus.CHOICES,
                                default=DocumentStatus.PENDING)

      class Meta:
          indexes = [models.Index(fields=["institute", "status"], name="institutes_doc_status_idx")]


  class InstituteLocation(BaseModel):
      institute = models.ForeignKey(Institute, on_delete=models.CASCADE, related_name="locations")
      # must be a MUNICIPALITY-level, active Location; checked in the service (see below)
      location = models.ForeignKey("catalog.Location", on_delete=models.PROTECT, related_name="+")
      address = models.CharField(max_length=255)
      contact_phone = models.CharField(max_length=25, blank=True, validators=[validate_phone_number])
      is_main = models.BooleanField(default=False)
      is_active = models.BooleanField(default=True)

      class Meta:
          constraints = [
              models.UniqueConstraint(
                  fields=["institute"], condition=models.Q(is_main=True, is_active=True),
                  name="institutes_one_main_location",
              ),
              models.CheckConstraint(
                  condition=~models.Q(is_main=True, is_active=False),
                  name="institutes_main_location_is_active",
              ),
          ]
          indexes = [models.Index(fields=["institute", "is_active"], name="institutes_loc_active_idx")]
  ```

- [ ] A validator used by the serializer and the service, because a foreign key alone would also accept a province or a retired municipality:

  ```python
  def validate_institute_location(location):
      if location.level != LocationLevel.MUNICIPALITY or not location.is_active:
          raise ValidationError({"location": "Choose an active city / municipality."})
  ```

- [ ] `python manage.py makemigrations institutes`, then `migrate`. Do not hand-edit migrations.
- [ ] Read-only admin, same pattern as `users` (no add / change / delete). Documents are private, so the admin must not link to the files.

> **Correction to the Notion review page (section 6):** it proposes a composite foreign key
> `(institute_id, institute_location_id)` on `Training`. Django 5.2 has no composite foreign keys. The rule
> "a training's location belongs to the same institute" must be enforced in `TrainingService` plus a test, not by the database.

## 5. Permissions and scoping

- [ ] `apps/institutes/permissions.py` (the existing `IsInstituteStaff` checks only the role; these also check membership):

  ```python
  from rest_framework.permissions import BasePermission

  from apps.institutes.constants import MemberRole


  class IsInstituteMember(BasePermission):
      def has_permission(self, request, view):
          u = request.user
          return bool(u and u.is_authenticated and hasattr(u, "membership"))


  class IsInstituteOwner(IsInstituteMember):
      def has_permission(self, request, view):
          return super().has_permission(request, view) and request.user.membership.role == MemberRole.OWNER
  ```

- [ ] A mixin so other institutes' rows are never reachable (they return 404, not 403):

  ```python
  class InstituteScopedMixin:
      """Limit the queryset to the caller's institute."""
      def get_queryset(self):
          return super().get_queryset().filter(institute_id=self.request.user.membership.institute_id)
  ```

- [ ] Query cost: `request.user.membership` is one query per request. If it matters, `select_related("membership")`
  where `ActiveAccountJWTAuthentication` loads the user.

## 6. Services (`apps/institutes/services.py`)

All writes live here, inside `transaction.atomic()`, locking before check-then-write. There is no `AuditLog` or notification
service yet, so leave TODO markers like `users/services.py` does.

- [ ] Institute workflow:

  ```python
  import hashlib
  import secrets
  from datetime import timedelta

  from django.conf import settings
  from django.contrib.auth import get_user_model
  from django.core.exceptions import ValidationError
  from django.db import transaction
  from django.utils import timezone

  from apps.institutes.constants import InstituteStatus, InvitationStatus, MemberRole
  from apps.institutes.models import (
      Institute, InstituteDocument, InstituteInvitation, InstituteLocation, InstituteMember,
  )
  from apps.users.constants import Role

  User = get_user_model()


  def _transition(institute, to, *, reason=""):
      """Caller must be inside transaction.atomic()."""
      institute = Institute.objects.select_for_update().get(pk=institute.pk)
      if to not in InstituteStatus.TRANSITIONS[institute.status]:
          raise ValidationError(f"Cannot move from {institute.status} to {to}.")
      if to in InstituteStatus.REASON_REQUIRED and not reason.strip():
          raise ValidationError({"reason": "A reason is required."})
      institute.status = to
      institute.status_reason = reason
      institute.save(update_fields=["status", "status_reason", "modified_at"])
      return institute


  @transaction.atomic
  def approve(institute, *, by):
      institute = Institute.objects.select_for_update().get(pk=institute.pk)
      if not institute.locations.filter(is_active=True).exists():   # proposal, see section 0
          raise ValidationError("Add at least one active location before approval.")
      # TODO(audit) + TODO(notify): institute owner
      return _transition(institute, InstituteStatus.APPROVED)


  @transaction.atomic
  def reject(institute, *, by, reason):
      return _transition(institute, InstituteStatus.REJECTED, reason=reason)


  @transaction.atomic
  def request_info(institute, *, by, reason):
      return _transition(institute, InstituteStatus.INFO_REQUESTED, reason=reason)


  @transaction.atomic
  def suspend(institute, *, by, reason):
      # Staff keep their accounts (they can still log in, Q12); public queries hide the institute.
      return _transition(institute, InstituteStatus.SUSPENDED, reason=reason)


  @transaction.atomic
  def reinstate(institute, *, by):
      return _transition(institute, InstituteStatus.APPROVED)


  @transaction.atomic
  def resubmit(institute):
      """Owner answers an info request, or re-applies after a rejection."""
      return _transition(institute, InstituteStatus.PENDING)
  ```

- [ ] Registration (public): institute, owner, locations and documents in **one** transaction, with bulk inserts:

  ```python
  @transaction.atomic
  def register(*, institute_data, owner, locations=(), documents=()):
      """owner = {"email", "password", "full_name", ...}. The owner is always INSTITUTE_STAFF."""
      for loc in locations:
          validate_institute_location(loc["location"])   # bulk_create skips model validation
      institute = Institute.objects.create(**institute_data)
      owner_user = User.objects.create_user(role=Role.INSTITUTE_STAFF, **owner)
      InstituteMember.objects.create(user=owner_user, institute=institute, role=MemberRole.OWNER)

      InstituteLocation.objects.bulk_create([
          InstituteLocation(institute=institute, is_main=(i == 0), **loc)   # first = main office
          for i, loc in enumerate(locations)
      ])
      InstituteDocument.objects.bulk_create(
          [InstituteDocument(institute=institute, **doc) for doc in documents]
      )
      # TODO(notify): admins with manage_institutes
      return institute
  ```

  A duplicate owner email raises `IntegrityError`, which the exception handler turns into 409. Prefer a serializer
  `UniqueValidator(lookup="iexact")` so the user gets a 400 first.

- [ ] Locations (also validate the municipality on add and update):

  ```python
  @transaction.atomic
  def set_main_location(location):
      Institute.objects.select_for_update().get(pk=location.institute_id)   # serialise per institute
      location = InstituteLocation.objects.get(pk=location.pk)
      if not location.is_active:
          raise ValidationError("An inactive location cannot be the main office.")
      InstituteLocation.objects.filter(
          institute_id=location.institute_id, is_main=True
      ).exclude(pk=location.pk).update(is_main=False)     # clear first, then set (partial unique index)
      location.is_main = True
      location.save(update_fields=["is_main", "modified_at"])
      return location


  @transaction.atomic
  def deactivate_location(location):
      Institute.objects.select_for_update().get(pk=location.institute_id)
      location = InstituteLocation.objects.get(pk=location.pk)
      if location.is_main:
          raise ValidationError("Choose another main office first.")
      # TODO(catalog): refuse while non-terminal trainings use it (409)
      location.is_active = False
      location.save(update_fields=["is_active", "modified_at"])
      return location
  ```

- [ ] Staff invitations (token stored hashed, single use, role always STAFF because there is one owner):

  ```python
  def _hash(token):
      return hashlib.sha256(token.encode()).hexdigest()


  @transaction.atomic
  def invite(*, institute, email, by):
      if User.objects.filter(email__iexact=email).exists():
          raise ValidationError({"email": "This email already has an account."})   # one institute per user
      token = secrets.token_urlsafe(32)
      invitation = InstituteInvitation.objects.create(
          institute=institute, email=email, role=MemberRole.STAFF, invited_by=by,
          token_hash=_hash(token),
          expires_at=timezone.now() + timedelta(days=settings.INSTITUTE_INVITATION_TTL_DAYS),
      )
      # TODO(notify): transaction.on_commit(lambda: send invite email containing `token`)
      return invitation


  @transaction.atomic
  def accept_invitation(*, token, full_name, password):
      invitation = (
          InstituteInvitation.objects.select_for_update(of=("self",))
          .select_related("institute")
          .filter(token_hash=_hash(token), status=InvitationStatus.PENDING)
          .first()
      )
      if invitation is None or invitation.expires_at < timezone.now():
          raise ValidationError("This invitation is invalid or has expired.")
      user = User.objects.create_user(
          email=invitation.email, password=password, full_name=full_name, role=Role.INSTITUTE_STAFF,
      )
      InstituteMember.objects.create(user=user, institute=invitation.institute, role=invitation.role)
      invitation.status = InvitationStatus.ACCEPTED
      invitation.save(update_fields=["status", "modified_at"])
      return user
  ```

- [ ] Also needed: `revoke_invitation`, `remove_staff` (owner only; never the owner; deactivate the user and revoke their
  tokens like `users.services.set_status`), `upload_document`, `review_document` (admin: verified / rejected).

## 7. Profile fields (decided: option A, plain columns)

The institute profile uses plain columns on `Institute` (easy to validate and filter), plus a small gallery table.
"About" is the existing `description` column. The exact column list below is a proposal to confirm.

- [ ] Add the columns to `Institute` (all optional, so registration needs none of them):

  ```python
  # apps/institutes/models.py, inside Institute
  ceo_name = models.CharField(max_length=150, blank=True)
  ceo_message = models.TextField(blank=True)
  website = models.URLField(blank=True)
  contact_email = models.EmailField(blank=True)
  contact_phone = models.CharField(max_length=25, blank=True, validators=[validate_phone_number])
  facebook_url = models.URLField(blank=True)
  linkedin_url = models.URLField(blank=True)
  ```

- [ ] Gallery table. No unique constraint on `position`, so a reorder can run as one `bulk_update` (a swap would break a unique constraint halfway):

  ```python
  class InstituteGalleryImage(BaseModel):
      institute = models.ForeignKey(Institute, on_delete=models.CASCADE, related_name="gallery")
      image = models.ImageField(upload_to=get_upload_path)
      caption = models.CharField(max_length=200, blank=True)
      position = models.PositiveSmallIntegerField(default=0)

      class Meta:
          indexes = [models.Index(fields=["institute", "position"], name="institutes_gallery_pos_idx")]
  ```

- [ ] Gallery images are public (shown on the institute page), so they use the normal `media/` storage, unlike verification documents. Image upload still needs `ATTACHMENT_MAX_UPLOAD_SIZE` or a size rule of its own.
- [ ] Public institute page: `prefetch_related("gallery")`; the owner edits the profile through `institute/profile/` and the gallery through `institute/gallery/`.

## 8. API layer (generic views, logic in serializers and services)

| Audience | Endpoint | View | Permission |
|---|---|---|---|
| Public | `POST institute/register/` | `CreateAPIView` | public, `institute_register` throttle, captcha later |
| Public | `POST institute/invitations/accept/` | `CreateAPIView` | public, `invitation_accept` throttle |
| Public | `GET institutes/`, `institutes/{slug}/` | `ReadOnlyViewSet` | public, only `APPROVED` |
| Portal | `GET, PATCH institute/profile/` | `RetrieveUpdateAPIView` | member (PATCH: owner) |
| Portal | `institute/gallery/` (list, create, update, delete, reorder) | `CreateListRetrieveUpdateViewSet` + delete | owner |
| Portal | `institute/locations/` (list, create, update) + `.../{id}/set-main` | `CreateListRetrieveUpdateViewSet` | member (write: owner) |
| Portal | `institute/documents/` | `CreateListRetrieveUpdateViewSet` (create, list) | owner |
| Portal | `institute/staff/`, `institute/invitations/` | list / create / delete | owner |
| Admin | `admin/institutes/`, `.../{id}/{approve,reject,request-info,suspend,reinstate}` | `ReadOnlyViewSet` + actions | `users.manage_institutes` |
| Admin | `admin/institutes/{id}/documents/{doc}/` | download + review | `users.manage_institutes` |

- [ ] Public registration serializer: calls the service, never trusts `status` or `role`:

  ```python
  class RegisterSerializer(serializers.Serializer):
      name = serializers.CharField(max_length=255)
      # ... type, established_year, description, logo
      owner = OwnerSerializer()                         # email (iexact unique), full_name, password
      locations = LocationInputSerializer(many=True, required=False)
      documents = DocumentInputSerializer(many=True, required=False)

      def create(self, validated):
          owner = validated.pop("owner")
          locations = validated.pop("locations", [])
          documents = validated.pop("documents", [])
          return services.register(
              institute_data=validated, owner=owner, locations=locations, documents=documents,
          )


  class RegisterView(CreateAPIView):
      serializer_class = RegisterSerializer
      permission_classes = [AllowAny]
      authentication_classes = []
      throttle_scope = "institute_register"
  ```

- [ ] Public list: no N+1, only approved, stable order, locations prefetched with their municipality, district and province
  (the ancestors are on the row, so only `select_related("location__district", "location__province")` is needed):

  ```python
  class PublicInstituteViewSet(ReadOnlyViewSet):
      serializer_class = PublicInstituteSerializer
      permission_classes = []                    # public
      lookup_field = "slug"
      queryset = (
          Institute.objects.filter(status=InstituteStatus.APPROVED)
          .prefetch_related(Prefetch(
              "locations",
              queryset=InstituteLocation.objects.filter(is_active=True)
                       .select_related("location", "location__district", "location__province"),
          ))
          .order_by("name", "pk")
      )
  ```

  The card's city, district and province come from the main location inside the serializer
  (`next(l for l in prefetched if l.is_main)`), not from a new query.

- [ ] Admin review actions without four copies of the same code:

  ```python
  class AdminInstituteViewSet(ReadOnlyViewSet):
      queryset = Institute.objects.prefetch_related("documents").order_by("-created_at", "-pk")
      serializer_class = AdminInstituteSerializer
      permission_classes = [HasPlatformPermission]
      required_permission = "users.manage_institutes"
      filterset_fields = ["status"]

      def _review(self, request, service, *, reason_required=False):
          serializer = ReviewSerializer(data=request.data, context={"reason_required": reason_required})
          serializer.is_valid(raise_exception=True)
          institute = service(self.get_object(), by=request.user, **serializer.validated_data)
          return Response(self.get_serializer(institute).data)

      @action(detail=True, methods=["post"])
      def approve(self, request, pk=None):
          return self._review(request, services.approve)

      @action(detail=True, methods=["post"], url_path="request-info")
      def request_info(self, request, pk=None):
          return self._review(request, services.request_info, reason_required=True)

      # reject, suspend, reinstate in the same way
  ```

- [ ] Documents are private: never return `file.url`. Serve through an authorized view that checks admin permission or the
  owner's membership and streams with `FileResponse` (switch to a signed URL when S3 arrives).
- [ ] Error handling relies on the existing handler: Django `ValidationError` -> 400, `IntegrityError` -> 409.

## 9. Tests

### `apps/catalog/tests/`

- [x] Loader: run twice, 7 / 77 / 752 rows, no change on the second run; every municipality's `province_id` matches its district's.
- [x] Constraints: a province with a parent is rejected, a municipality without a district is rejected, duplicate `(parent, name)` is rejected, duplicate `(level, code)` is rejected.
- [x] `save()` derives `province` and `district` correctly.
- [x] Location list has a constant query count (`assertNumQueries`) with the district shown.

### `apps/institutes/tests/`

- [ ] Constraints: second owner rejected, two active main locations rejected, an inactive main rejected, duplicate pending invite (case-insensitive) rejected, one membership per user.
- [ ] A province or district (or an inactive municipality) is rejected as an institute location.
- [ ] A rejected institute can re-apply (`REJECTED` to `PENDING`); a rejected or pending institute is never in the public list.
- [ ] Workflow: every allowed transition works, every other one raises; reason required for reject / request-info / suspend; approve fails with no active location.
- [ ] Registration: creates institute + owner + locations + documents atomically; a failing step leaves nothing behind; `role` / `status` in the payload are ignored; duplicate email (any case) -> 400.
- [ ] Invitation: accept works once; expired or unknown token -> 400; invited email that already has an account -> 400; token not stored in plaintext.
- [ ] Permissions matrix: public / staff of institute A / staff of institute B (gets 404 on A's rows) / admin without `manage_institutes` (403) / admin with it.
- [ ] Public list shows only `APPROVED`, hides `SUSPENDED`, and has a constant query count (`assertNumQueries`) with 1 and with 20 institutes.
- [ ] Concurrency: two simultaneous approvals -> one succeeds, the other gets a clean 400 (`TransactionTestCase`).
- [ ] Throttle: the 6th registration in an hour gets 429 (clear the cache in `setUp`, as the `users` tests do).

## 10. Docs to update in the same change

- [ ] `CLAUDE.md`: move `institutes` and `catalog` out of "Planned apps" into Layout; add the endpoints, the two new throttle scopes, `PRIVATE_MEDIA_ROOT`, `INSTITUTE_INVITATION_TTL_DAYS`, the `load_locations` command and the `apps/catalog/data/` files; add the "documents are private" landmine; update the tests line; remove the answered location line from Open decisions.
- [ ] `docs/System Design.md`: mark build step 3 done; fix `registered_at` (covered by `created_at`); record the answers to Q4, Q12, Q13, the profile fields, the location level name and the "at least one location before approval" rule; update the `Location` description (`code`, `type`, `is_active`, level `MUNICIPALITY`); correct the "composite FK" wording (Django 5.2 cannot); record the URL convention once confirmed; answer Q5.
- [ ] `README.md`: layout, the `load_locations` step in setup, and the endpoint table.
- [ ] Notion review page: update diagrams 4b.2 and 4b.3 (no `registered_at`, `InstituteMember.user` is one-to-one, documents are private, `Location` with `code`, `type`, `is_active`) and section 6.

## 11. Definition of done

- [ ] `python manage.py check` and `makemigrations --check --dry-run` clean
- [ ] All tests pass (`python manage.py test`)
- [ ] `load_locations` run twice leaves 7 / 77 / 752 rows
- [ ] No hand-edited migrations
- [ ] Docs above updated in the same change
- [ ] Open questions this work answered are removed from System Design.md section 8
