# Graph Report - traininghub-backend  (2026-11-03)

## Corpus Check
- 102 files · ~62,297 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 3)

## Summary
- 1918 nodes · 4347 edges · 130 communities (65 shown, 65 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 556 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `81f6b27a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- StatusApiTests
- .summary
- institutes/services.py
- training/services.py
- viewsets.py
- DynamicFieldsModelSerializer
- RegistrationApiTests
- RegistrationOtpApiTests
- AcceptInvitationSerializer
- TooManyRequests
- RegistrationTests
- TrainingSessionConstraintTests
- institutes/models.py
- LoginSerializer
- .as_
- training/models.py
- PublicTrainingTestCase
- Location
- settings/base.py
- .url
- .create
- common/validators.py
- enquiries/tests/test_services.py
- AdminTrainingSerializer
- AdminApiTests
- InstituteCEO
- PublicTrainingListSerializer
- EditTests
- LoadLocationsTests
- institutes/api/v1/serializers.py
- SubmitTests
- Enquiry
- DynamicFieldsSerializer
- PortalEnquiryNoteView
- AdminEnquiryTests
- Role
- fields.py
- SubmitTests
- ContactTests
- Training
- OtpApiTests
- ActionRequiredTests
- PortalEditTests
- EnquiryConstraintTests
- StaffTests
- users/services.py
- helpers.py
- InvitationTests
- models/base.py
- validate_phone_number
- AdminEnquiryViewSet
- send_otp
- TrainingFilter
- Open questions (section 8)
- Product Requirements Document (PRD)
- institutes/api/v1/views.py
- test_locations.py
- Entity: Institute
- TrainingConstraintTests
- Core entities (section 3)
- OTPPurpose
- PortalTestCase
- LocationTests
- UserConstraintTests
- change_status
- LocationApiTests
- DocumentTests
- InstituteRegistrationSerializer
- System Design (DRAFT v0.6)
- Entity: Training
- register
- InstituteConstraintTests
- UpdateStatusSerializer
- GalleryTests
- SocialLinkTests
- expire_trainings
- AdminCategoryApiTests
- ActiveAccountJWTAuthentication
- CategoryTreeView
- InstituteProfileSerializer
- NormalizedEmailSerializer
- AuthApiTests
- PrivateStorage
- Category
- PasswordChangeSerializer
- IdentityScopedRateThrottle
- Entity: Enquiry (planned)
- InstituteDocument
- Training status workflow: DRAFT, SUBMITTED, APPROVED, CHANGES_REQUESTED, REJECTED, UNPUBLISHED, CANCELLED, EXPIRED
- Dependency: Django 5.2.4
- Dependency: django-q2 1.8.0
- Dependency: django-redis 6.0.0
- Dependency: djangorestframework 3.16.0
- Dev extras: debug toolbar, django-extensions, ipdb, ipython, fabric3, pylint
- LocationModelTests
- AdminSerializer
- InstituteContact
- User
- CategoryConstraintTests
- CategoryServiceTests
- AdminApiTests
- ControlPanelRoutesTests
- AdminApiTests
- users/api/v1/views.py
- VisitorEnquirySerializer
- InstituteCoverSerializer
- signals.py
- submit_enquiry
- re
- SendOTPSerializer
- InstituteActionRequiredView
- ActionQueryCountTests
- Command
- InstituteExperienceTests
- InstituteGalleryImage
- PortalTestCase
- training/api/v1/serializers.py
- PortalTrainingListSerializer
- SummaryTests
- AdminEnquiryListSerializer
- annotate_institute_public_counts
- SeatRaceTests
- SummaryTests
- PermissionMatrixTests
- MeView
- LogoutView

## God Nodes (most connected - your core abstractions)
1. `Training` - 70 edges
2. `Institute` - 57 edges
3. `RegistrationApiTests` - 49 edges
4. `Enquiry` - 45 edges
5. `Role` - 45 edges
6. `InstituteStatus` - 44 edges
7. `DynamicFieldsModelSerializer` - 37 edges
8. `TrainingStatus` - 35 edges
9. `BaseModel` - 30 edges
10. `Category` - 29 edges

## Surprising Connections (you probably didn't know these)
- `Decision: PAN/VAT number unique, nine digits, contact telephone optional` --references--> `validate_pan_vat_number()`  [EXTRACTED]
  docs/System Design.md → apps/common/validators.py
- `2.1 Data (`apps/enquiries/models.py`)` --references--> `Enquiry`  [INFERRED]
  docs/enquiries-status.md → apps/enquiries/models.py
- `2.1 Data (`apps/enquiries/models.py`)` --references--> `EnquiryNote`  [INFERRED]
  docs/enquiries-status.md → apps/enquiries/models.py
- `2.2 Rules (`apps/enquiries/services.py`)` --references--> `change_status()`  [INFERRED]
  docs/enquiries-status.md → apps/enquiries/services.py
- `4.3 Backend work not done` --references--> `change_status()`  [INFERRED]
  docs/enquiries-status.md → apps/enquiries/services.py

## Import Cycles
- None detected.

## Communities (130 total, 65 thin omitted)

### Community 2 - "institutes/services.py"
Cohesion: 0.12
Nodes (29): InstituteStatus, Institute, Meta, InstituteLocation, Meta, InstituteSocialLink, Meta, add_social_link() (+21 more)

### Community 3 - "training/services.py"
Cohesion: 0.14
Nodes (27): TrainingMode, TrainingStatus, approve(), _build_search_vector(), cancel(), _check_category(), _check_dates(), _check_sessions() (+19 more)

### Community 4 - "viewsets.py"
Cohesion: 0.08
Nodes (24): BaseViewSet, CreateListDestroyViewSet, CreateListRetrieveUpdateViewSet, CreateListUpdateDestroyViewSet, CreateListUpdateViewSet, CreateListViewSet, CreateRetrieveUpdateViewSet, CreateRetrieveViewSet (+16 more)

### Community 5 - "DynamicFieldsModelSerializer"
Cohesion: 0.09
Nodes (13): DynamicFieldsModelSerializer, AdminDocumentSerializer, Meta, AdminInstituteSerializer, Meta, InstituteCEOSerializer, Meta, InstituteContactSerializer (+5 more)

### Community 8 - "AcceptInvitationSerializer"
Cohesion: 0.29
Nodes (3): AcceptInvitationSerializer, AcceptInvitationView, RegisterView

### Community 9 - "TooManyRequests"
Cohesion: 0.25
Nodes (3): TooManyRequests, _claim_phone_slot(), api_exception_handler()

### Community 10 - "RegistrationTests"
Cohesion: 0.07
Nodes (4): InvitationTests, LocationTests, RegistrationOtpServiceTests, RegistrationTests

### Community 12 - "institutes/models.py"
Cohesion: 0.13
Nodes (17): InvitationSerializer, Meta, DocumentStatus, InstituteType, InvitationStatus, MemberRole, InstituteInvitation, Meta (+9 more)

### Community 15 - "training/models.py"
Cohesion: 0.12
Nodes (12): BaseModel, Meta, DurationUnit, TrainingLevel, TrainingShift, WeekDay, TrainingContact, TrainingDetail (+4 more)

### Community 16 - "PublicTrainingTestCase"
Cohesion: 0.12
Nodes (7): DetailTests, FilterTests, PublicTrainingTestCase, SearchTests, ShiftsAreShownTests, titles(), VisibilityTests

### Community 17 - "Location"
Cohesion: 0.22
Nodes (7): LocationFilter, Meta, LocationSerializer, Meta, LocationViewSet, Location, Meta

### Community 20 - ".url"
Cohesion: 0.07
Nodes (7): AccessTests, DetailTests, ListTests, NoteTests, PortalTestCase, StatusChangeTests, SummaryTests

### Community 22 - "common/validators.py"
Cohesion: 0.16
Nodes (9): combine_date_parts(), get_today(), validate_attachment(), validate_coded_phone_number(), validate_dob(), validate_future_datetime(), validate_is_future_datetime(), validate_otp() (+1 more)

### Community 23 - "enquiries/tests/test_services.py"
Cohesion: 0.24
Nodes (6): EnquiryStatus, EnquiryType, PreferredTime, EnquiryNote, Meta, add_note()

### Community 24 - "AdminTrainingSerializer"
Cohesion: 0.08
Nodes (10): AdminTrainingSerializer, Meta, PortalTrainingSerializer, Meta, TrainingContentFields, PortalTrainingViewSet, transition(), run() (+2 more)

### Community 25 - "AdminApiTests"
Cohesion: 0.06
Nodes (4): add_location(), AdminApiTests, PublicInstituteApiTests, WorkflowTests

### Community 26 - "InstituteCEO"
Cohesion: 0.22
Nodes (4): PortalCEOView, InstituteCEO, annotate_profile_completion(), _at_least()

### Community 27 - "PublicTrainingListSerializer"
Cohesion: 0.09
Nodes (8): duration_text(), format_class_days(), PublicTrainingDetailSerializer, Meta, PublicTrainingListSerializer, Meta, PublicTrainingViewSet, annotate_institute_training_count()

### Community 28 - "EditTests"
Cohesion: 0.06
Nodes (7): CreateTests, EditTests, ExpiryTests, ReviewTests, SubmitTests, TrainingTestCase, TransitionTableTests

### Community 29 - "LoadLocationsTests"
Cohesion: 0.29
Nodes (3): level_counts(), load(), LoadLocationsTests

### Community 30 - "institutes/api/v1/serializers.py"
Cohesion: 0.13
Nodes (5): active_municipalities(), OTPField, ProfileSerializer, Meta, UserRegistrationSerializer

### Community 31 - "SubmitTests"
Cohesion: 0.14
Nodes (4): NoVisitorIdentityTests, PublicTestCase, SubmitTests, ThrottleTests

### Community 32 - "Enquiry"
Cohesion: 0.11
Nodes (10): PortalEnquiryFilter, Meta, EnquiryCreateSerializer, Meta, PortalEnquiryListSerializer, Meta, EnquiryCreateView, PortalEnquiryViewSet (+2 more)

### Community 34 - "PortalEnquiryNoteView"
Cohesion: 0.22
Nodes (6): PortalEnquiryNoteView, 4.1 Before it works end to end, 4.2 Frontend changes against the prototype, 4.4 Risks and limits to know about, 4.5 Questions still open (numbers as in `docs/System Design.md`, section 8), 4. What needs changes

### Community 37 - "fields.py"
Cohesion: 0.07
Nodes (4): DistributedKeyAuthentication, DistributedAppKey, Base64FieldMixin, Base64ImageField

### Community 38 - "SubmitTests"
Cohesion: 0.11
Nodes (5): ChangeStatusTests, NoteTests, ServiceTestCase, submit(), SubmitTests

### Community 40 - "Training"
Cohesion: 0.13
Nodes (12): build_category_tree(), DeleteTrainingTests, Training, Meta, annotate_category_training_count(), delete_training(), refresh_search_vectors(), refresh_category_trainings() (+4 more)

### Community 42 - "ActionRequiredTests"
Cohesion: 0.07
Nodes (4): ActionRequiredTests, CoverTests, DocumentAndGalleryTests, CoverTests

### Community 46 - "users/services.py"
Cohesion: 0.16
Nodes (6): change_password(), create_admin(), _revoke_refresh_tokens(), _set_permissions(), set_status(), update_admin()

### Community 47 - "helpers.py"
Cohesion: 0.09
Nodes (12): _duration(), get_upload_path(), get_uuid_filename(), institute_experience(), membership_duration(), nested_getattr(), set_instance_fields(), update_instance() (+4 more)

### Community 49 - "models/base.py"
Cohesion: 0.21
Nodes (4): SlugModel, Meta, _slug_strip(), unique_slugify()

### Community 50 - "validate_phone_number"
Cohesion: 0.29
Nodes (4): ValidatePanVatNumberTests, ValidatePhoneNumberTests, validate_pan_vat_number(), validate_phone_number()

### Community 51 - "AdminEnquiryViewSet"
Cohesion: 0.20
Nodes (4): AdminEnquiryFilter, Meta, AdminEnquiryViewSet, counts()

### Community 52 - "send_otp"
Cohesion: 0.24
Nodes (4): normalize_email(), _otp_keys(), send_otp(), send_registration_otp()

### Community 53 - "TrainingFilter"
Cohesion: 0.22
Nodes (3): prefix_query(), TrainingFilter, Meta

### Community 54 - "Open questions (section 8)"
Cohesion: 0.22
Nodes (10): Entity: InstituteMember (one institute per user), Auth: email + password, JWT RS256 via simplejwt, Open questions (section 8), Open question: how an admin's password is reset, Open question: endpoint that consumes a verified password-reset code, Open question: where the frontend stores access/refresh tokens, Roles and grantable Django permissions (users.manage_*), Entity: User (+2 more)

### Community 55 - "Product Requirements Document (PRD)"
Cohesion: 0.25
Nodes (10): Phase 2: Application (approve/reject/capacity) and learners, My enquiries: browser device token, last 90 days, Open question: do institutes keep enquiries after 90 days, Reviews and ratings out of MVP, Workflow: enquiry (planned), Product Requirements Document (PRD), PRD training enquiry rules (captcha, rate limit, 90-day My enquiries), PRD later phase: applications, reviews and ratings (+2 more)

### Community 56 - "institutes/api/v1/views.py"
Cohesion: 0.08
Nodes (17): AdminDocumentDownloadView, GalleryReorderSerializer, StaffSerializer, Meta, InstituteProfileView, PortalContactView, PortalDocumentDownloadView, PortalDocumentViewSet (+9 more)

### Community 58 - "Entity: Institute"
Cohesion: 0.38
Nodes (7): Entity: Institute, Entity: InstituteCEO, Entity: InstituteContact, Entity: InstituteGalleryImage, Institute profile split: columns plus contact, CEO, social-link tables, Entity: InstituteSocialLink, Institute types: fixed list of seven

### Community 60 - "Core entities (section 3)"
Cohesion: 0.38
Nodes (6): Core entities (section 3), Entity: InstituteLocation (office), Entity: Location, Managed Nepal location list (province / district / municipality), Entity: TrainingLocation (venue), PRD institute locations (several, one main office)

### Community 61 - "OTPPurpose"
Cohesion: 0.33
Nodes (6): OTPPurpose, send_otp_email(), send_registration_otp_email(), _deliver_otp(), send_otp_email_task(), send_registration_otp_email_task()

### Community 62 - "PortalTestCase"
Cohesion: 0.15
Nodes (5): LifecycleTests, PortalPermissionTests, PortalTestCase, QueryCountTests, SubmitNeedsShiftsTests

### Community 65 - "change_status"
Cohesion: 0.15
Nodes (6): EnquiryNoteSerializer, Meta, PortalEnquirySerializer, Meta, change_status(), 4.3 Backend work not done

### Community 68 - "InstituteRegistrationSerializer"
Cohesion: 0.20
Nodes (4): LocationInputSerializer, InstituteRegistrationSerializer, Meta, VenueSerializer

### Community 69 - "System Design (DRAFT v0.6)"
Cohesion: 0.17
Nodes (7): System Design (DRAFT v0.6), Django apps and their state (section 2), Proposed: AuditLog (append-only), not built, Decision log (answered questions), Decisions made (section 1), Non-functional requirements (section 6), Training mode: PHYSICAL or ONLINE

### Community 70 - "Entity: Training"
Cohesion: 0.17
Nodes (12): Categories: two-level tree with icon and hue, training uses a leaf, Entity: Category, Entity: LearningOutcome, Entity: Training, Entity: TrainingContact, Entity: TrainingDetail, Training duration (value + unit, derived weeks) and weekly class slots, Entity: TrainingModule (+4 more)

### Community 71 - "register"
Cohesion: 0.18
Nodes (10): register(), consume_otp(), Entity: InstituteDocument, Entity: InstituteInvitation, Institute registration: one JSON request creates institute, owner, contact, locations, Institute status workflow: PENDING, APPROVED, REJECTED, INFO_REQUESTED, SUSPENDED, One-time codes (OTP): six digits, 5 minutes, Redis only, Staff invitations: 7-day token, hash stored, email queued after commit (+2 more)

### Community 76 - "expire_trainings"
Cohesion: 0.22
Nodes (3): Command, expire_trainings(), expire_trainings()

### Community 80 - "CategoryTreeView"
Cohesion: 0.25
Nodes (3): build_tree(), CategoryTreeView, LocationTreeView

### Community 81 - "InstituteProfileSerializer"
Cohesion: 0.20
Nodes (4): InstituteProfileSerializer, Meta, ResubmitView, update_profile()

### Community 82 - "NormalizedEmailSerializer"
Cohesion: 0.12
Nodes (6): NormalizedEmailSerializer, RegistrationOTPSerializer, RegistrationOTPVerifySerializer, VerifyOTPSerializer, verify_otp(), verify_registration_otp()

### Community 85 - "Category"
Cohesion: 0.09
Nodes (13): Command, Category, Meta, _check_parent(), create_category(), update_category(), AdminCategoryFilter, Meta (+5 more)

### Community 87 - "IdentityScopedRateThrottle"
Cohesion: 0.15
Nodes (6): IdentityScopedRateThrottle, ActionAPIView, RegisterSendOTPView, RegisterVerifyOTPView, SendOTPView, VerifyOTPView

### Community 88 - "Entity: Enquiry (planned)"
Cohesion: 0.40
Nodes (5): Availability: seats minus CONVERTED enquiries above zero, Entity: Enquiry (planned), Open question: PRD 'Instructor Name' search has no field, Search: PostgreSQL full-text, simple config, word-prefix match, PRD search and discovery filters

### Community 89 - "InstituteDocument"
Cohesion: 0.15
Nodes (8): DocumentReviewSerializer, AdminDocumentView, InstituteDocumentSerializer, Meta, InstituteDocument, Meta, add_document(), reupload_document()

### Community 90 - "Training status workflow: DRAFT, SUBMITTED, APPROVED, CHANGES_REQUESTED, REJECTED, UNPUBLISHED, CANCELLED, EXPIRED"
Cohesion: 0.50
Nodes (3): Training expiry: daily expire_trainings job sets EXPIRED after end_date, Training status workflow: DRAFT, SUBMITTED, APPROVED, CHANGES_REQUESTED, REJECTED, UNPUBLISHED, CANCELLED, EXPIRED, Workflow: training lifecycle

### Community 99 - "InstituteContact"
Cohesion: 0.21
Nodes (3): InstituteContact, add_contact(), InstituteAdminSiteTests

### Community 106 - "users/api/v1/views.py"
Cohesion: 0.19
Nodes (5): RefreshView, UserStatusView, HasPlatformPermission, IsInstituteStaff, IsPlatformAdmin

### Community 107 - "VisitorEnquirySerializer"
Cohesion: 0.33
Nodes (3): VisitorEnquirySerializer, Meta, VisitorViewTests

### Community 109 - "InstituteCoverSerializer"
Cohesion: 0.20
Nodes (4): InstituteCoverSerializer, Meta, PortalCoverView, set_cover_img()

### Community 111 - "submit_enquiry"
Cohesion: 0.09
Nodes (15): _is_open_duplicate(), _require_accepting(), _require_open_for_enquiry(), submit_enquiry(), registration_open_q(), 1. In short, 2.1 Data (`apps/enquiries/models.py`), 2.2 Rules (`apps/enquiries/services.py`) (+7 more)

### Community 118 - "InstituteGalleryImage"
Cohesion: 0.25
Nodes (6): GalleryImageSerializer, Meta, PublicInstituteViewSet, InstituteGalleryImage, Meta, add_gallery_image()

### Community 119 - "PortalTestCase"
Cohesion: 0.25
Nodes (3): EndToEndTests, PortalTestCase, ResubmitTests

### Community 120 - "training/api/v1/serializers.py"
Cohesion: 0.15
Nodes (14): validate_document_file(), validate_image_file(), _validate_upload(), available_categories(), LearningOutcomeSerializer, Meta, TrainingModuleSerializer, Meta (+6 more)

### Community 121 - "PortalTrainingListSerializer"
Cohesion: 0.40
Nodes (4): AdminTrainingListSerializer, Meta, PortalTrainingListSerializer, Meta

## Ambiguous Edges - Review These
- `PRD training modes: Physical, Online, Hybrid` → `Decision: hybrid mode dropped (2026-10-13)`  [AMBIGUOUS]
  docs/Training for Merojob (PRD).md · relation: conceptually_related_to
- `PRD institute locations (several, one main office)` → `Training venue: exactly one TrainingLocation, independent of institute offices`  [AMBIGUOUS]
  docs/Training for Merojob (PRD).md · relation: conceptually_related_to

## Knowledge Gaps
- **21 isolated node(s):** `Dependency: djangorestframework-simplejwt 5.5.1 (with PyJWT crypto)`, `Entity: InstituteGalleryImage`, `Institute types: fixed list of seven`, `Managed Nepal location list (province / district / municipality)`, `Django apps and their state (section 2)` (+16 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 647 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **65 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Training` connect `Training` to `institutes/services.py`, `training/services.py`, `viewsets.py`, `TrainingSessionConstraintTests`, `training/models.py`, `PublicTrainingTestCase`, `.create`, `enquiries/tests/test_services.py`, `AdminTrainingSerializer`, `PublicTrainingListSerializer`, `EditTests`, `institutes/api/v1/serializers.py`, `Enquiry`, `SubmitTests`, `PortalEditTests`, `models/base.py`, `TrainingFilter`, `institutes/api/v1/views.py`, `TrainingConstraintTests`, `change_status`, `expire_trainings`, `Category`, `submit_enquiry`, `training/api/v1/serializers.py`, `PortalTrainingListSerializer`, `annotate_institute_public_counts`?**
  _High betweenness centrality (0.104) - this node is a cross-community bridge._
- **Are the 47 inferred relationships involving `Training` (e.g. with `AdminTrainingFilter` and `AdminTrainingSerializer`) actually correct?**
  _`Training` has 47 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Dependency: djangorestframework-simplejwt 5.5.1 (with PyJWT crypto)`, `Entity: InstituteGalleryImage`, `Institute types: fixed list of seven` to the rest of the system?**
  _21 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `institutes/services.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11923076923076924 - nodes in this community are weakly interconnected._
- **Why does `Institute` connect `institutes/services.py` to `training/services.py`, `viewsets.py`, `DynamicFieldsModelSerializer`, `RegistrationApiTests`, `RegistrationTests`, `institutes/models.py`, `.as_`, `training/models.py`, `enquiries/tests/test_services.py`, `AdminApiTests`, `institutes/api/v1/serializers.py`, `SubmitTests`, `Enquiry`, `SubmitTests`, `Training`, `ActionRequiredTests`, `helpers.py`, `models/base.py`, `institutes/api/v1/views.py`, `InstituteRegistrationSerializer`, `institutes/tests/test_api_portal.py`, `InstituteProfileSerializer`, `InstituteDocument`, `InstituteCoverSerializer`, `InstituteActionRequiredView`, `InstituteGalleryImage`, `PortalTestCase`?**
  _High betweenness centrality (0.092) - this node is a cross-community bridge._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `PRD training modes: Physical, Online, Hybrid` and `Decision: hybrid mode dropped (2026-10-13)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `PRD institute locations (several, one main office)` and `Training venue: exactly one TrainingLocation, independent of institute offices`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._