# Graph Report - traininghub-backend  (2026-10-28)

## Corpus Check
- 101 files · ~60,702 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 3)

## Summary
- 1858 nodes · 4217 edges · 100 communities (58 shown, 42 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 533 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9c09c4d1`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- update_admin
- PortalEnquiryViewSet
- institutes/services.py
- training/services.py
- viewsets.py
- institutes/api/v1/serializers.py
- RegistrationApiTests
- RegistrationTests
- institutes/api/v1/views.py
- BaseModel
- InvitationTests
- Location
- institutes/models.py
- users/api/v1/views.py
- .as_
- Training
- FilterTests
- common/api/v1/views.py
- settings/base.py
- .url
- .create
- common/validators.py
- Enquiry
- AdminTrainingSerializer
- AdminApiTests
- InstituteCEO
- PublicTrainingListSerializer
- EditTests
- LoadLocationsTests
- PublicInstituteApiTests
- .post
- enquiries/api/v1/views.py
- TrainingModule
- PortalEnquiryNoteView
- v1/permissions.py
- User
- fields.py
- SubmitTests
- ContactTests
- delete_training
- OtpApiTests
- ActionRequiredTests
- load_locations.py
- EnquiryConstraintTests
- PortalTestCase
- register
- Institute
- InvitationTests
- validate_phone_number
- WorkflowTests
- InstituteDocument
- 4. What needs changes
- TrainingFilter
- Open questions (section 8)
- Product Requirements Document (PRD)
- Base64FieldMixin
- Entity: Institute
- TrainingConstraintTests
- Core entities (section 3)
- EnquiryRelationTests
- add_location
- LocationTests
- UserConstraintTests
- EnquiryNote
- LocationApiTests
- DocumentTests
- LocationInputSerializer
- System Design (DRAFT v0.6)
- Entity: Training
- Workflow: institute onboarding
- InstituteConstraintTests
- set_status
- GalleryTests
- SocialLinkTests
- expire_trainings
- institutes/validators.py
- ActiveAccountJWTAuthentication
- signals.py
- Command
- ControlPanelRoutesTests
- AuthApiTests
- PrivateStorage
- enquiries/api/v1/serializers.py
- PasswordChangeSerializer
- Entity: Enquiry (planned)
- LocationModelTests
- Training status workflow: DRAFT, SUBMITTED, APPROVED, CHANGES_REQUESTED, REJECTED, UNPUBLISHED, CANCELLED, EXPIRED
- Dependency: Django 5.2.4
- Dependency: django-q2 1.8.0
- Dependency: django-redis 6.0.0
- Dependency: djangorestframework 3.16.0
- Dev extras: debug toolbar, django-extensions, ipdb, ipython, fabric3, pylint
- AdminSerializer
- InstituteAdminSiteTests
- test_categories.py
- create_admin
- VisitorEnquirySerializer

## God Nodes (most connected - your core abstractions)
1. `Training` - 67 edges
2. `Institute` - 55 edges
3. `RegistrationApiTests` - 49 edges
4. `Role` - 44 edges
5. `Enquiry` - 43 edges
6. `InstituteStatus` - 43 edges
7. `DynamicFieldsModelSerializer` - 35 edges
8. `TrainingStatus` - 32 edges
9. `BaseModel` - 30 edges
10. `ActionRequiredTests` - 29 edges

## Surprising Connections (you probably didn't know these)
- `4.3 Backend work not done` --references--> `change_status()`  [INFERRED]
  docs/enquiries-status.md → apps/enquiries/services.py
- `Decision: PAN/VAT number unique, nine digits, contact telephone optional` --references--> `validate_pan_vat_number()`  [EXTRACTED]
  docs/System Design.md → apps/common/validators.py
- `2.1 Data (`apps/enquiries/models.py`)` --references--> `Enquiry`  [INFERRED]
  docs/enquiries-status.md → apps/enquiries/models.py
- `2.1 Data (`apps/enquiries/models.py`)` --references--> `EnquiryNote`  [INFERRED]
  docs/enquiries-status.md → apps/enquiries/models.py
- `2.2 Rules (`apps/enquiries/services.py`)` --references--> `submit_enquiry()`  [INFERRED]
  docs/enquiries-status.md → apps/enquiries/services.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Institute onboarding: OTP, register, upload documents, admin review** — docs_system_design_one_time_codes, docs_system_design_institute_registration, docs_system_design_verification_documents, docs_system_design_institute_status_workflow [EXTRACTED 1.00]
- **Training lifecycle: draft, review, edit-back-to-review, daily expiry** — docs_system_design_training_statuses, docs_system_design_editing_training, docs_system_design_training_expiry [EXTRACTED 1.00]

## Communities (100 total, 42 thin omitted)

### Community 0 - "update_admin"
Cohesion: 0.31
Nodes (3): _set_permissions(), update_admin(), StatusApiTests

### Community 1 - "PortalEnquiryViewSet"
Cohesion: 0.15
Nodes (5): PortalEnquiryFilter, Meta, PortalEnquiryListSerializer, Meta, PortalEnquiryViewSet

### Community 2 - "institutes/services.py"
Cohesion: 0.09
Nodes (30): InstituteLocationSerializer, Meta, PortalLocationViewSet, InstituteStatus, InstituteLocation, Meta, InstituteSocialLink, Meta (+22 more)

### Community 3 - "training/services.py"
Cohesion: 0.11
Nodes (32): TrainingMode, TrainingStatus, LearningOutcome, Meta, TrainingContact, TrainingLocation, approve(), _build_search_vector() (+24 more)

### Community 4 - "viewsets.py"
Cohesion: 0.09
Nodes (24): BaseViewSet, CreateListDestroyViewSet, CreateListRetrieveUpdateViewSet, CreateListUpdateDestroyViewSet, CreateListUpdateViewSet, CreateListViewSet, CreateRetrieveUpdateViewSet, CreateRetrieveViewSet (+16 more)

### Community 5 - "institutes/api/v1/serializers.py"
Cohesion: 0.06
Nodes (21): DynamicFieldsModelSerializer, AdminDocumentSerializer, Meta, AdminInstituteSerializer, Meta, InstituteCEOSerializer, Meta, InstituteContactSerializer (+13 more)

### Community 6 - "RegistrationApiTests"
Cohesion: 0.09
Nodes (3): SeatRaceTests, convert(), RegistrationApiTests

### Community 7 - "RegistrationTests"
Cohesion: 0.07
Nodes (9): RegistrationOtpApiTests, RegistrationTests, get_otp(), send_otp_email(), send_password_reset_otp(), send_registration_otp_email(), _deliver_otp(), send_otp_email_task() (+1 more)

### Community 8 - "institutes/api/v1/views.py"
Cohesion: 0.06
Nodes (18): AdminTrainingListSerializer, Meta, AdminDocumentDownloadView, AcceptInvitationSerializer, InstituteActionRequiredSerializer, AcceptInvitationView, InstituteActionRequiredView, InstituteProfileView (+10 more)

### Community 9 - "BaseModel"
Cohesion: 0.14
Nodes (12): BaseModel, Meta, Category, Meta, _check_parent(), create_category(), update_category(), AdminCategoryFilter (+4 more)

### Community 10 - "InvitationTests"
Cohesion: 0.07
Nodes (5): send_invitation_email(), InvitationTests, LocationTests, RegistrationOtpServiceTests, RemoveStaffTests

### Community 11 - "Location"
Cohesion: 0.36
Nodes (5): active_municipalities(), LocationLevel, MunicipalityType, Location, Meta

### Community 12 - "institutes/models.py"
Cohesion: 0.12
Nodes (14): InstituteType, InvitationStatus, MemberRole, InstituteContact, InstituteInvitation, Meta, InstituteMember, Meta (+6 more)

### Community 13 - "users/api/v1/views.py"
Cohesion: 0.05
Nodes (18): IdentityScopedRateThrottle, ActionAPIView, AdminViewSet, RegisterSendOTPView, RegisterVerifyOTPView, LoginSerializer, UpdateStatusSerializer, Meta (+10 more)

### Community 14 - ".as_"
Cohesion: 0.12
Nodes (3): CEOTests, ProfileTests, StaffTests

### Community 15 - "Training"
Cohesion: 0.09
Nodes (23): CoverSerializer, LearningOutcomeSerializer, Meta, PortalTrainingListSerializer, Meta, TrainingSessionSerializer, Meta, DurationUnit (+15 more)

### Community 16 - "FilterTests"
Cohesion: 0.15
Nodes (4): FilterTests, SearchTests, titles(), VisibilityTests

### Community 17 - "common/api/v1/views.py"
Cohesion: 0.14
Nodes (9): LocationFilter, Meta, LocationSerializer, Meta, build_category_tree(), build_tree(), CategoryTreeView, LocationTreeView (+1 more)

### Community 20 - ".url"
Cohesion: 0.07
Nodes (7): AccessTests, DetailTests, ListTests, NoteTests, PortalTestCase, StatusChangeTests, SummaryTests

### Community 21 - ".create"
Cohesion: 0.05
Nodes (10): ActionQueryCountTests, AdminApiTests, LifecycleTests, PortalCreateTests, PortalEditTests, PortalPermissionTests, PortalTestCase, QueryCountTests (+2 more)

### Community 22 - "common/validators.py"
Cohesion: 0.16
Nodes (9): combine_date_parts(), get_today(), validate_attachment(), validate_coded_phone_number(), validate_dob(), validate_future_datetime(), validate_is_future_datetime(), validate_otp() (+1 more)

### Community 23 - "Enquiry"
Cohesion: 0.06
Nodes (20): TooManyRequests, get_upload_path(), get_uuid_filename(), nested_getattr(), set_instance_fields(), update_instance(), EnquiryStatus, EnquiryType (+12 more)

### Community 24 - "AdminTrainingSerializer"
Cohesion: 0.05
Nodes (13): DynamicFieldsSerializer, AdminTrainingSerializer, Meta, ReasonSerializer, AdminInstituteViewSet, AdminTrainingViewSet, PortalTrainingSerializer, Meta (+5 more)

### Community 26 - "InstituteCEO"
Cohesion: 0.13
Nodes (12): GalleryImageSerializer, Meta, GalleryReorderSerializer, PortalCEOView, PortalGalleryViewSet, InstituteCEO, InstituteGalleryImage, Meta (+4 more)

### Community 27 - "PublicTrainingListSerializer"
Cohesion: 0.10
Nodes (7): duration_text(), format_class_days(), PublicTrainingDetailSerializer, Meta, PublicTrainingListSerializer, Meta, PublicTrainingViewSet

### Community 28 - "EditTests"
Cohesion: 0.06
Nodes (7): CreateTests, EditTests, ExpiryTests, ReviewTests, SubmitTests, TrainingTestCase, TransitionTableTests

### Community 29 - "LoadLocationsTests"
Cohesion: 0.29
Nodes (3): level_counts(), load(), LoadLocationsTests

### Community 31 - ".post"
Cohesion: 0.11
Nodes (5): DeviceTokenTests, MyEnquiriesTests, PublicTestCase, SubmitTests, ThrottleTests

### Community 32 - "enquiries/api/v1/views.py"
Cohesion: 0.16
Nodes (4): device_token_from(), EnquiryCreateSerializer, Meta, EnquiryCreateView

### Community 33 - "TrainingModule"
Cohesion: 0.40
Nodes (4): TrainingModuleSerializer, Meta, TrainingModule, Meta

### Community 34 - "PortalEnquiryNoteView"
Cohesion: 0.22
Nodes (6): PortalEnquiryNoteView, 2.1 Data (`apps/enquiries/models.py`), 2.2 Rules (`apps/enquiries/services.py`), 2.3 API (all under `/api/v1/`), 2.5 Tests (`apps/enquiries/tests/`), 2. What was built

### Community 36 - "User"
Cohesion: 0.16
Nodes (3): UserManager, User, Meta

### Community 38 - "SubmitTests"
Cohesion: 0.09
Nodes (6): ChangeStatusTests, NoteTests, ServiceTestCase, submit(), SubmitTests, SummaryTests

### Community 40 - "delete_training"
Cohesion: 0.25
Nodes (4): DeleteTrainingTests, delete_training(), registration_open_q(), 2.4 Changes outside the new app

### Community 42 - "ActionRequiredTests"
Cohesion: 0.09
Nodes (3): ActionRequiredTests, DocumentAndGalleryTests, CoverTests

### Community 45 - "PortalTestCase"
Cohesion: 0.15
Nodes (4): EndToEndTests, PermissionMatrixTests, PortalTestCase, ResubmitTests

### Community 46 - "register"
Cohesion: 0.07
Nodes (13): register(), NormalizedEmailSerializer, RegistrationOTPSerializer, RegistrationOTPVerifySerializer, SendOTPSerializer, VerifyOTPSerializer, consume_otp(), normalize_email() (+5 more)

### Community 47 - "Institute"
Cohesion: 0.09
Nodes (11): InstituteProfileSerializer, Meta, PublicInstituteDetailSerializer, Meta, PublicInstituteListSerializer, Meta, PublicInstituteViewSet, ResubmitView (+3 more)

### Community 49 - "validate_phone_number"
Cohesion: 0.29
Nodes (4): ValidatePanVatNumberTests, ValidatePhoneNumberTests, validate_pan_vat_number(), validate_phone_number()

### Community 51 - "InstituteDocument"
Cohesion: 0.13
Nodes (10): DocumentReviewSerializer, AdminDocumentView, InstituteDocumentSerializer, Meta, DocumentStatus, InstituteDocument, Meta, add_document() (+2 more)

### Community 52 - "4. What needs changes"
Cohesion: 0.18
Nodes (10): 1. In short, 3. Where the build differs from the prototype, 4.1 Before it works end to end, 4.2 Frontend changes against the prototype, 4.3 Backend work not done, 4.4 Risks and limits to know about, 4.5 Questions still open (numbers as in `docs/System Design.md`, section 8), 4. What needs changes (+2 more)

### Community 53 - "TrainingFilter"
Cohesion: 0.16
Nodes (5): prefix_query(), TrainingFilter, Meta, found(), SearchVectorTests

### Community 54 - "Open questions (section 8)"
Cohesion: 0.22
Nodes (10): Entity: InstituteMember (one institute per user), Auth: email + password, JWT RS256 via simplejwt, Open questions (section 8), Open question: how an admin's password is reset, Open question: endpoint that consumes a verified password-reset code, Open question: where the frontend stores access/refresh tokens, Roles and grantable Django permissions (users.manage_*), Entity: User (+2 more)

### Community 55 - "Product Requirements Document (PRD)"
Cohesion: 0.25
Nodes (10): Phase 2: Application (approve/reject/capacity) and learners, My enquiries: browser device token, last 90 days, Open question: do institutes keep enquiries after 90 days, Reviews and ratings out of MVP, Workflow: enquiry (planned), Product Requirements Document (PRD), PRD training enquiry rules (captcha, rate limit, 90-day My enquiries), PRD later phase: applications, reviews and ratings (+2 more)

### Community 58 - "Entity: Institute"
Cohesion: 0.38
Nodes (7): Entity: Institute, Entity: InstituteCEO, Entity: InstituteContact, Entity: InstituteGalleryImage, Institute profile split: columns plus contact, CEO, social-link tables, Entity: InstituteSocialLink, Institute types: fixed list of seven

### Community 60 - "Core entities (section 3)"
Cohesion: 0.38
Nodes (6): Core entities (section 3), Entity: InstituteLocation (office), Entity: Location, Managed Nepal location list (province / district / municipality), Entity: TrainingLocation (venue), PRD institute locations (several, one main office)

### Community 65 - "EnquiryNote"
Cohesion: 0.18
Nodes (7): EnquiryNoteSerializer, Meta, PortalEnquirySerializer, Meta, EnquiryNote, Meta, add_note()

### Community 69 - "System Design (DRAFT v0.6)"
Cohesion: 0.17
Nodes (7): System Design (DRAFT v0.6), Django apps and their state (section 2), Proposed: AuditLog (append-only), not built, Decision log (answered questions), Decisions made (section 1), Non-functional requirements (section 6), Training mode: PHYSICAL or ONLINE

### Community 70 - "Entity: Training"
Cohesion: 0.17
Nodes (12): Categories: two-level tree with icon and hue, training uses a leaf, Entity: Category, Entity: LearningOutcome, Entity: Training, Entity: TrainingContact, Entity: TrainingDetail, Training duration (value + unit, derived weeks) and weekly class slots, Entity: TrainingModule (+4 more)

### Community 71 - "Workflow: institute onboarding"
Cohesion: 0.29
Nodes (8): Entity: InstituteDocument, Entity: InstituteInvitation, Institute registration: one JSON request creates institute, owner, contact, locations, Institute status workflow: PENDING, APPROVED, REJECTED, INFO_REQUESTED, SUSPENDED, One-time codes (OTP): six digits, 5 minutes, Redis only, Staff invitations: 7-day token, hash stored, email queued after commit, Verification documents: private pdf/jpg/png up to 5 MB, Workflow: institute onboarding

### Community 73 - "set_status"
Cohesion: 0.40
Nodes (3): change_password(), _revoke_refresh_tokens(), set_status()

### Community 76 - "expire_trainings"
Cohesion: 0.25
Nodes (3): Command, expire_trainings(), expire_trainings()

### Community 77 - "institutes/validators.py"
Cohesion: 0.83
Nodes (3): validate_document_file(), validate_image_file(), _validate_upload()

### Community 85 - "enquiries/api/v1/serializers.py"
Cohesion: 0.13
Nodes (6): SlugModel, Meta, _slug_strip(), unique_slugify(), NepalMobileField, normalize_phone()

### Community 88 - "Entity: Enquiry (planned)"
Cohesion: 0.40
Nodes (5): Availability: seats minus CONVERTED enquiries above zero, Entity: Enquiry (planned), Open question: PRD 'Instructor Name' search has no field, Search: PostgreSQL full-text, simple config, word-prefix match, PRD search and discovery filters

### Community 90 - "Training status workflow: DRAFT, SUBMITTED, APPROVED, CHANGES_REQUESTED, REJECTED, UNPUBLISHED, CANCELLED, EXPIRED"
Cohesion: 0.50
Nodes (3): Training expiry: daily expire_trainings job sets EXPIRED after end_date, Training status workflow: DRAFT, SUBMITTED, APPROVED, CHANGES_REQUESTED, REJECTED, UNPUBLISHED, CANCELLED, EXPIRED, Workflow: training lifecycle

### Community 102 - "test_categories.py"
Cohesion: 0.07
Nodes (5): AdminCategoryApiTests, CategoryConstraintTests, CategoryServiceTests, CategoryTreeApiTests, LoadCategoriesTests

### Community 107 - "VisitorEnquirySerializer"
Cohesion: 0.17
Nodes (4): VisitorEnquirySerializer, Meta, MyEnquiriesView, device_enquiries()

## Ambiguous Edges - Review These
- `PRD training modes: Physical, Online, Hybrid` → `Decision: hybrid mode dropped (2026-10-13)`  [AMBIGUOUS]
  docs/Training for Merojob (PRD).md · relation: conceptually_related_to
- `PRD institute locations (several, one main office)` → `Training venue: exactly one TrainingLocation, independent of institute offices`  [AMBIGUOUS]
  docs/Training for Merojob (PRD).md · relation: conceptually_related_to

## Knowledge Gaps
- **21 isolated node(s):** `Dependency: djangorestframework-simplejwt 5.5.1 (with PyJWT crypto)`, `Entity: InstituteGalleryImage`, `Institute types: fixed list of seven`, `Managed Nepal location list (province / district / municipality)`, `Django apps and their state (section 2)` (+16 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 620 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **42 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Training` connect `Training` to `enquiries/api/v1/views.py`, `training/services.py`, `institutes/api/v1/serializers.py`, `SubmitTests`, `institutes/api/v1/views.py`, `BaseModel`, `delete_training`, `TrainingConstraintTests`, `expire_trainings`, `Institute`, `FilterTests`, `enquiries/api/v1/serializers.py`, `TrainingFilter`, `Enquiry`, `AdminTrainingSerializer`, `.create`, `PublicTrainingListSerializer`, `EditTests`?**
  _High betweenness centrality (0.126) - this node is a cross-community bridge._
- **Are the 44 inferred relationships involving `Training` (e.g. with `AdminTrainingFilter` and `AdminTrainingSerializer`) actually correct?**
  _`Training` has 44 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Dependency: djangorestframework-simplejwt 5.5.1 (with PyJWT crypto)`, `Entity: InstituteGalleryImage`, `Institute types: fixed list of seven` to the rest of the system?**
  _21 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `institutes/services.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08880666049953746 - nodes in this community are weakly interconnected._
- **Why does `Institute` connect `Institute` to `institutes/services.py`, `training/services.py`, `institutes/api/v1/serializers.py`, `RegistrationApiTests`, `RegistrationTests`, `institutes/api/v1/views.py`, `BaseModel`, `institutes/models.py`, `.as_`, `Training`, `Enquiry`, `AdminTrainingSerializer`, `AdminApiTests`, `InstituteCEO`, `.post`, `SubmitTests`, `ActionRequiredTests`, `PortalTestCase`, `WorkflowTests`, `InstituteDocument`, `add_location`, `enquiries/api/v1/serializers.py`?**
  _High betweenness centrality (0.096) - this node is a cross-community bridge._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `PRD training modes: Physical, Online, Hybrid` and `Decision: hybrid mode dropped (2026-10-13)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `PRD institute locations (several, one main office)` and `Training venue: exactly one TrainingLocation, independent of institute offices`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._