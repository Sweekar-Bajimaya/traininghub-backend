# Graph Report - traininghub-backend  (2026-10-15)

## Corpus Check
- 87 files · ~50,565 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 3)

## Summary
- 1569 nodes · 3541 edges · 102 communities (54 shown, 48 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 439 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `3cbe8748`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- OtpApiTests
- users/services.py
- institutes/services.py
- training/services.py
- viewsets.py
- DynamicFieldsModelSerializer
- RegistrationApiTests
- RegistrationTests
- institutes/api/v1/views.py
- common/services.py
- InvitationTests
- Location
- test_api_portal.py
- users/api/v1/views.py
- .as_
- training/tests/test_services.py
- PublicTrainingTestCase
- control_panel/api/v1/views.py
- settings/base.py
- common/validators.py
- .create
- IdentityScopedRateThrottle
- AdminCategoryApiTests
- AdminTrainingSerializer
- AdminApiTests
- Institute
- PublicTrainingListSerializer
- EditTests
- LoadLocationsTests
- django_db
- fields.py
- InstituteRegistrationSerializer
- PublicInstituteApiTests
- LocationTests
- NormalizedEmailSerializer
- User
- v1/permissions.py
- OTPPurpose
- ContactTests
- TrainingFilter
- InstituteCEO
- ActionRequiredTests
- load_locations.py
- Base64FieldMixin
- PortalTestCase
- LocationModelTests
- institutes/api/v1/serializers.py
- InvitationTests
- WorkflowTests
- BaseViewSet
- AdminDocumentDownloadView
- institutes/models.py
- Training
- Open questions (section 8)
- Product Requirements Document (PRD)
- helpers.py
- AcceptInvitationSerializer
- InstituteLocation
- TrainingConstraintTests
- Entity: Institute
- InstituteActionRequiredView
- PermissionMatrixTests
- LocationTests
- UserConstraintTests
- InstituteContact
- LocationApiTests
- DocumentTests
- LocationSerializer
- System Design (DRAFT v0.6)
- Entity: Training
- Workflow: institute onboarding
- DynamicFieldsSerializer
- GalleryTests
- SocialLinkTests
- training/tasks.py
- ActiveAccountJWTAuthentication
- signals.py
- Command
- ControlPanelRoutesTests
- add_location
- Core entities (section 3)
- institutes/validators.py
- training/models.py
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
- users/api/v1/serializers.py
- CategoryConstraintTests
- InstituteProfileSerializer
- UserManager
- validate_pan_vat_number
- IsInstituteStaff
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

## Communities (102 total, 48 thin omitted)

### Community 0 - "OtpApiTests"
Cohesion: 0.06
Nodes (10): AdminSerializer, Meta, create_admin(), _set_permissions(), update_admin(), AdminApiTests, AuthApiTests, OtpApiTests (+2 more)

### Community 1 - "users/services.py"
Cohesion: 0.13
Nodes (10): register(), change_password(), consume_otp(), normalize_email(), _otp_keys(), _revoke_refresh_tokens(), send_otp(), send_registration_otp() (+2 more)

### Community 2 - "institutes/services.py"
Cohesion: 0.15
Nodes (19): InstituteStatus, InstituteGalleryImage, Meta, add_document(), add_gallery_image(), approve(), deactivate_location(), _ready_for_approval() (+11 more)

### Community 3 - "training/services.py"
Cohesion: 0.13
Nodes (29): TrainingMode, TrainingStatus, approve(), _build_search_vector(), cancel(), _check_category(), _check_dates(), _check_sessions() (+21 more)

### Community 4 - "viewsets.py"
Cohesion: 0.19
Nodes (18): CreateListDestroyViewSet, CreateListRetrieveUpdateViewSet, CreateListUpdateDestroyViewSet, CreateListUpdateViewSet, CreateListViewSet, CreateRetrieveUpdateViewSet, CreateRetrieveViewSet, CreateUpdateViewSet (+10 more)

### Community 5 - "DynamicFieldsModelSerializer"
Cohesion: 0.11
Nodes (11): DynamicFieldsModelSerializer, AdminInstituteSerializer, Meta, InstituteCEOSerializer, Meta, InstituteContactSerializer, Meta, InstituteLocationSerializer (+3 more)

### Community 7 - "RegistrationTests"
Cohesion: 0.09
Nodes (3): RegistrationOtpApiTests, RegistrationTests, get_otp()

### Community 8 - "institutes/api/v1/views.py"
Cohesion: 0.12
Nodes (12): GalleryReorderSerializer, InstituteProfileView, PortalContactView, PortalDocumentViewSet, PortalGalleryViewSet, PortalInvitationViewSet, PortalLocationViewSet, PortalSocialLinkViewSet (+4 more)

### Community 9 - "common/services.py"
Cohesion: 0.23
Nodes (5): _check_parent(), create_category(), update_category(), AdminCategorySerializer, Meta

### Community 11 - "Location"
Cohesion: 0.30
Nodes (5): active_municipalities(), LocationLevel, MunicipalityType, Location, Meta

### Community 13 - "users/api/v1/views.py"
Cohesion: 0.10
Nodes (9): AdminViewSet, LoginView, LogoutView, MeView, PasswordChangeView, RefreshView, UserStatusView, HasPlatformPermission (+1 more)

### Community 14 - ".as_"
Cohesion: 0.12
Nodes (3): CEOTests, ProfileTests, ResubmitTests

### Community 15 - "training/tests/test_services.py"
Cohesion: 0.13
Nodes (7): DurationUnit, TrainingShift, WeekDay, TrainingSession, Meta, DetailTests, TrainingSessionConstraintTests

### Community 16 - "PublicTrainingTestCase"
Cohesion: 0.13
Nodes (7): FilterTests, PublicTrainingTestCase, QueryCountTests, SearchTests, ShiftsAreShownTests, titles(), VisibilityTests

### Community 17 - "control_panel/api/v1/views.py"
Cohesion: 0.12
Nodes (11): LocationFilter, Meta, build_category_tree(), build_tree(), CategoryTreeView, LocationTreeView, LocationViewSet, ReadOnlyViewSet (+3 more)

### Community 19 - "common/validators.py"
Cohesion: 0.16
Nodes (9): combine_date_parts(), get_today(), validate_attachment(), validate_coded_phone_number(), validate_dob(), validate_future_datetime(), validate_is_future_datetime(), validate_otp() (+1 more)

### Community 21 - ".create"
Cohesion: 0.05
Nodes (10): ActionQueryCountTests, AdminApiTests, LifecycleTests, PortalCreateTests, PortalEditTests, PortalPermissionTests, PortalTestCase, QueryCountTests (+2 more)

### Community 22 - "IdentityScopedRateThrottle"
Cohesion: 0.12
Nodes (6): IdentityScopedRateThrottle, ActionAPIView, RegisterSendOTPView, RegisterVerifyOTPView, SendOTPView, VerifyOTPView

### Community 24 - "AdminTrainingSerializer"
Cohesion: 0.06
Nodes (12): AdminTrainingSerializer, Meta, ReasonSerializer, AdminInstituteViewSet, AdminTrainingViewSet, PortalTrainingSerializer, Meta, TrainingContentFields (+4 more)

### Community 26 - "Institute"
Cohesion: 0.18
Nodes (10): Institute, Meta, InstituteSocialLink, Meta, add_social_link(), _check_platform_free(), _set_website(), update_contact() (+2 more)

### Community 27 - "PublicTrainingListSerializer"
Cohesion: 0.10
Nodes (7): duration_text(), format_class_days(), PublicTrainingDetailSerializer, Meta, PublicTrainingListSerializer, Meta, PublicTrainingViewSet

### Community 28 - "EditTests"
Cohesion: 0.06
Nodes (7): CreateTests, EditTests, ExpiryTests, ReviewTests, SubmitTests, TrainingTestCase, TransitionTableTests

### Community 29 - "LoadLocationsTests"
Cohesion: 0.29
Nodes (3): level_counts(), load(), LoadLocationsTests

### Community 32 - "InstituteRegistrationSerializer"
Cohesion: 0.18
Nodes (4): LocationInputSerializer, InstituteRegistrationSerializer, Meta, VenueSerializer

### Community 35 - "NormalizedEmailSerializer"
Cohesion: 0.10
Nodes (7): NormalizedEmailSerializer, RegistrationOTPSerializer, RegistrationOTPVerifySerializer, SendOTPSerializer, VerifyOTPSerializer, send_password_reset_otp(), verify_registration_otp()

### Community 38 - "OTPPurpose"
Cohesion: 0.33
Nodes (6): OTPPurpose, send_otp_email(), send_registration_otp_email(), _deliver_otp(), send_otp_email_task(), send_registration_otp_email_task()

### Community 40 - "TrainingFilter"
Cohesion: 0.11
Nodes (5): _slug_strip(), unique_slugify(), prefix_query(), TrainingFilter, Meta

### Community 41 - "InstituteCEO"
Cohesion: 0.29
Nodes (3): PortalCEOView, InstituteCEO, save_ceo()

### Community 42 - "ActionRequiredTests"
Cohesion: 0.12
Nodes (3): ActionRequiredTests, DocumentAndGalleryTests, CoverTests

### Community 45 - "PortalTestCase"
Cohesion: 0.16
Nodes (4): EndToEndTests, make_staff(), PortalTestCase, StaffTests

### Community 47 - "institutes/api/v1/serializers.py"
Cohesion: 0.11
Nodes (12): GalleryImageSerializer, Meta, InstituteDocumentSerializer, Meta, InvitationSerializer, Meta, PublicInstituteDetailSerializer, Meta (+4 more)

### Community 51 - "AdminDocumentDownloadView"
Cohesion: 0.25
Nodes (3): AdminDocumentDownloadView, PortalDocumentDownloadView, private_file_response()

### Community 52 - "institutes/models.py"
Cohesion: 0.15
Nodes (12): InstituteType, InvitationStatus, MemberRole, InstituteInvitation, Meta, InstituteMember, Meta, accept_invitation() (+4 more)

### Community 53 - "Training"
Cohesion: 0.17
Nodes (10): AdminTrainingFilter, Meta, TrainingLevel, Training, Meta, refresh_search_vectors(), refresh_category_trainings(), refresh_institute_trainings() (+2 more)

### Community 54 - "Open questions (section 8)"
Cohesion: 0.22
Nodes (10): Entity: InstituteMember (one institute per user), Auth: email + password, JWT RS256 via simplejwt, Open questions (section 8), Open question: how an admin's password is reset, Open question: endpoint that consumes a verified password-reset code, Open question: where the frontend stores access/refresh tokens, Roles and grantable Django permissions (users.manage_*), Entity: User (+2 more)

### Community 55 - "Product Requirements Document (PRD)"
Cohesion: 0.25
Nodes (10): Phase 2: Application (approve/reject/capacity) and learners, My enquiries: browser device token, last 90 days, Open question: do institutes keep enquiries after 90 days, Reviews and ratings out of MVP, Workflow: enquiry (planned), Product Requirements Document (PRD), PRD training enquiry rules (captcha, rate limit, 90-day My enquiries), PRD later phase: applications, reviews and ratings (+2 more)

### Community 56 - "helpers.py"
Cohesion: 0.18
Nodes (5): get_upload_path(), get_uuid_filename(), nested_getattr(), set_instance_fields(), update_instance()

### Community 57 - "AcceptInvitationSerializer"
Cohesion: 0.29
Nodes (3): AcceptInvitationSerializer, AcceptInvitationView, RegisterView

### Community 58 - "InstituteLocation"
Cohesion: 0.25
Nodes (6): PublicInstituteViewSet, InstituteLocation, Meta, _create_registration(), update_location(), validate_institute_location()

### Community 60 - "Entity: Institute"
Cohesion: 0.38
Nodes (7): Entity: Institute, Entity: InstituteCEO, Entity: InstituteContact, Entity: InstituteGalleryImage, Institute profile split: columns plus contact, CEO, social-link tables, Entity: InstituteSocialLink, Institute types: fixed list of seven

### Community 65 - "InstituteContact"
Cohesion: 0.29
Nodes (3): InstituteContact, annotate_profile_completion(), _at_least()

### Community 69 - "System Design (DRAFT v0.6)"
Cohesion: 0.17
Nodes (7): System Design (DRAFT v0.6), Django apps and their state (section 2), Proposed: AuditLog (append-only), not built, Decision log (answered questions), Decisions made (section 1), Non-functional requirements (section 6), Training mode: PHYSICAL or ONLINE

### Community 70 - "Entity: Training"
Cohesion: 0.17
Nodes (12): Categories: two-level tree with icon and hue, training uses a leaf, Entity: Category, Entity: LearningOutcome, Entity: Training, Entity: TrainingContact, Entity: TrainingDetail, Training duration (value + unit, derived weeks) and weekly class slots, Entity: TrainingModule (+4 more)

### Community 71 - "Workflow: institute onboarding"
Cohesion: 0.29
Nodes (8): Entity: InstituteDocument, Entity: InstituteInvitation, Institute registration: one JSON request creates institute, owner, contact, locations, Institute status workflow: PENDING, APPROVED, REJECTED, INFO_REQUESTED, SUSPENDED, One-time codes (OTP): six digits, 5 minutes, Redis only, Staff invitations: 7-day token, hash stored, email queued after commit, Verification documents: private pdf/jpg/png up to 5 MB, Workflow: institute onboarding

### Community 76 - "training/tasks.py"
Cohesion: 0.18
Nodes (3): Command, expire_trainings(), expire_trainings()

### Community 83 - "Core entities (section 3)"
Cohesion: 0.38
Nodes (6): Core entities (section 3), Entity: InstituteLocation (office), Entity: Location, Managed Nepal location list (province / district / municipality), Entity: TrainingLocation (venue), PRD institute locations (several, one main office)

### Community 84 - "institutes/validators.py"
Cohesion: 0.19
Nodes (4): PrivateStorage, validate_document_file(), validate_image_file(), _validate_upload()

### Community 85 - "training/models.py"
Cohesion: 0.09
Nodes (22): BaseModel, Meta, SlugModel, Meta, Category, Meta, validate_phone_number(), available_categories() (+14 more)

### Community 87 - "control_panel/api/v1/serializers.py"
Cohesion: 0.18
Nodes (12): AdminDocumentSerializer, Meta, AdminTrainingListSerializer, Meta, DocumentReviewSerializer, AdminDocumentView, DocumentStatus, InstituteDocument (+4 more)

### Community 88 - "Entity: Enquiry (planned)"
Cohesion: 0.40
Nodes (5): Availability: seats minus CONVERTED enquiries above zero, Entity: Enquiry (planned), Open question: PRD 'Instructor Name' search has no field, Search: PostgreSQL full-text, simple config, word-prefix match, PRD search and discovery filters

### Community 90 - "Training status workflow: DRAFT, SUBMITTED, APPROVED, CHANGES_REQUESTED, REJECTED, UNPUBLISHED, CANCELLED, EXPIRED"
Cohesion: 0.50
Nodes (3): Training expiry: daily expire_trainings job sets EXPIRED after end_date, Training status workflow: DRAFT, SUBMITTED, APPROVED, CHANGES_REQUESTED, REJECTED, UNPUBLISHED, CANCELLED, EXPIRED, Workflow: training lifecycle

### Community 100 - "users/api/v1/serializers.py"
Cohesion: 0.11
Nodes (6): LoginSerializer, OTPField, ProfileSerializer, Meta, UpdateStatusSerializer, Meta

### Community 102 - "CategoryConstraintTests"
Cohesion: 0.13
Nodes (3): CategoryConstraintTests, CategoryServiceTests, LoadCategoriesTests

### Community 104 - "InstituteProfileSerializer"
Cohesion: 0.25
Nodes (3): InstituteProfileSerializer, Meta, ResubmitView

## Ambiguous Edges - Review These
- `PRD training modes: Physical, Online, Hybrid` → `Decision: hybrid mode dropped (2026-10-13)`  [AMBIGUOUS]
  docs/Training for Merojob (PRD).md · relation: conceptually_related_to
- `PRD institute locations (several, one main office)` → `Training venue: exactly one TrainingLocation, independent of institute offices`  [AMBIGUOUS]
  docs/Training for Merojob (PRD).md · relation: conceptually_related_to

## Knowledge Gaps
- **21 isolated node(s):** `Dependency: djangorestframework-simplejwt 5.5.1 (with PyJWT crypto)`, `Entity: InstituteGalleryImage`, `Institute types: fixed list of seven`, `Django apps and their state (section 2)`, `Proposed: AuditLog (append-only), not built` (+16 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 521 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **48 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Role` connect `test_api_portal.py` to `OtpApiTests`, `users/services.py`, `institutes/services.py`, `RegistrationApiTests`, `RegistrationTests`, `institutes/api/v1/views.py`, `InvitationTests`, `users/api/v1/views.py`, `control_panel/api/v1/views.py`, `.create`, `PublicInstituteApiTests`, `User`, `ContactTests`, `ActionRequiredTests`, `PortalTestCase`, `WorkflowTests`, `institutes/models.py`, `helpers.py`, `InstituteLocation`, `PermissionMatrixTests`, `UserConstraintTests`, `ControlPanelRoutesTests`, `training/models.py`, `InstituteAdminSiteTests`, `UserManager`, `IsInstituteStaff`, `RemoveStaffTests`?**
  _High betweenness centrality (0.103) - this node is a cross-community bridge._
- **Are the 38 inferred relationships involving `Training` (e.g. with `AdminTrainingFilter` and `AdminTrainingSerializer`) actually correct?**
  _`Training` has 38 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Dependency: djangorestframework-simplejwt 5.5.1 (with PyJWT crypto)`, `Entity: InstituteGalleryImage`, `Institute types: fixed list of seven` to the rest of the system?**
  _21 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `OtpApiTests` be split into smaller, more focused modules?**
  _Cohesion score 0.06015037593984962 - nodes in this community are weakly interconnected._
- **Why does `Institute` connect `Institute` to `institutes/services.py`, `training/services.py`, `DynamicFieldsModelSerializer`, `RegistrationApiTests`, `RegistrationTests`, `institutes/api/v1/views.py`, `test_api_portal.py`, `.as_`, `control_panel/api/v1/views.py`, `AdminTrainingSerializer`, `AdminApiTests`, `InstituteRegistrationSerializer`, `InstituteCEO`, `ActionRequiredTests`, `PortalTestCase`, `institutes/api/v1/serializers.py`, `WorkflowTests`, `institutes/models.py`, `Training`, `InstituteLocation`, `InstituteActionRequiredView`, `add_location`, `training/models.py`, `control_panel/api/v1/serializers.py`, `InstituteProfileSerializer`?**
  _High betweenness centrality (0.083) - this node is a cross-community bridge._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `PRD training modes: Physical, Online, Hybrid` and `Decision: hybrid mode dropped (2026-10-13)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `PRD institute locations (several, one main office)` and `Training venue: exactly one TrainingLocation, independent of institute offices`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._