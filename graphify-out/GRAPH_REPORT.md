# Graph Report - traininghub-backend  (2026-11-20)

## Corpus Check
- 127 files · ~77,049 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 3)

## Summary
- 2423 nodes · 5633 edges · 135 communities (67 shown, 68 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 736 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e52ca46d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- .create
- training/services.py
- training/models.py
- Institute
- IsInstituteMember
- institutes/services.py
- ActionRequiredTests
- control_panel/api/v1/views.py
- users/api/v1/serializers.py
- InvitationTests
- RegistrationApiTests
- TrainingTestCase
- AdminInstituteViewSet
- viewsets.py
- AdminInstitutesApiTests
- FilterTests
- Institute model
- AdminEnquiryTests
- PublicTrainingViewSet
- institutes app
- SubmitTests
- .as_
- control_panel/api/v1/serializers.py
- InstituteDocument
- Training
- institutes/tests/test_api_portal.py
- enquiries/services.py
- CappedLimitOffsetPaginationTests
- slugify.py
- EnquiryNote
- enquiries-status.md
- 8. Open questions
- OtpApiTests
- InstituteCategoriesTests
- HasPlatformPermission
- SubmitTests
- AdminApiTests
- common/validators.py
- training/api/v1/serializers.py
- notify() service (notification.services.notify)
- .url
- DocumentTests
- Location
- DynamicFieldsModelSerializer
- test_categories.py
- RegistrationTests
- institutes/validators.py
- AppKeyPermissionTests
- LoadLocationsTests
- PublicInstituteApiTests
- InvitationSerializer
- NotificationViewset
- enquiries/api/v1/views.py
- ContactTests
- RegistrationOtpApiTests
- InstituteDocumentSerializer
- validate_phone_number
- EnquiryConstraintTests
- app_key/tests.py
- AdminTrainingsFeaturedAndReviewApiTests
- Notification event registry (registry.EVENTS)
- EnquiryEventTests
- notify
- AdminCategoryApiTests
- Enquiry model (apps/enquiries)
- InstituteProfileSerializer
- users/services.py
- EditTests
- load_categories.py
- notification/services.py
- EnforcedEndpointTests
- training app
- InvitationTests
- purge_old
- TooManyRequests
- PortalTestCase
- InstituteTrainingModesTests
- BaseViewSet
- LocationModelTests
- LocationTests
- add_location
- NotificationApiTests
- TrainingSession
- Enquiry
- BaseModel
- User
- create_admin
- InstituteAdminSiteTests
- InstituteSummaryView
- UserConstraintTests
- Notification
- AuthApiTests
- AdminTrainingSerializer
- InstituteConstraintTests
- TrainingReviewEventTests
- UpdateStatusSerializer
- DistributedAppKey
- LocationTests
- GalleryTests
- SocialLinkTests
- LocationApiTests
- users/api/v1/views.py
- rest_framework_permissions
- StatusChangeTests
- common/api/v1/views.py
- InstituteGalleryImage
- PrivateStorage
- notification/tasks.py
- is_valid_key
- ActionAPIView
- institutes/api/v1/views.py
- summary
- AdminSerializer
- ListTests
- Dependency: Django 5.2.4
- Dependency: django-q2 1.8.0
- Dependency: django-redis 6.0.0
- Dependency: djangorestframework 3.16.0
- Dev extras: debug toolbar, django-extensions, ipdb, ipython, fabric3, pylint
- TrainingHub Backend System Design (DRAFT v0.6)
- InstituteCoverSerializer
- PasswordChangeSerializer
- StableOrderingFilter
- CategoryConstraintTests
- IdentityScopedRateThrottle
- UserManager
- AppKeyModelTests
- apps_notification_init
- SlugModel
- SendOTPSerializer
- VerifyOTPSerializer

## God Nodes (most connected - your core abstractions)
1. `Training` - 88 edges
2. `Institute` - 65 edges
3. `InstituteStatus` - 62 edges
4. `TrainingStatus` - 54 edges
5. `Enquiry` - 53 edges
6. `AdminInstitutesApiTests` - 52 edges
7. `RegistrationApiTests` - 49 edges
8. `Role` - 46 edges
9. `DynamicFieldsModelSerializer` - 40 edges
10. `Category` - 36 edges

## Surprising Connections (you probably didn't know these)
- `2.1 Data (`apps/enquiries/models.py`)` --references--> `Enquiry`  [INFERRED]
  docs/enquiries-status.md → apps/enquiries/models.py
- `2.2 Rules (`apps/enquiries/services.py`)` --references--> `submit_enquiry()`  [INFERRED]
  docs/enquiries-status.md → apps/enquiries/services.py
- `2.2 Rules (`apps/enquiries/services.py`)` --references--> `change_status()`  [INFERRED]
  docs/enquiries-status.md → apps/enquiries/services.py
- `4.3 Backend work not done` --references--> `change_status()`  [INFERRED]
  docs/enquiries-status.md → apps/enquiries/services.py
- `2.4 Changes outside the new app` --references--> `delete_training()`  [INFERRED]
  docs/enquiries-status.md → apps/training/services.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Enquiry milestone alerting: submit/convert services fire thresholds recorded once in the dedupe table** — docs_system_design_submit_enquiry, docs_system_design_change_status, docs_system_design_event_milestone, docs_system_design_notification_milestones, docs_system_design_notificationdedupe, docs_system_design_seats [EXTRACTED 1.00]
- **Notification dispatch pipeline: notify() looks up the registry, writes rows, queues email after commit** — docs_system_design_notify_service, docs_system_design_event_registry, docs_system_design_notification_model, docs_system_design_notificationdedupe, docs_system_design_notification_email_task, docs_system_design_savepoint_isolation [EXTRACTED 1.00]
- **Domain apps that call notify() and resolve their own recipients** — docs_system_design_users_app, docs_system_design_institutes_app, docs_system_design_training_app, docs_system_design_enquiries_app, docs_system_design_notify_service, docs_system_design_recipient_resolution [EXTRACTED 1.00]

## Communities (135 total, 68 thin omitted)

### Community 0 - ".create"
Cohesion: 0.05
Nodes (10): ActionQueryCountTests, AdminApiTests, CoverTests, LifecycleTests, PortalCreateTests, PortalEditTests, PortalPermissionTests, PortalTestCase (+2 more)

### Community 1 - "training/services.py"
Cohesion: 0.07
Nodes (40): TrainingMode, TrainingStatus, Command, LearningOutcome, Meta, TrainingContact, TrainingDetail, Meta (+32 more)

### Community 2 - "training/models.py"
Cohesion: 0.09
Nodes (12): duration_q(), prefix_query(), TrainingFilter, Meta, DurationBucket, DurationUnit, StartBucket, TrainingLevel (+4 more)

### Community 3 - "Institute"
Cohesion: 0.17
Nodes (10): AdminInstituteFilter, Meta, ChoiceInFilter, DocumentStatus, InstituteStatus, InstituteType, Institute, Meta (+2 more)

### Community 4 - "IsInstituteMember"
Cohesion: 0.13
Nodes (10): GalleryReorderSerializer, PortalDocumentViewSet, PortalGalleryViewSet, PortalInvitationViewSet, PortalLocationViewSet, PortalSocialLinkViewSet, PortalStaffViewSet, InstituteScopedMixin (+2 more)

### Community 5 - "institutes/services.py"
Cohesion: 0.08
Nodes (25): InvitationStatus, InstituteInvitation, Meta, accept_invitation(), approve(), deactivate_location(), _hash(), invite() (+17 more)

### Community 6 - "ActionRequiredTests"
Cohesion: 0.08
Nodes (3): ActionRequiredTests, CoverTests, DocumentAndGalleryTests

### Community 7 - "control_panel/api/v1/views.py"
Cohesion: 0.08
Nodes (17): AdminCategoryFilter, Meta, AdminEnquiryFilter, Meta, AdminTrainingFilter, Meta, AdminDashboardSummarySerializer, AdminCategoryViewSet (+9 more)

### Community 8 - "users/api/v1/serializers.py"
Cohesion: 0.11
Nodes (4): NormalizedEmailSerializer, OTPField, RegistrationOTPSerializer, RegistrationOTPVerifySerializer

### Community 11 - "TrainingTestCase"
Cohesion: 0.09
Nodes (6): CreateTests, ExpiryTests, ReviewTests, SubmitTests, TrainingTestCase, TransitionTableTests

### Community 12 - "AdminInstituteViewSet"
Cohesion: 0.07
Nodes (6): DynamicFieldsSerializer, AdminTrainingFeaturedSerializer, ReasonSerializer, AdminEnquiryViewSet, AdminInstituteViewSet, AdminTrainingViewSet

### Community 13 - "viewsets.py"
Cohesion: 0.19
Nodes (19): CreateListDestroyViewSet, CreateListRetrieveUpdateViewSet, CreateListUpdateDestroyViewSet, CreateListUpdateViewSet, CreateListViewSet, CreateRetrieveUpdateViewSet, CreateRetrieveViewSet, CreateUpdateViewSet (+11 more)

### Community 15 - "FilterTests"
Cohesion: 0.08
Nodes (8): DetailTests, FilterOptionTests, FilterTests, PublicTrainingTestCase, SearchTests, ShiftsAreShownTests, titles(), VisibilityTests

### Community 16 - "Institute model"
Cohesion: 0.11
Nodes (26): Categories: two-level tree with icon and hue, training uses a leaf, Category (two-level tree), common app (shared base classes and reference data), Core entities (section 3), Institute model, Entity: InstituteCEO, Entity: InstituteContact, Entity: InstituteGalleryImage (+18 more)

### Community 17 - "AdminEnquiryTests"
Cohesion: 0.07
Nodes (3): AdminDashboardSummaryTests, AdminEnquiryTests, ControlPanelRoutesTests

### Community 18 - "PublicTrainingViewSet"
Cohesion: 0.08
Nodes (12): DeleteTrainingTests, PortalTrainingListSerializer, Meta, as_options(), PortalTrainingViewSet, PublicTrainingViewSet, transition(), run() (+4 more)

### Community 19 - "institutes app"
Cohesion: 0.13
Nodes (24): Dashboard analytics gap (needs analytics app and view counting), admin/dashboard/summary/ endpoint, analytics app (planned), Admin audience (Super Admin plus holders of matching manage_* permission, in-app only), Event admin.document_reuploaded, Event admin.institute_verification, InstituteDocument (with rejection reason), Entity: InstituteInvitation (+16 more)

### Community 20 - "SubmitTests"
Cohesion: 0.11
Nodes (5): ChangeStatusTests, NoteTests, ServiceTestCase, submit(), SubmitTests

### Community 21 - ".as_"
Cohesion: 0.09
Nodes (4): CEOTests, ProfileTests, StaffTests, SummaryTests

### Community 22 - "control_panel/api/v1/serializers.py"
Cohesion: 0.06
Nodes (32): AdminInstituteSerializer, Meta, AdminTrainingListSerializer, Meta, DashboardEnquiryCountsSerializer, DashboardInstituteCountsSerializer, DashboardTrainingCountsSerializer, DocumentReviewSerializer (+24 more)

### Community 23 - "InstituteDocument"
Cohesion: 0.16
Nodes (8): AdminDocumentSerializer, Meta, AdminDocumentView, InstituteDocument, Meta, reupload_document(), review_document(), DocumentEventTests

### Community 24 - "Training"
Cohesion: 0.09
Nodes (14): _event(), institute_activity(), Training, Meta, annotate_institute_public_categories(), annotate_institute_public_counts(), annotate_institute_public_training_modes(), refresh_search_vectors() (+6 more)

### Community 25 - "institutes/tests/test_api_portal.py"
Cohesion: 0.13
Nodes (8): PortalTestCase, MemberRole, InstituteMember, Meta, remove_staff(), make_staff(), RemoveStaffTests, Role

### Community 26 - "enquiries/services.py"
Cohesion: 0.15
Nodes (14): admin_counts(), _check_converted_milestone(), _check_intake_milestones(), _claim_phone_slot(), counts(), _fire_highest(), _is_open_duplicate(), _milestone_counts() (+6 more)

### Community 27 - "CappedLimitOffsetPaginationTests"
Cohesion: 0.17
Nodes (3): CappedLimitOffsetPagination, CappedLimitOffsetPaginationTests, limit_for()

### Community 29 - "EnquiryNote"
Cohesion: 0.10
Nodes (13): EnquiryNoteSerializer, Meta, PortalEnquiryNoteView, EnquiryNote, Meta, add_note(), registration_open_q(), 2.1 Data (`apps/enquiries/models.py`) (+5 more)

### Community 30 - "enquiries-status.md"
Cohesion: 0.10
Nodes (25): 1. In short, 3. Where the build differs from the prototype, 4.1 Before it works end to end, 4.2 Frontend changes against the prototype, 4.3 Backend work not done, 4.4 Risks and limits to know about, 4.5 Questions still open (numbers as in `docs/System Design.md`, section 8), 4. What needs changes (+17 more)

### Community 31 - "8. Open questions"
Cohesion: 0.11
Nodes (23): 4.5 Questions still open (1, 8, 14), Phase 2: Application (approve/reject/capacity) and learners, Availability: seats minus CONVERTED enquiries above zero, Auth: email + password, JWT RS256 via simplejwt, My enquiries: browser device token, last 90 days, 8. Open questions, Open question 1: enquiry retention, Open question: do institutes keep enquiries after 90 days (+15 more)

### Community 33 - "InstituteCategoriesTests"
Cohesion: 0.21
Nodes (4): entry(), InstituteCategoriesQueryTests, InstituteCategoriesTests, top_level()

### Community 34 - "HasPlatformPermission"
Cohesion: 0.18
Nodes (5): AdminDocumentDownloadView, HasAnyPlatformPermission, HasPlatformPermission, IsInstituteStaff, IsPlatformAdmin

### Community 35 - "SubmitTests"
Cohesion: 0.10
Nodes (7): VisitorEnquirySerializer, Meta, NoVisitorIdentityTests, PublicTestCase, SubmitTests, ThrottleTests, VisitorViewTests

### Community 37 - "common/validators.py"
Cohesion: 0.15
Nodes (9): combine_date_parts(), get_today(), validate_attachment(), validate_coded_phone_number(), validate_dob(), validate_future_datetime(), validate_is_future_datetime(), validate_otp() (+1 more)

### Community 38 - "training/api/v1/serializers.py"
Cohesion: 0.05
Nodes (24): build_category_tree(), Category, Meta, InstituteExperienceTests, _duration(), get_upload_path(), get_uuid_filename(), institute_experience() (+16 more)

### Community 39 - "notify() service (notification.services.notify)"
Cohesion: 0.13
Nodes (18): Claim: qcluster is not needed for enquiries, users.services.admins_with_permission, control_panel app (admin API under admin/), users.services.create_admin, Event admin.account_created (note to change initial password), notification app (apps/notification), Notification email task (django-q2, one per row), Notifications inbox API (notifications/) (+10 more)

### Community 40 - ".url"
Cohesion: 0.18
Nodes (3): AccessTests, DetailTests, NoteTests

### Community 42 - "Location"
Cohesion: 0.18
Nodes (9): active_municipalities(), LocationLevel, MunicipalityType, Command, Location, Meta, clear_category_tree_cache(), clear_location_tree_cache() (+1 more)

### Community 43 - "DynamicFieldsModelSerializer"
Cohesion: 0.05
Nodes (19): LocationInputSerializer, DynamicFieldsModelSerializer, _check_parent(), create_category(), update_category(), membership_duration(), AdminCategorySerializer, Meta (+11 more)

### Community 46 - "institutes/validators.py"
Cohesion: 0.11
Nodes (6): validate_document_file(), validate_image_file(), _validate_upload(), Command, env_list(), load_jwt_key()

### Community 51 - "NotificationViewset"
Cohesion: 0.24
Nodes (4): NotificationViewset, mark_all_read(), mark_read(), unread_count()

### Community 53 - "enquiries/api/v1/views.py"
Cohesion: 0.09
Nodes (10): PortalEnquiryFilter, Meta, EnquiryCreateSerializer, Meta, PortalEnquiryListSerializer, Meta, PortalEnquirySerializer, Meta (+2 more)

### Community 57 - "validate_phone_number"
Cohesion: 0.26
Nodes (4): ValidatePanVatNumberTests, ValidatePhoneNumberTests, validate_pan_vat_number(), validate_phone_number()

### Community 61 - "Notification event registry (registry.EVENTS)"
Cohesion: 0.26
Nodes (10): Update 2026-11-20: enquiry events now notify institute staff, Institute staff audience (owner and staff, in-app and email), Event document.rejected, Event enquiry.converted (other staff only), Event enquiry.new (plain enquiry or interest), Events institute.approved/.rejected/.info_requested/.suspended/.reinstated, Events milestone.enquiries/.interest/.converted, Notification event registry (registry.EVENTS) (+2 more)

### Community 63 - "notify"
Cohesion: 0.18
Nodes (3): Event, notify(), NotifyTests

### Community 65 - "Enquiry model (apps/enquiries)"
Cohesion: 0.19
Nodes (17): Changing the status rules (change_status), EnquiryNote, Seat check on submit does not lock the training, Enquiry statuses, types and preferred time, admin/enquiries/ read-only monitor, enquiries.services.change_status, enquiries app, Enquiry model (apps/enquiries) (+9 more)

### Community 66 - "InstituteProfileSerializer"
Cohesion: 0.17
Nodes (5): InstituteProfileSerializer, Meta, InstituteProfileView, PortalContactView, ResubmitView

### Community 67 - "users/services.py"
Cohesion: 0.11
Nodes (17): register(), OTPPurpose, admins_with_permission(), consume_otp(), get_otp(), normalize_email(), _otp_keys(), send_otp() (+9 more)

### Community 70 - "notification/services.py"
Cohesion: 0.20
Nodes (5): Channel, NotificationDedupe, Meta, claim(), mark_seen()

### Community 72 - "training app"
Cohesion: 0.18
Nodes (15): registration_open_q change in training/services.py, Event admin.training_review, expire_trainings daily job, Training.is_featured flag and set_featured, institute/summary/ endpoint (portal counts), users.manage_trainings permission, purge_notifications daily purge, Redis cache and django-q2 (qcluster worker) (+7 more)

### Community 75 - "TooManyRequests"
Cohesion: 0.16
Nodes (3): TooManyRequests, RegistrationOtpServiceTests, api_exception_handler()

### Community 76 - "PortalTestCase"
Cohesion: 0.15
Nodes (4): EndToEndTests, PermissionMatrixTests, PortalTestCase, ResubmitTests

### Community 83 - "TrainingSession"
Cohesion: 0.22
Nodes (4): WeekDay, TrainingSession, Meta, TrainingSessionConstraintTests

### Community 84 - "Enquiry"
Cohesion: 0.14
Nodes (9): NepalMobileField, EnquiryStatus, EnquiryType, PreferredTime, Enquiry, Meta, SeatRaceTests, SummaryTests (+1 more)

### Community 85 - "BaseModel"
Cohesion: 0.17
Nodes (5): BaseModel, Meta, InstituteCEO, annotate_profile_completion(), _at_least()

### Community 87 - "create_admin"
Cohesion: 0.11
Nodes (8): change_password(), create_admin(), _revoke_refresh_tokens(), _set_permissions(), set_status(), update_admin(), AdminApiTests, StatusApiTests

### Community 89 - "InstituteSummaryView"
Cohesion: 0.18
Nodes (4): InstituteActionRequiredSerializer, InstituteSummarySerializer, InstituteActionRequiredView, InstituteSummaryView

### Community 91 - "Notification"
Cohesion: 0.27
Nodes (4): NotificationSerializer, Meta, Notification, Meta

### Community 93 - "AdminTrainingSerializer"
Cohesion: 0.10
Nodes (9): AdminTrainingSerializer, Meta, LearningOutcomeSerializer, Meta, PortalTrainingSerializer, Meta, TrainingContentFields, TrainingSessionSerializer (+1 more)

### Community 96 - "UpdateStatusSerializer"
Cohesion: 0.25
Nodes (4): UpdateStatusSerializer, Meta, PasswordChangeView, UserStatusView

### Community 103 - "users/api/v1/views.py"
Cohesion: 0.14
Nodes (7): LoginSerializer, ProfileSerializer, Meta, LoginView, LogoutView, MeView, RefreshView

### Community 106 - "common/api/v1/views.py"
Cohesion: 0.12
Nodes (8): LocationFilter, Meta, LocationSerializer, Meta, build_tree(), CategoryTreeView, LocationTreeView, LocationViewSet

### Community 107 - "InstituteGalleryImage"
Cohesion: 0.25
Nodes (6): GalleryImageSerializer, Meta, PublicInstituteViewSet, InstituteGalleryImage, Meta, add_gallery_image()

### Community 109 - "notification/tasks.py"
Cohesion: 0.25
Nodes (3): send(), purge_notifications(), send_notification_email()

### Community 111 - "is_valid_key"
Cohesion: 0.29
Nodes (4): _cache_key(), forget_key(), is_valid_key(), parse_app_key()

### Community 112 - "ActionAPIView"
Cohesion: 0.25
Nodes (3): ActionAPIView, RegisterSendOTPView, RegisterVerifyOTPView

### Community 113 - "institutes/api/v1/views.py"
Cohesion: 0.12
Nodes (6): AcceptInvitationSerializer, AcceptInvitationView, PortalCEOView, PortalDocumentDownloadView, private_file_response(), RegisterView

### Community 123 - "TrainingHub Backend System Design (DRAFT v0.6)"
Cohesion: 0.13
Nodes (11): Audit trail gap (change_status takes by, TODO(audit)), TrainingHub Backend System Design (DRAFT v0.6), Django apps and their state (section 2), AuditLog (proposed, not built), Decision log (answered questions), Decisions made (section 1), admin/institutes/{slug}/activity/ timeline, InstituteStatusLog (+3 more)

### Community 124 - "InstituteCoverSerializer"
Cohesion: 0.25
Nodes (3): InstituteCoverSerializer, Meta, PortalCoverView

## Ambiguous Edges - Review These
- `Decision: hybrid mode dropped (2026-10-13)` → `PRD training modes: Physical, Online, Hybrid`  [AMBIGUOUS]
  docs/Training for Merojob (PRD).md · relation: conceptually_related_to
- `PRD institute locations (several, one main office)` → `Training venue: exactly one TrainingLocation, independent of institute offices`  [AMBIGUOUS]
  docs/Training for Merojob (PRD).md · relation: conceptually_related_to
- `admin/enquiries/ read-only monitor` → `Admin enquiries monitor listed as not built`  [AMBIGUOUS]
  docs/enquiries-status.md · relation: conceptually_related_to
- `Claim: qcluster is not needed for enquiries` → `Notification email task (django-q2, one per row)`  [AMBIGUOUS]
  docs/enquiries-status.md · relation: conceptually_related_to

## Knowledge Gaps
- **23 isolated node(s):** `Dependency: Django 5.2.4`, `Dependency: django-q2 1.8.0`, `Dependency: django-redis 6.0.0`, `Dependency: djangorestframework 3.16.0`, `Dev extras: debug toolbar, django-extensions, ipdb, ipython, fabric3, pylint` (+18 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 792 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **68 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Training` connect `Training` to `.create`, `training/services.py`, `training/models.py`, `Institute`, `SlugModel`, `control_panel/api/v1/views.py`, `TrainingTestCase`, `AdminInstituteViewSet`, `AdminInstitutesApiTests`, `FilterTests`, `AdminEnquiryTests`, `PublicTrainingViewSet`, `SubmitTests`, `control_panel/api/v1/serializers.py`, `institutes/tests/test_api_portal.py`, `enquiries/services.py`, `training/api/v1/serializers.py`, `enquiries/api/v1/views.py`, `AdminTrainingsFeaturedAndReviewApiTests`, `EnquiryEventTests`, `EditTests`, `TrainingSession`, `Enquiry`, `BaseModel`, `InstituteSummaryView`, `AdminTrainingSerializer`, `institutes/api/v1/views.py`?**
  _High betweenness centrality (0.155) - this node is a cross-community bridge._
- **Are the 59 inferred relationships involving `Training` (e.g. with `AdminTrainingFilter` and `institute_activity()`) actually correct?**
  _`Training` has 59 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Dependency: Django 5.2.4`, `Dependency: django-q2 1.8.0`, `Dependency: django-redis 6.0.0` to the rest of the system?**
  _23 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `.create` be split into smaller, more focused modules?**
  _Cohesion score 0.0504828797190518 - nodes in this community are weakly interconnected._
- **Why does `Role` connect `institutes/tests/test_api_portal.py` to `.create`, `UserManager`, `Institute`, `IsInstituteMember`, `institutes/services.py`, `ActionRequiredTests`, `control_panel/api/v1/views.py`, `InvitationTests`, `RegistrationApiTests`, `AdminEnquiryTests`, `control_panel/api/v1/serializers.py`, `HasPlatformPermission`, `.url`, `DocumentTests`, `RegistrationTests`, `PublicInstituteApiTests`, `ContactTests`, `users/services.py`, `PortalTestCase`, `add_location`, `Enquiry`, `BaseModel`, `User`, `create_admin`, `InstituteAdminSiteTests`, `UserConstraintTests`, `AuthApiTests`?**
  _High betweenness centrality (0.079) - this node is a cross-community bridge._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `Decision: hybrid mode dropped (2026-10-13)` and `PRD training modes: Physical, Online, Hybrid`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `PRD institute locations (several, one main office)` and `Training venue: exactly one TrainingLocation, independent of institute offices`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._