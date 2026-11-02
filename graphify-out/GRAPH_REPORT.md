# Graph Report - traininghub-backend  (2026-11-02)

## Corpus Check
- 101 files · ~59,150 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 3)

## Summary
- 1805 nodes · 4097 edges · 110 communities (64 shown, 46 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 521 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9c09c4d1`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- AdminCategoryApiTests
- .url
- institutes/services.py
- training/services.py
- viewsets.py
- InstituteSocialLink
- RegistrationApiTests
- RegistrationOtpApiTests
- institutes/api/v1/views.py
- Category
- InvitationTests
- Location
- institutes/tests/test_api_portal.py
- users/api/v1/views.py
- .as_
- training/models.py
- PublicTrainingTestCase
- CategoryTreeView
- settings/base.py
- .url
- .create
- IdentityScopedRateThrottle
- SubmitTests
- AdminTrainingSerializer
- AdminApiTests
- InstituteContact
- PublicTrainingListSerializer
- TrainingTestCase
- LocationModelTests
- enquiries/services.py
- change_status
- InstituteRegistrationSerializer
- Enquiry
- EditTests
- RegistrationTests
- UserConstraintTests
- fields.py
- control_panel/api/v1/views.py
- ContactTests
- TrainingFilter
- enquiries/api/v1/views.py
- ActionRequiredTests
- load_locations.py
- SubmitTests
- PortalTestCase
- OtpApiTests
- PublicInstituteViewSet
- InvitationTests
- PublicInstituteApiTests
- EnquiryNote
- AdminDocumentDownloadView
- institutes/models.py
- Training
- Open question: how an admin's password is reset
- Product Requirements Document (PRD)
- Base64FieldMixin
- Entity: Institute
- EnquiryConstraintTests
- NormalizedEmailSerializer
- LocationTests
- PortalEnquiryViewSet
- WorkflowTests
- LocationApiTests
- DocumentTests
- System Design (DRAFT v0.6)
- Entity: Training
- register
- test_locations.py
- set_status
- GalleryTests
- SocialLinkTests
- expire_trainings
- update_admin
- ActiveAccountJWTAuthentication
- signals.py
- Command
- StaffTests
- send_otp
- BaseViewSet
- InstituteConstraintTests
- slugify.py
- PasswordChangeSerializer
- institutes/api/v1/serializers.py
- Open questions (section 8)
- AuthApiTests
- Training status workflow: DRAFT, SUBMITTED, APPROVED, CHANGES_REQUESTED, REJECTED, UNPUBLISHED, CANCELLED, EXPIRED
- Dependency: Django 5.2.4
- Dependency: django-q2 1.8.0
- Dependency: django-redis 6.0.0
- Dependency: djangorestframework 3.16.0
- Dev extras: debug toolbar, django-extensions, ipdb, ipython, fabric3, pylint
- verify_otp
- users/tasks.py
- VisitorEnquirySerializer
- AdminSerializer
- AdminApiTests
- CategoryConstraintTests
- create_admin
- InstituteProfileSerializer
- add_location
- validate_phone_number
- institutes/validators.py
- TrainingSessionConstraintTests
- IsInstituteStaff

## God Nodes (most connected - your core abstractions)
1. `Training` - 67 edges
2. `Institute` - 54 edges
3. `RegistrationApiTests` - 49 edges
4. `InstituteStatus` - 43 edges
5. `Role` - 43 edges
6. `Enquiry` - 39 edges
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
- `2.2 Rules (`apps/enquiries/services.py`)` --references--> `submit_enquiry()`  [INFERRED]
  docs/enquiries-status.md → apps/enquiries/services.py
- `4.3 Backend work not done` --references--> `change_status()`  [INFERRED]
  docs/enquiries-status.md → apps/enquiries/services.py
- `2.4 Changes outside the new app` --references--> `delete_training()`  [INFERRED]
  docs/enquiries-status.md → apps/training/services.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Institute onboarding: OTP, register, upload documents, admin review** — docs_system_design_one_time_codes, docs_system_design_institute_registration, docs_system_design_verification_documents, docs_system_design_institute_status_workflow [EXTRACTED 1.00]
- **Training lifecycle: draft, review, edit-back-to-review, daily expiry** — docs_system_design_training_statuses, docs_system_design_editing_training, docs_system_design_training_expiry [EXTRACTED 1.00]

## Communities (110 total, 46 thin omitted)

### Community 1 - ".url"
Cohesion: 0.07
Nodes (7): AccessTests, DetailTests, ListTests, NoteTests, PortalTestCase, StatusChangeTests, SummaryTests

### Community 2 - "institutes/services.py"
Cohesion: 0.11
Nodes (29): InstituteStatus, Institute, Meta, InstituteLocation, Meta, accept_invitation(), add_document(), add_gallery_image() (+21 more)

### Community 3 - "training/services.py"
Cohesion: 0.13
Nodes (28): TrainingMode, TrainingStatus, TrainingLocation, approve(), _build_search_vector(), cancel(), _check_category(), _check_dates() (+20 more)

### Community 4 - "viewsets.py"
Cohesion: 0.19
Nodes (19): CreateListDestroyViewSet, CreateListRetrieveUpdateViewSet, CreateListUpdateDestroyViewSet, CreateListUpdateViewSet, CreateListViewSet, CreateRetrieveUpdateViewSet, CreateRetrieveViewSet, CreateUpdateViewSet (+11 more)

### Community 5 - "InstituteSocialLink"
Cohesion: 0.13
Nodes (11): InstituteContactSerializer, Meta, InstituteSocialLinkSerializer, Meta, InstituteSocialLink, Meta, add_social_link(), _check_platform_free() (+3 more)

### Community 8 - "institutes/api/v1/views.py"
Cohesion: 0.10
Nodes (16): GalleryReorderSerializer, InstituteActionRequiredSerializer, StaffSerializer, Meta, InstituteActionRequiredView, InstituteProfileView, PortalContactView, PortalDocumentViewSet (+8 more)

### Community 9 - "Category"
Cohesion: 0.11
Nodes (11): SlugModel, Meta, Category, Meta, _check_parent(), create_category(), update_category(), AdminCategoryFilter (+3 more)

### Community 10 - "InvitationTests"
Cohesion: 0.09
Nodes (3): InvitationTests, LocationTests, RegistrationOtpServiceTests

### Community 11 - "Location"
Cohesion: 0.20
Nodes (10): LocationFilter, Meta, active_municipalities(), LocationSerializer, Meta, LocationViewSet, LocationLevel, MunicipalityType (+2 more)

### Community 13 - "users/api/v1/views.py"
Cohesion: 0.10
Nodes (10): LoginSerializer, UpdateStatusSerializer, Meta, LoginView, LogoutView, PasswordChangeView, RefreshView, UserStatusView (+2 more)

### Community 15 - "training/models.py"
Cohesion: 0.08
Nodes (23): BaseModel, Meta, available_categories(), CoverSerializer, LearningOutcomeSerializer, Meta, TrainingModuleSerializer, Meta (+15 more)

### Community 16 - "FilterTests"
Cohesion: 0.15
Nodes (4): FilterTests, SearchTests, titles(), VisibilityTests

### Community 17 - "CategoryTreeView"
Cohesion: 0.22
Nodes (4): build_category_tree(), build_tree(), CategoryTreeView, LocationTreeView

### Community 20 - ".url"
Cohesion: 0.07
Nodes (7): AccessTests, DetailTests, ListTests, NoteTests, PortalTestCase, StatusChangeTests, SummaryTests

### Community 21 - ".create"
Cohesion: 0.05
Nodes (10): ActionQueryCountTests, AdminApiTests, LifecycleTests, PortalCreateTests, PortalEditTests, PortalPermissionTests, PortalTestCase, QueryCountTests (+2 more)

### Community 22 - "common/validators.py"
Cohesion: 0.16
Nodes (9): combine_date_parts(), get_today(), validate_attachment(), validate_coded_phone_number(), validate_dob(), validate_future_datetime(), validate_is_future_datetime(), validate_otp() (+1 more)

### Community 21 - ".create"
Cohesion: 0.05
Nodes (10): ActionQueryCountTests, AdminApiTests, LifecycleTests, PortalCreateTests, PortalEditTests, PortalPermissionTests, PortalTestCase, QueryCountTests (+2 more)

### Community 22 - "IdentityScopedRateThrottle"
Cohesion: 0.11
Nodes (7): IdentityScopedRateThrottle, ActionAPIView, RegisterSendOTPView, RegisterVerifyOTPView, RegistrationOTPVerifySerializer, SendOTPView, VerifyOTPView

### Community 23 - "SubmitTests"
Cohesion: 0.11
Nodes (5): ChangeStatusTests, NoteTests, ServiceTestCase, submit(), SubmitTests

### Community 24 - "AdminTrainingSerializer"
Cohesion: 0.06
Nodes (11): DynamicFieldsSerializer, AdminTrainingFilter, Meta, AdminTrainingSerializer, Meta, ReasonSerializer, AdminInstituteViewSet, AdminTrainingViewSet (+3 more)

### Community 26 - "InstituteContact"
Cohesion: 0.14
Nodes (7): PortalCEOView, InstituteCEO, InstituteContact, InstituteGalleryImage, Meta, annotate_profile_completion(), _at_least()

### Community 27 - "PublicTrainingListSerializer"
Cohesion: 0.10
Nodes (7): duration_text(), format_class_days(), PublicTrainingDetailSerializer, Meta, PublicTrainingListSerializer, Meta, PublicTrainingViewSet

### Community 28 - "TrainingTestCase"
Cohesion: 0.09
Nodes (6): CreateTests, ExpiryTests, ReviewTests, SubmitTests, TrainingTestCase, TransitionTableTests

### Community 30 - "enquiries/services.py"
Cohesion: 0.16
Nodes (7): TooManyRequests, _claim_phone_slot(), _is_open_duplicate(), _require_accepting(), _require_open_for_enquiry(), submit_enquiry(), api_exception_handler()

### Community 31 - "change_status"
Cohesion: 0.08
Nodes (18): PortalEnquirySerializer, Meta, change_status(), registration_open_q(), 1. In short, 2.2 Rules (`apps/enquiries/services.py`), 2.3 API (all under `/api/v1/`), 2.4 Changes outside the new app (+10 more)

### Community 32 - "InstituteRegistrationSerializer"
Cohesion: 0.15
Nodes (5): LocationInputSerializer, InstituteRegistrationSerializer, Meta, VenueSerializer, OTPField

### Community 33 - "Enquiry"
Cohesion: 0.17
Nodes (7): EnquiryStatus, EnquiryType, PreferredTime, Enquiry, Meta, SeatRaceTests, SummaryTests

### Community 36 - "UserConstraintTests"
Cohesion: 0.05
Nodes (7): ControlPanelRoutesTests, add_contact(), InstituteAdminSiteTests, UserManager, User, Meta, UserConstraintTests

### Community 38 - "SubmitTests"
Cohesion: 0.09
Nodes (6): ChangeStatusTests, NoteTests, ServiceTestCase, submit(), SubmitTests, SummaryTests

### Community 38 - "control_panel/api/v1/views.py"
Cohesion: 0.10
Nodes (10): AdminTrainingListSerializer, Meta, AdminCategoryViewSet, PortalTrainingListSerializer, Meta, PortalTrainingViewSet, transition(), run() (+2 more)

### Community 40 - "TrainingFilter"
Cohesion: 0.22
Nodes (3): prefix_query(), TrainingFilter, Meta

### Community 41 - "enquiries/api/v1/views.py"
Cohesion: 0.12
Nodes (7): EnquiryCreateSerializer, Meta, NepalMobileField, PortalEnquiryListSerializer, Meta, EnquiryCreateView, normalize_phone()

### Community 42 - "ActionRequiredTests"
Cohesion: 0.12
Nodes (3): ActionRequiredTests, DocumentAndGalleryTests, CoverTests

### Community 44 - "SubmitTests"
Cohesion: 0.14
Nodes (4): NoVisitorIdentityTests, PublicTestCase, SubmitTests, ThrottleTests

### Community 45 - "PortalTestCase"
Cohesion: 0.18
Nodes (4): EndToEndTests, PermissionMatrixTests, PortalTestCase, ResubmitTests

### Community 46 - "register"
Cohesion: 0.07
Nodes (13): register(), NormalizedEmailSerializer, RegistrationOTPSerializer, RegistrationOTPVerifySerializer, SendOTPSerializer, VerifyOTPSerializer, consume_otp(), normalize_email() (+5 more)

### Community 50 - "EnquiryNote"
Cohesion: 0.17
Nodes (8): EnquiryNoteSerializer, Meta, PortalEnquiryNoteView, EnquiryNote, Meta, add_note(), 2.1 Data (`apps/enquiries/models.py`), 4.4 Risks and limits to know about

### Community 51 - "AdminDocumentDownloadView"
Cohesion: 0.25
Nodes (3): AdminDocumentDownloadView, PortalDocumentDownloadView, private_file_response()

### Community 52 - "institutes/models.py"
Cohesion: 0.14
Nodes (10): InstituteType, InvitationStatus, MemberRole, InstituteInvitation, Meta, InstituteMember, Meta, PrivateStorage (+2 more)

### Community 53 - "Training"
Cohesion: 0.17
Nodes (9): DeleteTrainingTests, Training, Meta, delete_training(), refresh_search_vectors(), refresh_category_trainings(), refresh_institute_trainings(), found() (+1 more)

### Community 54 - "Open question: how an admin's password is reset"
Cohesion: 0.40
Nodes (5): Entity: InstituteMember (one institute per user), Open question: how an admin's password is reset, Roles and grantable Django permissions (users.manage_*), Entity: User, PRD target users: Learner, Training Provider, Administrator

### Community 55 - "Product Requirements Document (PRD)"
Cohesion: 0.21
Nodes (12): Phase 2: Application (approve/reject/capacity) and learners, My enquiries: browser device token, last 90 days, Reviews and ratings out of MVP, Training duration (value + unit, derived weeks) and weekly class slots, Entity: TrainingSession (weekly slot), Workflow: enquiry (planned), Product Requirements Document (PRD), PRD training enquiry rules (captcha, rate limit, 90-day My enquiries) (+4 more)

### Community 56 - "helpers.py"
Cohesion: 0.22
Nodes (5): get_upload_path(), get_uuid_filename(), nested_getattr(), set_instance_fields(), update_instance()

### Community 57 - "AcceptInvitationSerializer"
Cohesion: 0.29
Nodes (3): AcceptInvitationSerializer, AcceptInvitationView, RegisterView

### Community 60 - "Entity: Institute"
Cohesion: 0.22
Nodes (11): Entity: Institute, Entity: InstituteCEO, Entity: InstituteContact, Entity: InstituteDocument, Entity: InstituteGalleryImage, Entity: InstituteInvitation, Institute profile split: columns plus contact, CEO, social-link tables, Entity: InstituteSocialLink (+3 more)

### Community 62 - "NormalizedEmailSerializer"
Cohesion: 0.15
Nodes (4): NormalizedEmailSerializer, RegistrationOTPSerializer, SendOTPSerializer, send_password_reset_otp()

### Community 64 - "PortalEnquiryViewSet"
Cohesion: 0.17
Nodes (4): PortalEnquiryFilter, Meta, PortalEnquiryViewSet, summary()

### Community 69 - "System Design (DRAFT v0.6)"
Cohesion: 0.20
Nodes (6): System Design (DRAFT v0.6), Django apps and their state (section 2), Proposed: AuditLog (append-only), not built, Decision log (answered questions), Decisions made (section 1), Non-functional requirements (section 6)

### Community 70 - "Entity: Training"
Cohesion: 0.13
Nodes (18): Availability: seats minus CONVERTED enquiries above zero, Categories: two-level tree with icon and hue, training uses a leaf, Entity: Category, Core entities (section 3), Entity: Enquiry (planned), Entity: InstituteLocation (office), Entity: LearningOutcome, Entity: Location (+10 more)

### Community 71 - "register"
Cohesion: 0.27
Nodes (7): register(), consume_otp(), Institute registration: one JSON request creates institute, owner, contact, locations, Institute status workflow: PENDING, APPROVED, REJECTED, INFO_REQUESTED, SUSPENDED, One-time codes (OTP): six digits, 5 minutes, Redis only, Open question: endpoint that consumes a verified password-reset code, Workflow: institute onboarding

### Community 72 - "test_locations.py"
Cohesion: 0.33
Nodes (3): level_counts(), load(), LoadLocationsTests

### Community 73 - "set_status"
Cohesion: 0.40
Nodes (3): change_password(), _revoke_refresh_tokens(), set_status()

### Community 76 - "expire_trainings"
Cohesion: 0.25
Nodes (3): Command, expire_trainings(), expire_trainings()

### Community 77 - "update_admin"
Cohesion: 0.31
Nodes (3): _set_permissions(), update_admin(), StatusApiTests

### Community 82 - "send_otp"
Cohesion: 0.24
Nodes (4): normalize_email(), _otp_keys(), send_otp(), send_registration_otp()

### Community 87 - "institutes/api/v1/serializers.py"
Cohesion: 0.07
Nodes (21): DynamicFieldsModelSerializer, AdminDocumentSerializer, Meta, AdminInstituteSerializer, Meta, DocumentReviewSerializer, AdminDocumentView, GalleryImageSerializer (+13 more)

### Community 88 - "Open questions (section 8)"
Cohesion: 0.25
Nodes (8): Auth: email + password, JWT RS256 via simplejwt, Open questions (section 8), Open question: do institutes keep enquiries after 90 days, Open question: PRD 'Instructor Name' search has no field, Open question: where the frontend stores access/refresh tokens, Search: PostgreSQL full-text, simple config, word-prefix match, PRD search and discovery filters, Dependency: djangorestframework-simplejwt 5.5.1 (with PyJWT crypto)

### Community 90 - "Training status workflow: DRAFT, SUBMITTED, APPROVED, CHANGES_REQUESTED, REJECTED, UNPUBLISHED, CANCELLED, EXPIRED"
Cohesion: 0.50
Nodes (3): Training expiry: daily expire_trainings job sets EXPIRED after end_date, Training status workflow: DRAFT, SUBMITTED, APPROVED, CHANGES_REQUESTED, REJECTED, UNPUBLISHED, CANCELLED, EXPIRED, Workflow: training lifecycle

### Community 97 - "verify_otp"
Cohesion: 0.25
Nodes (3): VerifyOTPSerializer, verify_otp(), verify_registration_otp()

### Community 98 - "users/tasks.py"
Cohesion: 0.39
Nodes (5): send_otp_email(), send_registration_otp_email(), _deliver_otp(), send_otp_email_task(), send_registration_otp_email_task()

### Community 99 - "VisitorEnquirySerializer"
Cohesion: 0.33
Nodes (3): VisitorEnquirySerializer, Meta, VisitorViewTests

### Community 100 - "AdminSerializer"
Cohesion: 0.14
Nodes (6): AdminSerializer, Meta, AdminViewSet, ProfileSerializer, Meta, MeView

### Community 102 - "CategoryConstraintTests"
Cohesion: 0.13
Nodes (3): CategoryConstraintTests, CategoryServiceTests, LoadCategoriesTests

### Community 104 - "InstituteProfileSerializer"
Cohesion: 0.25
Nodes (3): InstituteProfileSerializer, Meta, ResubmitView

### Community 106 - "validate_phone_number"
Cohesion: 0.29
Nodes (4): ValidatePanVatNumberTests, ValidatePhoneNumberTests, validate_pan_vat_number(), validate_phone_number()

### Community 107 - "institutes/validators.py"
Cohesion: 0.83
Nodes (3): validate_document_file(), validate_image_file(), _validate_upload()

## Ambiguous Edges - Review These
- `PRD training modes: Physical, Online, Hybrid` → `Decision: hybrid mode dropped (2026-10-13)`  [AMBIGUOUS]
  docs/Training for Merojob (PRD).md · relation: conceptually_related_to
- `PRD institute locations (several, one main office)` → `Training venue: exactly one TrainingLocation, independent of institute offices`  [AMBIGUOUS]
  docs/Training for Merojob (PRD).md · relation: conceptually_related_to

## Knowledge Gaps
- **21 isolated node(s):** `Dependency: djangorestframework-simplejwt 5.5.1 (with PyJWT crypto)`, `Entity: InstituteGalleryImage`, `Institute types: fixed list of seven`, `Django apps and their state (section 2)`, `Proposed: AuditLog (append-only), not built` (+16 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 604 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **46 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Role` connect `institutes/tests/test_api_portal.py` to `.url`, `institutes/services.py`, `RegistrationApiTests`, `institutes/api/v1/views.py`, `InvitationTests`, `users/api/v1/views.py`, `training/models.py`, `.create`, `Enquiry`, `RegistrationTests`, `UserConstraintTests`, `control_panel/api/v1/views.py`, `ContactTests`, `ActionRequiredTests`, `PortalTestCase`, `PublicInstituteApiTests`, `institutes/models.py`, `WorkflowTests`, `set_status`, `StaffTests`, `AuthApiTests`, `AdminSerializer`, `AdminApiTests`, `create_admin`, `IsInstituteStaff`?**
  _High betweenness centrality (0.113) - this node is a cross-community bridge._
- **Are the 44 inferred relationships involving `Training` (e.g. with `AdminTrainingFilter` and `AdminTrainingSerializer`) actually correct?**
  _`Training` has 44 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Dependency: djangorestframework-simplejwt 5.5.1 (with PyJWT crypto)`, `Entity: InstituteGalleryImage`, `Institute types: fixed list of seven` to the rest of the system?**
  _21 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `.url` be split into smaller, more focused modules?**
  _Cohesion score 0.07084785133565621 - nodes in this community are weakly interconnected._
- **Why does `Training` connect `Training` to `institutes/services.py`, `training/services.py`, `Category`, `training/models.py`, `PublicTrainingTestCase`, `.create`, `SubmitTests`, `AdminTrainingSerializer`, `PublicTrainingListSerializer`, `TrainingTestCase`, `enquiries/services.py`, `change_status`, `Enquiry`, `EditTests`, `control_panel/api/v1/views.py`, `TrainingFilter`, `enquiries/api/v1/views.py`, `TrainingConstraintTests`, `expire_trainings`, `institutes/api/v1/serializers.py`, `TrainingSessionConstraintTests`?**
  _High betweenness centrality (0.111) - this node is a cross-community bridge._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `PRD training modes: Physical, Online, Hybrid` and `Decision: hybrid mode dropped (2026-10-13)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `PRD institute locations (several, one main office)` and `Training venue: exactly one TrainingLocation, independent of institute offices`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._