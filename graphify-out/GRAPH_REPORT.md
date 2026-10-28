# Graph Report - traininghub-backend  (2026-10-15)

## Corpus Check
- 87 files · ~50,681 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 3)

## Summary
- 1573 nodes · 3550 edges · 100 communities (59 shown, 41 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 439 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `03bf8587`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- create_admin
- test_api_portal_admin.py
- institutes/services.py
- training/services.py
- viewsets.py
- DynamicFieldsModelSerializer
- RegistrationApiTests
- OtpApiTests
- IsInstituteMember
- AdminCategorySerializer
- InvitationTests
- Location
- test_api_portal.py
- users/api/v1/views.py
- .as_
- training/models.py
- PublicTrainingTestCase
- common/api/v1/views.py
- settings/base.py
- common/validators.py
- .create
- IdentityScopedRateThrottle
- PortalEditTests
- AdminTrainingViewSet
- AdminApiTests
- InstituteSocialLink
- PublicTrainingListSerializer
- TrainingTestCase
- LocationModelTests
- institutes/tests/test_services.py
- .png
- InstituteRegistrationSerializer
- AdminTrainingSerializer
- EditTests
- RegistrationTests
- User
- fields.py
- PortalTrainingViewSet
- ContactTests
- TrainingFilter
- InstituteCEO
- ActionRequiredTests
- load_locations.py
- BaseModel
- PortalTestCase
- PortalTrainingSerializer
- PublicInstituteViewSet
- InvitationTests
- AdminApiTests
- InstituteDocument
- institutes/api/v1/views.py
- institutes/models.py
- Training
- Open questions (section 8)
- Product Requirements Document (PRD)
- helpers.py
- AcceptInvitationSerializer
- TrainingConstraintTests
- Entity: Institute
- InstituteActionRequiredView
- ActionQueryCountTests
- LocationTests
- UserConstraintTests
- AdminDocumentSerializer
- LocationApiTests
- DocumentTests
- LocationInputSerializer
- System Design (DRAFT v0.6)
- Entity: Training
- register
- DynamicFieldsSerializer
- UpdateStatusSerializer
- GalleryTests
- SocialLinkTests
- expire_trainings
- ActiveAccountJWTAuthentication
- signals.py
- Command
- ControlPanelRoutesTests
- Core entities (section 3)
- PrivateStorage
- SlugModel
- PasswordChangeSerializer
- control_panel/api/v1/serializers.py
- Entity: Enquiry (planned)
- Training status workflow: DRAFT, SUBMITTED, APPROVED, CHANGES_REQUESTED, REJECTED, UNPUBLISHED, CANCELLED, EXPIRED
- Dependency: Django 5.2.4
- Dependency: django-q2 1.8.0
- Dependency: django-redis 6.0.0
- Dependency: djangorestframework 3.16.0
- Dev extras: debug toolbar, django-extensions, ipdb, ipython, fabric3, pylint
- InstituteAdminSiteTests
- AdminSerializer
- CategoryConstraintTests
- InstituteProfileSerializer
- validate_phone_number
- RemoveStaffTests

## God Nodes (most connected - your core abstractions)
1. `Training` - 57 edges
2. `RegistrationApiTests` - 49 edges
3. `Institute` - 48 edges
4. `Role` - 40 edges
5. `InstituteStatus` - 35 edges
6. `DynamicFieldsModelSerializer` - 31 edges
7. `ActionRequiredTests` - 29 edges
8. `BaseModel` - 27 edges
9. `Category` - 27 edges
10. `Location` - 27 edges

## Surprising Connections (you probably didn't know these)
- `Decision: PAN/VAT number unique, nine digits, contact telephone optional` --references--> `validate_pan_vat_number()`  [EXTRACTED]
  docs/System Design.md → apps/common/validators.py
- `Institute registration: one JSON request creates institute, owner, contact, locations` --references--> `register()`  [INFERRED]
  docs/System Design.md → apps/institutes/services.py
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

## Communities (100 total, 41 thin omitted)

### Community 0 - "create_admin"
Cohesion: 0.05
Nodes (10): AdminCategoryApiTests, CategoryTreeApiTests, change_password(), create_admin(), _set_permissions(), update_admin(), AdminApiTests, AuthApiTests (+2 more)

### Community 1 - "test_api_portal_admin.py"
Cohesion: 0.15
Nodes (6): LifecycleTests, PortalPermissionTests, PortalTestCase, QueryCountTests, SubmitNeedsShiftsTests, SummaryTests

### Community 2 - "institutes/services.py"
Cohesion: 0.12
Nodes (29): InstituteStatus, Institute, Meta, InstituteLocation, Meta, add_document(), add_gallery_image(), add_social_link() (+21 more)

### Community 3 - "training/services.py"
Cohesion: 0.12
Nodes (30): TrainingStatus, TrainingContact, TrainingLocation, approve(), _build_search_vector(), cancel(), _check_category(), _check_dates() (+22 more)

### Community 4 - "viewsets.py"
Cohesion: 0.13
Nodes (19): BaseViewSet, CreateListDestroyViewSet, CreateListRetrieveUpdateViewSet, CreateListUpdateDestroyViewSet, CreateListUpdateViewSet, CreateListViewSet, CreateRetrieveUpdateViewSet, CreateRetrieveViewSet (+11 more)

### Community 5 - "DynamicFieldsModelSerializer"
Cohesion: 0.11
Nodes (9): DynamicFieldsModelSerializer, AdminInstituteSerializer, Meta, InstituteContactSerializer, Meta, InstituteLocationSerializer, Meta, InstituteSocialLinkSerializer (+1 more)

### Community 7 - "OtpApiTests"
Cohesion: 0.09
Nodes (8): RegistrationOtpApiTests, get_otp(), send_otp_email(), send_registration_otp_email(), _deliver_otp(), send_otp_email_task(), send_registration_otp_email_task(), OtpApiTests

### Community 8 - "IsInstituteMember"
Cohesion: 0.12
Nodes (12): GalleryReorderSerializer, StaffSerializer, Meta, PortalDocumentViewSet, PortalGalleryViewSet, PortalInvitationViewSet, PortalLocationViewSet, PortalSocialLinkViewSet (+4 more)

### Community 9 - "AdminCategorySerializer"
Cohesion: 0.24
Nodes (5): _check_parent(), create_category(), update_category(), AdminCategorySerializer, Meta

### Community 10 - "InvitationTests"
Cohesion: 0.09
Nodes (4): send_invitation_email(), InvitationTests, LocationTests, RegistrationOtpServiceTests

### Community 11 - "Location"
Cohesion: 0.32
Nodes (5): active_municipalities(), LocationLevel, MunicipalityType, Location, Meta

### Community 12 - "test_api_portal.py"
Cohesion: 0.16
Nodes (5): InstituteContact, InstituteMember, Meta, make_staff(), Role

### Community 13 - "users/api/v1/views.py"
Cohesion: 0.12
Nodes (8): AdminViewSet, LogoutView, PasswordChangeView, RefreshView, UserStatusView, HasPlatformPermission, IsInstituteStaff, IsPlatformAdmin

### Community 14 - ".as_"
Cohesion: 0.11
Nodes (3): CEOTests, ProfileTests, StaffTests

### Community 15 - "training/models.py"
Cohesion: 0.10
Nodes (16): CoverSerializer, TrainingSessionSerializer, Meta, DurationUnit, TrainingLevel, TrainingMode, TrainingShift, WeekDay (+8 more)

### Community 16 - "PublicTrainingTestCase"
Cohesion: 0.13
Nodes (7): FilterTests, PublicTrainingTestCase, QueryCountTests, SearchTests, ShiftsAreShownTests, titles(), VisibilityTests

### Community 17 - "common/api/v1/views.py"
Cohesion: 0.14
Nodes (9): LocationFilter, Meta, LocationSerializer, Meta, build_category_tree(), build_tree(), CategoryTreeView, LocationTreeView (+1 more)

### Community 19 - "common/validators.py"
Cohesion: 0.16
Nodes (9): combine_date_parts(), get_today(), validate_attachment(), validate_coded_phone_number(), validate_dob(), validate_future_datetime(), validate_is_future_datetime(), validate_otp() (+1 more)

### Community 22 - "IdentityScopedRateThrottle"
Cohesion: 0.11
Nodes (7): IdentityScopedRateThrottle, ActionAPIView, RegisterSendOTPView, RegisterVerifyOTPView, RegistrationOTPVerifySerializer, SendOTPView, VerifyOTPView

### Community 24 - "AdminTrainingViewSet"
Cohesion: 0.24
Nodes (3): ReasonSerializer, AdminInstituteViewSet, AdminTrainingViewSet

### Community 25 - "AdminApiTests"
Cohesion: 0.05
Nodes (5): add_location(), AdminApiTests, PublicInstituteApiTests, InstituteConstraintTests, WorkflowTests

### Community 26 - "InstituteSocialLink"
Cohesion: 0.15
Nodes (8): GalleryImageSerializer, Meta, InstituteGalleryImage, Meta, InstituteSocialLink, Meta, annotate_profile_completion(), _at_least()

### Community 27 - "PublicTrainingListSerializer"
Cohesion: 0.10
Nodes (7): duration_text(), format_class_days(), PublicTrainingDetailSerializer, Meta, PublicTrainingListSerializer, Meta, PublicTrainingViewSet

### Community 28 - "TrainingTestCase"
Cohesion: 0.09
Nodes (6): CreateTests, ExpiryTests, ReviewTests, SubmitTests, TrainingTestCase, TransitionTableTests

### Community 29 - "LocationModelTests"
Cohesion: 0.14
Nodes (4): level_counts(), load(), LoadLocationsTests, LocationModelTests

### Community 30 - "institutes/tests/test_services.py"
Cohesion: 0.12
Nodes (6): TooManyRequests, remove_staff(), OTPPurpose, _revoke_refresh_tokens(), set_status(), api_exception_handler()

### Community 32 - "InstituteRegistrationSerializer"
Cohesion: 0.22
Nodes (3): InstituteRegistrationSerializer, Meta, OTPField

### Community 33 - "AdminTrainingSerializer"
Cohesion: 0.15
Nodes (7): AdminTrainingSerializer, Meta, LearningOutcomeSerializer, Meta, TrainingContentFields, TrainingModuleSerializer, Meta

### Community 35 - "RegistrationTests"
Cohesion: 0.06
Nodes (12): RegistrationTests, NormalizedEmailSerializer, RegistrationOTPSerializer, SendOTPSerializer, VerifyOTPSerializer, normalize_email(), _otp_keys(), send_otp() (+4 more)

### Community 36 - "User"
Cohesion: 0.16
Nodes (3): UserManager, User, Meta

### Community 37 - "fields.py"
Cohesion: 0.07
Nodes (4): DistributedKeyAuthentication, DistributedAppKey, Base64FieldMixin, Base64ImageField

### Community 38 - "PortalTrainingViewSet"
Cohesion: 0.23
Nodes (3): PortalTrainingViewSet, transition(), run()

### Community 40 - "TrainingFilter"
Cohesion: 0.17
Nodes (3): prefix_query(), TrainingFilter, Meta

### Community 41 - "InstituteCEO"
Cohesion: 0.28
Nodes (4): InstituteCEOSerializer, Meta, PortalCEOView, InstituteCEO

### Community 45 - "PortalTestCase"
Cohesion: 0.15
Nodes (4): EndToEndTests, PermissionMatrixTests, PortalTestCase, ResubmitTests

### Community 47 - "PublicInstituteViewSet"
Cohesion: 0.20
Nodes (5): PublicInstituteDetailSerializer, Meta, PublicInstituteListSerializer, Meta, PublicInstituteViewSet

### Community 50 - "InstituteDocument"
Cohesion: 0.33
Nodes (6): InstituteDocumentSerializer, Meta, DocumentStatus, InstituteDocument, Meta, review_document()

### Community 51 - "institutes/api/v1/views.py"
Cohesion: 0.12
Nodes (8): ReadOnlyViewSet, AdminCategoryFilter, Meta, AdminCategoryViewSet, AdminDocumentDownloadView, PortalDocumentDownloadView, private_file_response(), with_content()

### Community 52 - "institutes/models.py"
Cohesion: 0.17
Nodes (14): InvitationSerializer, Meta, InstituteType, InvitationStatus, MemberRole, InstituteInvitation, Meta, accept_invitation() (+6 more)

### Community 53 - "Training"
Cohesion: 0.11
Nodes (13): Category, Meta, AdminTrainingFilter, Meta, available_categories(), Training, Meta, refresh_search_vectors() (+5 more)

### Community 54 - "Open questions (section 8)"
Cohesion: 0.22
Nodes (10): Entity: InstituteMember (one institute per user), Auth: email + password, JWT RS256 via simplejwt, Open questions (section 8), Open question: how an admin's password is reset, Open question: endpoint that consumes a verified password-reset code, Open question: where the frontend stores access/refresh tokens, Roles and grantable Django permissions (users.manage_*), Entity: User (+2 more)

### Community 55 - "Product Requirements Document (PRD)"
Cohesion: 0.25
Nodes (10): Phase 2: Application (approve/reject/capacity) and learners, My enquiries: browser device token, last 90 days, Open question: do institutes keep enquiries after 90 days, Reviews and ratings out of MVP, Workflow: enquiry (planned), Product Requirements Document (PRD), PRD training enquiry rules (captcha, rate limit, 90-day My enquiries), PRD later phase: applications, reviews and ratings (+2 more)

### Community 56 - "helpers.py"
Cohesion: 0.22
Nodes (5): get_upload_path(), get_uuid_filename(), nested_getattr(), set_instance_fields(), update_instance()

### Community 57 - "AcceptInvitationSerializer"
Cohesion: 0.29
Nodes (3): AcceptInvitationSerializer, AcceptInvitationView, RegisterView

### Community 60 - "Entity: Institute"
Cohesion: 0.38
Nodes (7): Entity: Institute, Entity: InstituteCEO, Entity: InstituteContact, Entity: InstituteGalleryImage, Institute profile split: columns plus contact, CEO, social-link tables, Entity: InstituteSocialLink, Institute types: fixed list of seven

### Community 65 - "AdminDocumentSerializer"
Cohesion: 0.50
Nodes (3): AdminDocumentSerializer, Meta, AdminDocumentView

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
Cohesion: 0.25
Nodes (3): Command, expire_trainings(), expire_trainings()

### Community 83 - "Core entities (section 3)"
Cohesion: 0.38
Nodes (6): Core entities (section 3), Entity: InstituteLocation (office), Entity: Location, Managed Nepal location list (province / district / municipality), Entity: TrainingLocation (venue), PRD institute locations (several, one main office)

### Community 85 - "SlugModel"
Cohesion: 0.20
Nodes (4): SlugModel, Meta, _slug_strip(), unique_slugify()

### Community 87 - "control_panel/api/v1/serializers.py"
Cohesion: 0.14
Nodes (5): AdminTrainingListSerializer, Meta, DocumentReviewSerializer, PortalTrainingListSerializer, Meta

### Community 88 - "Entity: Enquiry (planned)"
Cohesion: 0.40
Nodes (5): Availability: seats minus CONVERTED enquiries above zero, Entity: Enquiry (planned), Open question: PRD 'Instructor Name' search has no field, Search: PostgreSQL full-text, simple config, word-prefix match, PRD search and discovery filters

### Community 90 - "Training status workflow: DRAFT, SUBMITTED, APPROVED, CHANGES_REQUESTED, REJECTED, UNPUBLISHED, CANCELLED, EXPIRED"
Cohesion: 0.50
Nodes (3): Training expiry: daily expire_trainings job sets EXPIRED after end_date, Training status workflow: DRAFT, SUBMITTED, APPROVED, CHANGES_REQUESTED, REJECTED, UNPUBLISHED, CANCELLED, EXPIRED, Workflow: training lifecycle

### Community 100 - "AdminSerializer"
Cohesion: 0.12
Nodes (7): AdminSerializer, Meta, LoginSerializer, ProfileSerializer, Meta, LoginView, MeView

### Community 102 - "CategoryConstraintTests"
Cohesion: 0.13
Nodes (3): CategoryConstraintTests, CategoryServiceTests, LoadCategoriesTests

### Community 104 - "InstituteProfileSerializer"
Cohesion: 0.17
Nodes (5): InstituteProfileSerializer, Meta, InstituteProfileView, PortalContactView, ResubmitView

### Community 106 - "validate_phone_number"
Cohesion: 0.29
Nodes (4): ValidatePanVatNumberTests, ValidatePhoneNumberTests, validate_pan_vat_number(), validate_phone_number()

## Ambiguous Edges - Review These
- `PRD training modes: Physical, Online, Hybrid` → `Decision: hybrid mode dropped (2026-10-13)`  [AMBIGUOUS]
  docs/Training for Merojob (PRD).md · relation: conceptually_related_to
- `PRD institute locations (several, one main office)` → `Training venue: exactly one TrainingLocation, independent of institute offices`  [AMBIGUOUS]
  docs/Training for Merojob (PRD).md · relation: conceptually_related_to

## Knowledge Gaps
- **21 isolated node(s):** `Dependency: djangorestframework-simplejwt 5.5.1 (with PyJWT crypto)`, `Entity: InstituteGalleryImage`, `Institute types: fixed list of seven`, `Django apps and their state (section 2)`, `Proposed: AuditLog (append-only), not built` (+16 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 520 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **41 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Role` connect `test_api_portal.py` to `create_admin`, `test_api_portal_admin.py`, `institutes/services.py`, `RegistrationApiTests`, `IsInstituteMember`, `InvitationTests`, `users/api/v1/views.py`, `AdminApiTests`, `institutes/tests/test_services.py`, `.png`, `RegistrationTests`, `User`, `ContactTests`, `BaseModel`, `PortalTestCase`, `institutes/api/v1/views.py`, `institutes/models.py`, `UserConstraintTests`, `ControlPanelRoutesTests`, `InstituteAdminSiteTests`, `RemoveStaffTests`?**
  _High betweenness centrality (0.115) - this node is a cross-community bridge._
- **Are the 38 inferred relationships involving `Training` (e.g. with `AdminTrainingFilter` and `AdminTrainingSerializer`) actually correct?**
  _`Training` has 38 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Dependency: djangorestframework-simplejwt 5.5.1 (with PyJWT crypto)`, `Entity: InstituteGalleryImage`, `Institute types: fixed list of seven` to the rest of the system?**
  _21 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `create_admin` be split into smaller, more focused modules?**
  _Cohesion score 0.05102040816326531 - nodes in this community are weakly interconnected._
- **Why does `Training` connect `Training` to `test_api_portal_admin.py`, `institutes/services.py`, `training/services.py`, `training/models.py`, `PublicTrainingTestCase`, `.create`, `PortalEditTests`, `AdminTrainingViewSet`, `PublicTrainingListSerializer`, `TrainingTestCase`, `AdminTrainingSerializer`, `EditTests`, `PortalTrainingViewSet`, `TrainingFilter`, `BaseModel`, `PortalTrainingSerializer`, `institutes/api/v1/views.py`, `TrainingConstraintTests`, `expire_trainings`, `SlugModel`, `control_panel/api/v1/serializers.py`?**
  _High betweenness centrality (0.083) - this node is a cross-community bridge._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `PRD training modes: Physical, Online, Hybrid` and `Decision: hybrid mode dropped (2026-10-13)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `PRD institute locations (several, one main office)` and `Training venue: exactly one TrainingLocation, independent of institute offices`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._