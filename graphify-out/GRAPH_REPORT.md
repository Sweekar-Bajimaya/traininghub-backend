# Graph Report - traininghub-backend  (2026-11-17)

## Corpus Check
- 105 files · ~69,265 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 3)

## Summary
- 2085 nodes · 4764 edges · 119 communities (58 shown, 61 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 626 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ee0f2868`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- RegistrationTests
- AdminInstitutesApiTests
- institutes/services.py
- training/services.py
- viewsets.py
- Base64FieldMixin
- RegistrationApiTests
- RegistrationOtpApiTests
- institutes/api/v1/views.py
- enquiries/services.py
- InvitationTests
- Category
- Enquiry
- InstituteCEO
- .as_
- training/models.py
- FilterTests
- helpers.py
- settings/base.py
- .url
- .create
- common/validators.py
- enquiries/api/v1/views.py
- PublicInstituteApiTests
- AdminApiTests
- add_location
- training/api/v1/serializers.py
- EditTests
- test_locations.py
- fields.py
- SubmitTests
- EnquiryCreateSerializer
- LocationModelTests
- PortalEnquiryNoteView
- AdminEnquiryTests
- UserManager
- v1/permissions.py
- SubmitTests
- ContactTests
- Training
- OtpApiTests
- ActionRequiredTests
- User
- EnquiryConstraintTests
- AdminInstituteViewSet
- create_admin
- PortalTestCase
- InvitationTests
- slugify.py
- validate_phone_number
- WorkflowTests
- ChangeStatusTests
- AdminTrainingsFeaturedAndReviewApiTests
- Open questions (section 8)
- Product Requirements Document (PRD)
- Role
- django_core_cache
- Entity: Institute
- TrainingConstraintTests
- Core entities (section 3)
- users/services.py
- PortalTrainingSerializer
- LocationTests
- UserConstraintTests
- Command
- LocationApiTests
- DocumentTests
- PasswordChangeSerializer
- System Design (DRAFT v0.6)
- Entity: Training
- register
- control_panel/api/v1/serializers.py
- institutes/api/v1/serializers.py
- GalleryTests
- SocialLinkTests
- OTPPurpose
- AdminCategoryApiTests
- rest_framework_permissions
- institutes/models.py
- Location
- ResubmitView
- users/api/v1/serializers.py
- load_locations.py
- institutes/validators.py
- HasPlatformPermission
- StatusChangeTests
- IdentityScopedRateThrottle
- Entity: Enquiry (planned)
- CollapseDuplicateDocumentsTests
- Training status workflow: DRAFT, SUBMITTED, APPROVED, CHANGES_REQUESTED, REJECTED, UNPUBLISHED, CANCELLED, EXPIRED
- Dependency: Django 5.2.4
- Dependency: django-q2 1.8.0
- Dependency: django-redis 6.0.0
- Dependency: djangorestframework 3.16.0
- Dev extras: debug toolbar, django-extensions, ipdb, ipython, fabric3, pylint
- build_category_tree
- AdminSerializer
- InstituteAdminSiteTests
- institute_experience
- ListTests
- CategoryConstraintTests
- AuthApiTests
- InstituteGalleryImage
- ServiceTestCase
- users/api/v1/views.py
- UpdateStatusSerializer
- AdminDashboardSummaryView
- PrivateStorage
- StartDateRangeTests
- PublicTrainingViewSet
- summary
- StableOrderingFilter
- PortalCoverView
- expire_trainings.py
- OTPField
- StaffTests
- InstituteRegistrationSerializer

## God Nodes (most connected - your core abstractions)
1. `Training` - 84 edges
2. `Institute` - 65 edges
3. `InstituteStatus` - 59 edges
4. `AdminInstitutesApiTests` - 51 edges
5. `Enquiry` - 50 edges
6. `RegistrationApiTests` - 49 edges
7. `TrainingStatus` - 48 edges
8. `Role` - 45 edges
9. `DynamicFieldsModelSerializer` - 38 edges
10. `Category` - 32 edges

## Surprising Connections (you probably didn't know these)
- `Decision: PAN/VAT number unique, nine digits, contact telephone optional` --references--> `validate_pan_vat_number()`  [EXTRACTED]
  docs/System Design.md → apps/common/validators.py
- `2.1 Data (`apps/enquiries/models.py`)` --references--> `Enquiry`  [INFERRED]
  docs/enquiries-status.md → apps/enquiries/models.py
- `2.1 Data (`apps/enquiries/models.py`)` --references--> `EnquiryNote`  [INFERRED]
  docs/enquiries-status.md → apps/enquiries/models.py
- `2.2 Rules (`apps/enquiries/services.py`)` --references--> `submit_enquiry()`  [INFERRED]
  docs/enquiries-status.md → apps/enquiries/services.py
- `2.2 Rules (`apps/enquiries/services.py`)` --references--> `change_status()`  [INFERRED]
  docs/enquiries-status.md → apps/enquiries/services.py

## Import Cycles
- None detected.

## Communities (119 total, 61 thin omitted)

### Community 2 - "institutes/services.py"
Cohesion: 0.11
Nodes (28): InstituteStatus, Institute, Meta, InstituteStatusLog, Meta, accept_invitation(), add_gallery_image(), add_social_link() (+20 more)

### Community 3 - "training/services.py"
Cohesion: 0.09
Nodes (37): DurationUnit, TrainingMode, TrainingStatus, LearningOutcome, Meta, TrainingContact, TrainingLocation, admin_counts() (+29 more)

### Community 4 - "viewsets.py"
Cohesion: 0.08
Nodes (27): BaseViewSet, CreateListDestroyViewSet, CreateListRetrieveUpdateViewSet, CreateListUpdateDestroyViewSet, CreateListUpdateViewSet, CreateListViewSet, CreateRetrieveUpdateViewSet, CreateRetrieveViewSet (+19 more)

### Community 8 - "institutes/api/v1/views.py"
Cohesion: 0.06
Nodes (17): AdminDocumentDownloadView, _locations_queryset(), AcceptInvitationSerializer, InstituteProfileSerializer, Meta, InstituteSocialLinkSerializer, Meta, InvitationSerializer (+9 more)

### Community 9 - "enquiries/services.py"
Cohesion: 0.11
Nodes (10): TooManyRequests, change_status(), _claim_phone_slot(), counts(), _is_open_duplicate(), _require_accepting(), _require_open_for_enquiry(), submit_enquiry() (+2 more)

### Community 10 - "InvitationTests"
Cohesion: 0.07
Nodes (5): send_invitation_email(), InvitationTests, LocationTests, RegistrationOtpServiceTests, RemoveStaffTests

### Community 11 - "Category"
Cohesion: 0.11
Nodes (14): BaseModel, Meta, SlugModel, Meta, Category, Meta, _check_parent(), create_category() (+6 more)

### Community 12 - "Enquiry"
Cohesion: 0.21
Nodes (6): EnquiryStatus, EnquiryType, PreferredTime, Enquiry, Meta, SeatRaceTests

### Community 13 - "InstituteCEO"
Cohesion: 0.24
Nodes (5): InstituteCEOSerializer, Meta, PortalCEOView, InstituteCEO, save_ceo()

### Community 14 - ".as_"
Cohesion: 0.11
Nodes (3): CEOTests, ProfileTests, SummaryTests

### Community 15 - "training/models.py"
Cohesion: 0.10
Nodes (12): duration_q(), prefix_query(), TrainingFilter, Meta, DurationBucket, StartBucket, TrainingLevel, TrainingShift (+4 more)

### Community 16 - "FilterTests"
Cohesion: 0.08
Nodes (9): DetailTests, FilterOptionTests, FilterTests, PublicTrainingTestCase, QueryCountTests, SearchTests, ShiftsAreShownTests, titles() (+1 more)

### Community 17 - "helpers.py"
Cohesion: 0.14
Nodes (7): _duration(), get_upload_path(), get_uuid_filename(), membership_duration(), nested_getattr(), set_instance_fields(), update_instance()

### Community 20 - ".url"
Cohesion: 0.16
Nodes (4): AccessTests, DetailTests, NoteTests, PortalTestCase

### Community 21 - ".create"
Cohesion: 0.05
Nodes (10): ActionQueryCountTests, AdminApiTests, CoverTests, LifecycleTests, PortalCreateTests, PortalEditTests, PortalPermissionTests, PortalTestCase (+2 more)

### Community 22 - "common/validators.py"
Cohesion: 0.16
Nodes (9): combine_date_parts(), get_today(), validate_attachment(), validate_coded_phone_number(), validate_dob(), validate_future_datetime(), validate_is_future_datetime(), validate_otp() (+1 more)

### Community 23 - "enquiries/api/v1/views.py"
Cohesion: 0.08
Nodes (14): PortalEnquiryFilter, Meta, EnquiryNoteSerializer, Meta, NepalMobileField, PortalEnquiryListSerializer, Meta, PortalEnquirySerializer (+6 more)

### Community 27 - "training/api/v1/serializers.py"
Cohesion: 0.05
Nodes (23): AdminTrainingSerializer, Meta, available_categories(), CoverSerializer, duration_text(), format_class_days(), LearningOutcomeSerializer, Meta (+15 more)

### Community 28 - "EditTests"
Cohesion: 0.06
Nodes (7): CreateTests, EditTests, ExpiryTests, ReviewTests, SubmitTests, TrainingTestCase, TransitionTableTests

### Community 29 - "test_locations.py"
Cohesion: 0.33
Nodes (3): level_counts(), load(), LoadLocationsTests

### Community 31 - "SubmitTests"
Cohesion: 0.14
Nodes (4): NoVisitorIdentityTests, PublicTestCase, SubmitTests, ThrottleTests

### Community 32 - "EnquiryCreateSerializer"
Cohesion: 0.14
Nodes (6): EnquiryCreateSerializer, Meta, VisitorEnquirySerializer, Meta, EnquiryCreateView, VisitorViewTests

### Community 34 - "PortalEnquiryNoteView"
Cohesion: 0.09
Nodes (17): PortalEnquiryNoteView, registration_open_q(), 1. In short, 2.1 Data (`apps/enquiries/models.py`), 2.2 Rules (`apps/enquiries/services.py`), 2.3 API (all under `/api/v1/`), 2.4 Changes outside the new app, 2.5 Tests (`apps/enquiries/tests/`) (+9 more)

### Community 35 - "AdminEnquiryTests"
Cohesion: 0.07
Nodes (3): AdminDashboardSummaryTests, AdminEnquiryTests, ControlPanelRoutesTests

### Community 40 - "Training"
Cohesion: 0.11
Nodes (11): _event(), institute_activity(), Training, Meta, annotate_institute_public_counts(), refresh_search_vectors(), expire_trainings(), refresh_category_trainings() (+3 more)

### Community 42 - "ActionRequiredTests"
Cohesion: 0.08
Nodes (3): ActionRequiredTests, CoverTests, DocumentAndGalleryTests

### Community 45 - "AdminInstituteViewSet"
Cohesion: 0.05
Nodes (11): DynamicFieldsSerializer, AdminEnquiryListSerializer, Meta, AdminInstituteListSerializer, Meta, AdminTrainingFeaturedSerializer, ReasonSerializer, AdminEnquiryViewSet (+3 more)

### Community 46 - "create_admin"
Cohesion: 0.13
Nodes (5): create_admin(), _set_permissions(), update_admin(), AdminApiTests, StatusApiTests

### Community 47 - "PortalTestCase"
Cohesion: 0.18
Nodes (4): EndToEndTests, PermissionMatrixTests, PortalTestCase, ResubmitTests

### Community 50 - "validate_phone_number"
Cohesion: 0.29
Nodes (4): ValidatePanVatNumberTests, ValidatePhoneNumberTests, validate_pan_vat_number(), validate_phone_number()

### Community 54 - "Open questions (section 8)"
Cohesion: 0.22
Nodes (10): Entity: InstituteMember (one institute per user), Auth: email + password, JWT RS256 via simplejwt, Open questions (section 8), Open question: how an admin's password is reset, Open question: endpoint that consumes a verified password-reset code, Open question: where the frontend stores access/refresh tokens, Roles and grantable Django permissions (users.manage_*), Entity: User (+2 more)

### Community 55 - "Product Requirements Document (PRD)"
Cohesion: 0.25
Nodes (10): Phase 2: Application (approve/reject/capacity) and learners, My enquiries: browser device token, last 90 days, Open question: do institutes keep enquiries after 90 days, Reviews and ratings out of MVP, Workflow: enquiry (planned), Product Requirements Document (PRD), PRD training enquiry rules (captcha, rate limit, 90-day My enquiries), PRD later phase: applications, reviews and ratings (+2 more)

### Community 56 - "Role"
Cohesion: 0.17
Nodes (5): InstituteActionRequiredView, InstituteSummaryView, IsInstituteMember, IsInstituteOwner, Role

### Community 58 - "Entity: Institute"
Cohesion: 0.28
Nodes (9): Entity: Institute, Entity: InstituteCEO, Entity: InstituteContact, Entity: InstituteDocument, Entity: InstituteGalleryImage, Institute profile split: columns plus contact, CEO, social-link tables, Entity: InstituteSocialLink, Institute types: fixed list of seven (+1 more)

### Community 60 - "Core entities (section 3)"
Cohesion: 0.38
Nodes (6): Core entities (section 3), Entity: InstituteLocation (office), Entity: Location, Managed Nepal location list (province / district / municipality), Entity: TrainingLocation (venue), PRD institute locations (several, one main office)

### Community 61 - "users/services.py"
Cohesion: 0.11
Nodes (10): change_password(), normalize_email(), _otp_keys(), _revoke_refresh_tokens(), send_otp(), send_password_reset_otp(), send_registration_otp(), set_status() (+2 more)

### Community 69 - "System Design (DRAFT v0.6)"
Cohesion: 0.17
Nodes (7): System Design (DRAFT v0.6), Django apps and their state (section 2), Proposed: AuditLog (append-only), not built, Decision log (answered questions), Decisions made (section 1), Non-functional requirements (section 6), Training mode: PHYSICAL or ONLINE

### Community 70 - "Entity: Training"
Cohesion: 0.17
Nodes (12): Categories: two-level tree with icon and hue, training uses a leaf, Entity: Category, Entity: LearningOutcome, Entity: Training, Entity: TrainingContact, Entity: TrainingDetail, Training duration (value + unit, derived weeks) and weekly class slots, Entity: TrainingModule (+4 more)

### Community 71 - "register"
Cohesion: 0.22
Nodes (8): register(), consume_otp(), Entity: InstituteInvitation, Institute registration: one JSON request creates institute, owner, contact, locations, Institute status workflow: PENDING, APPROVED, REJECTED, INFO_REQUESTED, SUSPENDED, One-time codes (OTP): six digits, 5 minutes, Redis only, Staff invitations: 7-day token, hash stored, email queued after commit, Workflow: institute onboarding

### Community 72 - "control_panel/api/v1/serializers.py"
Cohesion: 0.06
Nodes (25): AdminEnquiryFilter, Meta, AdminInstituteFilter, Meta, AdminTrainingFilter, Meta, ChoiceInFilter, AdminDashboardSummarySerializer (+17 more)

### Community 73 - "institutes/api/v1/serializers.py"
Cohesion: 0.06
Nodes (27): DynamicFieldsModelSerializer, AdminInstituteSerializer, Meta, EnquiryCountsSerializer, GalleryImageSerializer, Meta, InstituteActionRequiredSerializer, InstituteContactSerializer (+19 more)

### Community 76 - "OTPPurpose"
Cohesion: 0.33
Nodes (6): OTPPurpose, send_otp_email(), send_registration_otp_email(), _deliver_otp(), send_otp_email_task(), send_registration_otp_email_task()

### Community 79 - "institutes/models.py"
Cohesion: 0.13
Nodes (9): _owner_prefetch(), InstituteType, InvitationStatus, MemberRole, InstituteContact, InstituteInvitation, Meta, InstituteMember (+1 more)

### Community 80 - "Location"
Cohesion: 0.17
Nodes (11): LocationFilter, Meta, active_municipalities(), LocationSerializer, Meta, build_tree(), LocationViewSet, LocationLevel (+3 more)

### Community 82 - "users/api/v1/serializers.py"
Cohesion: 0.11
Nodes (5): NormalizedEmailSerializer, RegistrationOTPSerializer, RegistrationOTPVerifySerializer, SendOTPSerializer, VerifyOTPSerializer

### Community 84 - "institutes/validators.py"
Cohesion: 0.83
Nodes (3): validate_document_file(), validate_image_file(), _validate_upload()

### Community 85 - "HasPlatformPermission"
Cohesion: 0.24
Nodes (4): HasAnyPlatformPermission, HasPlatformPermission, IsInstituteStaff, IsPlatformAdmin

### Community 87 - "IdentityScopedRateThrottle"
Cohesion: 0.15
Nodes (6): IdentityScopedRateThrottle, ActionAPIView, RegisterSendOTPView, RegisterVerifyOTPView, SendOTPView, VerifyOTPView

### Community 88 - "Entity: Enquiry (planned)"
Cohesion: 0.40
Nodes (5): Availability: seats minus CONVERTED enquiries above zero, Entity: Enquiry (planned), Open question: PRD 'Instructor Name' search has no field, Search: PostgreSQL full-text, simple config, word-prefix match, PRD search and discovery filters

### Community 90 - "Training status workflow: DRAFT, SUBMITTED, APPROVED, CHANGES_REQUESTED, REJECTED, UNPUBLISHED, CANCELLED, EXPIRED"
Cohesion: 0.50
Nodes (3): Training expiry: daily expire_trainings job sets EXPIRED after end_date, Training status workflow: DRAFT, SUBMITTED, APPROVED, CHANGES_REQUESTED, REJECTED, UNPUBLISHED, CANCELLED, EXPIRED, Workflow: training lifecycle

### Community 97 - "build_category_tree"
Cohesion: 0.25
Nodes (3): build_category_tree(), CategoryTreeView, LocationTreeView

### Community 102 - "CategoryConstraintTests"
Cohesion: 0.13
Nodes (3): CategoryConstraintTests, CategoryServiceTests, LoadCategoriesTests

### Community 104 - "InstituteGalleryImage"
Cohesion: 0.13
Nodes (9): PublicInstituteDetailSerializer, Meta, PublicInstituteListSerializer, Meta, PublicInstituteViewSet, InstituteGalleryImage, Meta, annotate_profile_completion() (+1 more)

### Community 105 - "ServiceTestCase"
Cohesion: 0.25
Nodes (3): NoteTests, ServiceTestCase, SummaryTests

### Community 106 - "users/api/v1/views.py"
Cohesion: 0.14
Nodes (7): LoginSerializer, ProfileSerializer, Meta, LoginView, LogoutView, MeView, RefreshView

### Community 107 - "UpdateStatusSerializer"
Cohesion: 0.25
Nodes (4): UpdateStatusSerializer, Meta, PasswordChangeView, UserStatusView

### Community 111 - "PublicTrainingViewSet"
Cohesion: 0.08
Nodes (12): DeleteTrainingTests, PortalTrainingListSerializer, Meta, as_options(), PortalTrainingViewSet, PublicTrainingViewSet, transition(), run() (+4 more)

### Community 120 - "InstituteRegistrationSerializer"
Cohesion: 0.20
Nodes (4): LocationInputSerializer, InstituteRegistrationSerializer, Meta, VenueSerializer

## Ambiguous Edges - Review These
- `PRD training modes: Physical, Online, Hybrid` → `Decision: hybrid mode dropped (2026-10-13)`  [AMBIGUOUS]
  docs/Training for Merojob (PRD).md · relation: conceptually_related_to
- `PRD institute locations (several, one main office)` → `Training venue: exactly one TrainingLocation, independent of institute offices`  [AMBIGUOUS]
  docs/Training for Merojob (PRD).md · relation: conceptually_related_to

## Knowledge Gaps
- **21 isolated node(s):** `Dependency: djangorestframework-simplejwt 5.5.1 (with PyJWT crypto)`, `Entity: InstituteGalleryImage`, `Institute types: fixed list of seven`, `Managed Nepal location list (province / district / municipality)`, `Django apps and their state (section 2)` (+16 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 729 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **61 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Training` connect `Training` to `AdminInstitutesApiTests`, `institutes/services.py`, `training/services.py`, `institutes/api/v1/views.py`, `enquiries/services.py`, `Category`, `Enquiry`, `training/models.py`, `FilterTests`, `.create`, `enquiries/api/v1/views.py`, `training/api/v1/serializers.py`, `EditTests`, `EnquiryCreateSerializer`, `AdminEnquiryTests`, `SubmitTests`, `AdminInstituteViewSet`, `AdminTrainingsFeaturedAndReviewApiTests`, `Role`, `TrainingConstraintTests`, `PortalTrainingSerializer`, `control_panel/api/v1/serializers.py`, `institutes/models.py`, `AdminDashboardSummaryView`, `PublicTrainingViewSet`?**
  _High betweenness centrality (0.125) - this node is a cross-community bridge._
- **Are the 56 inferred relationships involving `Training` (e.g. with `AdminTrainingFilter` and `institute_activity()`) actually correct?**
  _`Training` has 56 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Dependency: djangorestframework-simplejwt 5.5.1 (with PyJWT crypto)`, `Entity: InstituteGalleryImage`, `Institute types: fixed list of seven` to the rest of the system?**
  _21 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `AdminInstitutesApiTests` be split into smaller, more focused modules?**
  _Cohesion score 0.07435897435897436 - nodes in this community are weakly interconnected._
- **Why does `InstituteStatus` connect `institutes/services.py` to `RegistrationTests`, `AdminInstitutesApiTests`, `training/services.py`, `RegistrationApiTests`, `institutes/api/v1/views.py`, `enquiries/services.py`, `Enquiry`, `.as_`, `training/models.py`, `FilterTests`, `.create`, `enquiries/api/v1/views.py`, `PublicInstituteApiTests`, `AdminApiTests`, `EditTests`, `SubmitTests`, `EnquiryCreateSerializer`, `AdminEnquiryTests`, `SubmitTests`, `Training`, `AdminInstituteViewSet`, `PortalTestCase`, `WorkflowTests`, `AdminTrainingsFeaturedAndReviewApiTests`, `control_panel/api/v1/serializers.py`, `institutes/models.py`, `InstituteGalleryImage`, `PublicTrainingViewSet`?**
  _High betweenness centrality (0.106) - this node is a cross-community bridge._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `PRD training modes: Physical, Online, Hybrid` and `Decision: hybrid mode dropped (2026-10-13)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `PRD institute locations (several, one main office)` and `Training venue: exactly one TrainingLocation, independent of institute offices`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._