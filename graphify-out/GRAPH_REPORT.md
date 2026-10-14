# Graph Report - traininghub-backend  (2026-10-14)

## Corpus Check
- 91 files · ~124,808 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 3)

## Summary
- 1505 nodes · 3373 edges · 97 communities (55 shown, 42 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 414 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Auth, OTP & Admin API Tests
- Users Services & OTP Tasks
- Institute Services
- Training Services & Workflow
- Mixin Viewsets
- Admin, Institute & User Serializers
- Institute Registration API Tests
- Registration & OTP Service Tests
- Institute Portal Views & Permissions
- Training Serializers & Category
- Invitation, Location & Email Tests
- Location Model & Tests
- Institute Tests & Constants
- User Auth Views
- Institute Profile & Contact Tests
- Training Models & Tests
- Public Training Search Tests
- Admin, Training & Common Views
- Settings & Management Commands
- Validators & User Model
- Training Portal Create Tests
- Throttling & OTP Views
- Category Tests
- Training Content Serializers
- Admin Institute API Tests
- Admin Review Viewsets
- Public Training Serializers
- Training Create & Submit Tests
- Location Loader Tests
- Platform Permissions & Downloads
- Training Edit Tests
- Registration & Invitation Serializers
- Public Institute API Tests
- Misc: InstituteContact
- Misc: NormalizedEmailSerializer
- Misc: User
- Misc: Base64FieldMixin
- Misc: SlugModel
- Misc: AdminCategoryApiTests
- Misc: Role
- Misc: institutes/models.py
- Misc: DocumentAndGalleryTests
- Misc: PortalTrainingViewSet
- Misc: PortalTestCase
- Misc: TrainingTestCase
- Misc: v1/permissions.py
- Misc: InstituteGalleryImage
- Misc: InvitationTests
- Misc: WorkflowTests
- Misc: EditTests
- Misc: common/services.py
- Misc: InstituteLocation
- Misc: Training
- Misc: consume_otp()
- Misc: Product Requirements Document (PRD)
- Misc: helpers.py
- Misc: TrainingFilter
- Misc: TrainingSession
- Misc: TrainingConstraintTests
- Misc: Entity: Institute
- Misc: StaffTests
- Misc: PortalTestCase
- Misc: LocationTests
- Misc: UserConstraintTests
- Misc: CategoryTreeView
- Misc: LocationApiTests
- Misc: DocumentTests
- Misc: InstituteConstraintTests
- Misc: System Design (DRAFT v0.6)
- Misc: Entity: Training
- Misc: DynamicFieldsSerializer
- Misc: CEOTests
- Misc: GalleryTests
- Misc: SocialLinkTests
- Misc: expire_trainings()
- Misc: AdminApiTests
- Misc: ActiveAccountJWTAuthentication
- Misc: Core entities (section 3)
- Misc: validate_pan_vat_number()
- Misc: ControlPanelRoutesTests
- Misc: add_location()
- Misc: Entity: InstituteLocation (office)
- Misc: PrivateStorage
- Misc: ActionQueryCountTests
- Misc: PasswordChangeSerializer
- Misc: PortalTrainingListSerializer
- Misc: Entity: Enquiry (planned)
- Misc: LocationInputSerializer
- Misc: Training status workflow: DRAFT, SUBMITT
- Misc: Dependency: Django 5.2.4
- Misc: Dependency: django-q2 1.8.0
- Misc: Dependency: django-redis 6.0.0
- Misc: Dependency: djangorestframework 3.16.0
- Misc: Dev extras: debug toolbar, django-extens

## God Nodes (most connected - your core abstractions)
1. `Training` - 57 edges
2. `Institute` - 45 edges
3. `RegistrationApiTests` - 42 edges
4. `Role` - 38 edges
5. `InstituteStatus` - 35 edges
6. `DynamicFieldsModelSerializer` - 31 edges
7. `BaseModel` - 27 edges
8. `Category` - 27 edges
9. `Location` - 27 edges
10. `AdminApiTests` - 26 edges

## Surprising Connections (you probably didn't know these)
- `Institute registration: one JSON request creates institute, owner, contact, locations` --references--> `register()`  [INFERRED]
  docs/System Design.md → apps/institutes/services.py
- `Decision: PAN/VAT number unique, nine digits, contact telephone optional` --references--> `validate_pan_vat_number()`  [EXTRACTED]
  docs/System Design.md → apps/common/validators.py
- `One-time codes (OTP): six digits, 5 minutes, Redis only` --references--> `consume_otp()`  [INFERRED]
  docs/System Design.md → apps/users/services.py
- `Open question: endpoint that consumes a verified password-reset code` --references--> `consume_otp()`  [EXTRACTED]
  docs/System Design.md → apps/users/services.py
- `api_exception_handler()` --uses--> `TooManyRequests`  [INFERRED]
  config/exception_handlers.py → apps/common/exceptions.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Institute onboarding: OTP, register, upload documents, admin review** — docs_system_design_one_time_codes, docs_system_design_institute_registration, docs_system_design_verification_documents, docs_system_design_institute_status_workflow [EXTRACTED 1.00]
- **Training lifecycle: draft, review, edit-back-to-review, daily expiry** — docs_system_design_training_statuses, docs_system_design_editing_training, docs_system_design_training_expiry [EXTRACTED 1.00]

## Communities (97 total, 42 thin omitted)

### Community 0 - "Auth, OTP & Admin API Tests"
Cohesion: 0.06
Nodes (8): AdminSerializer, Meta, update_admin(), AdminApiTests, AuthApiTests, OtpApiTests, StatusApiTests, UsersApiTestCase

### Community 1 - "Users Services & OTP Tasks"
Cohesion: 0.07
Nodes (20): TooManyRequests, OTPPurpose, change_password(), create_admin(), normalize_email(), _otp_keys(), _revoke_refresh_tokens(), send_otp() (+12 more)

### Community 2 - "Institute Services"
Cohesion: 0.10
Nodes (27): InstituteStatus, Institute, Meta, accept_invitation(), add_document(), add_gallery_image(), add_social_link(), approve() (+19 more)

### Community 3 - "Training Services & Workflow"
Cohesion: 0.12
Nodes (30): TrainingMode, TrainingStatus, approve(), _build_search_vector(), cancel(), _check_category(), _check_dates(), _check_sessions() (+22 more)

### Community 4 - "Mixin Viewsets"
Cohesion: 0.11
Nodes (21): BaseViewSet, CreateListDestroyViewSet, CreateListRetrieveUpdateViewSet, CreateListUpdateDestroyViewSet, CreateListUpdateViewSet, CreateListViewSet, CreateRetrieveUpdateViewSet, CreateRetrieveViewSet (+13 more)

### Community 5 - "Admin, Institute & User Serializers"
Cohesion: 0.09
Nodes (20): DynamicFieldsModelSerializer, AdminDocumentSerializer, Meta, AdminInstituteSerializer, Meta, GalleryImageSerializer, Meta, InstituteCEOSerializer (+12 more)

### Community 7 - "Registration & OTP Service Tests"
Cohesion: 0.10
Nodes (3): RegistrationOtpApiTests, RegistrationTests, get_otp()

### Community 8 - "Institute Portal Views & Permissions"
Cohesion: 0.11
Nodes (17): GalleryReorderSerializer, InvitationSerializer, Meta, StaffSerializer, Meta, PortalCEOView, PortalDocumentViewSet, PortalGalleryViewSet (+9 more)

### Community 9 - "Training Serializers & Category"
Cohesion: 0.08
Nodes (20): BaseModel, Meta, Category, Meta, AdminCategoryFilter, Meta, AdminTrainingFilter, Meta (+12 more)

### Community 10 - "Invitation, Location & Email Tests"
Cohesion: 0.09
Nodes (3): InvitationTests, LocationTests, RegistrationOtpServiceTests

### Community 11 - "Location Model & Tests"
Cohesion: 0.14
Nodes (9): active_municipalities(), LocationLevel, MunicipalityType, Command, Location, Meta, clear_category_tree_cache(), clear_location_tree_cache() (+1 more)

### Community 12 - "Institute Tests & Constants"
Cohesion: 0.18
Nodes (6): DocumentStatus, InvitationStatus, MemberRole, InstituteInvitation, Meta, send_invitation_email()

### Community 13 - "User Auth Views"
Cohesion: 0.08
Nodes (11): LoginSerializer, ProfileSerializer, Meta, UpdateStatusSerializer, Meta, LoginView, LogoutView, MeView (+3 more)

### Community 15 - "Training Models & Tests"
Cohesion: 0.17
Nodes (6): DurationUnit, TrainingLevel, TrainingShift, WeekDay, TrainingContact, TrainingDetail

### Community 16 - "Public Training Search Tests"
Cohesion: 0.13
Nodes (7): FilterTests, PublicTrainingTestCase, QueryCountTests, SearchTests, ShiftsAreShownTests, titles(), VisibilityTests

### Community 17 - "Admin, Training & Common Views"
Cohesion: 0.14
Nodes (8): LocationFilter, Meta, LocationSerializer, Meta, LocationViewSet, ReadOnlyViewSet, DocumentReviewSerializer, AdminDocumentView

### Community 18 - "Settings & Management Commands"
Cohesion: 0.10
Nodes (3): Command, Command, load_jwt_key()

### Community 19 - "Validators & User Model"
Cohesion: 0.13
Nodes (10): combine_date_parts(), get_today(), validate_attachment(), validate_coded_phone_number(), validate_dob(), validate_future_datetime(), validate_is_future_datetime(), validate_otp() (+2 more)

### Community 22 - "Throttling & OTP Views"
Cohesion: 0.12
Nodes (6): IdentityScopedRateThrottle, ActionAPIView, RegisterSendOTPView, RegisterVerifyOTPView, SendOTPView, VerifyOTPView

### Community 23 - "Category Tests"
Cohesion: 0.13
Nodes (3): CategoryConstraintTests, CategoryServiceTests, LoadCategoriesTests

### Community 24 - "Training Content Serializers"
Cohesion: 0.13
Nodes (5): AdminTrainingSerializer, Meta, PortalTrainingSerializer, Meta, TrainingContentFields

### Community 26 - "Admin Review Viewsets"
Cohesion: 0.23
Nodes (3): ReasonSerializer, AdminInstituteViewSet, AdminTrainingViewSet

### Community 27 - "Public Training Serializers"
Cohesion: 0.12
Nodes (6): duration_text(), PublicTrainingDetailSerializer, Meta, PublicTrainingListSerializer, Meta, PublicTrainingViewSet

### Community 29 - "Location Loader Tests"
Cohesion: 0.15
Nodes (3): load(), LoadLocationsTests, LocationModelTests

### Community 30 - "Platform Permissions & Downloads"
Cohesion: 0.14
Nodes (6): AdminDocumentDownloadView, PortalDocumentDownloadView, private_file_response(), HasPlatformPermission, IsInstituteStaff, IsPlatformAdmin

### Community 32 - "Registration & Invitation Serializers"
Cohesion: 0.12
Nodes (6): AcceptInvitationSerializer, InstituteRegistrationSerializer, Meta, AcceptInvitationView, RegisterView, OTPField

### Community 34 - "Misc: InstituteContact"
Cohesion: 0.13
Nodes (6): InstituteProfileSerializer, Meta, InstituteProfileView, PortalContactView, ResubmitView, InstituteContact

### Community 35 - "Misc: NormalizedEmailSerializer"
Cohesion: 0.13
Nodes (5): NormalizedEmailSerializer, RegistrationOTPSerializer, RegistrationOTPVerifySerializer, SendOTPSerializer, VerifyOTPSerializer

### Community 36 - "Misc: User"
Cohesion: 0.16
Nodes (3): UserManager, User, Meta

### Community 38 - "Misc: SlugModel"
Cohesion: 0.19
Nodes (4): SlugModel, Meta, _slug_strip(), unique_slugify()

### Community 40 - "Misc: Role"
Cohesion: 0.16
Nodes (4): PermissionMatrixTests, RemoveStaffTests, Role, SocialPlatform

### Community 41 - "Misc: institutes/models.py"
Cohesion: 0.21
Nodes (5): InstituteType, InstituteCEO, validate_document_file(), validate_image_file(), _validate_upload()

### Community 43 - "Misc: PortalTrainingViewSet"
Cohesion: 0.20
Nodes (4): PortalTrainingViewSet, transition(), run(), with_content()

### Community 44 - "Misc: PortalTestCase"
Cohesion: 0.14
Nodes (5): LifecycleTests, PortalPermissionTests, PortalTestCase, QueryCountTests, SummaryTests

### Community 45 - "Misc: TrainingTestCase"
Cohesion: 0.18
Nodes (4): ExpiryTests, ReviewTests, TrainingTestCase, TransitionTableTests

### Community 47 - "Misc: InstituteGalleryImage"
Cohesion: 0.17
Nodes (7): PublicInstituteDetailSerializer, Meta, PublicInstituteListSerializer, Meta, PublicInstituteViewSet, InstituteGalleryImage, Meta

### Community 51 - "Misc: common/services.py"
Cohesion: 0.23
Nodes (5): _check_parent(), create_category(), update_category(), AdminCategorySerializer, Meta

### Community 52 - "Misc: InstituteLocation"
Cohesion: 0.18
Nodes (8): InstituteLocation, Meta, InstituteSocialLink, Meta, _create_registration(), register(), update_location(), validate_institute_location()

### Community 53 - "Misc: Training"
Cohesion: 0.24
Nodes (6): Training, Meta, refresh_category_trainings(), refresh_institute_trainings(), found(), SearchVectorTests

### Community 54 - "Misc: consume_otp()"
Cohesion: 0.21
Nodes (11): consume_otp(), Institute registration: one JSON request creates institute, owner, contact, locations, Institute status workflow: PENDING, APPROVED, REJECTED, INFO_REQUESTED, SUSPENDED, Auth: email + password, JWT RS256 via simplejwt, One-time codes (OTP): six digits, 5 minutes, Redis only, Open questions (section 8), Open question: how an admin's password is reset, Open question: endpoint that consumes a verified password-reset code (+3 more)

### Community 55 - "Misc: Product Requirements Document (PRD)"
Cohesion: 0.23
Nodes (11): Phase 2: Application (approve/reject/capacity) and learners, My enquiries: browser device token, last 90 days, Open question: do institutes keep enquiries after 90 days, Reviews and ratings out of MVP, Workflow: enquiry (planned), Product Requirements Document (PRD), PRD training enquiry rules (captcha, rate limit, 90-day My enquiries), PRD institute locations (several, one main office) (+3 more)

### Community 56 - "Misc: helpers.py"
Cohesion: 0.22
Nodes (5): get_upload_path(), get_uuid_filename(), nested_getattr(), set_instance_fields(), update_instance()

### Community 57 - "Misc: TrainingFilter"
Cohesion: 0.18
Nodes (3): prefix_query(), TrainingFilter, Meta

### Community 58 - "Misc: TrainingSession"
Cohesion: 0.18
Nodes (6): TrainingSessionSerializer, Meta, TrainingSession, Meta, DetailTests, TrainingSessionConstraintTests

### Community 60 - "Misc: Entity: Institute"
Cohesion: 0.22
Nodes (11): Entity: Institute, Entity: InstituteCEO, Entity: InstituteContact, Entity: InstituteDocument, Entity: InstituteGalleryImage, Entity: InstituteInvitation, Institute profile split: columns plus contact, CEO, social-link tables, Entity: InstituteSocialLink (+3 more)

### Community 62 - "Misc: PortalTestCase"
Cohesion: 0.22
Nodes (3): EndToEndTests, PortalTestCase, ResubmitTests

### Community 65 - "Misc: CategoryTreeView"
Cohesion: 0.22
Nodes (4): build_category_tree(), build_tree(), CategoryTreeView, LocationTreeView

### Community 69 - "Misc: System Design (DRAFT v0.6)"
Cohesion: 0.22
Nodes (6): System Design (DRAFT v0.6), Django apps and their state (section 2), Proposed: AuditLog (append-only), not built, Decision log (answered questions), Decisions made (section 1), Non-functional requirements (section 6)

### Community 70 - "Misc: Entity: Training"
Cohesion: 0.22
Nodes (9): Entity: LearningOutcome, Entity: Training, Entity: TrainingContact, Entity: TrainingDetail, Training duration (value + unit, derived weeks) and weekly class slots, Entity: TrainingModule, Entity: TrainingSession (weekly slot), Training shifts: Morning / Day / Evening labels (+1 more)

### Community 76 - "Misc: expire_trainings()"
Cohesion: 0.25
Nodes (3): Command, expire_trainings(), expire_trainings()

### Community 79 - "Misc: Core entities (section 3)"
Cohesion: 0.25
Nodes (8): Categories: two-level tree with icon and hue, training uses a leaf, Entity: Category, Core entities (section 3), Entity: InstituteMember (one institute per user), Roles and grantable Django permissions (users.manage_*), Entity: User, PRD target users: Learner, Training Provider, Administrator, PRD training categories

### Community 83 - "Misc: Entity: InstituteLocation (office)"
Cohesion: 0.33
Nodes (5): Entity: InstituteLocation (office), Entity: Location, Managed Nepal location list (province / district / municipality), Entity: TrainingLocation (venue), Training mode: PHYSICAL or ONLINE

### Community 87 - "Misc: PortalTrainingListSerializer"
Cohesion: 0.40
Nodes (4): AdminTrainingListSerializer, Meta, PortalTrainingListSerializer, Meta

### Community 88 - "Misc: Entity: Enquiry (planned)"
Cohesion: 0.40
Nodes (5): Availability: seats minus CONVERTED enquiries above zero, Entity: Enquiry (planned), Open question: PRD 'Instructor Name' search has no field, Search: PostgreSQL full-text, simple config, word-prefix match, PRD search and discovery filters

### Community 90 - "Misc: Training status workflow: DRAFT, SUBMITT"
Cohesion: 0.50
Nodes (3): Training expiry: daily expire_trainings job sets EXPIRED after end_date, Training status workflow: DRAFT, SUBMITTED, APPROVED, CHANGES_REQUESTED, REJECTED, UNPUBLISHED, CANCELLED, EXPIRED, Workflow: training lifecycle

## Ambiguous Edges - Review These
- `Decision: hybrid mode dropped (2026-10-13)` → `PRD training modes: Physical, Online, Hybrid`  [AMBIGUOUS]
  docs/Training for Merojob (PRD).md · relation: conceptually_related_to
- `Training venue: exactly one TrainingLocation, independent of institute offices` → `PRD institute locations (several, one main office)`  [AMBIGUOUS]
  docs/Training for Merojob (PRD).md · relation: conceptually_related_to

## Knowledge Gaps
- **21 isolated node(s):** `Decisions made (section 1)`, `Django apps and their state (section 2)`, `Training expiry: daily expire_trainings job sets EXPIRED after end_date`, `Institute status workflow: PENDING, APPROVED, REJECTED, INFO_REQUESTED, SUSPENDED`, `Search: PostgreSQL full-text, simple config, word-prefix match` (+16 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 506 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **42 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Role` connect `Misc: Role` to `Auth, OTP & Admin API Tests`, `Users Services & OTP Tasks`, `Institute Services`, `Mixin Viewsets`, `Institute Registration API Tests`, `Registration & OTP Service Tests`, `Institute Portal Views & Permissions`, `Invitation, Location & Email Tests`, `Institute Tests & Constants`, `Institute Profile & Contact Tests`, `Training Models & Tests`, `Admin, Training & Common Views`, `Validators & User Model`, `Platform Permissions & Downloads`, `Public Institute API Tests`, `Misc: User`, `Misc: DocumentAndGalleryTests`, `Misc: PortalTestCase`, `Misc: WorkflowTests`, `Misc: InstituteLocation`, `Misc: StaffTests`, `Misc: UserConstraintTests`, `Misc: ControlPanelRoutesTests`?**
  _High betweenness centrality (0.112) - this node is a cross-community bridge._
- **Are the 38 inferred relationships involving `Training` (e.g. with `AdminTrainingFilter` and `AdminTrainingSerializer`) actually correct?**
  _`Training` has 38 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Decisions made (section 1)`, `Django apps and their state (section 2)`, `Training expiry: daily expire_trainings job sets EXPIRED after end_date` to the rest of the system?**
  _21 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Auth, OTP & Admin API Tests` be split into smaller, more focused modules?**
  _Cohesion score 0.06219426974143955 - nodes in this community are weakly interconnected._
- **Why does `InstituteStatus` connect `Institute Services` to `Training Services & Workflow`, `Institute Registration API Tests`, `Registration & OTP Service Tests`, `Institute Portal Views & Permissions`, `Institute Tests & Constants`, `Institute Profile & Contact Tests`, `Training Models & Tests`, `Public Training Search Tests`, `Admin, Training & Common Views`, `Training Portal Create Tests`, `Admin Institute API Tests`, `Public Training Serializers`, `Training Create & Submit Tests`, `Public Institute API Tests`, `Misc: institutes/models.py`, `Misc: InstituteGalleryImage`, `Misc: WorkflowTests`, `Misc: PortalTestCase`, `Misc: AdminApiTests`?**
  _High betweenness centrality (0.072) - this node is a cross-community bridge._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `Decision: hybrid mode dropped (2026-10-13)` and `PRD training modes: Physical, Online, Hybrid`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Training venue: exactly one TrainingLocation, independent of institute offices` and `PRD institute locations (several, one main office)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._