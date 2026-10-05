# Institutes App – Todo List

Ordered work list for the `institutes` app, with code snippets. Follow it top to bottom: each milestone is its own commit,
with `python manage.py check`, `makemigrations --check --dry-run` and the full test suite green before you move on.
Notion copy: "Institutes App – Todo List (M0–M5)" under the System Design Review page.

The snippets follow `docs/System Design.md` and the project skills (services for writes, DRF generics, locking, no N+1).
They were checked against the repo as of 2026-10-02 (43 tests passing, `catalog` locations loaded).

## Status (2026-10-02)

**M0 to M5 are built and tested** (the whole suite is 174 tests, 131 of them in `institutes`; `check` and
`makemigrations --check` are clean). Still open:
- a manual run of the full journey with `runserver` and `qcluster` (the `EndToEndTests` test covers it through the API);

What differs from the snippets below, because the code was checked against the repo:
- `validators.py` and `models.py` use `from django.conf import settings` (the raw `config.settings` module ignores `override_settings`).
- `OwnerSerializer.phone_number` also has a uniqueness check, so a duplicate phone is a 400 instead of a 409.
- The public queryset orders locations `-is_main, pk`; the admin review actions re-read the institute through the viewset queryset so the response keeps the owner and documents.
- `AdminDocumentView` has an empty `queryset` only so the Swagger schema generator is happy.
- The tests clear throttles with `cache.delete_pattern("throttle_*")`; `cache.clear()` would also flush the django-q broker (same Redis database). `apps/users/tests.py` was changed the same way.
- Query-count tests warm up first (permissions and membership are loaded once per user), and start from one row (an empty page skips the data query).

## Decisions this list assumes

The nine decisions below were open when this list was written. Each row shows the default the code was built on. They were
confirmed on 2026-10-02 (ticked in the Notion work list). To change one later, edit the place named in the last column.

| # | Decision | Default used | Milestone |
|---|---|---|---|
| 1 | Can a suspended institute's staff log in? | Yes. They cannot publish, and the institute is hidden from the public site | M2 |
| 2 | Staff powers | Staff can do everything except manage staff and invitations (owner only). No ownership transfer | M2, M4 |
| 3 | Locations at registration | Optional at registration; at least one active location before approval | M2 |
| 4 | Documents | pdf / jpg / png, max 5 MB. Uploaded **after** registration, by the owner, in the portal; at least one before approval | M1, M2 |
| 5 | Invitation expiry | 7 days | M2 |
| 6 | Unique institute name | No (the slug is unique) | M1 |
| 7 | Profile columns | CEO name and message, website, contact email and phone, Facebook, LinkedIn | M1 |
| 8 | URL split | `institutes/` public, `institute/` portal, `admin/` console | M3 |
| 9 | Invitation email | Sent now with Django `send_mail`, queued with django-q2 after commit. The full `notifications` app comes later | M2 |

Already decided: the seven institute types, profile as plain columns plus a gallery table, a rejected institute can re-apply
(`REJECTED` to `PENDING`), only `APPROVED` institutes are public, a staff user belongs to one institute, level `MUNICIPALITY`.

Two corrections to earlier snippets, found by reading the repo:
- `BASE_DIR` is the `config/` folder, not the project root, so `BASE_DIR / "private_media"` would land inside `config/`. Use `BASE_DIR.parent / "private_media"` (next to `keys/`).
- A `FileField` with a callable storage builds the storage **once at import**, so `override_settings` cannot redirect it in tests. The storage below reads the setting on every use.

---

## M0 – Before you start

- [x] Commit the finished `catalog` work, then branch:

  ```sh
  git add apps/catalog apps/api/v1/urls.py config/settings/base.py CLAUDE.md README.md docs
  git commit -m "Add catalog app: Location model, load_locations command and public locations API"
  git switch -c feature/institutes
  ```

- [x] Confirm the nine decisions above (or reply "use the defaults"). Ticked in the Notion work list on 2026-10-02, so the defaults are the decisions.

## M1 – Data layer (models, settings, admin, constraint tests)

- [x] Scaffold the app:

  ```sh
  mkdir -p apps/institutes/{migrations,tests,api/v1/urls}
  touch apps/institutes/{__init__,constants,storage,validators,models,services,tasks,permissions,admin}.py \
        apps/institutes/{migrations,tests,api,api/v1,api/v1/urls}/__init__.py \
        apps/institutes/api/v1/{serializers,views}.py
  ```

  ```python
  # apps/institutes/apps.py
  from django.apps import AppConfig


  class InstitutesConfig(AppConfig):
      name = "apps.institutes"
  ```

- [x] Settings and `.gitignore`:

  ```python
  # config/settings/base.py
  LOCAL_APPS = ["apps.users", "apps.catalog", "apps.institutes"]

  # Verification documents are private: outside MEDIA_ROOT and never served by URL.
  # BASE_DIR is config/, so .parent is the project root (next to keys/).
  PRIVATE_MEDIA_ROOT = BASE_DIR.parent / "private_media"

  INSTITUTE_INVITATION_TTL_DAYS = 7
  INSTITUTE_UPLOAD_MAX_BYTES = 5 * 1024 * 1024
  INSTITUTE_DOCUMENT_EXTENSIONS = ("pdf", "jpg", "jpeg", "png")
  INSTITUTE_IMAGE_EXTENSIONS = ("jpg", "jpeg", "png")
  FRONTEND_BASE_URL = os.environ.get("FRONTEND_BASE_URL", "http://localhost:3000")

  # inside REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]:
  #     "institute_register": "5/hour",
  #     "invitation_accept": "10/hour",
  ```

  Add `private_media/` to `.gitignore`.

- [x] `apps/institutes/constants.py`:

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
      TRANSITIONS = {
          PENDING: {APPROVED, REJECTED, INFO_REQUESTED},
          INFO_REQUESTED: {PENDING},
          REJECTED: {PENDING},               # a rejected institute can re-apply
          APPROVED: {SUSPENDED},
          SUSPENDED: {APPROVED},
      }
      REASON_REQUIRED = {REJECTED, INFO_REQUESTED, SUSPENDED}


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
  ```

- [x] Private storage (reads the setting on every use; has no URL on purpose):

  ```python
  # apps/institutes/storage.py
  import os

  from django.conf import settings
  from django.core.files.storage import FileSystemStorage


  class PrivateStorage(FileSystemStorage):
      """Files live under settings.PRIVATE_MEDIA_ROOT and are only served by an authorised view."""

      @property
      def base_location(self):
          return settings.PRIVATE_MEDIA_ROOT

      @property
      def location(self):
          return os.path.abspath(self.base_location)

      def url(self, name):
          raise ValueError("Private files have no URL.")
  ```

- [x] Validators. The upload checks look at the extension and size only; add content sniffing (for example `python-magic`) if documents ever need it:

  ```python
  # apps/institutes/validators.py
  import os

  from django.conf import settings
  from django.core.exceptions import ValidationError

  from apps.catalog.constants import LocationLevel


  def validate_institute_location(location):
      if location.level != LocationLevel.MUNICIPALITY or not location.is_active:
          raise ValidationError("Choose an active municipality.")


  def _validate_upload(file, extensions):
      extension = os.path.splitext(file.name)[1].lower().lstrip(".")
      if extension not in extensions:
          raise ValidationError(f"Allowed file types: {', '.join(extensions)}.")
      if file.size > settings.INSTITUTE_UPLOAD_MAX_BYTES:
          raise ValidationError(f"The file is larger than {settings.INSTITUTE_UPLOAD_MAX_BYTES // (1024 * 1024)} MB.")


  def validate_document_file(file):
      _validate_upload(file, settings.INSTITUTE_DOCUMENT_EXTENSIONS)


  def validate_image_file(file):
      _validate_upload(file, settings.INSTITUTE_IMAGE_EXTENSIONS)
  ```

  This deliberately does not use `validate_attachment`, which needs the undefined `ATTACHMENT_MAX_UPLOAD_SIZE`.

- [x] Models (`registered_at` is `BaseModel.created_at`; the profile is plain columns):

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
  from apps.institutes.storage import PrivateStorage
  from apps.institutes.validators import validate_document_file, validate_image_file


  class Institute(BaseModel, SlugModel):
      name = models.CharField(max_length=255)
      type = models.CharField(max_length=30, choices=InstituteType.CHOICES)
      established_year = models.PositiveSmallIntegerField(null=True, blank=True)
      description = models.TextField(blank=True)                      # "about"
      logo = models.ImageField(upload_to=get_upload_path, blank=True, validators=[validate_image_file])
      status = models.CharField(max_length=20, choices=InstituteStatus.CHOICES,
                                default=InstituteStatus.PENDING)
      status_reason = models.TextField(blank=True)
      # profile
      ceo_name = models.CharField(max_length=150, blank=True)
      ceo_message = models.TextField(blank=True)
      website = models.URLField(blank=True)
      contact_email = models.EmailField(blank=True)
      contact_phone = models.CharField(max_length=25, blank=True, validators=[validate_phone_number])
      facebook_url = models.URLField(blank=True)
      linkedin_url = models.URLField(blank=True)

      class Meta:
          indexes = [models.Index(fields=["status"], name="institutes_status_idx")]

      def __str__(self):
          return self.name


  class InstituteMember(BaseModel):
      # OneToOne: a staff user belongs to ONE institute only, enforced by the database.
      user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="membership")
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
      token_hash = models.CharField(max_length=64, unique=True)       # sha256 of the emailed token
      status = models.CharField(max_length=10, choices=InvitationStatus.CHOICES,
                                default=InvitationStatus.PENDING)
      expires_at = models.DateTimeField()
      invited_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL,
                                     related_name="+")

      class Meta:
          constraints = [
              models.UniqueConstraint(                                # one pending invite per institute and email
                  Lower("email"), "institute", condition=models.Q(status=InvitationStatus.PENDING),
                  name="institutes_one_pending_invite",
              ),
          ]
          indexes = [models.Index(fields=["expires_at"], name="institutes_invite_expiry_idx")]


  class InstituteDocument(BaseModel):
      institute = models.ForeignKey(Institute, on_delete=models.CASCADE, related_name="documents")
      name = models.CharField(max_length=150)
      file = models.FileField(upload_to=get_upload_path, storage=PrivateStorage,
                              validators=[validate_document_file])
      status = models.CharField(max_length=10, choices=DocumentStatus.CHOICES,
                                default=DocumentStatus.PENDING)

      class Meta:
          indexes = [models.Index(fields=["institute", "status"], name="institutes_doc_status_idx")]


  class InstituteLocation(BaseModel):
      institute = models.ForeignKey(Institute, on_delete=models.CASCADE, related_name="locations")
      # must be an active MUNICIPALITY-level Location; checked by validate_institute_location
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


  class InstituteGalleryImage(BaseModel):
      institute = models.ForeignKey(Institute, on_delete=models.CASCADE, related_name="gallery")
      image = models.ImageField(upload_to=get_upload_path, validators=[validate_image_file])
      caption = models.CharField(max_length=200, blank=True)
      position = models.PositiveSmallIntegerField(default=0)          # no unique: a reorder is one bulk_update

      class Meta:
          indexes = [models.Index(fields=["institute", "position"], name="institutes_gallery_pos_idx")]
  ```

- [x] `python manage.py makemigrations institutes`, read the migration, then `python manage.py migrate`. Never hand-edit it.
- [x] Read-only admin, same pattern as `users`. Do **not** register `InstituteDocument` (its files are private):

  ```python
  # apps/institutes/admin.py
  from django.contrib import admin

  from apps.institutes.models import Institute


  @admin.register(Institute)
  class InstituteAdmin(admin.ModelAdmin):
      list_display = ("name", "type", "status", "created_at")
      list_filter = ("status", "type")
      search_fields = ("name", "slug")
      ordering = ("-created_at", "-pk")

      def has_add_permission(self, request):
          return False

      def has_change_permission(self, request, obj=None):
          return False

      def has_delete_permission(self, request, obj=None):
          return False
  ```

- [x] Test helpers. Uploads go to temporary folders, so tests never write into `private_media/` or `config/media/`:

  ```python
  # apps/institutes/tests/helpers.py
  import tempfile

  from django.contrib.auth import get_user_model
  from django.core.files.uploadedfile import SimpleUploadedFile
  from django.test import override_settings

  from apps.catalog.models import Location
  from apps.institutes.constants import InstituteStatus, InstituteType, MemberRole
  from apps.institutes.models import Institute, InstituteLocation, InstituteMember
  from apps.users.constants import Role

  User = get_user_model()
  PASSWORD = "Str0ng-pass-123!"


  def make_municipality(code=1, name="Municipality"):
      province, _ = Location.objects.get_or_create(level="PROVINCE", code=1, defaults={"name": "Province"})
      district, _ = Location.objects.get_or_create(
          level="DISTRICT", code=1, defaults={"name": "District", "parent": province})
      return Location.objects.create(level="MUNICIPALITY", code=code, name=name, parent=district,
                                     type="MUNICIPALITY")


  def make_institute(name="Alpha Institute", status=InstituteStatus.PENDING, email="owner@example.com"):
      institute = Institute.objects.create(name=name, type=InstituteType.COMPANY, status=status)
      owner = User.objects.create_user(email, PASSWORD, full_name="Owner", role=Role.INSTITUTE_STAFF)
      InstituteMember.objects.create(user=owner, institute=institute, role=MemberRole.OWNER)
      return institute, owner


  def add_location(institute, municipality, *, is_main=False, is_active=True):
      return InstituteLocation.objects.create(
          institute=institute, location=municipality, address="Main Road", is_main=is_main, is_active=is_active)


  def pdf(name="license.pdf"):
      return SimpleUploadedFile(name, b"%PDF-1.4 test", content_type="application/pdf")


  class TempMediaMixin:
      """Put MEDIA_ROOT and PRIVATE_MEDIA_ROOT in temporary folders for the test."""

      def setUp(self):
          super().setUp()
          for setting in ("MEDIA_ROOT", "PRIVATE_MEDIA_ROOT"):
              folder = tempfile.TemporaryDirectory()
              self.addCleanup(folder.cleanup)
              override = override_settings(**{setting: folder.name})
              override.enable()
              self.addCleanup(override.disable)
  ```

- [x] Constraint tests:

  ```python
  # apps/institutes/tests/test_models.py
  from django.db import IntegrityError, transaction
  from django.test import TestCase
  from django.utils import timezone

  from apps.institutes.constants import InvitationStatus, MemberRole
  from apps.institutes.models import InstituteInvitation, InstituteMember
  from apps.institutes.tests.helpers import (
      PASSWORD, User, add_location, make_institute, make_municipality,
  )


  class InstituteConstraintTests(TestCase):
      def setUp(self):
          self.institute, self.owner = make_institute()
          self.municipality = make_municipality()

      def test_second_owner_rejected(self):
          other = User.objects.create_user("other@example.com", PASSWORD)
          with self.assertRaises(IntegrityError), transaction.atomic():
              InstituteMember.objects.create(user=other, institute=self.institute, role=MemberRole.OWNER)

      def test_user_cannot_belong_to_two_institutes(self):
          other_institute, _ = make_institute(name="Beta", email="beta@example.com")
          with self.assertRaises(IntegrityError), transaction.atomic():
              InstituteMember.objects.create(user=self.owner, institute=other_institute, role=MemberRole.STAFF)

      def test_two_active_main_locations_rejected(self):
          add_location(self.institute, self.municipality, is_main=True)
          with self.assertRaises(IntegrityError), transaction.atomic():
              add_location(self.institute, self.municipality, is_main=True)

      def test_inactive_main_location_rejected(self):
          with self.assertRaises(IntegrityError), transaction.atomic():
              add_location(self.institute, self.municipality, is_main=True, is_active=False)

      def test_duplicate_pending_invitation_rejected_case_insensitively(self):
          make = lambda email, status: InstituteInvitation.objects.create(
              institute=self.institute, email=email, status=status, token_hash=email,
              expires_at=timezone.now())
          make("a@example.com", InvitationStatus.PENDING)
          with self.assertRaises(IntegrityError), transaction.atomic():
              make("A@Example.com", InvitationStatus.PENDING)
          make("b@example.com", InvitationStatus.REVOKED)      # revoked ones do not block
          make("B@example.com", InvitationStatus.PENDING)
  ```

- [x] **M1 done when:** `check` clean, `makemigrations --check --dry-run` clean, constraint tests pass, the whole suite still passes.

## M2 – Services (all business rules and transactions)

- [x] `apps/institutes/services.py`, part 1: the status workflow. Every move is checked against `TRANSITIONS` under a row lock:

  ```python
  import hashlib
  import secrets
  from datetime import timedelta

  from django.conf import settings
  from django.contrib.auth import get_user_model
  from django.core.exceptions import ValidationError
  from django.db import transaction
  from django.utils import timezone
  from django_q.tasks import async_task

  from apps.institutes.constants import (
      DocumentStatus, InstituteStatus, InvitationStatus, MemberRole,
  )
  from apps.institutes.models import (
      Institute, InstituteDocument, InstituteGalleryImage, InstituteInvitation,
      InstituteLocation, InstituteMember,
  )
  from apps.institutes.validators import validate_institute_location
  from apps.users import services as user_services
  from apps.users.constants import Role

  User = get_user_model()


  def _transition(institute, to, *, reason="", check=None):
      """Caller must be inside transaction.atomic()."""
      institute = Institute.objects.select_for_update().get(pk=institute.pk)
      if to not in InstituteStatus.TRANSITIONS[institute.status]:
          raise ValidationError(f"Cannot move from {institute.status} to {to}.")
      if to in InstituteStatus.REASON_REQUIRED and not reason.strip():
          raise ValidationError({"reason": "A reason is required."})
      if check:
          check(institute)
      institute.status = to
      institute.status_reason = reason
      institute.save(update_fields=["status", "status_reason", "modified_at"])
      return institute


  def _ready_for_approval(institute):
      if not institute.locations.filter(is_active=True).exists():
          raise ValidationError("Add at least one active location before approval.")
      if not institute.documents.exists():
          raise ValidationError("Upload at least one verification document before approval.")


  @transaction.atomic
  def approve(institute, *, by):
      # TODO(audit) + TODO(notify): the institute owner
      return _transition(institute, InstituteStatus.APPROVED, check=_ready_for_approval)


  @transaction.atomic
  def reject(institute, *, by, reason):
      return _transition(institute, InstituteStatus.REJECTED, reason=reason)


  @transaction.atomic
  def request_info(institute, *, by, reason):
      return _transition(institute, InstituteStatus.INFO_REQUESTED, reason=reason)


  @transaction.atomic
  def suspend(institute, *, by, reason):
      # Staff keep their accounts (decision 1); the public queries hide the institute.
      return _transition(institute, InstituteStatus.SUSPENDED, reason=reason)


  @transaction.atomic
  def reinstate(institute, *, by):
      return _transition(institute, InstituteStatus.APPROVED)


  @transaction.atomic
  def resubmit(institute):
      """The owner answers an info request, or re-applies after a rejection."""
      return _transition(institute, InstituteStatus.PENDING)
  ```

- [x] Part 2: registration and locations:

  ```python
  @transaction.atomic
  def register(*, institute_data, owner, locations=()):
      """owner = {"email", "password", "full_name", optional "phone_number"}; the owner is always INSTITUTE_STAFF.
      Documents are uploaded afterwards through the portal (decision 4)."""
      for item in locations:
          validate_institute_location(item["location"])        # bulk_create skips model validation
      institute = Institute.objects.create(**institute_data)
      owner_user = User.objects.create_user(role=Role.INSTITUTE_STAFF, **owner)
      InstituteMember.objects.create(user=owner_user, institute=institute, role=MemberRole.OWNER)
      InstituteLocation.objects.bulk_create([
          InstituteLocation(institute=institute, is_main=(i == 0), **item)      # the first one is the main office
          for i, item in enumerate(locations)
      ])
      # TODO(notify): admins with manage_institutes
      return institute


  @transaction.atomic
  def add_location(institute, *, location, address, contact_phone=""):
      validate_institute_location(location)
      Institute.objects.select_for_update().get(pk=institute.pk)             # serialise per institute
      first = not institute.locations.filter(is_active=True).exists()
      return InstituteLocation.objects.create(
          institute=institute, location=location, address=address,
          contact_phone=contact_phone, is_main=first,
      )


  @transaction.atomic
  def update_location(instance, **fields):
      if "location" in fields:
          validate_institute_location(fields["location"])
      instance = InstituteLocation.objects.select_for_update().get(pk=instance.pk)
      for name, value in fields.items():
          setattr(instance, name, value)
      instance.save(update_fields=[*fields, "modified_at"])
      return instance


  @transaction.atomic
  def set_main_location(location):
      Institute.objects.select_for_update().get(pk=location.institute_id)
      location = InstituteLocation.objects.get(pk=location.pk)
      if not location.is_active:
          raise ValidationError("An inactive location cannot be the main office.")
      InstituteLocation.objects.filter(
          institute_id=location.institute_id, is_main=True
      ).exclude(pk=location.pk).update(is_main=False)         # clear first, then set (partial unique index)
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

- [x] Part 3: documents and gallery:

  ```python
  @transaction.atomic
  def add_document(institute, *, name, file):
      return InstituteDocument.objects.create(institute=institute, name=name, file=file)


  @transaction.atomic
  def review_document(document, *, status, by):
      if status not in (DocumentStatus.VERIFIED, DocumentStatus.REJECTED):
          raise ValidationError({"status": "Choose VERIFIED or REJECTED."})
      document = InstituteDocument.objects.select_for_update().get(pk=document.pk)
      document.status = status
      document.save(update_fields=["status", "modified_at"])
      return document


  @transaction.atomic
  def add_gallery_image(institute, *, image, caption=""):
      Institute.objects.select_for_update().get(pk=institute.pk)
      return InstituteGalleryImage.objects.create(
          institute=institute, image=image, caption=caption,
          position=institute.gallery.count(),                  # appended at the end
      )


  @transaction.atomic
  def reorder_gallery(institute, ids):
      images = {i.pk: i for i in InstituteGalleryImage.objects.select_for_update().filter(institute=institute)}
      if sorted(images) != sorted(ids):
          raise ValidationError("Send every gallery image id exactly once.")
      for position, pk in enumerate(ids):
          images[pk].position = position
      InstituteGalleryImage.objects.bulk_update(images.values(), ["position"])
  ```

- [x] Part 4: staff and invitations. The raw token exists only in the email and in memory; the database keeps a hash, and the queued task is not saved in django-q's results table (`save=False`):

  ```python
  def _hash(token):
      return hashlib.sha256(token.encode()).hexdigest()


  @transaction.atomic
  def invite(*, institute, email, by):
      email = email.strip()
      Institute.objects.select_for_update().get(pk=institute.pk)
      institute.invitations.filter(                            # an expired invite must not block a new one
          email__iexact=email, status=InvitationStatus.PENDING, expires_at__lt=timezone.now(),
      ).update(status=InvitationStatus.REVOKED)
      if User.objects.filter(email__iexact=email).exists():
          raise ValidationError({"email": "This email already has an account."})   # one institute per user
      if institute.invitations.filter(email__iexact=email, status=InvitationStatus.PENDING).exists():
          raise ValidationError({"email": "An invitation is already pending for this email."})
      token = secrets.token_urlsafe(32)
      invitation = InstituteInvitation.objects.create(
          institute=institute, email=email, role=MemberRole.STAFF, invited_by=by,
          token_hash=_hash(token),
          expires_at=timezone.now() + timedelta(days=settings.INSTITUTE_INVITATION_TTL_DAYS),
      )
      transaction.on_commit(lambda: async_task(
          "apps.institutes.tasks.send_invitation_email", invitation.pk, token, save=False))
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
      if User.objects.filter(email__iexact=invitation.email).exists():
          raise ValidationError("This email already has an account.")
      user = User.objects.create_user(
          email=invitation.email, password=password, full_name=full_name, role=Role.INSTITUTE_STAFF,
      )
      InstituteMember.objects.create(user=user, institute=invitation.institute, role=invitation.role)
      invitation.status = InvitationStatus.ACCEPTED
      invitation.save(update_fields=["status", "modified_at"])
      return user


  @transaction.atomic
  def revoke_invitation(invitation, *, by):
      invitation = InstituteInvitation.objects.select_for_update().get(pk=invitation.pk)
      if invitation.status != InvitationStatus.PENDING:
          raise ValidationError("Only a pending invitation can be revoked.")
      invitation.status = InvitationStatus.REVOKED
      invitation.save(update_fields=["status", "modified_at"])
      return invitation


  @transaction.atomic
  def remove_staff(member, *, by):
      member = InstituteMember.objects.select_for_update().select_related("user").get(pk=member.pk)
      if member.role == MemberRole.OWNER:
          raise ValidationError("The owner cannot be removed.")
      user = member.user
      member.delete()
      user_services.set_status(user, active=False, by=by)      # deactivates and revokes refresh tokens
  ```

  ```python
  # apps/institutes/tasks.py
  from django.conf import settings
  from django.core.mail import send_mail

  from apps.institutes.constants import InvitationStatus
  from apps.institutes.models import InstituteInvitation


  def send_invitation_email(invitation_id, token):
      invitation = InstituteInvitation.objects.select_related("institute").get(pk=invitation_id)
      if invitation.status != InvitationStatus.PENDING:
          return
      link = f"{settings.FRONTEND_BASE_URL}/accept-invitation?token={token}"
      send_mail(
          subject=f"You are invited to join {invitation.institute.name} on TrainingHub",
          message=f"Open this link to set your password and join:\n\n{link}\n\nIt expires on "
                  f"{invitation.expires_at:%d %b %Y}.",
          from_email=None,                                      # DEFAULT_FROM_EMAIL
          recipient_list=[invitation.email],
      )
  ```

  The queued email is only delivered while `python manage.py qcluster` is running (it also needs Redis).

- [x] Service tests (`apps/institutes/tests/test_services.py`). These show the pattern; add the rest from the list below:

  ```python
  import hashlib
  from unittest import mock

  from django.core.exceptions import ValidationError
  from django.test import TestCase
  from django.utils import timezone

  from apps.institutes import services
  from apps.institutes.constants import InstituteStatus
  from apps.institutes.models import Institute, InstituteInvitation, InstituteLocation
  from apps.institutes.tests.helpers import (
      PASSWORD, TempMediaMixin, User, add_location, make_institute, make_municipality, pdf,
  )
  from apps.users.constants import Role


  class WorkflowTests(TempMediaMixin, TestCase):
      def setUp(self):
          super().setUp()
          self.institute, self.owner = make_institute()
          self.admin = User.objects.create_user("admin@example.com", PASSWORD, role=Role.ADMIN)

      def test_every_pair_of_statuses(self):
          for start, allowed in InstituteStatus.TRANSITIONS.items():
              for target in InstituteStatus.TRANSITIONS:
                  with self.subTest(start=start, target=target):
                      Institute.objects.filter(pk=self.institute.pk).update(status=start)
                      if target in allowed:
                          result = services._transition(self.institute, target, reason="because")
                          self.assertEqual(result.status, target)
                      else:
                          with self.assertRaises(ValidationError):
                              services._transition(self.institute, target, reason="because")

      def test_reason_is_required_to_reject(self):
          with self.assertRaises(ValidationError):
              services.reject(self.institute, by=self.admin, reason="  ")

      def test_approval_needs_a_location_and_a_document(self):
          with self.assertRaises(ValidationError):
              services.approve(self.institute, by=self.admin)
          add_location(self.institute, make_municipality(), is_main=True)
          with self.assertRaises(ValidationError):
              services.approve(self.institute, by=self.admin)
          services.add_document(self.institute, name="License", file=pdf())
          self.assertEqual(services.approve(self.institute, by=self.admin).status, InstituteStatus.APPROVED)

      def test_rejected_institute_can_re_apply(self):
          services.reject(self.institute, by=self.admin, reason="Unclear documents")
          self.assertEqual(services.resubmit(self.institute).status, InstituteStatus.PENDING)


  class RegistrationTests(TestCase):
      def setUp(self):
          self.municipality = make_municipality()
          self.owner = {"email": "new@example.com", "password": PASSWORD, "full_name": "New Owner"}
          self.data = {"name": "New Institute", "type": "COMPANY"}

      def test_creates_everything_with_the_first_location_as_main(self):
          institute = services.register(
              institute_data=self.data, owner=self.owner,
              locations=[{"location": self.municipality, "address": "A"},
                         {"location": self.municipality, "address": "B"}],
          )
          self.assertEqual(institute.status, InstituteStatus.PENDING)
          self.assertEqual(institute.members.get().user.role, Role.INSTITUTE_STAFF)
          self.assertEqual(list(institute.locations.order_by("pk").values_list("is_main", flat=True)), [True, False])

      def test_a_failure_leaves_nothing_behind(self):
          with mock.patch.object(InstituteLocation.objects, "bulk_create", side_effect=RuntimeError("boom")):
              with self.assertRaises(RuntimeError):
                  services.register(institute_data=self.data, owner=self.owner,
                                    locations=[{"location": self.municipality, "address": "A"}])
          self.assertFalse(Institute.objects.exists())
          self.assertFalse(User.objects.filter(email="new@example.com").exists())


  class InvitationTests(TestCase):
      def setUp(self):
          self.institute, self.owner = make_institute()

      def invite(self, email="new@example.com"):
          with mock.patch("apps.institutes.services.async_task") as queued, \
                  self.captureOnCommitCallbacks(execute=True):
              invitation = services.invite(institute=self.institute, email=email, by=self.owner)
          return invitation, queued

      def test_only_a_hash_is_stored_and_the_task_is_not_saved(self):
          invitation, queued = self.invite()
          token = queued.call_args.args[2]
          self.assertEqual(invitation.token_hash, hashlib.sha256(token.encode()).hexdigest())
          self.assertIs(queued.call_args.kwargs["save"], False)

      def test_accept_works_once(self):
          invitation, queued = self.invite()
          token = queued.call_args.args[2]
          user = services.accept_invitation(token=token, full_name="New Staff", password=PASSWORD)
          self.assertEqual(user.membership.institute, self.institute)
          with self.assertRaises(ValidationError):
              services.accept_invitation(token=token, full_name="Again", password=PASSWORD)

      def test_expired_invitation_is_refused(self):
          invitation, queued = self.invite()
          InstituteInvitation.objects.filter(pk=invitation.pk).update(expires_at=timezone.now())
          with self.assertRaises(ValidationError):
              services.accept_invitation(token=queued.call_args.args[2], full_name="X", password=PASSWORD)

      def test_existing_account_cannot_be_invited(self):
          with self.assertRaises(ValidationError):
              self.invite(email=self.owner.email.upper())
  ```

  Still to write: removing staff (membership gone, user inactive, refresh tokens blacklisted, owner cannot be removed),
  location switching and deactivation, gallery reorder, document review, a second pending invitation, and re-inviting after expiry.

- [x] **M2 done when:** all service tests pass and the suite is green.

## M3 – Public and admin API

- [x] Wire the URLs. Prefixes live only in `apps/api/v1/urls.py`:

  ```python
  # apps/api/v1/urls.py
  urlpatterns = [
      path("user/", include("apps.users.api.v1.urls.users")),
      path("locations/", include("apps.catalog.api.v1.urls.locations")),
      path("institutes/", include("apps.institutes.api.v1.urls.public")),
      path("institute/", include("apps.institutes.api.v1.urls.portal")),     # added in M4
      path("admin/", include("apps.institutes.api.v1.urls.admin")),
  ]
  ```

- [x] Imports for the two API files (the non-obvious ones; your editor will suggest the rest):

  ```python
  # apps/institutes/api/v1/serializers.py
  from django.contrib.auth import get_user_model
  from django.contrib.auth.password_validation import validate_password
  from rest_framework import serializers
  from rest_framework.validators import UniqueValidator

  from apps.catalog.constants import LocationLevel
  from apps.catalog.models import Location
  from apps.common.serializers import DynamicFieldsModelSerializer
  from apps.common.validators import validate_phone_number
  from apps.institutes import services
  from apps.institutes.constants import DocumentStatus
  from apps.institutes.models import (
      Institute, InstituteDocument, InstituteGalleryImage, InstituteInvitation,
      InstituteLocation, InstituteMember,
  )

  # apps/institutes/api/v1/views.py
  import os

  from django.db.models import Prefetch
  from django.http import FileResponse
  from django.shortcuts import get_object_or_404
  from django_filters.rest_framework import DjangoFilterBackend
  from rest_framework.decorators import action
  from rest_framework.filters import SearchFilter
  from rest_framework.generics import CreateAPIView, GenericAPIView, RetrieveUpdateAPIView
  from rest_framework.permissions import AllowAny
  from rest_framework.response import Response
  from rest_framework.views import APIView

  from apps.common.viewsets import (
      CreateListDestroyViewSet, CreateListRetrieveUpdateViewSet, CreateListUpdateDestroyViewSet,
      CreateListViewSet, DestroyViewSet, ListViewSet, ReadOnlyViewSet,
  )
  from apps.institutes import services
  from apps.institutes.constants import InstituteStatus, MemberRole
  from apps.institutes.models import (
      Institute, InstituteDocument, InstituteGalleryImage, InstituteInvitation,
      InstituteLocation, InstituteMember,
  )
  from apps.institutes.permissions import IsInstituteMember, IsInstituteOwner, InstituteScopedMixin
  from apps.users.permissions import HasPlatformPermission
  ```

- [x] Registration serializer (the owner's email is checked case-insensitively; role and status are never read from the payload):

  ```python
  # apps/institutes/api/v1/serializers.py (part 1)
  User = get_user_model()


  class OwnerSerializer(serializers.Serializer):
      email = serializers.EmailField(validators=[UniqueValidator(
          queryset=User.objects.all(), lookup="iexact", message="A user with that email already exists.")])
      full_name = serializers.CharField(max_length=150)
      password = serializers.CharField(write_only=True)
      phone_number = serializers.CharField(max_length=25, required=False, validators=[validate_phone_number])

      def validate_password(self, value):
          validate_password(value)
          return value


  class LocationInputSerializer(serializers.Serializer):
      location = serializers.PrimaryKeyRelatedField(
          queryset=Location.objects.filter(level=LocationLevel.MUNICIPALITY, is_active=True))
      address = serializers.CharField(max_length=255)
      contact_phone = serializers.CharField(max_length=25, required=False, allow_blank=True,
                                            validators=[validate_phone_number])


  class RegisterSerializer(DynamicFieldsModelSerializer):
      owner = OwnerSerializer(write_only=True)
      locations = LocationInputSerializer(many=True, write_only=True, required=False)

      class Meta:
          model = Institute
          fields = ("id", "slug", "name", "type", "established_year", "description", "status",
                    "owner", "locations")
          read_only_fields = ("id", "slug", "status")

      def create(self, validated_data):
          return services.register(
              owner=validated_data.pop("owner"),
              locations=validated_data.pop("locations", []),
              institute_data=validated_data,
          )
  ```

  ```python
  # apps/institutes/api/v1/views.py (part 1): public registration
  class RegisterView(CreateAPIView):
      serializer_class = RegisterSerializer
      permission_classes = [AllowAny]
      authentication_classes = []
      throttle_scope = "institute_register"
  ```

  It lives in the portal URL module as `institute/register/`, and must come before the router paths there.
  The owner can log in straight away, while the institute is still `PENDING`, to upload documents and answer requests.

- [x] Public list and detail: only `APPROVED`, stable order, a constant number of queries:

  ```python
  # apps/institutes/api/v1/serializers.py (part 2)
  class PublicInstituteListSerializer(DynamicFieldsModelSerializer):
      location = serializers.SerializerMethodField()

      class Meta:
          model = Institute
          fields = ("id", "slug", "name", "type", "logo", "location")

      def get_location(self, obj):
          main = next((l for l in obj.locations.all() if l.is_main), None)   # prefetched, no query
          if main is None:
              return None
          return {"municipality": main.location.name, "district": main.location.district.name,
                  "province": main.location.province.name, "address": main.address}


  class PublicInstituteDetailSerializer(PublicInstituteListSerializer):
      locations = serializers.SerializerMethodField()
      gallery = serializers.SerializerMethodField()

      class Meta(PublicInstituteListSerializer.Meta):
          fields = PublicInstituteListSerializer.Meta.fields + (
              "established_year", "description", "ceo_name", "ceo_message", "website", "contact_email",
              "contact_phone", "facebook_url", "linkedin_url", "locations", "gallery")

      def get_locations(self, obj):
          return [{"municipality": l.location.name, "district": l.location.district.name,
                   "province": l.location.province.name, "address": l.address,
                   "contact_phone": l.contact_phone, "is_main": l.is_main} for l in obj.locations.all()]

      def get_gallery(self, obj):
          return [{"image": i.image.url, "caption": i.caption} for i in obj.gallery.all()]
  ```

  ```python
  # apps/institutes/api/v1/views.py (part 2)
  class PublicInstituteViewSet(ReadOnlyViewSet):
      permission_classes = []                     # public
      lookup_field = "slug"
      filter_backends = (DjangoFilterBackend, SearchFilter)
      filterset_fields = ("type",)
      search_fields = ("name",)

      def get_serializer_class(self):
          return PublicInstituteDetailSerializer if self.action == "retrieve" else PublicInstituteListSerializer

      def get_queryset(self):
          return (
              Institute.objects.filter(status=InstituteStatus.APPROVED)
              .prefetch_related(
                  Prefetch("locations", queryset=InstituteLocation.objects.filter(is_active=True)
                           .select_related("location", "location__district", "location__province")),
                  Prefetch("gallery", queryset=InstituteGalleryImage.objects.order_by("position", "pk")),
              )
              .order_by("name", "pk")
          )
  ```

  ```python
  # apps/institutes/api/v1/urls/public.py
  from rest_framework import routers

  from apps.institutes.api.v1 import views

  app_name = "institutes_public"

  router = routers.SimpleRouter()
  router.register("", views.PublicInstituteViewSet, basename="institute")
  urlpatterns = router.urls
  ```

- [x] Admin review API. `users.manage_institutes` is the permission, and the five decisions share one helper:

  ```python
  # apps/institutes/api/v1/serializers.py (part 3)
  class ReasonSerializer(serializers.Serializer):
      reason = serializers.CharField()


  class AdminDocumentSerializer(DynamicFieldsModelSerializer):
      class Meta:
          model = InstituteDocument
          fields = ("id", "name", "status", "created_at")          # never the file path or URL
          read_only_fields = ("id", "name", "created_at")


  class DocumentReviewSerializer(serializers.Serializer):
      status = serializers.ChoiceField(choices=(DocumentStatus.VERIFIED, DocumentStatus.REJECTED))


  class AdminInstituteSerializer(DynamicFieldsModelSerializer):
      documents = AdminDocumentSerializer(many=True, read_only=True)
      owner_email = serializers.SerializerMethodField()

      class Meta:
          model = Institute
          fields = ("id", "slug", "name", "type", "status", "status_reason", "established_year", "description",
                    "created_at", "owner_email", "documents")

      def get_owner_email(self, obj):
          owners = getattr(obj, "owner_members", [])               # prefetched below
          return owners[0].user.email if owners else None
  ```

  ```python
  # apps/institutes/api/v1/views.py (part 3)
  class AdminInstituteViewSet(ReadOnlyViewSet):
      serializer_class = AdminInstituteSerializer
      permission_classes = [HasPlatformPermission]
      required_permission = "users.manage_institutes"
      lookup_value_regex = r"[0-9]+"
      filter_backends = (DjangoFilterBackend, SearchFilter)
      filterset_fields = ("status", "type")
      search_fields = ("name",)
      queryset = (
          Institute.objects.prefetch_related(
              "documents",
              Prefetch("members", queryset=InstituteMember.objects.filter(role=MemberRole.OWNER).select_related("user"),
                       to_attr="owner_members"),
          ).order_by("-created_at", "-pk")
      )

      def _review(self, request, service, *, with_reason):
          kwargs = {}
          if with_reason:
              serializer = ReasonSerializer(data=request.data)
              serializer.is_valid(raise_exception=True)
              kwargs["reason"] = serializer.validated_data["reason"]
          institute = service(self.get_object(), by=request.user, **kwargs)
          return Response(AdminInstituteSerializer(institute, context=self.get_serializer_context()).data)

      @action(detail=True, methods=["post"])
      def approve(self, request, pk=None):
          return self._review(request, services.approve, with_reason=False)

      @action(detail=True, methods=["post"])
      def reject(self, request, pk=None):
          return self._review(request, services.reject, with_reason=True)

      @action(detail=True, methods=["post"], url_path="request-info")
      def request_info(self, request, pk=None):
          return self._review(request, services.request_info, with_reason=True)

      @action(detail=True, methods=["post"])
      def suspend(self, request, pk=None):
          return self._review(request, services.suspend, with_reason=True)

      @action(detail=True, methods=["post"])
      def reinstate(self, request, pk=None):
          return self._review(request, services.reinstate, with_reason=False)
  ```

  Documents are private. A reviewer reviews one with a `PATCH` and downloads it through an authorised stream; nothing ever returns `file.url`:

  ```python
  # apps/institutes/api/v1/views.py (part 4)
  def private_file_response(document):
      return FileResponse(document.file.open("rb"), as_attachment=True,
                          filename=os.path.basename(document.file.name))


  class AdminDocumentView(GenericAPIView):
      permission_classes = [HasPlatformPermission]
      required_permission = "users.manage_institutes"
      serializer_class = DocumentReviewSerializer

      def patch(self, request, institute_id, pk):
          document = get_object_or_404(InstituteDocument, pk=pk, institute_id=institute_id)
          serializer = self.get_serializer(data=request.data)
          serializer.is_valid(raise_exception=True)
          document = services.review_document(document, status=serializer.validated_data["status"], by=request.user)
          return Response(AdminDocumentSerializer(document).data)


  class AdminDocumentDownloadView(APIView):
      permission_classes = [HasPlatformPermission]
      required_permission = "users.manage_institutes"

      def get(self, request, institute_id, pk):
          return private_file_response(get_object_or_404(InstituteDocument, pk=pk, institute_id=institute_id))
  ```

  ```python
  # apps/institutes/api/v1/urls/admin.py
  from django.urls import path
  from rest_framework import routers

  from apps.institutes.api.v1 import views

  app_name = "institutes_admin"

  router = routers.SimpleRouter()
  router.register("institutes", views.AdminInstituteViewSet, basename="admin-institute")

  urlpatterns = [
      path("institutes/<int:institute_id>/documents/<int:pk>/", views.AdminDocumentView.as_view()),
      path("institutes/<int:institute_id>/documents/<int:pk>/download/", views.AdminDocumentDownloadView.as_view()),
  ] + router.urls
  ```

- [x] API tests (`apps/institutes/tests/test_api_public_admin.py`):
  - Registration: `201` creates institute, owner and locations; `status`, `role` and `slug` in the payload are ignored; a duplicate
    email in any case gives `400`; a province id as a location gives `400`; the 6th registration in an hour gives `429` (`cache.clear()` in `setUp`).
  - Public list: only `APPROVED` institutes appear; `SUSPENDED`, `PENDING`, `REJECTED` and `INFO_REQUESTED` do not.
  - Query count: the same number of queries with 1 and with 20 institutes:

    ```python
    from django.db import connection
    from django.test.utils import CaptureQueriesContext

    def queries_for_list(self):
        with CaptureQueriesContext(connection) as captured:
            self.assertEqual(self.client.get("/api/v1/institutes/").status_code, 200)
        return len(captured)

    # create 1 approved institute with a main location, record the count; create 19 more; the count is unchanged
    ```

  - Admin: anonymous gets `401`, staff `403`, an admin without `manage_institutes` `403`, with it `200`; each review action
    returns the new status; a missing reason gives `400`; an illegal move gives `400`.
  - Documents: the admin list shows no file path; the download returns the bytes; a staff user gets `403`.

- [ ] **M3 done when:** suite green (it is), and the public endpoints work from Swagger at `/api/root/`. The schema generates (HTTP 200, all 28 institute paths); trying the endpoints by hand in the Swagger UI is still to do.

## M4 – Portal API (the institute's own staff)

- [x] Permissions and queryset scoping. Other institutes' rows return `404`, not `403`:

  ```python
  # apps/institutes/permissions.py
  from rest_framework.permissions import BasePermission

  from apps.institutes.constants import MemberRole
  from apps.users.constants import Role


  class IsInstituteMember(BasePermission):
      def has_permission(self, request, view):
          user = request.user
          return bool(user and user.is_authenticated and user.role == Role.INSTITUTE_STAFF
                      and hasattr(user, "membership"))        # one query per request, then cached on the user


  class IsInstituteOwner(IsInstituteMember):
      def has_permission(self, request, view):
          return super().has_permission(request, view) and request.user.membership.role == MemberRole.OWNER


  class InstituteScopedMixin:
      """Limit the queryset to the caller's institute."""

      def get_queryset(self):
          queryset = super().get_queryset()
          if getattr(self, "swagger_fake_view", False):
              return queryset.none()
          return queryset.filter(institute_id=self.request.user.membership.institute_id)
  ```

- [x] Serializers for the portal:

  ```python
  # apps/institutes/api/v1/serializers.py (part 4)
  class InstituteProfileSerializer(DynamicFieldsModelSerializer):
      class Meta:
          model = Institute
          fields = ("id", "slug", "name", "type", "status", "status_reason", "established_year", "description",
                    "logo", "ceo_name", "ceo_message", "website", "contact_email", "contact_phone",
                    "facebook_url", "linkedin_url")
          read_only_fields = ("id", "slug", "status", "status_reason")


  class InstituteLocationSerializer(DynamicFieldsModelSerializer):
      location = serializers.PrimaryKeyRelatedField(
          queryset=Location.objects.filter(level=LocationLevel.MUNICIPALITY, is_active=True))
      municipality_name = serializers.CharField(source="location.name", read_only=True)
      district_name = serializers.CharField(source="location.district.name", read_only=True)
      province_name = serializers.CharField(source="location.province.name", read_only=True)

      class Meta:
          model = InstituteLocation
          fields = ("id", "location", "municipality_name", "district_name", "province_name", "address",
                    "contact_phone", "is_main", "is_active")
          read_only_fields = ("id", "is_main", "is_active")

      def create(self, validated_data):
          return services.add_location(self.request.user.membership.institute, **validated_data)

      def update(self, instance, validated_data):
          return services.update_location(instance, **validated_data)


  class InstituteDocumentSerializer(DynamicFieldsModelSerializer):
      class Meta:
          model = InstituteDocument
          fields = ("id", "name", "file", "status", "created_at")
          read_only_fields = ("id", "status", "created_at")
          extra_kwargs = {"file": {"write_only": True}}          # never echoed back

      def create(self, validated_data):
          return services.add_document(self.request.user.membership.institute, **validated_data)


  class GalleryImageSerializer(DynamicFieldsModelSerializer):
      class Meta:
          model = InstituteGalleryImage
          fields = ("id", "image", "caption", "position")
          read_only_fields = ("id", "position")

      def create(self, validated_data):
          return services.add_gallery_image(self.request.user.membership.institute, **validated_data)


  class GalleryReorderSerializer(serializers.Serializer):
      ids = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)


  class StaffSerializer(DynamicFieldsModelSerializer):
      email = serializers.EmailField(source="user.email", read_only=True)
      full_name = serializers.CharField(source="user.full_name", read_only=True)

      class Meta:
          model = InstituteMember
          fields = ("id", "email", "full_name", "role", "created_at")


  class InvitationSerializer(DynamicFieldsModelSerializer):
      class Meta:
          model = InstituteInvitation
          fields = ("id", "email", "role", "status", "expires_at", "created_at")
          read_only_fields = ("id", "role", "status", "expires_at", "created_at")      # the token is never returned

      def create(self, validated_data):
          return services.invite(institute=self.request.user.membership.institute,
                                 email=validated_data["email"], by=self.request.user)


  class AcceptInvitationSerializer(serializers.Serializer):
      token = serializers.CharField(write_only=True)
      full_name = serializers.CharField(max_length=150, write_only=True)
      password = serializers.CharField(write_only=True)

      def validate_password(self, value):
          validate_password(value)
          return value

      def create(self, validated_data):
          return services.accept_invitation(**validated_data)

      def to_representation(self, instance):
          return {"email": instance.email}
  ```

- [x] Portal views. Staff can do everything except staff and invitations (decision 2):

  ```python
  # apps/institutes/api/v1/views.py (part 5)
  class InstituteProfileView(RetrieveUpdateAPIView):
      serializer_class = InstituteProfileSerializer
      permission_classes = [IsInstituteMember]
      http_method_names = ["get", "patch", "head", "options"]

      def get_object(self):
          return self.request.user.membership.institute


  class ResubmitView(GenericAPIView):
      """Answer an info request, or re-apply after a rejection."""
      permission_classes = [IsInstituteMember]
      serializer_class = InstituteProfileSerializer

      def post(self, request):
          institute = services.resubmit(request.user.membership.institute)
          return Response(self.get_serializer(institute).data)


  class PortalLocationViewSet(InstituteScopedMixin, CreateListRetrieveUpdateViewSet):
      serializer_class = InstituteLocationSerializer
      permission_classes = [IsInstituteMember]
      lookup_value_regex = r"[0-9]+"
      http_method_names = ["get", "post", "patch", "head", "options"]
      queryset = (InstituteLocation.objects
                  .select_related("location", "location__district", "location__province")
                  .order_by("-is_main", "pk"))

      @action(detail=True, methods=["post"], url_path="set-main")
      def set_main(self, request, pk=None):
          return Response(self.get_serializer(services.set_main_location(self.get_object())).data)

      @action(detail=True, methods=["post"])
      def deactivate(self, request, pk=None):
          return Response(self.get_serializer(services.deactivate_location(self.get_object())).data)


  class PortalDocumentViewSet(InstituteScopedMixin, CreateListViewSet):
      serializer_class = InstituteDocumentSerializer
      permission_classes = [IsInstituteMember]
      queryset = InstituteDocument.objects.order_by("-created_at", "-pk")


  class PortalDocumentDownloadView(APIView):
      permission_classes = [IsInstituteMember]

      def get(self, request, pk):
          return private_file_response(get_object_or_404(
              InstituteDocument, pk=pk, institute_id=request.user.membership.institute_id))


  class PortalGalleryViewSet(InstituteScopedMixin, CreateListUpdateDestroyViewSet):
      serializer_class = GalleryImageSerializer
      permission_classes = [IsInstituteMember]
      lookup_value_regex = r"[0-9]+"
      http_method_names = ["get", "post", "patch", "delete", "head", "options"]
      queryset = InstituteGalleryImage.objects.order_by("position", "pk")

      @action(detail=False, methods=["post"])
      def reorder(self, request):
          serializer = GalleryReorderSerializer(data=request.data)
          serializer.is_valid(raise_exception=True)
          services.reorder_gallery(request.user.membership.institute, serializer.validated_data["ids"])
          return Response(self.get_serializer(self.get_queryset(), many=True).data)


  class PortalStaffViewSet(InstituteScopedMixin, ListViewSet, DestroyViewSet):
      serializer_class = StaffSerializer
      permission_classes = [IsInstituteOwner]
      lookup_value_regex = r"[0-9]+"
      queryset = InstituteMember.objects.select_related("user").order_by("role", "pk")

      def perform_destroy(self, instance):
          services.remove_staff(instance, by=self.request.user)


  class PortalInvitationViewSet(InstituteScopedMixin, CreateListDestroyViewSet):
      serializer_class = InvitationSerializer
      permission_classes = [IsInstituteOwner]
      lookup_value_regex = r"[0-9]+"
      queryset = InstituteInvitation.objects.order_by("-created_at", "-pk")

      def perform_destroy(self, instance):
          services.revoke_invitation(instance, by=self.request.user)


  class AcceptInvitationView(CreateAPIView):
      serializer_class = AcceptInvitationSerializer
      permission_classes = [AllowAny]
      authentication_classes = []
      throttle_scope = "invitation_accept"
  ```

  ```python
  # apps/institutes/api/v1/urls/portal.py
  from django.urls import path
  from rest_framework import routers

  from apps.institutes.api.v1 import views

  app_name = "institutes_portal"

  router = routers.SimpleRouter()
  router.register("locations", views.PortalLocationViewSet, basename="portal-location")
  router.register("documents", views.PortalDocumentViewSet, basename="portal-document")
  router.register("gallery", views.PortalGalleryViewSet, basename="portal-gallery")
  router.register("staff", views.PortalStaffViewSet, basename="portal-staff")
  router.register("invitations", views.PortalInvitationViewSet, basename="portal-invitation")

  urlpatterns = [
      path("register/", views.RegisterView.as_view(), name="register"),
      path("invitations/accept/", views.AcceptInvitationView.as_view(), name="invitation-accept"),
      path("profile/", views.InstituteProfileView.as_view(), name="profile"),
      path("resubmit/", views.ResubmitView.as_view(), name="resubmit"),
      path("documents/<int:pk>/download/", views.PortalDocumentDownloadView.as_view(), name="document-download"),
  ] + router.urls
  ```

  `invitations/accept/` and `register/` come before the router, and the routers use numeric ids, so `accept` is never read as an id.

- [x] Portal tests (`apps/institutes/tests/test_api_portal.py`):
  - Permission matrix for every endpoint: anonymous `401`; an admin `403`; staff of institute B gets `404` on institute A's rows;
    staff can use profile, locations, documents and gallery; only the owner can use `staff/` and `invitations/` (staff gets `403`).
  - Locations: the first becomes main; `set-main` moves it; deactivating the main one gives `400`; a province id gives `400`.
  - Documents: upload needs multipart; the response has no file path; a `.exe`, or a file over 5 MB, gives `400`; another institute's document download gives `404`.
  - Gallery: add, rename, delete, and reorder (a missing or extra id gives `400`).
  - Invitations: create returns no token; accepting works once and the new user can log in; a bad or expired token gives `400`;
    the 11th accept in an hour gives `429`; removing staff deactivates the user and revokes their tokens.
  - Resubmit: allowed from `REJECTED` and `INFO_REQUESTED`, refused from `APPROVED` and `PENDING`.
  - Query counts stay constant for the location, staff and invitation lists.

- [ ] **M4 done when:** (`EndToEndTests` runs this whole journey through the API and passes; a manual run is still to do) the whole flow works end to end by hand with `runserver` and `qcluster`: register, log in, upload a document, add a
  location, an admin approves, the institute appears at `/api/v1/institutes/`, the owner invites staff (the email shows in the console), the staff member accepts and logs in.

## M5 – Docs and wrap-up

- [x] `CLAUDE.md`: add `institutes` to Layout (and remove it from Planned apps); the endpoints; the settings
  (`PRIVATE_MEDIA_ROOT`, `INSTITUTE_*`, `FRONTEND_BASE_URL`); the throttle scopes; that invitation emails need `qcluster`; the landmines
  (documents are private and never get a URL; `BASE_DIR` is `config/`; the storage reads its setting on every use); the tests line.
- [x] `docs/System Design.md`: build step 3 done; record the answers to decisions 1 to 9 and delete them from the open questions;
  `registered_at` is `created_at`; documents are uploaded after registration; correct the "composite FK" wording for `Training`; the URL split.
- [x] `README.md`: the setup step for `private_media/` and `FRONTEND_BASE_URL`, and the new endpoint tables.
- [x] Notion review page: diagram 4b.2 (documents uploaded after registration, `InstituteGalleryImage`, no `registered_at`) and section 19.
- [x] Definition of done: `check` clean; `makemigrations --check --dry-run` clean; all tests pass; no hand-edited migrations; docs updated in the same change.

## Known limits and follow-ups (not in this list)

- No `AuditLog` and no `notifications` app yet: `# TODO(audit)` and `# TODO(notify)` markers sit where they will be called.
  Approval and rejection emails to the owner are part of that later work.
- No captcha on registration yet (the throttle is the only protection); reCAPTCHA comes with the shared abuse-protection work.
- Editing an `APPROVED` institute's profile is allowed without re-review. Whether it should need one is an open question, like Q10 for trainings.
- Upload checks look at the extension and size only.
- `Training` will point at `InstituteLocation`; "a training's location belongs to the same institute" must be checked in the training service (Django has no composite foreign keys).
