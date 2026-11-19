# Graph Report - traininghub-backend  (2026-11-19)

## Corpus Check
- 118 files · ~72,347 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 3)

## Summary
- 2194 nodes · 5057 edges · 136 communities (65 shown, 71 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 660 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `4902434e`
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
- enquiries/tests/test_services.py
- InvitationTests
- Category
- SeatRaceTests
- InstituteCEO
- .as_
- training/models.py
- FilterTests
- helpers.py
- settings/base.py
- .url
- .create
- common/validators.py
- Enquiry
- PublicInstituteApiTests
- AdminApiTests
- ActionRequiredTests
- training/api/v1/serializers.py
- EditTests
- LoadLocationsTests
- fields.py
- enquiries/tests/test_api_public.py
- CreateTests
- LocationModelTests
- change_status
- AdminEnquiryTests
- UserManager
- v1/permissions.py
- SubmitTests
- ContactTests
- Training
- OtpApiTests
- .png
- User
- EnquiryConstraintTests
- AdminInstituteViewSet
- create_admin
- PortalTestCase
- InvitationTests
- models/base.py
- validate_phone_number
- add_location
- ChangeStatusTests
- AdminTrainingsFeaturedAndReviewApiTests
- Open questions (section 8)
- Product Requirements Document (PRD)
- IsInstituteMember
- django_core_cache
- Entity: Institute
- TrainingConstraintTests
- EnquiryNote
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
- Workflow: institute onboarding
- control_panel/api/v1/serializers.py
- institutes/api/v1/serializers.py
- GalleryTests
- SocialLinkTests
- notification/services.py
- AdminCategoryApiTests
- rest_framework_permissions
- institutes/tests/test_api_portal.py
- Location
- InstituteProfileSerializer
- users/api/v1/serializers.py
- django_db
- Notification
- HasPlatformPermission
- StatusChangeTests
- IdentityScopedRateThrottle
- Entity: Enquiry (planned)
- InstituteConstraintTests
- Training status workflow: DRAFT, SUBMITTED, APPROVED, CHANGES_REQUESTED, REJECTED, UNPUBLISHED, CANCELLED, EXPIRED
- Dependency: Django 5.2.4
- Dependency: django-q2 1.8.0
- Dependency: django-redis 6.0.0
- Dependency: djangorestframework 3.16.0
- Dev extras: debug toolbar, django-extensions, ipdb, ipython, fabric3, pylint
- common/api/v1/views.py
- AdminSerializer
- InstituteAdminSiteTests
- institute_experience
- ListTests
- test_categories.py
- AuthApiTests
- Institute
- ServiceTestCase
- users/api/v1/views.py
- UpdateStatusSerializer
- control_panel/api/v1/views.py
- PrivateStorage
- notify
- PublicTrainingViewSet
- AdminTrainingViewSet
- StableOrderingFilter
- InstituteCoverSerializer
- expire_trainings.py
- DynamicFieldsSerializer
- AdminTrainingSerializer
- TrainingSession
- institutes/models.py
- InstituteRegistrationSerializer
- PortalGalleryViewSet
- NotificationViewset
- NotificationApiTests
- InstituteReviewEventTests
- BaseViewSet
- delete_training
- DynamicFieldsModelSerializer
- CategoryConstraintTests
- AdminInstituteListSerializer
- InstituteDocumentSerializer
- CategoryTreeApiTests
- PortalDocumentDownloadView
- resubmit
- emails.py
- purge_old

## God Nodes (most connected - your core abstractions)
1. `Training` - 84 edges
2. `Institute` - 65 edges
3. `InstituteStatus` - 62 edges
4. `AdminInstitutesApiTests` - 52 edges
5. `Enquiry` - 50 edges
6. `TrainingStatus` - 50 edges
7. `RegistrationApiTests` - 49 edges
8. `Role` - 46 edges
9. `DynamicFieldsModelSerializer` - 40 edges
10. `BaseModel` - 34 edges

## Surprising Connections (you probably didn't know these)
- `Decision: PAN/VAT number unique, nine digits, contact telephone optional` --references--> `validate_pan_vat_number()`  [EXTRACTED]
  docs/System Design.md → apps/common/validators.py
- `2.1 Data (`apps/enquiries/models.py`)` --references--> `Enquiry`  [INFERRED]
  docs/enquiries-status.md → apps/enquiries/models.py
- `2.2 Rules (`apps/enquiries/services.py`)` --references--> `submit_enquiry()`  [INFERRED]
  docs/enquiries-status.md → apps/enquiries/services.py
- `4.3 Backend work not done` --references--> `change_status()`  [INFERRED]
  docs/enquiries-status.md → apps/enquiries/services.py
- `Institute registration: one JSON request creates institute, owner, contact, locations` --references--> `register()`  [INFERRED]
  docs/System Design.md → apps/institutes/services.py

## Import Cycles
- None detected.

## Communities (136 total, 71 thin omitted)

### Community 2 - "institutes/services.py"
Cohesion: 0.09
Nodes (26): InstituteGalleryImage, Meta, add_gallery_image(), add_social_link(), annotate_profile_completion(), approve(), _at_least(), _check_platform_free() (+18 more)

### Community 3 - "training/services.py"
Cohesion: 0.08
Nodes (41): TrainingMode, TrainingStatus, LearningOutcome, Meta, TrainingContact, TrainingDetail, Meta, TrainingLocation (+33 more)

### Community 4 - "viewsets.py"
Cohesion: 0.19
Nodes (19): CreateListDestroyViewSet, CreateListRetrieveUpdateViewSet, CreateListUpdateDestroyViewSet, CreateListUpdateViewSet, CreateListViewSet, CreateRetrieveUpdateViewSet, CreateRetrieveViewSet, CreateUpdateViewSet (+11 more)

### Community 8 - "institutes/api/v1/views.py"
Cohesion: 0.09
Nodes (9): AcceptInvitationSerializer, InstituteActionRequiredSerializer, InstituteSummarySerializer, InvitationSerializer, Meta, AcceptInvitationView, InstituteActionRequiredView, InstituteSummaryView (+1 more)

### Community 9 - "enquiries/tests/test_services.py"
Cohesion: 0.11
Nodes (12): TooManyRequests, EnquiryStatus, EnquiryType, PreferredTime, admin_counts(), _claim_phone_slot(), counts(), _require_accepting() (+4 more)

### Community 10 - "InvitationTests"
Cohesion: 0.09
Nodes (3): InvitationTests, LocationTests, RegistrationOtpServiceTests

### Community 11 - "Category"
Cohesion: 0.22
Nodes (7): Category, Meta, _check_parent(), create_category(), update_category(), AdminCategorySerializer, Meta

### Community 13 - "InstituteCEO"
Cohesion: 0.24
Nodes (5): InstituteCEOSerializer, Meta, PortalCEOView, InstituteCEO, save_ceo()

### Community 14 - ".as_"
Cohesion: 0.09
Nodes (4): CEOTests, ProfileTests, StaffTests, SummaryTests

### Community 15 - "training/models.py"
Cohesion: 0.08
Nodes (14): duration_q(), prefix_query(), TrainingFilter, Meta, DurationBucket, DurationUnit, StartBucket, TrainingLevel (+6 more)

### Community 16 - "FilterTests"
Cohesion: 0.09
Nodes (8): FilterOptionTests, FilterTests, PublicTrainingTestCase, QueryCountTests, SearchTests, ShiftsAreShownTests, titles(), VisibilityTests

### Community 17 - "helpers.py"
Cohesion: 0.18
Nodes (5): get_upload_path(), get_uuid_filename(), nested_getattr(), set_instance_fields(), update_instance()

### Community 20 - ".url"
Cohesion: 0.16
Nodes (4): AccessTests, DetailTests, NoteTests, PortalTestCase

### Community 21 - ".create"
Cohesion: 0.05
Nodes (10): ActionQueryCountTests, AdminApiTests, CoverTests, LifecycleTests, PortalCreateTests, PortalEditTests, PortalPermissionTests, PortalTestCase (+2 more)

### Community 22 - "common/validators.py"
Cohesion: 0.16
Nodes (9): combine_date_parts(), get_today(), validate_attachment(), validate_coded_phone_number(), validate_dob(), validate_future_datetime(), validate_is_future_datetime(), validate_otp() (+1 more)

### Community 23 - "Enquiry"
Cohesion: 0.07
Nodes (14): PortalEnquiryFilter, Meta, EnquiryCreateSerializer, Meta, NepalMobileField, PortalEnquiryListSerializer, Meta, PortalEnquirySerializer (+6 more)

### Community 27 - "training/api/v1/serializers.py"
Cohesion: 0.06
Nodes (19): LocationInputSerializer, validate_document_file(), validate_image_file(), _validate_upload(), available_categories(), CoverSerializer, duration_text(), format_class_days() (+11 more)

### Community 28 - "EditTests"
Cohesion: 0.08
Nodes (5): EditTests, ExpiryTests, ReviewTests, TrainingTestCase, TransitionTableTests

### Community 31 - "enquiries/tests/test_api_public.py"
Cohesion: 0.11
Nodes (7): VisitorEnquirySerializer, Meta, NoVisitorIdentityTests, PublicTestCase, SubmitTests, ThrottleTests, VisitorViewTests

### Community 34 - "change_status"
Cohesion: 0.11
Nodes (15): change_status(), _is_open_duplicate(), 1. In short, 2.2 Rules (`apps/enquiries/services.py`), 2.3 API (all under `/api/v1/`), 2.5 Tests (`apps/enquiries/tests/`), 2. What was built, 3. Where the build differs from the prototype (+7 more)

### Community 35 - "AdminEnquiryTests"
Cohesion: 0.07
Nodes (3): AdminDashboardSummaryTests, AdminEnquiryTests, ControlPanelRoutesTests

### Community 40 - "Training"
Cohesion: 0.13
Nodes (9): _event(), institute_activity(), Training, Meta, annotate_institute_public_counts(), refresh_category_trainings(), refresh_institute_trainings(), found() (+1 more)

### Community 46 - "create_admin"
Cohesion: 0.13
Nodes (5): create_admin(), _set_permissions(), update_admin(), AdminApiTests, StatusApiTests

### Community 47 - "PortalTestCase"
Cohesion: 0.15
Nodes (4): EndToEndTests, PermissionMatrixTests, PortalTestCase, ResubmitTests

### Community 49 - "models/base.py"
Cohesion: 0.21
Nodes (4): SlugModel, Meta, _slug_strip(), unique_slugify()

### Community 50 - "validate_phone_number"
Cohesion: 0.29
Nodes (4): ValidatePanVatNumberTests, ValidatePhoneNumberTests, validate_pan_vat_number(), validate_phone_number()

### Community 54 - "Open questions (section 8)"
Cohesion: 0.29
Nodes (8): Auth: email + password, JWT RS256 via simplejwt, Open questions (section 8), Open question: how an admin's password is reset, Open question: endpoint that consumes a verified password-reset code, Open question: where the frontend stores access/refresh tokens, Roles and grantable Django permissions (users.manage_*), PRD target users: Learner, Training Provider, Administrator, Dependency: djangorestframework-simplejwt 5.5.1 (with PyJWT crypto)

### Community 55 - "Product Requirements Document (PRD)"
Cohesion: 0.25
Nodes (10): Phase 2: Application (approve/reject/capacity) and learners, My enquiries: browser device token, last 90 days, Open question: do institutes keep enquiries after 90 days, Reviews and ratings out of MVP, Workflow: enquiry (planned), Product Requirements Document (PRD), PRD training enquiry rules (captcha, rate limit, 90-day My enquiries), PRD later phase: applications, reviews and ratings (+2 more)

### Community 56 - "IsInstituteMember"
Cohesion: 0.17
Nodes (7): PortalDocumentViewSet, PortalInvitationViewSet, PortalSocialLinkViewSet, PortalStaffViewSet, InstituteScopedMixin, IsInstituteMember, IsInstituteOwner

### Community 58 - "Entity: Institute"
Cohesion: 0.17
Nodes (15): Core entities (section 3), Entity: Institute, Entity: InstituteCEO, Entity: InstituteContact, Entity: InstituteGalleryImage, Entity: InstituteLocation (office), Entity: InstituteMember (one institute per user), Institute profile split: columns plus contact, CEO, social-link tables (+7 more)

### Community 60 - "EnquiryNote"
Cohesion: 0.15
Nodes (8): EnquiryNoteSerializer, Meta, PortalEnquiryNoteView, EnquiryNote, Meta, add_note(), 2.1 Data (`apps/enquiries/models.py`), 4.4 Risks and limits to know about

### Community 61 - "users/services.py"
Cohesion: 0.10
Nodes (17): OTPPurpose, change_password(), get_otp(), normalize_email(), _otp_keys(), _revoke_refresh_tokens(), send_otp(), send_otp_email() (+9 more)

### Community 62 - "PortalTrainingSerializer"
Cohesion: 0.21
Nodes (3): PortalTrainingSerializer, Meta, TrainingContentFields

### Community 69 - "System Design (DRAFT v0.6)"
Cohesion: 0.17
Nodes (7): System Design (DRAFT v0.6), Django apps and their state (section 2), Proposed: AuditLog (append-only), not built, Decision log (answered questions), Decisions made (section 1), Non-functional requirements (section 6), Training mode: PHYSICAL or ONLINE

### Community 70 - "Entity: Training"
Cohesion: 0.17
Nodes (12): Categories: two-level tree with icon and hue, training uses a leaf, Entity: Category, Entity: LearningOutcome, Entity: Training, Entity: TrainingContact, Entity: TrainingDetail, Training duration (value + unit, derived weeks) and weekly class slots, Entity: TrainingModule (+4 more)

### Community 71 - "Workflow: institute onboarding"
Cohesion: 0.29
Nodes (8): Entity: InstituteDocument, Entity: InstituteInvitation, Institute registration: one JSON request creates institute, owner, contact, locations, Institute status workflow: PENDING, APPROVED, REJECTED, INFO_REQUESTED, SUSPENDED, One-time codes (OTP): six digits, 5 minutes, Redis only, Staff invitations: 7-day token, hash stored, email queued after commit, Verification documents: private pdf/jpg/png up to 5 MB, Workflow: institute onboarding

### Community 72 - "control_panel/api/v1/serializers.py"
Cohesion: 0.12
Nodes (14): AdminDocumentSerializer, Meta, DashboardEnquiryCountsSerializer, DashboardInstituteCountsSerializer, DashboardTrainingCountsSerializer, DocumentReviewSerializer, AdminDocumentView, DocumentStatus (+6 more)

### Community 73 - "institutes/api/v1/serializers.py"
Cohesion: 0.07
Nodes (20): AdminInstituteSerializer, Meta, EnquiryCountsSerializer, InstituteContactSerializer, Meta, InstituteLocationSerializer, Meta, InstituteSocialLinkSerializer (+12 more)

### Community 76 - "notification/services.py"
Cohesion: 0.22
Nodes (6): Channel, EventType, NotificationDedupe, Meta, claim(), mark_seen()

### Community 80 - "Location"
Cohesion: 0.24
Nodes (8): LocationFilter, Meta, active_municipalities(), LocationLevel, MunicipalityType, Location, Meta, level_counts()

### Community 81 - "InstituteProfileSerializer"
Cohesion: 0.17
Nodes (5): InstituteProfileSerializer, Meta, InstituteProfileView, PortalContactView, ResubmitView

### Community 82 - "users/api/v1/serializers.py"
Cohesion: 0.11
Nodes (5): NormalizedEmailSerializer, OTPField, RegistrationOTPVerifySerializer, SendOTPSerializer, VerifyOTPSerializer

### Community 84 - "Notification"
Cohesion: 0.19
Nodes (5): NotificationSerializer, Meta, Notification, Meta, send_notification_email()

### Community 85 - "HasPlatformPermission"
Cohesion: 0.12
Nodes (8): AdminCategoryViewSet, AdminDocumentDownloadView, AdminEnquiryViewSet, AdminViewSet, HasAnyPlatformPermission, HasPlatformPermission, IsInstituteStaff, IsPlatformAdmin

### Community 87 - "IdentityScopedRateThrottle"
Cohesion: 0.11
Nodes (7): IdentityScopedRateThrottle, ActionAPIView, RegisterSendOTPView, RegisterVerifyOTPView, RegistrationOTPSerializer, SendOTPView, VerifyOTPView

### Community 88 - "Entity: Enquiry (planned)"
Cohesion: 0.40
Nodes (5): Availability: seats minus CONVERTED enquiries above zero, Entity: Enquiry (planned), Open question: PRD 'Instructor Name' search has no field, Search: PostgreSQL full-text, simple config, word-prefix match, PRD search and discovery filters

### Community 90 - "Training status workflow: DRAFT, SUBMITTED, APPROVED, CHANGES_REQUESTED, REJECTED, UNPUBLISHED, CANCELLED, EXPIRED"
Cohesion: 0.50
Nodes (3): Training expiry: daily expire_trainings job sets EXPIRED after end_date, Training status workflow: DRAFT, SUBMITTED, APPROVED, CHANGES_REQUESTED, REJECTED, UNPUBLISHED, CANCELLED, EXPIRED, Workflow: training lifecycle

### Community 97 - "common/api/v1/views.py"
Cohesion: 0.14
Nodes (7): LocationSerializer, Meta, build_category_tree(), build_tree(), CategoryTreeView, LocationTreeView, LocationViewSet

### Community 100 - "institute_experience"
Cohesion: 0.12
Nodes (8): InstituteExperienceTests, _duration(), institute_experience(), membership_duration(), PublicInstituteDetailSerializer, Meta, PublicInstituteListSerializer, Meta

### Community 104 - "Institute"
Cohesion: 0.16
Nodes (10): AdminInstituteFilter, Meta, ChoiceInFilter, PublicInstituteViewSet, InstituteStatus, InstituteType, Institute, Meta (+2 more)

### Community 105 - "ServiceTestCase"
Cohesion: 0.25
Nodes (3): NoteTests, ServiceTestCase, SummaryTests

### Community 106 - "users/api/v1/views.py"
Cohesion: 0.14
Nodes (7): LoginSerializer, ProfileSerializer, Meta, LoginView, LogoutView, MeView, RefreshView

### Community 107 - "UpdateStatusSerializer"
Cohesion: 0.25
Nodes (4): UpdateStatusSerializer, Meta, PasswordChangeView, UserStatusView

### Community 108 - "control_panel/api/v1/views.py"
Cohesion: 0.08
Nodes (16): AdminCategoryFilter, Meta, AdminEnquiryFilter, Meta, AdminTrainingFilter, Meta, AdminDashboardSummarySerializer, AdminTrainingListSerializer (+8 more)

### Community 110 - "notify"
Cohesion: 0.18
Nodes (3): Event, notify(), NotifyTests

### Community 111 - "PublicTrainingViewSet"
Cohesion: 0.10
Nodes (8): as_options(), PortalTrainingViewSet, PublicTrainingViewSet, transition(), run(), with_content(), annotate_institute_training_count(), institute_counts()

### Community 114 - "InstituteCoverSerializer"
Cohesion: 0.25
Nodes (3): InstituteCoverSerializer, Meta, PortalCoverView

### Community 117 - "AdminTrainingSerializer"
Cohesion: 0.18
Nodes (6): AdminTrainingSerializer, Meta, LearningOutcomeSerializer, Meta, TrainingModuleSerializer, Meta

### Community 118 - "TrainingSession"
Cohesion: 0.20
Nodes (4): TrainingSession, Meta, DetailTests, TrainingSessionConstraintTests

### Community 119 - "institutes/models.py"
Cohesion: 0.13
Nodes (15): BaseModel, Meta, _owner_prefetch(), InvitationStatus, MemberRole, InstituteInvitation, Meta, InstituteMember (+7 more)

### Community 120 - "InstituteRegistrationSerializer"
Cohesion: 0.18
Nodes (4): InstituteRegistrationSerializer, Meta, register(), consume_otp()

### Community 121 - "PortalGalleryViewSet"
Cohesion: 0.24
Nodes (5): GalleryImageSerializer, Meta, GalleryReorderSerializer, PortalGalleryViewSet, PortalLocationViewSet

### Community 122 - "NotificationViewset"
Cohesion: 0.24
Nodes (4): NotificationViewset, mark_all_read(), mark_read(), unread_count()

### Community 126 - "delete_training"
Cohesion: 0.25
Nodes (4): DeleteTrainingTests, delete_training(), registration_open_q(), 2.4 Changes outside the new app

### Community 127 - "DynamicFieldsModelSerializer"
Cohesion: 0.25
Nodes (3): DynamicFieldsModelSerializer, AdminEnquiryListSerializer, Meta

## Ambiguous Edges - Review These
- `PRD training modes: Physical, Online, Hybrid` → `Decision: hybrid mode dropped (2026-10-13)`  [AMBIGUOUS]
  docs/Training for Merojob (PRD).md · relation: conceptually_related_to
- `PRD institute locations (several, one main office)` → `Training venue: exactly one TrainingLocation, independent of institute offices`  [AMBIGUOUS]
  docs/Training for Merojob (PRD).md · relation: conceptually_related_to

## Knowledge Gaps
- **21 isolated node(s):** `Dependency: djangorestframework-simplejwt 5.5.1 (with PyJWT crypto)`, `Entity: InstituteGalleryImage`, `Institute types: fixed list of seven`, `Managed Nepal location list (province / district / municipality)`, `Django apps and their state (section 2)` (+16 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 761 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **71 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Training` connect `Training` to `AdminInstitutesApiTests`, `training/services.py`, `institutes/api/v1/views.py`, `enquiries/tests/test_services.py`, `Category`, `training/models.py`, `FilterTests`, `.create`, `Enquiry`, `training/api/v1/serializers.py`, `EditTests`, `CreateTests`, `change_status`, `AdminEnquiryTests`, `SubmitTests`, `models/base.py`, `AdminTrainingsFeaturedAndReviewApiTests`, `TrainingConstraintTests`, `PortalTrainingSerializer`, `control_panel/api/v1/serializers.py`, `institutes/tests/test_api_portal.py`, `Institute`, `control_panel/api/v1/views.py`, `PublicTrainingViewSet`, `AdminTrainingViewSet`, `AdminTrainingSerializer`, `TrainingSession`, `institutes/models.py`, `delete_training`?**
  _High betweenness centrality (0.132) - this node is a cross-community bridge._
- **Are the 56 inferred relationships involving `Training` (e.g. with `AdminTrainingFilter` and `institute_activity()`) actually correct?**
  _`Training` has 56 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Dependency: djangorestframework-simplejwt 5.5.1 (with PyJWT crypto)`, `Entity: InstituteGalleryImage`, `Institute types: fixed list of seven` to the rest of the system?**
  _21 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `AdminInstitutesApiTests` be split into smaller, more focused modules?**
  _Cohesion score 0.07422402159244265 - nodes in this community are weakly interconnected._
- **Why does `InstituteStatus` connect `Institute` to `RegistrationTests`, `AdminInstitutesApiTests`, `institutes/services.py`, `training/services.py`, `resubmit`, `RegistrationApiTests`, `institutes/api/v1/views.py`, `enquiries/tests/test_services.py`, `.as_`, `training/models.py`, `FilterTests`, `.create`, `Enquiry`, `PublicInstituteApiTests`, `AdminApiTests`, `enquiries/tests/test_api_public.py`, `CreateTests`, `AdminEnquiryTests`, `SubmitTests`, `Training`, `AdminInstituteViewSet`, `PortalTestCase`, `add_location`, `AdminTrainingsFeaturedAndReviewApiTests`, `control_panel/api/v1/serializers.py`, `institutes/tests/test_api_portal.py`, `control_panel/api/v1/views.py`, `PublicTrainingViewSet`, `institutes/models.py`, `InstituteReviewEventTests`?**
  _High betweenness centrality (0.093) - this node is a cross-community bridge._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `PRD training modes: Physical, Online, Hybrid` and `Decision: hybrid mode dropped (2026-10-13)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `PRD institute locations (several, one main office)` and `Training venue: exactly one TrainingLocation, independent of institute offices`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._