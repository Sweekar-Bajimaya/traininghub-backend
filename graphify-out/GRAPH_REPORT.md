# Graph Report - traininghub-backend  (2026-11-03)

## Corpus Check
- 102 files · ~63,419 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 3)

## Summary
- 1949 nodes · 4413 edges · 119 communities (69 shown, 50 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 567 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `6cb696bd`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- StatusApiTests
- .summary
- institutes/services.py
- training/services.py
- viewsets.py
- InstituteContactSerializer
- RegistrationApiTests
- RegistrationOtpApiTests
- institutes/api/v1/views.py
- TooManyRequests
- RegistrationTests
- training/tests/test_api_public.py
- institutes/constants.py
- PortalTrainingViewSet
- .as_
- training/models.py
- FilterTests
- LocationSerializer
- settings/base.py
- .url
- .create
- common/validators.py
- Enquiry
- AdminTrainingSerializer
- AdminApiTests
- BaseModel
- PublicTrainingListSerializer
- EditTests
- LocationModelTests
- control_panel/api/v1/serializers.py
- SubmitTests
- enquiries/api/v1/views.py
- DynamicFieldsSerializer
- 4. What needs changes
- AdminEnquiryTests
- users/models.py
- fields.py
- SubmitTests
- ContactTests
- Training
- OtpApiTests
- ActionRequiredTests
- PortalEditTests
- EnquiryConstraintTests
- AdminTrainingViewSet
- users/services.py
- helpers.py
- InvitationTests
- models/base.py
- validate_phone_number
- Meta
- register
- TrainingStatus
- Open questions (section 8)
- Product Requirements Document (PRD)
- IsInstituteMember
- Location
- Entity: Institute
- TrainingConstraintTests
- Core entities (section 3)
- OTPPurpose
- PortalTestCase
- LocationTests
- UserConstraintTests
- PublicInstituteApiTests
- LocationApiTests
- DocumentTests
- InstituteRegistrationSerializer
- System Design (DRAFT v0.6)
- Entity: Training
- Workflow: institute onboarding
- InstituteConstraintTests
- DynamicFieldsModelSerializer
- GalleryTests
- SocialLinkTests
- expire_trainings
- AdminCategoryApiTests
- ActiveAccountJWTAuthentication
- institutes/tests/test_api_portal.py
- CategoryTreeView
- InstituteProfileSerializer
- NormalizedEmailSerializer
- add_location
- institutes/models.py
- control_panel/api/v1/views.py
- common/services.py
- IdentityScopedRateThrottle
- Entity: Enquiry (planned)
- InstituteDocumentSerializer
- Training status workflow: DRAFT, SUBMITTED, APPROVED, CHANGES_REQUESTED, REJECTED, UNPUBLISHED, CANCELLED, EXPIRED
- Dependency: Django 5.2.4
- Dependency: django-q2 1.8.0
- Dependency: django-redis 6.0.0
- Dependency: djangorestframework 3.16.0
- Dev extras: debug toolbar, django-extensions, ipdb, ipython, fabric3, pylint
- BaseViewSet
- AdminSerializer
- InstituteAdminSiteTests
- StatusChangeTests
- ListTests
- CategoryConstraintTests
- AdminApiTests
- PublicInstituteListSerializer
- AdminApiTests
- users/api/v1/views.py
- VisitorEnquirySerializer
- load_categories.py
- PortalCoverView
- StartDateRangeTests
- EnquiryNote
- SendOTPSerializer
- InstituteActionRequiredView
- ActionQueryCountTests
- InstituteExperienceTests
- PortalTestCase
- institutes/api/v1/serializers.py
- SummaryTests

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
- `4.3 Backend work not done` --references--> `change_status()`  [INFERRED]
  docs/enquiries-status.md → apps/enquiries/services.py
- `Decision: PAN/VAT number unique, nine digits, contact telephone optional` --references--> `validate_pan_vat_number()`  [EXTRACTED]
  docs/System Design.md → apps/common/validators.py
- `2.1 Data (`apps/enquiries/models.py`)` --references--> `Enquiry`  [INFERRED]
  docs/enquiries-status.md → apps/enquiries/models.py
- `Institute registration: one JSON request creates institute, owner, contact, locations` --references--> `register()`  [INFERRED]
  docs/System Design.md → apps/institutes/services.py
- `2.4 Changes outside the new app` --references--> `delete_training()`  [INFERRED]
  docs/enquiries-status.md → apps/training/services.py

## Import Cycles
- None detected.

## Communities (119 total, 50 thin omitted)

### Community 2 - "institutes/services.py"
Cohesion: 0.10
Nodes (33): PublicInstituteViewSet, InstituteStatus, Institute, Meta, InstituteGalleryImage, Meta, InstituteLocation, Meta (+25 more)

### Community 3 - "training/services.py"
Cohesion: 0.12
Nodes (21): LearningOutcome, Meta, TrainingContact, TrainingLocation, TrainingModule, Meta, _build_search_vector(), _check_category() (+13 more)

### Community 4 - "viewsets.py"
Cohesion: 0.19
Nodes (19): CreateListDestroyViewSet, CreateListRetrieveUpdateViewSet, CreateListUpdateDestroyViewSet, CreateListUpdateViewSet, CreateListViewSet, CreateRetrieveUpdateViewSet, CreateRetrieveViewSet, CreateUpdateViewSet (+11 more)

### Community 5 - "InstituteContactSerializer"
Cohesion: 0.11
Nodes (10): AdminInstituteSerializer, Meta, InstituteCEOSerializer, Meta, InstituteContactSerializer, Meta, InstituteLocationSerializer, Meta (+2 more)

### Community 8 - "institutes/api/v1/views.py"
Cohesion: 0.11
Nodes (6): AcceptInvitationSerializer, AcceptInvitationView, PortalCEOView, PortalDocumentDownloadView, private_file_response(), RegisterView

### Community 10 - "RegistrationTests"
Cohesion: 0.07
Nodes (4): InvitationTests, LocationTests, RegistrationOtpServiceTests, RegistrationTests

### Community 11 - "training/tests/test_api_public.py"
Cohesion: 0.13
Nodes (7): TrainingDetail, Meta, TrainingSession, Meta, DetailTests, QueryCountTests, TrainingSessionConstraintTests

### Community 12 - "institutes/constants.py"
Cohesion: 0.15
Nodes (13): InvitationStatus, MemberRole, InstituteInvitation, Meta, InstituteMember, Meta, accept_invitation(), _hash() (+5 more)

### Community 13 - "PortalTrainingViewSet"
Cohesion: 0.11
Nodes (8): as_options(), PortalTrainingViewSet, PublicTrainingViewSet, transition(), run(), with_content(), annotate_institute_training_count(), institute_counts()

### Community 14 - ".as_"
Cohesion: 0.11
Nodes (3): CEOTests, ProfileTests, StaffTests

### Community 15 - "training/models.py"
Cohesion: 0.10
Nodes (13): duration_q(), prefix_query(), TrainingFilter, Meta, DurationBucket, DurationUnit, StartBucket, TrainingLevel (+5 more)

### Community 16 - "FilterTests"
Cohesion: 0.09
Nodes (7): FilterOptionTests, FilterTests, PublicTrainingTestCase, SearchTests, ShiftsAreShownTests, titles(), VisibilityTests

### Community 17 - "LocationSerializer"
Cohesion: 0.33
Nodes (3): LocationSerializer, Meta, LocationViewSet

### Community 20 - ".url"
Cohesion: 0.12
Nodes (5): AccessTests, DetailTests, NoteTests, PortalTestCase, SummaryTests

### Community 22 - "common/validators.py"
Cohesion: 0.16
Nodes (9): combine_date_parts(), get_today(), validate_attachment(), validate_coded_phone_number(), validate_dob(), validate_future_datetime(), validate_is_future_datetime(), validate_otp() (+1 more)

### Community 23 - "Enquiry"
Cohesion: 0.11
Nodes (15): EnquiryStatus, EnquiryType, PreferredTime, Enquiry, Meta, change_status(), _claim_phone_slot(), counts() (+7 more)

### Community 24 - "AdminTrainingSerializer"
Cohesion: 0.09
Nodes (11): AdminTrainingSerializer, Meta, LearningOutcomeSerializer, Meta, PortalTrainingSerializer, Meta, TrainingContentFields, TrainingModuleSerializer (+3 more)

### Community 26 - "BaseModel"
Cohesion: 0.13
Nodes (8): BaseModel, Meta, InstituteCEO, InstituteContact, InstituteSocialLink, Meta, annotate_profile_completion(), _at_least()

### Community 27 - "PublicTrainingListSerializer"
Cohesion: 0.12
Nodes (6): duration_text(), format_class_days(), PublicTrainingDetailSerializer, Meta, PublicTrainingListSerializer, Meta

### Community 28 - "EditTests"
Cohesion: 0.06
Nodes (7): CreateTests, EditTests, ExpiryTests, ReviewTests, SubmitTests, TrainingTestCase, TransitionTableTests

### Community 29 - "LocationModelTests"
Cohesion: 0.15
Nodes (3): load(), LoadLocationsTests, LocationModelTests

### Community 30 - "control_panel/api/v1/serializers.py"
Cohesion: 0.11
Nodes (9): AdminDocumentSerializer, Meta, AdminTrainingListSerializer, Meta, PortalTrainingListSerializer, Meta, LoginSerializer, ProfileSerializer (+1 more)

### Community 31 - "SubmitTests"
Cohesion: 0.14
Nodes (4): NoVisitorIdentityTests, PublicTestCase, SubmitTests, ThrottleTests

### Community 32 - "enquiries/api/v1/views.py"
Cohesion: 0.09
Nodes (12): PortalEnquiryFilter, Meta, EnquiryCreateSerializer, Meta, NepalMobileField, PortalEnquiryListSerializer, Meta, PortalEnquirySerializer (+4 more)

### Community 34 - "4. What needs changes"
Cohesion: 0.18
Nodes (10): 1. In short, 3. Where the build differs from the prototype, 4.1 Before it works end to end, 4.2 Frontend changes against the prototype, 4.3 Backend work not done, 4.4 Risks and limits to know about, 4.5 Questions still open (numbers as in `docs/System Design.md`, section 8), 4. What needs changes (+2 more)

### Community 36 - "users/models.py"
Cohesion: 0.14
Nodes (3): UserManager, User, Meta

### Community 37 - "fields.py"
Cohesion: 0.07
Nodes (4): DistributedKeyAuthentication, DistributedAppKey, Base64FieldMixin, Base64ImageField

### Community 38 - "SubmitTests"
Cohesion: 0.11
Nodes (5): ChangeStatusTests, NoteTests, ServiceTestCase, submit(), SubmitTests

### Community 40 - "Training"
Cohesion: 0.13
Nodes (9): Training, Meta, annotate_category_training_count(), annotate_institute_public_counts(), refresh_search_vectors(), refresh_category_trainings(), refresh_institute_trainings(), found() (+1 more)

### Community 42 - "ActionRequiredTests"
Cohesion: 0.08
Nodes (4): ActionRequiredTests, CoverTests, DocumentAndGalleryTests, CoverTests

### Community 45 - "AdminTrainingViewSet"
Cohesion: 0.20
Nodes (3): ReasonSerializer, AdminInstituteViewSet, AdminTrainingViewSet

### Community 46 - "users/services.py"
Cohesion: 0.18
Nodes (6): change_password(), create_admin(), _revoke_refresh_tokens(), _set_permissions(), set_status(), update_admin()

### Community 47 - "helpers.py"
Cohesion: 0.15
Nodes (7): _duration(), get_upload_path(), get_uuid_filename(), membership_duration(), nested_getattr(), set_instance_fields(), update_instance()

### Community 49 - "models/base.py"
Cohesion: 0.21
Nodes (4): SlugModel, Meta, _slug_strip(), unique_slugify()

### Community 50 - "validate_phone_number"
Cohesion: 0.29
Nodes (4): ValidatePanVatNumberTests, ValidatePhoneNumberTests, validate_pan_vat_number(), validate_phone_number()

### Community 52 - "register"
Cohesion: 0.16
Nodes (6): register(), consume_otp(), normalize_email(), _otp_keys(), send_otp(), send_registration_otp()

### Community 53 - "TrainingStatus"
Cohesion: 0.24
Nodes (13): DeleteTrainingTests, TrainingStatus, approve(), cancel(), delete_training(), reject(), republish(), request_changes() (+5 more)

### Community 54 - "Open questions (section 8)"
Cohesion: 0.22
Nodes (10): Entity: InstituteMember (one institute per user), Auth: email + password, JWT RS256 via simplejwt, Open questions (section 8), Open question: how an admin's password is reset, Open question: endpoint that consumes a verified password-reset code, Open question: where the frontend stores access/refresh tokens, Roles and grantable Django permissions (users.manage_*), Entity: User (+2 more)

### Community 55 - "Product Requirements Document (PRD)"
Cohesion: 0.25
Nodes (10): Phase 2: Application (approve/reject/capacity) and learners, My enquiries: browser device token, last 90 days, Open question: do institutes keep enquiries after 90 days, Reviews and ratings out of MVP, Workflow: enquiry (planned), Product Requirements Document (PRD), PRD training enquiry rules (captcha, rate limit, 90-day My enquiries), PRD later phase: applications, reviews and ratings (+2 more)

### Community 56 - "IsInstituteMember"
Cohesion: 0.13
Nodes (10): GalleryReorderSerializer, PortalDocumentViewSet, PortalGalleryViewSet, PortalInvitationViewSet, PortalLocationViewSet, PortalSocialLinkViewSet, PortalStaffViewSet, InstituteScopedMixin (+2 more)

### Community 57 - "Location"
Cohesion: 0.13
Nodes (10): LocationFilter, Meta, LocationLevel, MunicipalityType, Command, Location, Meta, clear_category_tree_cache() (+2 more)

### Community 58 - "Entity: Institute"
Cohesion: 0.38
Nodes (7): Entity: Institute, Entity: InstituteCEO, Entity: InstituteContact, Entity: InstituteGalleryImage, Institute profile split: columns plus contact, CEO, social-link tables, Entity: InstituteSocialLink, Institute types: fixed list of seven

### Community 60 - "Core entities (section 3)"
Cohesion: 0.38
Nodes (6): Core entities (section 3), Entity: InstituteLocation (office), Entity: Location, Managed Nepal location list (province / district / municipality), Entity: TrainingLocation (venue), PRD institute locations (several, one main office)

### Community 61 - "OTPPurpose"
Cohesion: 0.27
Nodes (7): OTPPurpose, get_otp(), send_otp_email(), send_registration_otp_email(), _deliver_otp(), send_otp_email_task(), send_registration_otp_email_task()

### Community 62 - "PortalTestCase"
Cohesion: 0.15
Nodes (5): LifecycleTests, PortalPermissionTests, PortalTestCase, QueryCountTests, SubmitNeedsShiftsTests

### Community 68 - "InstituteRegistrationSerializer"
Cohesion: 0.12
Nodes (5): InstituteRegistrationSerializer, Meta, OTPField, PasswordChangeSerializer, UserRegistrationSerializer

### Community 69 - "System Design (DRAFT v0.6)"
Cohesion: 0.17
Nodes (7): System Design (DRAFT v0.6), Django apps and their state (section 2), Proposed: AuditLog (append-only), not built, Decision log (answered questions), Decisions made (section 1), Non-functional requirements (section 6), Training mode: PHYSICAL or ONLINE

### Community 70 - "Entity: Training"
Cohesion: 0.17
Nodes (12): Categories: two-level tree with icon and hue, training uses a leaf, Entity: Category, Entity: LearningOutcome, Entity: Training, Entity: TrainingContact, Entity: TrainingDetail, Training duration (value + unit, derived weeks) and weekly class slots, Entity: TrainingModule (+4 more)

### Community 71 - "Workflow: institute onboarding"
Cohesion: 0.29
Nodes (8): Entity: InstituteDocument, Entity: InstituteInvitation, Institute registration: one JSON request creates institute, owner, contact, locations, Institute status workflow: PENDING, APPROVED, REJECTED, INFO_REQUESTED, SUSPENDED, One-time codes (OTP): six digits, 5 minutes, Redis only, Staff invitations: 7-day token, hash stored, email queued after commit, Verification documents: private pdf/jpg/png up to 5 MB, Workflow: institute onboarding

### Community 73 - "DynamicFieldsModelSerializer"
Cohesion: 0.08
Nodes (13): DynamicFieldsModelSerializer, AdminEnquiryListSerializer, Meta, GalleryImageSerializer, Meta, InstituteCoverSerializer, Meta, InvitationSerializer (+5 more)

### Community 76 - "expire_trainings"
Cohesion: 0.25
Nodes (3): Command, expire_trainings(), expire_trainings()

### Community 79 - "institutes/tests/test_api_portal.py"
Cohesion: 0.18
Nodes (3): make_staff(), PermissionMatrixTests, Role

### Community 80 - "CategoryTreeView"
Cohesion: 0.25
Nodes (3): build_tree(), CategoryTreeView, LocationTreeView

### Community 81 - "InstituteProfileSerializer"
Cohesion: 0.15
Nodes (5): InstituteProfileSerializer, Meta, InstituteProfileView, PortalContactView, ResubmitView

### Community 82 - "NormalizedEmailSerializer"
Cohesion: 0.12
Nodes (6): NormalizedEmailSerializer, RegistrationOTPSerializer, RegistrationOTPVerifySerializer, VerifyOTPSerializer, verify_otp(), verify_registration_otp()

### Community 84 - "institutes/models.py"
Cohesion: 0.15
Nodes (10): DocumentStatus, InstituteType, InstituteDocument, Meta, reupload_document(), review_document(), PrivateStorage, validate_document_file() (+2 more)

### Community 85 - "control_panel/api/v1/views.py"
Cohesion: 0.12
Nodes (12): build_category_tree(), Category, Meta, AdminCategoryFilter, Meta, AdminEnquiryFilter, AdminTrainingFilter, Meta (+4 more)

### Community 86 - "common/services.py"
Cohesion: 0.23
Nodes (5): _check_parent(), create_category(), update_category(), AdminCategorySerializer, Meta

### Community 87 - "IdentityScopedRateThrottle"
Cohesion: 0.13
Nodes (6): IdentityScopedRateThrottle, ActionAPIView, RegisterSendOTPView, RegisterVerifyOTPView, SendOTPView, VerifyOTPView

### Community 88 - "Entity: Enquiry (planned)"
Cohesion: 0.40
Nodes (5): Availability: seats minus CONVERTED enquiries above zero, Entity: Enquiry (planned), Open question: PRD 'Instructor Name' search has no field, Search: PostgreSQL full-text, simple config, word-prefix match, PRD search and discovery filters

### Community 90 - "Training status workflow: DRAFT, SUBMITTED, APPROVED, CHANGES_REQUESTED, REJECTED, UNPUBLISHED, CANCELLED, EXPIRED"
Cohesion: 0.50
Nodes (3): Training expiry: daily expire_trainings job sets EXPIRED after end_date, Training status workflow: DRAFT, SUBMITTED, APPROVED, CHANGES_REQUESTED, REJECTED, UNPUBLISHED, CANCELLED, EXPIRED, Workflow: training lifecycle

### Community 102 - "CategoryConstraintTests"
Cohesion: 0.13
Nodes (3): CategoryConstraintTests, CategoryServiceTests, LoadCategoriesTests

### Community 103 - "AdminApiTests"
Cohesion: 0.11
Nodes (3): AdminApiTests, AuthApiTests, UsersApiTestCase

### Community 104 - "PublicInstituteListSerializer"
Cohesion: 0.25
Nodes (4): PublicInstituteDetailSerializer, Meta, PublicInstituteListSerializer, Meta

### Community 106 - "users/api/v1/views.py"
Cohesion: 0.08
Nodes (11): AdminDocumentDownloadView, AdminViewSet, LoginView, LogoutView, MeView, PasswordChangeView, RefreshView, UserStatusView (+3 more)

### Community 107 - "VisitorEnquirySerializer"
Cohesion: 0.33
Nodes (3): VisitorEnquirySerializer, Meta, VisitorViewTests

### Community 111 - "EnquiryNote"
Cohesion: 0.10
Nodes (12): EnquiryNoteSerializer, Meta, PortalEnquiryNoteView, EnquiryNote, Meta, add_note(), registration_open_q(), 2.1 Data (`apps/enquiries/models.py`) (+4 more)

### Community 119 - "PortalTestCase"
Cohesion: 0.18
Nodes (3): EndToEndTests, PortalTestCase, ResubmitTests

### Community 120 - "institutes/api/v1/serializers.py"
Cohesion: 0.17
Nodes (5): active_municipalities(), LocationInputSerializer, institute_experience(), available_categories(), VenueSerializer

## Ambiguous Edges - Review These
- `PRD training modes: Physical, Online, Hybrid` → `Decision: hybrid mode dropped (2026-10-13)`  [AMBIGUOUS]
  docs/Training for Merojob (PRD).md · relation: conceptually_related_to
- `PRD institute locations (several, one main office)` → `Training venue: exactly one TrainingLocation, independent of institute offices`  [AMBIGUOUS]
  docs/Training for Merojob (PRD).md · relation: conceptually_related_to

## Knowledge Gaps
- **21 isolated node(s):** `Dependency: djangorestframework-simplejwt 5.5.1 (with PyJWT crypto)`, `Entity: InstituteGalleryImage`, `Institute types: fixed list of seven`, `Managed Nepal location list (province / district / municipality)`, `Django apps and their state (section 2)` (+16 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 661 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **50 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Training` connect `Training` to `institutes/services.py`, `training/services.py`, `training/tests/test_api_public.py`, `PortalTrainingViewSet`, `training/models.py`, `FilterTests`, `.create`, `Enquiry`, `AdminTrainingSerializer`, `BaseModel`, `PublicTrainingListSerializer`, `EditTests`, `control_panel/api/v1/serializers.py`, `enquiries/api/v1/views.py`, `SubmitTests`, `PortalEditTests`, `AdminTrainingViewSet`, `models/base.py`, `TrainingStatus`, `TrainingConstraintTests`, `expire_trainings`, `institutes/tests/test_api_portal.py`, `control_panel/api/v1/views.py`, `institutes/api/v1/serializers.py`?**
  _High betweenness centrality (0.116) - this node is a cross-community bridge._
- **Are the 47 inferred relationships involving `Training` (e.g. with `AdminTrainingFilter` and `AdminTrainingSerializer`) actually correct?**
  _`Training` has 47 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Dependency: djangorestframework-simplejwt 5.5.1 (with PyJWT crypto)`, `Entity: InstituteGalleryImage`, `Institute types: fixed list of seven` to the rest of the system?**
  _21 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `institutes/services.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09574468085106383 - nodes in this community are weakly interconnected._
- **Why does `Institute` connect `institutes/services.py` to `training/services.py`, `InstituteContactSerializer`, `RegistrationApiTests`, `institutes/api/v1/views.py`, `RegistrationTests`, `institutes/constants.py`, `.as_`, `training/models.py`, `Enquiry`, `AdminApiTests`, `BaseModel`, `control_panel/api/v1/serializers.py`, `SubmitTests`, `SubmitTests`, `Training`, `ActionRequiredTests`, `AdminTrainingViewSet`, `models/base.py`, `PublicInstituteApiTests`, `InstituteRegistrationSerializer`, `DynamicFieldsModelSerializer`, `institutes/tests/test_api_portal.py`, `InstituteProfileSerializer`, `add_location`, `institutes/models.py`, `control_panel/api/v1/views.py`, `PublicInstituteListSerializer`, `InstituteActionRequiredView`, `PortalTestCase`, `institutes/api/v1/serializers.py`?**
  _High betweenness centrality (0.089) - this node is a cross-community bridge._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `PRD training modes: Physical, Online, Hybrid` and `Decision: hybrid mode dropped (2026-10-13)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `PRD institute locations (several, one main office)` and `Training venue: exactly one TrainingLocation, independent of institute offices`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._