# Graph Report - traininghub-backend  (2026-11-05)

## Corpus Check
- 102 files · ~63,773 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 3)

## Summary
- 1953 nodes · 4443 edges · 108 communities (64 shown, 44 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 573 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c3ea0017`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- RegistrationTests
- CreateTests
- institutes/services.py
- training/services.py
- viewsets.py
- Base64FieldMixin
- RegistrationApiTests
- RegistrationOtpApiTests
- institutes/api/v1/views.py
- TooManyRequests
- InvitationTests
- institutes/models.py
- MemberRole
- InstituteCEO
- .as_
- training/tests/test_services.py
- FilterTests
- TrainingTestCase
- PrivateStorage
- .url
- .create
- common/validators.py
- Enquiry
- control_panel/api/v1/serializers.py
- AdminApiTests
- InstituteSocialLink
- PublicTrainingListSerializer
- EditTests
- LoadLocationsTests
- SubmitTests
- EnquiryCreateSerializer
- LocationModelTests
- PortalEnquiryNoteView
- AdminEnquiryTests
- users/models.py
- v1/permissions.py
- SubmitTests
- ContactTests
- Training
- OtpApiTests
- ActionRequiredTests
- User
- EnquiryConstraintTests
- PortalTrainingSerializer
- create_admin
- AcceptInvitationSerializer
- InvitationTests
- re
- validate_phone_number
- SubmitTests
- register
- Open questions (section 8)
- Product Requirements Document (PRD)
- IsInstituteMember
- test_locations.py
- Entity: Institute
- TrainingConstraintTests
- Core entities (section 3)
- users/services.py
- found
- LocationTests
- UserConstraintTests
- Command
- LocationApiTests
- DocumentTests
- PasswordChangeSerializer
- System Design (DRAFT v0.6)
- Entity: Training
- Workflow: institute onboarding
- InstituteDocument
- institutes/api/v1/serializers.py
- GalleryTests
- SocialLinkTests
- Base64ImageField
- AdminCategoryApiTests
- ActiveAccountJWTAuthentication
- institutes/tests/test_api_portal.py
- Location
- InstituteProfileSerializer
- NormalizedEmailSerializer
- ReviewTests
- institutes/validators.py
- HasPlatformPermission
- AdminCategorySerializer
- IdentityScopedRateThrottle
- Entity: Enquiry (planned)
- Training status workflow: DRAFT, SUBMITTED, APPROVED, CHANGES_REQUESTED, REJECTED, UNPUBLISHED, CANCELLED, EXPIRED
- Dependency: Django 5.2.4
- Dependency: django-q2 1.8.0
- Dependency: django-redis 6.0.0
- Dependency: djangorestframework 3.16.0
- Dev extras: debug toolbar, django-extensions, ipdb, ipython, fabric3, pylint
- BaseViewSet
- AdminSerializer
- InstituteAdminSiteTests
- CategoryConstraintTests
- AuthApiTests
- institute_experience
- users/api/v1/views.py
- delete_training
- InstituteSummaryView
- PortalTestCase
- training/api/v1/serializers.py

## God Nodes (most connected - your core abstractions)
1. `Training` - 72 edges
2. `Institute` - 57 edges
3. `RegistrationApiTests` - 49 edges
4. `Enquiry` - 47 edges
5. `Role` - 45 edges
6. `InstituteStatus` - 44 edges
7. `DynamicFieldsModelSerializer` - 37 edges
8. `TrainingStatus` - 37 edges
9. `BaseModel` - 30 edges
10. `Category` - 29 edges

## Surprising Connections (you probably didn't know these)
- `4.3 Backend work not done` --references--> `change_status()`  [INFERRED]
  docs/enquiries-status.md → apps/enquiries/services.py
- `Decision: PAN/VAT number unique, nine digits, contact telephone optional` --references--> `validate_pan_vat_number()`  [EXTRACTED]
  docs/System Design.md → apps/common/validators.py
- `Institute registration: one JSON request creates institute, owner, contact, locations` --references--> `register()`  [INFERRED]
  docs/System Design.md → apps/institutes/services.py
- `One-time codes (OTP): six digits, 5 minutes, Redis only` --references--> `consume_otp()`  [INFERRED]
  docs/System Design.md → apps/users/services.py
- `2.1 Data (`apps/enquiries/models.py`)` --references--> `Enquiry`  [INFERRED]
  docs/enquiries-status.md → apps/enquiries/models.py

## Import Cycles
- None detected.

## Communities (108 total, 44 thin omitted)

### Community 2 - "institutes/services.py"
Cohesion: 0.14
Nodes (24): InstituteStatus, Institute, Meta, InstituteGalleryImage, Meta, add_gallery_image(), add_social_link(), approve() (+16 more)

### Community 3 - "training/services.py"
Cohesion: 0.11
Nodes (32): DurationUnit, TrainingMode, TrainingStatus, TrainingModule, Meta, annotate_category_training_count(), approve(), _build_search_vector() (+24 more)

### Community 4 - "viewsets.py"
Cohesion: 0.19
Nodes (19): CreateListDestroyViewSet, CreateListRetrieveUpdateViewSet, CreateListUpdateDestroyViewSet, CreateListUpdateViewSet, CreateListViewSet, CreateRetrieveUpdateViewSet, CreateRetrieveViewSet, CreateUpdateViewSet (+11 more)

### Community 6 - "RegistrationApiTests"
Cohesion: 0.09
Nodes (3): SeatRaceTests, convert(), RegistrationApiTests

### Community 8 - "institutes/api/v1/views.py"
Cohesion: 0.11
Nodes (7): AdminDocumentSerializer, Meta, DocumentReviewSerializer, AdminDocumentDownloadView, AdminDocumentView, PortalDocumentDownloadView, private_file_response()

### Community 9 - "TooManyRequests"
Cohesion: 0.24
Nodes (3): TooManyRequests, _claim_phone_slot(), api_exception_handler()

### Community 10 - "InvitationTests"
Cohesion: 0.09
Nodes (4): send_invitation_email(), InvitationTests, LocationTests, RegistrationOtpServiceTests

### Community 11 - "institutes/models.py"
Cohesion: 0.08
Nodes (17): Command, BaseModel, Meta, SlugModel, Meta, Category, Meta, InstituteType (+9 more)

### Community 12 - "MemberRole"
Cohesion: 0.18
Nodes (11): InvitationStatus, MemberRole, InstituteInvitation, Meta, InstituteMember, Meta, accept_invitation(), _hash() (+3 more)

### Community 13 - "InstituteCEO"
Cohesion: 0.22
Nodes (4): PortalCEOView, InstituteCEO, annotate_profile_completion(), _at_least()

### Community 14 - ".as_"
Cohesion: 0.10
Nodes (4): CEOTests, ProfileTests, ResubmitTests, SummaryTests

### Community 15 - "training/tests/test_services.py"
Cohesion: 0.07
Nodes (12): duration_q(), prefix_query(), TrainingFilter, Meta, PublicTrainingViewSet, DurationBucket, StartBucket, TrainingLevel (+4 more)

### Community 16 - "FilterTests"
Cohesion: 0.08
Nodes (9): DetailTests, FilterOptionTests, FilterTests, PublicTrainingTestCase, QueryCountTests, SearchTests, ShiftsAreShownTests, titles() (+1 more)

### Community 17 - "TrainingTestCase"
Cohesion: 0.27
Nodes (3): ExpiryTests, TrainingTestCase, TransitionTableTests

### Community 18 - "PrivateStorage"
Cohesion: 0.10
Nodes (3): PrivateStorage, Command, load_jwt_key()

### Community 20 - ".url"
Cohesion: 0.08
Nodes (6): AccessTests, DetailTests, ListTests, NoteTests, PortalTestCase, StatusChangeTests

### Community 21 - ".create"
Cohesion: 0.05
Nodes (10): ActionQueryCountTests, AdminApiTests, CoverTests, LifecycleTests, PortalCreateTests, PortalEditTests, PortalPermissionTests, PortalTestCase (+2 more)

### Community 22 - "common/validators.py"
Cohesion: 0.10
Nodes (14): combine_date_parts(), get_today(), get_upload_path(), get_uuid_filename(), nested_getattr(), set_instance_fields(), update_instance(), validate_attachment() (+6 more)

### Community 23 - "Enquiry"
Cohesion: 0.06
Nodes (29): PortalEnquiryFilter, Meta, EnquiryNoteSerializer, Meta, PortalEnquiryListSerializer, Meta, PortalEnquirySerializer, Meta (+21 more)

### Community 24 - "control_panel/api/v1/serializers.py"
Cohesion: 0.09
Nodes (13): AdminTrainingListSerializer, Meta, AdminTrainingSerializer, Meta, LearningOutcomeSerializer, Meta, PortalTrainingListSerializer, Meta (+5 more)

### Community 25 - "AdminApiTests"
Cohesion: 0.06
Nodes (4): add_location(), AdminApiTests, PublicInstituteApiTests, WorkflowTests

### Community 26 - "InstituteSocialLink"
Cohesion: 0.10
Nodes (15): InstituteContactSerializer, Meta, PortalContactView, PublicInstituteViewSet, InstituteContact, InstituteLocation, Meta, InstituteSocialLink (+7 more)

### Community 27 - "PublicTrainingListSerializer"
Cohesion: 0.12
Nodes (6): duration_text(), format_class_days(), PublicTrainingDetailSerializer, Meta, PublicTrainingListSerializer, Meta

### Community 29 - "LoadLocationsTests"
Cohesion: 0.29
Nodes (3): level_counts(), load(), LoadLocationsTests

### Community 31 - "SubmitTests"
Cohesion: 0.14
Nodes (4): NoVisitorIdentityTests, PublicTestCase, SubmitTests, ThrottleTests

### Community 32 - "EnquiryCreateSerializer"
Cohesion: 0.15
Nodes (6): EnquiryCreateSerializer, Meta, VisitorEnquirySerializer, Meta, EnquiryCreateView, VisitorViewTests

### Community 34 - "PortalEnquiryNoteView"
Cohesion: 0.13
Nodes (11): PortalEnquiryNoteView, 1. In short, 3. Where the build differs from the prototype, 4.1 Before it works end to end, 4.2 Frontend changes against the prototype, 4.3 Backend work not done, 4.4 Risks and limits to know about, 4.5 Questions still open (numbers as in `docs/System Design.md`, section 8) (+3 more)

### Community 38 - "SubmitTests"
Cohesion: 0.09
Nodes (6): ChangeStatusTests, NoteTests, ServiceTestCase, submit(), SubmitTests, SummaryTests

### Community 40 - "Training"
Cohesion: 0.09
Nodes (12): AdminTrainingFilter, Meta, Command, Training, Meta, annotate_institute_public_counts(), annotate_institute_training_count(), expire_trainings() (+4 more)

### Community 42 - "ActionRequiredTests"
Cohesion: 0.08
Nodes (3): ActionRequiredTests, CoverTests, DocumentAndGalleryTests

### Community 45 - "PortalTrainingSerializer"
Cohesion: 0.07
Nodes (10): ReasonSerializer, AdminInstituteViewSet, AdminTrainingViewSet, PortalTrainingSerializer, Meta, as_options(), PortalTrainingViewSet, transition() (+2 more)

### Community 46 - "create_admin"
Cohesion: 0.13
Nodes (5): create_admin(), _set_permissions(), update_admin(), AdminApiTests, StatusApiTests

### Community 47 - "AcceptInvitationSerializer"
Cohesion: 0.29
Nodes (3): AcceptInvitationSerializer, AcceptInvitationView, RegisterView

### Community 49 - "re"
Cohesion: 0.18
Nodes (4): _slug_strip(), unique_slugify(), NepalMobileField, normalize_phone()

### Community 50 - "validate_phone_number"
Cohesion: 0.29
Nodes (4): ValidatePanVatNumberTests, ValidatePhoneNumberTests, validate_pan_vat_number(), validate_phone_number()

### Community 52 - "register"
Cohesion: 0.14
Nodes (7): register(), consume_otp(), normalize_email(), _otp_keys(), send_otp(), send_registration_otp(), verify_otp()

### Community 54 - "Open questions (section 8)"
Cohesion: 0.22
Nodes (10): Entity: InstituteMember (one institute per user), Auth: email + password, JWT RS256 via simplejwt, Open questions (section 8), Open question: how an admin's password is reset, Open question: endpoint that consumes a verified password-reset code, Open question: where the frontend stores access/refresh tokens, Roles and grantable Django permissions (users.manage_*), Entity: User (+2 more)

### Community 55 - "Product Requirements Document (PRD)"
Cohesion: 0.25
Nodes (10): Phase 2: Application (approve/reject/capacity) and learners, My enquiries: browser device token, last 90 days, Open question: do institutes keep enquiries after 90 days, Reviews and ratings out of MVP, Workflow: enquiry (planned), Product Requirements Document (PRD), PRD training enquiry rules (captcha, rate limit, 90-day My enquiries), PRD later phase: applications, reviews and ratings (+2 more)

### Community 56 - "IsInstituteMember"
Cohesion: 0.10
Nodes (11): GalleryReorderSerializer, PortalCoverView, PortalDocumentViewSet, PortalGalleryViewSet, PortalInvitationViewSet, PortalLocationViewSet, PortalSocialLinkViewSet, PortalStaffViewSet (+3 more)

### Community 57 - "test_locations.py"
Cohesion: 0.24
Nodes (4): LocationLevel, MunicipalityType, clear_category_tree_cache(), clear_location_tree_cache()

### Community 58 - "Entity: Institute"
Cohesion: 0.38
Nodes (7): Entity: Institute, Entity: InstituteCEO, Entity: InstituteContact, Entity: InstituteGalleryImage, Institute profile split: columns plus contact, CEO, social-link tables, Entity: InstituteSocialLink, Institute types: fixed list of seven

### Community 60 - "Core entities (section 3)"
Cohesion: 0.38
Nodes (6): Core entities (section 3), Entity: InstituteLocation (office), Entity: Location, Managed Nepal location list (province / district / municipality), Entity: TrainingLocation (venue), PRD institute locations (several, one main office)

### Community 61 - "users/services.py"
Cohesion: 0.12
Nodes (11): OTPPurpose, change_password(), _revoke_refresh_tokens(), send_otp_email(), send_password_reset_otp(), send_registration_otp_email(), set_status(), verify_registration_otp() (+3 more)

### Community 69 - "System Design (DRAFT v0.6)"
Cohesion: 0.17
Nodes (7): System Design (DRAFT v0.6), Django apps and their state (section 2), Proposed: AuditLog (append-only), not built, Decision log (answered questions), Decisions made (section 1), Non-functional requirements (section 6), Training mode: PHYSICAL or ONLINE

### Community 70 - "Entity: Training"
Cohesion: 0.17
Nodes (12): Categories: two-level tree with icon and hue, training uses a leaf, Entity: Category, Entity: LearningOutcome, Entity: Training, Entity: TrainingContact, Entity: TrainingDetail, Training duration (value + unit, derived weeks) and weekly class slots, Entity: TrainingModule (+4 more)

### Community 71 - "Workflow: institute onboarding"
Cohesion: 0.29
Nodes (8): Entity: InstituteDocument, Entity: InstituteInvitation, Institute registration: one JSON request creates institute, owner, contact, locations, Institute status workflow: PENDING, APPROVED, REJECTED, INFO_REQUESTED, SUSPENDED, One-time codes (OTP): six digits, 5 minutes, Redis only, Staff invitations: 7-day token, hash stored, email queued after commit, Verification documents: private pdf/jpg/png up to 5 MB, Workflow: institute onboarding

### Community 72 - "InstituteDocument"
Cohesion: 0.08
Nodes (10): InstituteDocumentSerializer, Meta, DocumentStatus, InstituteDocument, Meta, add_document(), reupload_document(), review_document() (+2 more)

### Community 73 - "institutes/api/v1/serializers.py"
Cohesion: 0.05
Nodes (25): DynamicFieldsModelSerializer, AdminEnquiryListSerializer, Meta, AdminInstituteSerializer, Meta, EnquiryCountsSerializer, GalleryImageSerializer, Meta (+17 more)

### Community 80 - "Location"
Cohesion: 0.13
Nodes (11): LocationFilter, Meta, LocationSerializer, Meta, build_category_tree(), build_tree(), CategoryTreeView, LocationTreeView (+3 more)

### Community 81 - "InstituteProfileSerializer"
Cohesion: 0.18
Nodes (4): InstituteProfileSerializer, Meta, InstituteProfileView, ResubmitView

### Community 82 - "NormalizedEmailSerializer"
Cohesion: 0.22
Nodes (3): NormalizedEmailSerializer, RegistrationOTPSerializer, RegistrationOTPVerifySerializer

### Community 84 - "institutes/validators.py"
Cohesion: 0.83
Nodes (3): validate_document_file(), validate_image_file(), _validate_upload()

### Community 85 - "HasPlatformPermission"
Cohesion: 0.11
Nodes (10): AdminCategoryFilter, Meta, AdminEnquiryFilter, Meta, AdminCategoryViewSet, AdminEnquiryViewSet, AdminViewSet, HasPlatformPermission (+2 more)

### Community 86 - "AdminCategorySerializer"
Cohesion: 0.24
Nodes (5): _check_parent(), create_category(), update_category(), AdminCategorySerializer, Meta

### Community 87 - "IdentityScopedRateThrottle"
Cohesion: 0.18
Nodes (4): IdentityScopedRateThrottle, ActionAPIView, RegisterSendOTPView, RegisterVerifyOTPView

### Community 88 - "Entity: Enquiry (planned)"
Cohesion: 0.40
Nodes (5): Availability: seats minus CONVERTED enquiries above zero, Entity: Enquiry (planned), Open question: PRD 'Instructor Name' search has no field, Search: PostgreSQL full-text, simple config, word-prefix match, PRD search and discovery filters

### Community 90 - "Training status workflow: DRAFT, SUBMITTED, APPROVED, CHANGES_REQUESTED, REJECTED, UNPUBLISHED, CANCELLED, EXPIRED"
Cohesion: 0.50
Nodes (3): Training expiry: daily expire_trainings job sets EXPIRED after end_date, Training status workflow: DRAFT, SUBMITTED, APPROVED, CHANGES_REQUESTED, REJECTED, UNPUBLISHED, CANCELLED, EXPIRED, Workflow: training lifecycle

### Community 102 - "CategoryConstraintTests"
Cohesion: 0.13
Nodes (3): CategoryConstraintTests, CategoryServiceTests, LoadCategoriesTests

### Community 104 - "institute_experience"
Cohesion: 0.12
Nodes (8): InstituteExperienceTests, _duration(), institute_experience(), membership_duration(), PublicInstituteDetailSerializer, Meta, PublicInstituteListSerializer, Meta

### Community 106 - "users/api/v1/views.py"
Cohesion: 0.07
Nodes (15): LoginSerializer, ProfileSerializer, Meta, SendOTPSerializer, UpdateStatusSerializer, Meta, VerifyOTPSerializer, LoginView (+7 more)

### Community 111 - "delete_training"
Cohesion: 0.25
Nodes (4): DeleteTrainingTests, delete_training(), registration_open_q(), 2.4 Changes outside the new app

### Community 114 - "InstituteSummaryView"
Cohesion: 0.18
Nodes (4): InstituteActionRequiredSerializer, InstituteSummarySerializer, InstituteActionRequiredView, InstituteSummaryView

### Community 119 - "PortalTestCase"
Cohesion: 0.16
Nodes (4): EndToEndTests, make_staff(), PortalTestCase, StaffTests

### Community 120 - "training/api/v1/serializers.py"
Cohesion: 0.10
Nodes (6): active_municipalities(), LocationInputSerializer, DynamicFieldsSerializer, available_categories(), CoverSerializer, VenueSerializer

## Ambiguous Edges - Review These
- `PRD training modes: Physical, Online, Hybrid` → `Decision: hybrid mode dropped (2026-10-13)`  [AMBIGUOUS]
  docs/Training for Merojob (PRD).md · relation: conceptually_related_to
- `PRD institute locations (several, one main office)` → `Training venue: exactly one TrainingLocation, independent of institute offices`  [AMBIGUOUS]
  docs/Training for Merojob (PRD).md · relation: conceptually_related_to

## Knowledge Gaps
- **21 isolated node(s):** `Dependency: djangorestframework-simplejwt 5.5.1 (with PyJWT crypto)`, `Entity: InstituteGalleryImage`, `Institute types: fixed list of seven`, `Managed Nepal location list (province / district / municipality)`, `Django apps and their state (section 2)` (+16 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 657 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **44 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Training` connect `Training` to `CreateTests`, `institutes/services.py`, `training/services.py`, `institutes/api/v1/views.py`, `institutes/models.py`, `training/tests/test_services.py`, `FilterTests`, `TrainingTestCase`, `.create`, `Enquiry`, `control_panel/api/v1/serializers.py`, `PublicTrainingListSerializer`, `EditTests`, `EnquiryCreateSerializer`, `SubmitTests`, `PortalTrainingSerializer`, `SubmitTests`, `TrainingConstraintTests`, `found`, `ReviewTests`, `delete_training`, `InstituteSummaryView`, `training/api/v1/serializers.py`?**
  _High betweenness centrality (0.122) - this node is a cross-community bridge._
- **Are the 48 inferred relationships involving `Training` (e.g. with `AdminTrainingFilter` and `AdminTrainingSerializer`) actually correct?**
  _`Training` has 48 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Dependency: djangorestframework-simplejwt 5.5.1 (with PyJWT crypto)`, `Entity: InstituteGalleryImage`, `Institute types: fixed list of seven` to the rest of the system?**
  _21 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `institutes/services.py` be split into smaller, more focused modules?**
  _Cohesion score 0.14204545454545456 - nodes in this community are weakly interconnected._
- **Why does `Institute` connect `institutes/services.py` to `RegistrationTests`, `training/services.py`, `RegistrationApiTests`, `institutes/api/v1/views.py`, `institutes/models.py`, `MemberRole`, `.as_`, `Enquiry`, `control_panel/api/v1/serializers.py`, `AdminApiTests`, `InstituteSocialLink`, `SubmitTests`, `SubmitTests`, `Training`, `ActionRequiredTests`, `PortalTrainingSerializer`, `InstituteDocument`, `institutes/api/v1/serializers.py`, `institutes/tests/test_api_portal.py`, `InstituteProfileSerializer`, `institute_experience`, `InstituteSummaryView`?**
  _High betweenness centrality (0.091) - this node is a cross-community bridge._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `PRD training modes: Physical, Online, Hybrid` and `Decision: hybrid mode dropped (2026-10-13)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `PRD institute locations (several, one main office)` and `Training venue: exactly one TrainingLocation, independent of institute offices`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._