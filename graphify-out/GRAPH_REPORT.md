# Graph Report - traininghub-backend  (2026-11-20)

## Corpus Check
- 125 files · ~75,931 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 3)

## Summary
- 2383 nodes · 5539 edges · 123 communities (71 shown, 52 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 729 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `541e7630`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- .create
- training/services.py
- training/models.py
- InstituteRegistrationSerializer
- institutes/api/v1/views.py
- institutes/services.py
- ActionRequiredTests
- institutes/models.py
- users/api/v1/views.py
- InvitationTests
- RegistrationApiTests
- EditTests
- AdminInstituteViewSet
- viewsets.py
- AdminInstitutesApiTests
- FilterTests
- Institute model
- AdminEnquiryTests
- training/api/v1/views.py
- institutes app
- SubmitTests
- .as_
- InstituteSocialLink
- review_document
- Training
- institutes/tests/test_api_portal.py
- .get_object
- CappedLimitOffsetPaginationTests
- models/base.py
- 2. What was built
- enquiries-status.md
- Product Requirements Document (PRD)
- enquiries/services.py
- 8. Open questions
- control_panel/api/v1/views.py
- SubmitTests
- AdminApiTests
- Notification
- training/api/v1/serializers.py
- notify() service (notification.services.notify)
- .url
- DocumentTests
- django_db
- institutes/api/v1/serializers.py
- CategoryConstraintTests
- AdminInstituteListSerializer
- settings/base.py
- AppKeyPermissionTests
- LocationApiTests
- PublicInstituteApiTests
- RegistrationOtpApiTests
- users/api/v1/serializers.py
- common/validators.py
- Enquiry
- ContactTests
- OtpApiTests
- DynamicFieldsSerializer
- Enquiry model (apps/enquiries)
- EnquiryConstraintTests
- DynamicFieldsModelSerializer
- AdminTrainingsFeaturedAndReviewApiTests
- Notification event registry (registry.EVENTS)
- EnquiryEventTests
- notify
- AdminCategoryApiTests
- is_valid_key
- Institute
- users/services.py
- AdminTrainingViewSet
- Category
- notification/services.py
- TooManyRequests
- training app
- InvitationTests
- apps_notification_init
- enquiries/tests/test_services.py
- PortalTestCase
- RegistrationTests
- BaseViewSet
- StatusChangeTests
- LocationTests
- add_location
- NotificationApiTests
- TrainingConstraintTests
- EnforcedEndpointTests
- AdminTrainingSerializer
- User
- create_admin
- InstituteContact
- InstituteSummaryView
- UserConstraintTests
- Command
- LocationTests
- PortalTrainingSerializer
- InstituteConstraintTests
- InstituteReviewEventTests
- InstituteLocation
- CEOTests
- GuardedView
- app_key/tests.py
- GalleryTests
- SocialLinkTests
- InstituteDocumentSerializer
- AdminSerializer
- ActiveAccountJWTAuthentication
- .summary
- AcceptInvitationSerializer
- AuthApiTests
- ResubmitView
- InstituteCEO
- reset_keys
- UserManager
- IsInstituteMember
- summary
- expire_trainings
- Dependency: Django 5.2.4
- Dependency: django-q2 1.8.0
- Dependency: django-redis 6.0.0
- Dependency: djangorestframework 3.16.0
- Dev extras: debug toolbar, django-extensions, ipdb, ipython, fabric3, pylint
- TrainingHub Backend System Design (DRAFT v0.6)
- PasswordChangeSerializer

## God Nodes (most connected - your core abstractions)
1. `Training` - 86 edges
2. `Institute` - 65 edges
3. `InstituteStatus` - 62 edges
4. `Enquiry` - 53 edges
5. `AdminInstitutesApiTests` - 52 edges
6. `TrainingStatus` - 50 edges
7. `RegistrationApiTests` - 49 edges
8. `Role` - 46 edges
9. `DynamicFieldsModelSerializer` - 40 edges
10. `BaseModel` - 34 edges

## Surprising Connections (you probably didn't know these)
- `Decision: PAN/VAT number unique, nine digits, contact telephone optional` --references--> `validate_pan_vat_number()`  [EXTRACTED]
  docs/System Design.md → apps/common/validators.py
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

## Communities (123 total, 52 thin omitted)

### Community 0 - ".create"
Cohesion: 0.05
Nodes (10): ActionQueryCountTests, AdminApiTests, CoverTests, LifecycleTests, PortalCreateTests, PortalEditTests, PortalPermissionTests, PortalTestCase (+2 more)

### Community 1 - "training/services.py"
Cohesion: 0.09
Nodes (37): TrainingMode, TrainingStatus, LearningOutcome, Meta, TrainingLocation, admin_counts(), annotate_category_training_count(), approve() (+29 more)

### Community 2 - "training/models.py"
Cohesion: 0.08
Nodes (13): duration_q(), prefix_query(), TrainingFilter, Meta, DurationBucket, DurationUnit, StartBucket, TrainingLevel (+5 more)

### Community 3 - "InstituteRegistrationSerializer"
Cohesion: 0.22
Nodes (3): InstituteRegistrationSerializer, Meta, OTPField

### Community 4 - "institutes/api/v1/views.py"
Cohesion: 0.08
Nodes (15): DistributedKeyAuthentication, GalleryReorderSerializer, StaffSerializer, Meta, AcceptInvitationView, PortalCoverView, PortalDocumentViewSet, PortalGalleryViewSet (+7 more)

### Community 5 - "institutes/services.py"
Cohesion: 0.14
Nodes (19): InstituteStatus, accept_invitation(), admin_counts(), approve(), deactivate_location(), _hash(), invite(), _notify_status_change() (+11 more)

### Community 6 - "ActionRequiredTests"
Cohesion: 0.08
Nodes (3): ActionRequiredTests, CoverTests, DocumentAndGalleryTests

### Community 7 - "institutes/models.py"
Cohesion: 0.12
Nodes (17): BaseModel, Meta, AdminInstituteFilter, Meta, ChoiceInFilter, _pending_documents_count(), DocumentStatus, InstituteType (+9 more)

### Community 8 - "users/api/v1/views.py"
Cohesion: 0.07
Nodes (11): IdentityScopedRateThrottle, ActionAPIView, RegisterVerifyOTPView, UpdateStatusSerializer, Meta, LogoutView, PasswordChangeView, RefreshView (+3 more)

### Community 10 - "RegistrationApiTests"
Cohesion: 0.09
Nodes (3): SeatRaceTests, convert(), RegistrationApiTests

### Community 11 - "EditTests"
Cohesion: 0.06
Nodes (7): CreateTests, EditTests, ExpiryTests, ReviewTests, SubmitTests, TrainingTestCase, TransitionTableTests

### Community 12 - "AdminInstituteViewSet"
Cohesion: 0.18
Nodes (3): AdminInstituteViewSet, _locations_queryset(), _trainings_count()

### Community 13 - "viewsets.py"
Cohesion: 0.19
Nodes (19): CreateListDestroyViewSet, CreateListRetrieveUpdateViewSet, CreateListUpdateDestroyViewSet, CreateListUpdateViewSet, CreateListViewSet, CreateRetrieveUpdateViewSet, CreateRetrieveViewSet, CreateUpdateViewSet (+11 more)

### Community 15 - "FilterTests"
Cohesion: 0.08
Nodes (8): DetailTests, FilterOptionTests, FilterTests, PublicTrainingTestCase, SearchTests, ShiftsAreShownTests, titles(), VisibilityTests

### Community 16 - "Institute model"
Cohesion: 0.12
Nodes (24): Category (two-level tree), common app (shared base classes and reference data), Core entities (section 3), Institute model, Entity: InstituteCEO, Entity: InstituteContact, Entity: InstituteGalleryImage, Entity: InstituteLocation (office) (+16 more)

### Community 17 - "AdminEnquiryTests"
Cohesion: 0.07
Nodes (3): AdminDashboardSummaryTests, AdminEnquiryTests, ControlPanelRoutesTests

### Community 18 - "training/api/v1/views.py"
Cohesion: 0.07
Nodes (12): DeleteTrainingTests, CoverSerializer, PortalTrainingListSerializer, Meta, as_options(), PortalTrainingViewSet, PublicTrainingViewSet, transition() (+4 more)

### Community 19 - "institutes app"
Cohesion: 0.12
Nodes (26): Dashboard analytics gap (needs analytics app and view counting), admin/dashboard/summary/ endpoint, admin/enquiries/ read-only monitor, analytics app (planned), Admin audience (Super Admin plus holders of matching manage_* permission, in-app only), Event admin.document_reuploaded, Event admin.institute_verification, Event admin.training_review (+18 more)

### Community 20 - "SubmitTests"
Cohesion: 0.09
Nodes (6): ChangeStatusTests, NoteTests, ServiceTestCase, submit(), SubmitTests, SummaryTests

### Community 21 - ".as_"
Cohesion: 0.11
Nodes (3): ProfileTests, StaffTests, SummaryTests

### Community 22 - "InstituteSocialLink"
Cohesion: 0.10
Nodes (14): AdminInstituteSerializer, Meta, InstituteContactSerializer, Meta, InstituteSocialLinkSerializer, Meta, InstituteSocialLink, Meta (+6 more)

### Community 23 - "review_document"
Cohesion: 0.21
Nodes (3): reupload_document(), review_document(), DocumentEventTests

### Community 24 - "Training"
Cohesion: 0.12
Nodes (11): _event(), institute_activity(), Training, Meta, annotate_institute_public_counts(), refresh_search_vectors(), refresh_category_trainings(), refresh_institute_trainings() (+3 more)

### Community 25 - "institutes/tests/test_api_portal.py"
Cohesion: 0.09
Nodes (10): _owner_prefetch(), ListTests, PortalTestCase, MemberRole, InstituteMember, Meta, make_staff(), PermissionMatrixTests (+2 more)

### Community 27 - "CappedLimitOffsetPaginationTests"
Cohesion: 0.17
Nodes (3): CappedLimitOffsetPagination, CappedLimitOffsetPaginationTests, limit_for()

### Community 28 - "models/base.py"
Cohesion: 0.13
Nodes (6): SlugModel, Meta, _slug_strip(), unique_slugify(), NepalMobileField, normalize_phone()

### Community 29 - "2. What was built"
Cohesion: 0.22
Nodes (6): registration_open_q(), 2.2 Rules (`apps/enquiries/services.py`), 2.3 API (all under `/api/v1/`), 2.4 Changes outside the new app, 2.5 Tests (`apps/enquiries/tests/`), 2. What was built

### Community 30 - "enquiries-status.md"
Cohesion: 0.10
Nodes (25): 1. In short, 3. Where the build differs from the prototype, 4.1 Before it works end to end, 4.2 Frontend changes against the prototype, 4.3 Backend work not done, 4.4 Risks and limits to know about, 4.5 Questions still open (numbers as in `docs/System Design.md`, section 8), 4. What needs changes (+17 more)

### Community 31 - "Product Requirements Document (PRD)"
Cohesion: 0.15
Nodes (16): Phase 2: Application (approve/reject/capacity) and learners, Categories: two-level tree with icon and hue, training uses a leaf, My enquiries: browser device token, last 90 days, Open question: do institutes keep enquiries after 90 days, Reviews and ratings out of MVP, Training duration (value + unit, derived weeks) and weekly class slots, Entity: TrainingSession (weekly slot), Workflow: enquiry (planned) (+8 more)

### Community 32 - "enquiries/services.py"
Cohesion: 0.16
Nodes (14): EnquiryType, _check_converted_milestone(), _check_intake_milestones(), _claim_phone_slot(), _fire_highest(), _is_open_duplicate(), _milestone_counts(), _notify_converted() (+6 more)

### Community 33 - "8. Open questions"
Cohesion: 0.20
Nodes (12): 4.5 Questions still open (1, 8, 14), Availability: seats minus CONVERTED enquiries above zero, Auth: email + password, JWT RS256 via simplejwt, 8. Open questions, Open question 1: enquiry retention, Open question: how an admin's password is reset, Open question: PRD 'Instructor Name' search has no field, Open question: endpoint that consumes a verified password-reset code (+4 more)

### Community 34 - "control_panel/api/v1/views.py"
Cohesion: 0.05
Nodes (29): AdminCategoryFilter, Meta, AdminEnquiryFilter, Meta, AdminTrainingFilter, Meta, AdminDashboardSummarySerializer, AdminDocumentSerializer (+21 more)

### Community 35 - "SubmitTests"
Cohesion: 0.14
Nodes (4): NoVisitorIdentityTests, PublicTestCase, SubmitTests, ThrottleTests

### Community 37 - "Notification"
Cohesion: 0.19
Nodes (6): NotificationViewset, Notification, Meta, mark_all_read(), mark_read(), unread_count()

### Community 38 - "training/api/v1/serializers.py"
Cohesion: 0.07
Nodes (18): LocationInputSerializer, validate_document_file(), validate_image_file(), _validate_upload(), available_categories(), duration_text(), format_class_days(), PublicTrainingDetailSerializer (+10 more)

### Community 39 - "notify() service (notification.services.notify)"
Cohesion: 0.12
Nodes (22): Claim: qcluster is not needed for enquiries, users.services.admins_with_permission, control_panel app (admin API under admin/), users.services.create_admin, Event admin.account_created (note to change initial password), admin/institutes/{slug}/activity/ timeline, notification app (apps/notification), Notification email task (django-q2, one per row) (+14 more)

### Community 40 - ".url"
Cohesion: 0.18
Nodes (3): AccessTests, DetailTests, NoteTests

### Community 42 - "django_db"
Cohesion: 0.07
Nodes (18): LocationFilter, Meta, active_municipalities(), LocationSerializer, Meta, build_category_tree(), build_tree(), CategoryTreeView (+10 more)

### Community 43 - "institutes/api/v1/serializers.py"
Cohesion: 0.11
Nodes (13): membership_duration(), EnquiryCountsSerializer, GalleryImageSerializer, Meta, PublicInstituteDetailSerializer, Meta, PublicInstituteListSerializer, Meta (+5 more)

### Community 44 - "CategoryConstraintTests"
Cohesion: 0.13
Nodes (3): CategoryConstraintTests, CategoryServiceTests, LoadCategoriesTests

### Community 46 - "settings/base.py"
Cohesion: 0.09
Nodes (4): PrivateStorage, Command, env_list(), load_jwt_key()

### Community 48 - "LocationApiTests"
Cohesion: 0.09
Nodes (4): load(), LoadLocationsTests, LocationApiTests, LocationModelTests

### Community 51 - "users/api/v1/serializers.py"
Cohesion: 0.11
Nodes (5): NormalizedEmailSerializer, RegistrationOTPSerializer, RegistrationOTPVerifySerializer, SendOTPSerializer, VerifyOTPSerializer

### Community 52 - "common/validators.py"
Cohesion: 0.05
Nodes (13): ValidatePanVatNumberTests, ValidatePhoneNumberTests, combine_date_parts(), get_today(), validate_attachment(), validate_coded_phone_number(), validate_dob(), validate_future_datetime() (+5 more)

### Community 53 - "Enquiry"
Cohesion: 0.07
Nodes (24): PortalEnquiryFilter, Meta, EnquiryCreateSerializer, Meta, EnquiryNoteSerializer, Meta, PortalEnquiryListSerializer, Meta (+16 more)

### Community 57 - "Enquiry model (apps/enquiries)"
Cohesion: 0.24
Nodes (14): Changing the status rules (change_status), EnquiryNote, Seat check on submit does not lock the training, Enquiry statuses, types and preferred time, enquiries.services.change_status, enquiries app, Enquiry model (apps/enquiries), Enquiry statuses (seven, any to any) (+6 more)

### Community 59 - "DynamicFieldsModelSerializer"
Cohesion: 0.16
Nodes (5): DynamicFieldsModelSerializer, InvitationSerializer, Meta, NotificationSerializer, Meta

### Community 61 - "Notification event registry (registry.EVENTS)"
Cohesion: 0.24
Nodes (11): Update 2026-11-20: enquiry events now notify institute staff, Institute staff audience (owner and staff, in-app and email), Event document.rejected, Event enquiry.converted (other staff only), Event enquiry.new (plain enquiry or interest), Events institute.approved/.rejected/.info_requested/.suspended/.reinstated, Events milestone.enquiries/.interest/.converted, Notification event registry (registry.EVENTS) (+3 more)

### Community 63 - "notify"
Cohesion: 0.18
Nodes (3): Event, notify(), NotifyTests

### Community 65 - "is_valid_key"
Cohesion: 0.18
Nodes (5): _cache_key(), forget_key(), is_valid_key(), parse_app_key(), forget_deleted_key()

### Community 66 - "Institute"
Cohesion: 0.12
Nodes (10): InstituteCoverSerializer, Meta, InstituteProfileSerializer, Meta, InstituteProfileView, PortalContactView, Institute, Meta (+2 more)

### Community 67 - "users/services.py"
Cohesion: 0.11
Nodes (15): register(), OTPPurpose, admins_with_permission(), consume_otp(), get_otp(), normalize_email(), _otp_keys(), send_otp() (+7 more)

### Community 69 - "Category"
Cohesion: 0.20
Nodes (7): Category, Meta, _check_parent(), create_category(), update_category(), AdminCategorySerializer, Meta

### Community 70 - "notification/services.py"
Cohesion: 0.21
Nodes (5): Channel, NotificationDedupe, Meta, claim(), mark_seen()

### Community 71 - "TooManyRequests"
Cohesion: 0.12
Nodes (5): TooManyRequests, RegistrationOtpServiceTests, verify_otp(), verify_registration_otp(), api_exception_handler()

### Community 72 - "training app"
Cohesion: 0.29
Nodes (10): registration_open_q change in training/services.py, expire_trainings daily job, Training.is_featured flag and set_featured, training.services.registration_open_q, training app, Training expiry: daily expire_trainings job sets EXPIRED after end_date, training.services approve / reject / request_changes, Training status workflow (DRAFT to EXPIRED) (+2 more)

### Community 74 - "apps_notification_init"
Cohesion: 0.11
Nodes (6): send(), Command, purge_old(), purge_notifications(), send_notification_email(), PurgeTests

### Community 75 - "enquiries/tests/test_services.py"
Cohesion: 0.08
Nodes (11): InstituteExperienceTests, _duration(), get_upload_path(), get_uuid_filename(), institute_experience(), nested_getattr(), set_instance_fields(), update_instance() (+3 more)

### Community 76 - "PortalTestCase"
Cohesion: 0.20
Nodes (3): EndToEndTests, PortalTestCase, ResubmitTests

### Community 85 - "AdminTrainingSerializer"
Cohesion: 0.15
Nodes (7): AdminTrainingSerializer, Meta, LearningOutcomeSerializer, Meta, TrainingContentFields, TrainingModuleSerializer, Meta

### Community 87 - "create_admin"
Cohesion: 0.11
Nodes (8): change_password(), create_admin(), _revoke_refresh_tokens(), _set_permissions(), set_status(), update_admin(), AdminApiTests, StatusApiTests

### Community 88 - "InstituteContact"
Cohesion: 0.21
Nodes (3): InstituteContact, add_contact(), InstituteAdminSiteTests

### Community 89 - "InstituteSummaryView"
Cohesion: 0.20
Nodes (4): InstituteActionRequiredSerializer, InstituteSummarySerializer, InstituteActionRequiredView, InstituteSummaryView

### Community 95 - "InstituteReviewEventTests"
Cohesion: 0.18
Nodes (3): AdminAccountEventTests, InstituteReviewEventTests, TrainingReviewEventTests

### Community 96 - "InstituteLocation"
Cohesion: 0.28
Nodes (7): InstituteLocationSerializer, Meta, InstituteLocation, Meta, _create_registration(), update_location(), validate_institute_location()

### Community 99 - "app_key/tests.py"
Cohesion: 0.12
Nodes (3): DistributedAppKey, AppKeyCorsTests, AppKeyModelTests

### Community 103 - "AdminSerializer"
Cohesion: 0.11
Nodes (7): AdminSerializer, Meta, LoginSerializer, ProfileSerializer, Meta, LoginView, MeView

### Community 109 - "InstituteCEO"
Cohesion: 0.16
Nodes (7): InstituteCEOSerializer, Meta, PortalCEOView, InstituteCEO, annotate_profile_completion(), _at_least(), save_ceo()

### Community 113 - "IsInstituteMember"
Cohesion: 0.25
Nodes (3): PortalDocumentDownloadView, IsInstituteMember, IsInstituteOwner

### Community 115 - "expire_trainings"
Cohesion: 0.25
Nodes (3): Command, expire_trainings(), expire_trainings()

### Community 123 - "TrainingHub Backend System Design (DRAFT v0.6)"
Cohesion: 0.14
Nodes (9): Audit trail gap (change_status takes by, TODO(audit)), TrainingHub Backend System Design (DRAFT v0.6), Django apps and their state (section 2), AuditLog (proposed, not built), Decision log (answered questions), Decisions made (section 1), Non-functional requirements (section 6), 3.8 Notifications (built) (+1 more)

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
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 782 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **52 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Training` connect `Training` to `.create`, `training/services.py`, `training/models.py`, `institutes/api/v1/views.py`, `institutes/models.py`, `EditTests`, `AdminInstituteViewSet`, `AdminInstitutesApiTests`, `FilterTests`, `AdminEnquiryTests`, `training/api/v1/views.py`, `SubmitTests`, `institutes/tests/test_api_portal.py`, `models/base.py`, `enquiries/services.py`, `control_panel/api/v1/views.py`, `training/api/v1/serializers.py`, `Enquiry`, `AdminTrainingsFeaturedAndReviewApiTests`, `EnquiryEventTests`, `Institute`, `AdminTrainingViewSet`, `Category`, `notification/services.py`, `enquiries/tests/test_services.py`, `TrainingConstraintTests`, `AdminTrainingSerializer`, `InstituteSummaryView`, `PortalTrainingSerializer`, `expire_trainings`?**
  _High betweenness centrality (0.137) - this node is a cross-community bridge._
- **Are the 57 inferred relationships involving `Training` (e.g. with `AdminTrainingFilter` and `institute_activity()`) actually correct?**
  _`Training` has 57 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Dependency: Django 5.2.4`, `Dependency: django-q2 1.8.0`, `Dependency: django-redis 6.0.0` to the rest of the system?**
  _23 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `.create` be split into smaller, more focused modules?**
  _Cohesion score 0.0504828797190518 - nodes in this community are weakly interconnected._
- **Why does `Institute` connect `Institute` to `training/services.py`, `training/models.py`, `InstituteRegistrationSerializer`, `institutes/api/v1/views.py`, `institutes/services.py`, `ActionRequiredTests`, `institutes/models.py`, `RegistrationApiTests`, `AdminInstituteViewSet`, `AdminInstitutesApiTests`, `AdminEnquiryTests`, `SubmitTests`, `.as_`, `InstituteSocialLink`, `Training`, `institutes/tests/test_api_portal.py`, `models/base.py`, `control_panel/api/v1/views.py`, `SubmitTests`, `AdminApiTests`, `institutes/api/v1/serializers.py`, `AdminInstituteListSerializer`, `PublicInstituteApiTests`, `Enquiry`, `enquiries/tests/test_services.py`, `PortalTestCase`, `RegistrationTests`, `add_location`, `InstituteSummaryView`, `InstituteLocation`, `InstituteCEO`?**
  _High betweenness centrality (0.076) - this node is a cross-community bridge._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `Decision: hybrid mode dropped (2026-10-13)` and `PRD training modes: Physical, Online, Hybrid`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `PRD institute locations (several, one main office)` and `Training venue: exactly one TrainingLocation, independent of institute offices`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._