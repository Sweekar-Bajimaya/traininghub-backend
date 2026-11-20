# Graph Report - traininghub-backend  (2026-11-20)

## Corpus Check
- 75 files · ~74,492 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2345 nodes · 5258 edges · 123 communities (66 shown, 57 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 639 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- .create
- training/services.py
- training/models.py
- control_panel/api/v1/serializers.py
- institutes/api/v1/views.py
- institutes/services.py
- ActionRequiredTests
- control_panel/api/v1/views.py
- users/api/v1/views.py
- InvitationTests
- RegistrationApiTests
- EditTests
- AdminInstituteViewSet
- viewsets.py
- AdminInstitutesApiTests
- FilterTests
- training app
- AdminDashboardSummaryTests
- PublicTrainingViewSet
- institutes app
- SubmitTests
- .as_
- Enquiry
- InstituteStatus
- Training
- institutes/tests/test_api_portal.py
- enquiries/services.py
- institutes/models.py
- category.py
- EnquiryNote
- enquiries-status.md
- 8. Open questions
- AdminTrainingSerializer
- _transition
- HasPlatformPermission
- SubmitTests
- AdminApiTests
- Notification
- PublicTrainingListSerializer
- notify() service (notification.services.notify)
- .url
- DocumentTests
- Location
- institute_experience
- CategoryConstraintTests
- AdminInstituteListSerializer
- institutes/validators.py
- 4.3 Backend work not done
- LocationModelTests
- PublicInstituteApiTests
- RegistrationOtpApiTests
- Role
- PortalEnquiryViewSet
- ContactTests
- OtpApiTests
- DynamicFieldsModelSerializer
- common/validators.py
- EnquiryConstraintTests
- notification/services.py
- AdminTrainingsFeaturedAndReviewApiTests
- Notification event registry (registry.EVENTS)
- EnquiryEventTests
- notify
- AdminCategoryApiTests
- add_location
- _otp_keys
- NormalizedEmailSerializer
- Enquiry model (apps/enquiries)
- v1/permissions.py
- fields.py
- EnquiryCreateSerializer
- InstituteProfileSerializer
- InvitationTests
- purge_old
- helpers.py
- PortalTestCase
- AdminApiTests
- validate_phone_number
- create_admin
- LocationTests
- WorkflowTests
- NotificationApiTests
- TrainingConstraintTests
- get_otp
- Base64FieldMixin
- AdminEnquiryListSerializer
- update_admin
- InstituteAdminSiteTests
- StaffTests
- UserConstraintTests
- load_locations.py
- LocationApiTests
- StatusChangeTests
- CollapseDuplicateDocumentsTests
- TrainingReviewEventTests
- StartDateRangeTests
- exception_handlers.py
- ListTests
- InstituteCoverSerializer
- GalleryTests
- SocialLinkTests
- registry.py
- PasswordChangeSerializer
- ActiveAccountJWTAuthentication
- django_core_cache
- AdminSerializer
- AuthApiTests
- re
- InstituteCEO
- IsInstituteMember
- PrivateStorage
- SendOTPSerializer
- Command
- annotate_institute_public_counts
- expire_trainings.py
- VenueSerializer
- Dependency: Django 5.2.4
- Dependency: django-q2 1.8.0
- Dependency: django-redis 6.0.0
- Dependency: djangorestframework 3.16.0
- Dev extras: debug toolbar, django-extensions, ipdb, ipython, fabric3, pylint

## God Nodes (most connected - your core abstractions)
1. `Training` - 85 edges
2. `Institute` - 65 edges
3. `InstituteStatus` - 62 edges
4. `Enquiry` - 53 edges
5. `AdminInstitutesApiTests` - 51 edges
6. `TrainingStatus` - 50 edges
7. `RegistrationApiTests` - 47 edges
8. `InstituteDocument` - 33 edges
9. `ActionRequiredTests` - 29 edges
10. `EventType` - 29 edges

## Surprising Connections (you probably didn't know these)
- `2.2 Rules (`apps/enquiries/services.py`)` --references--> `change_status()`  [INFERRED]
  docs/enquiries-status.md → apps/enquiries/services.py
- `2.2 Rules (`apps/enquiries/services.py`)` --references--> `submit_enquiry()`  [INFERRED]
  docs/enquiries-status.md → apps/enquiries/services.py
- `2.4 Changes outside the new app` --references--> `delete_training()`  [INFERRED]
  docs/enquiries-status.md → apps/training/services.py
- `4.3 Backend work not done` --references--> `change_status()`  [INFERRED]
  docs/enquiries-status.md → apps/enquiries/services.py
- `2.1 Data (`apps/enquiries/models.py`)` --references--> `Enquiry`  [INFERRED]
  docs/enquiries-status.md → apps/enquiries/models.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Enquiry milestone alerting: submit/convert services fire thresholds recorded once in the dedupe table** — docs_system_design_submit_enquiry, docs_system_design_change_status, docs_system_design_event_milestone, docs_system_design_notification_milestones, docs_system_design_notificationdedupe, docs_system_design_seats [EXTRACTED 1.00]
- **Notification dispatch pipeline: notify() looks up the registry, writes rows, queues email after commit** — docs_system_design_notify_service, docs_system_design_event_registry, docs_system_design_notification_model, docs_system_design_notificationdedupe, docs_system_design_notification_email_task, docs_system_design_savepoint_isolation [EXTRACTED 1.00]
- **Domain apps that call notify() and resolve their own recipients** — docs_system_design_users_app, docs_system_design_institutes_app, docs_system_design_training_app, docs_system_design_enquiries_app, docs_system_design_notify_service, docs_system_design_recipient_resolution [EXTRACTED 1.00]

## Communities (123 total, 57 thin omitted)

### Community 0 - ".create"
Cohesion: 0.05
Nodes (10): ActionQueryCountTests, AdminApiTests, CoverTests, LifecycleTests, PortalCreateTests, PortalEditTests, PortalPermissionTests, PortalTestCase (+2 more)

### Community 1 - "training/services.py"
Cohesion: 0.08
Nodes (37): staff_users(), DurationUnit, TrainingMode, TrainingStatus, TrainingLocation, admin_counts(), annotate_category_training_count(), approve() (+29 more)

### Community 2 - "training/models.py"
Cohesion: 0.08
Nodes (21): duration_q(), prefix_query(), TrainingFilter, Meta, LearningOutcomeSerializer, Meta, TrainingSessionSerializer, Meta (+13 more)

### Community 3 - "control_panel/api/v1/serializers.py"
Cohesion: 0.06
Nodes (20): AdminInstituteSerializer, Meta, DashboardEnquiryCountsSerializer, DashboardInstituteCountsSerializer, DashboardTrainingCountsSerializer, EnquiryCountsSerializer, GalleryImageSerializer, Meta (+12 more)

### Community 4 - "institutes/api/v1/views.py"
Cohesion: 0.05
Nodes (19): AcceptInvitationSerializer, GalleryReorderSerializer, InstituteActionRequiredSerializer, InstituteDocumentSerializer, Meta, InstituteRegistrationSerializer, Meta, InstituteSummarySerializer (+11 more)

### Community 5 - "institutes/services.py"
Cohesion: 0.08
Nodes (29): PublicInstituteViewSet, Institute, Meta, InstituteContact, InstituteGalleryImage, Meta, InstituteLocation, Meta (+21 more)

### Community 6 - "ActionRequiredTests"
Cohesion: 0.08
Nodes (3): ActionRequiredTests, CoverTests, DocumentAndGalleryTests

### Community 7 - "control_panel/api/v1/views.py"
Cohesion: 0.05
Nodes (16): build_category_tree(), build_tree(), CategoryTreeView, LocationTreeView, LocationViewSet, AdminCategoryFilter, Meta, AdminDashboardSummarySerializer (+8 more)

### Community 8 - "users/api/v1/views.py"
Cohesion: 0.05
Nodes (17): IdentityScopedRateThrottle, ActionAPIView, RegisterSendOTPView, RegisterVerifyOTPView, LoginSerializer, ProfileSerializer, Meta, UpdateStatusSerializer (+9 more)

### Community 9 - "InvitationTests"
Cohesion: 0.07
Nodes (4): InvitationTests, LocationTests, RegistrationOtpServiceTests, RegistrationTests

### Community 11 - "EditTests"
Cohesion: 0.06
Nodes (7): CreateTests, EditTests, ExpiryTests, ReviewTests, SubmitTests, TrainingTestCase, TransitionTableTests

### Community 12 - "AdminInstituteViewSet"
Cohesion: 0.08
Nodes (8): AdminTrainingFilter, Meta, AdminTrainingFeaturedSerializer, ReasonSerializer, AdminInstituteViewSet, AdminTrainingViewSet, _locations_queryset(), _trainings_count()

### Community 13 - "viewsets.py"
Cohesion: 0.12
Nodes (21): BaseViewSet, CreateListDestroyViewSet, CreateListRetrieveUpdateViewSet, CreateListUpdateDestroyViewSet, CreateListUpdateViewSet, CreateListViewSet, CreateRetrieveUpdateViewSet, CreateRetrieveViewSet (+13 more)

### Community 15 - "FilterTests"
Cohesion: 0.08
Nodes (8): DetailTests, FilterOptionTests, FilterTests, PublicTrainingTestCase, SearchTests, ShiftsAreShownTests, titles(), VisibilityTests

### Community 16 - "training app"
Cohesion: 0.09
Nodes (32): Category (two-level tree), common app (shared base classes and reference data), Core entities (section 3), expire_trainings daily job, Training.is_featured flag and set_featured, Institute model, Entity: InstituteCEO, Entity: InstituteContact (+24 more)

### Community 17 - "AdminDashboardSummaryTests"
Cohesion: 0.07
Nodes (3): AdminDashboardSummaryTests, AdminEnquiryTests, ControlPanelRoutesTests

### Community 18 - "PublicTrainingViewSet"
Cohesion: 0.08
Nodes (11): DeleteTrainingTests, CoverSerializer, as_options(), PortalTrainingViewSet, PublicTrainingViewSet, transition(), run(), with_content() (+3 more)

### Community 19 - "institutes app"
Cohesion: 0.09
Nodes (32): consume_otp(), admin/enquiries/ read-only monitor, Admin audience (Super Admin plus holders of matching manage_* permission, in-app only), Event admin.document_reuploaded, Event admin.institute_verification, Event admin.training_review, admin/institutes/{slug}/activity/ timeline, InstituteDocument (with rejection reason) (+24 more)

### Community 20 - "SubmitTests"
Cohesion: 0.11
Nodes (5): ChangeStatusTests, NoteTests, ServiceTestCase, submit(), SubmitTests

### Community 21 - ".as_"
Cohesion: 0.11
Nodes (3): CEOTests, ProfileTests, SummaryTests

### Community 22 - "Enquiry"
Cohesion: 0.15
Nodes (8): PortalEnquiryFilter, Meta, EnquiryStatus, PreferredTime, Enquiry, Meta, SeatRaceTests, SummaryTests

### Community 23 - "InstituteStatus"
Cohesion: 0.12
Nodes (13): AdminInstituteFilter, Meta, ChoiceInFilter, _pending_documents_count(), DocumentStatus, InstituteStatus, InstituteType, InstituteDocument (+5 more)

### Community 24 - "Training"
Cohesion: 0.10
Nodes (12): _event(), institute_activity(), Training, Meta, refresh_search_vectors(), expire_trainings(), refresh_category_trainings(), refresh_institute_trainings() (+4 more)

### Community 26 - "enquiries/services.py"
Cohesion: 0.13
Nodes (15): EnquiryType, admin_counts(), _check_converted_milestone(), _check_intake_milestones(), _claim_phone_slot(), counts(), _fire_highest(), _is_open_duplicate() (+7 more)

### Community 27 - "institutes/models.py"
Cohesion: 0.14
Nodes (14): _owner_prefetch(), InvitationStatus, MemberRole, InstituteInvitation, Meta, InstituteMember, Meta, accept_invitation() (+6 more)

### Community 28 - "category.py"
Cohesion: 0.12
Nodes (11): BaseModel, Meta, SlugModel, Meta, Category, Meta, _check_parent(), create_category() (+3 more)

### Community 29 - "EnquiryNote"
Cohesion: 0.09
Nodes (13): EnquiryNoteSerializer, Meta, PortalEnquiryNoteView, EnquiryNote, Meta, add_note(), registration_open_q(), 2.1 Data (`apps/enquiries/models.py`) (+5 more)

### Community 30 - "enquiries-status.md"
Cohesion: 0.11
Nodes (23): 1. In short, 3. Where the build differs from the prototype, 4.1 Before it works end to end, 4.2 Frontend changes against the prototype, 4.4 Risks and limits to know about, 4.5 Questions still open (numbers as in `docs/System Design.md`, section 8), 4. What needs changes, 5. How to check it (+15 more)

### Community 31 - "8. Open questions"
Cohesion: 0.10
Nodes (25): 4.5 Questions still open (1, 8, 14), Phase 2: Application (approve/reject/capacity) and learners, Availability: seats minus CONVERTED enquiries above zero, Categories: two-level tree with icon and hue, training uses a leaf, Auth: email + password, JWT RS256 via simplejwt, My enquiries: browser device token, last 90 days, 8. Open questions, Open question 1: enquiry retention (+17 more)

### Community 32 - "AdminTrainingSerializer"
Cohesion: 0.10
Nodes (9): AdminTrainingSerializer, Meta, PortalTrainingSerializer, Meta, TrainingContentFields, TrainingModuleSerializer, Meta, TrainingModule (+1 more)

### Community 33 - "_transition"
Cohesion: 0.10
Nodes (11): InstituteStatusLog, Meta, _notify_status_change(), reinstate(), reject(), request_info(), resubmit(), suspend() (+3 more)

### Community 34 - "HasPlatformPermission"
Cohesion: 0.11
Nodes (8): AdminDocumentDownloadView, AdminViewSet, PortalDocumentDownloadView, private_file_response(), HasAnyPlatformPermission, HasPlatformPermission, IsInstituteStaff, IsPlatformAdmin

### Community 35 - "SubmitTests"
Cohesion: 0.14
Nodes (4): NoVisitorIdentityTests, PublicTestCase, SubmitTests, ThrottleTests

### Community 37 - "Notification"
Cohesion: 0.13
Nodes (8): NotificationSerializer, Meta, NotificationViewset, Notification, Meta, mark_all_read(), mark_read(), unread_count()

### Community 38 - "PublicTrainingListSerializer"
Cohesion: 0.10
Nodes (8): duration_text(), format_class_days(), PortalTrainingListSerializer, Meta, PublicTrainingDetailSerializer, Meta, PublicTrainingListSerializer, Meta

### Community 39 - "notify() service (notification.services.notify)"
Cohesion: 0.14
Nodes (18): Claim: qcluster is not needed for enquiries, users.services.admins_with_permission, control_panel app (admin API under admin/), users.services.create_admin, Event admin.account_created (note to change initial password), notification app (apps/notification), Notification email task (django-q2, one per row), Notifications inbox API (notifications/) (+10 more)

### Community 40 - ".url"
Cohesion: 0.16
Nodes (4): AccessTests, DetailTests, NoteTests, PortalTestCase

### Community 42 - "Location"
Cohesion: 0.19
Nodes (8): LocationFilter, Meta, active_municipalities(), LocationInputSerializer, LocationLevel, MunicipalityType, Location, Meta

### Community 43 - "institute_experience"
Cohesion: 0.12
Nodes (8): InstituteExperienceTests, _duration(), institute_experience(), membership_duration(), PublicInstituteDetailSerializer, Meta, PublicInstituteListSerializer, Meta

### Community 44 - "CategoryConstraintTests"
Cohesion: 0.13
Nodes (3): CategoryConstraintTests, CategoryServiceTests, LoadCategoriesTests

### Community 45 - "AdminInstituteListSerializer"
Cohesion: 0.13
Nodes (7): AdminCategorySerializer, Meta, AdminDocumentSerializer, Meta, AdminInstituteListSerializer, Meta, AdminDocumentView

### Community 46 - "institutes/validators.py"
Cohesion: 0.13
Nodes (6): validate_document_file(), validate_image_file(), validate_institute_location(), _validate_upload(), Command, load_jwt_key()

### Community 47 - "4.3 Backend work not done"
Cohesion: 0.11
Nodes (14): 4.3 Backend work not done, Admin enquiries monitor listed as not built, Audit trail gap (change_status takes by, TODO(audit)), Dashboard analytics gap (needs analytics app and view counting), Seats left and availability filter gap, TrainingHub Backend System Design (DRAFT v0.6), admin/dashboard/summary/ endpoint, analytics app (planned) (+6 more)

### Community 48 - "LocationModelTests"
Cohesion: 0.14
Nodes (4): level_counts(), load(), LoadLocationsTests, LocationModelTests

### Community 51 - "Role"
Cohesion: 0.15
Nodes (4): Role, UserManager, User, Meta

### Community 53 - "PortalEnquiryViewSet"
Cohesion: 0.12
Nodes (6): PortalEnquiryListSerializer, Meta, PortalEnquirySerializer, Meta, PortalEnquiryViewSet, summary()

### Community 56 - "DynamicFieldsModelSerializer"
Cohesion: 0.12
Nodes (4): LocationSerializer, Meta, DynamicFieldsModelSerializer, DynamicFieldsSerializer

### Community 57 - "common/validators.py"
Cohesion: 0.18
Nodes (9): combine_date_parts(), get_today(), validate_attachment(), validate_coded_phone_number(), validate_dob(), validate_future_datetime(), validate_is_future_datetime(), validate_otp() (+1 more)

### Community 59 - "notification/services.py"
Cohesion: 0.23
Nodes (4): NotificationDedupe, Meta, claim(), mark_seen()

### Community 61 - "Notification event registry (registry.EVENTS)"
Cohesion: 0.23
Nodes (12): Update 2026-11-20: enquiry events now notify institute staff, Institute staff audience (owner and staff, in-app and email), Event document.rejected, Event enquiry.converted (other staff only), Event enquiry.new (plain enquiry or interest), Events institute.approved/.rejected/.info_requested/.suspended/.reinstated, Events milestone.enquiries/.interest/.converted, Notification event registry (registry.EVENTS) (+4 more)

### Community 63 - "notify"
Cohesion: 0.18
Nodes (3): Event, notify(), NotifyTests

### Community 66 - "_otp_keys"
Cohesion: 0.16
Nodes (5): RegistrationOTPSerializer, normalize_email(), _otp_keys(), send_otp(), send_registration_otp()

### Community 67 - "NormalizedEmailSerializer"
Cohesion: 0.15
Nodes (5): NormalizedEmailSerializer, RegistrationOTPVerifySerializer, VerifyOTPSerializer, verify_otp(), verify_registration_otp()

### Community 68 - "Enquiry model (apps/enquiries)"
Cohesion: 0.24
Nodes (14): Changing the status rules (change_status), EnquiryNote, Seat check on submit does not lock the training, Enquiry statuses, types and preferred time, enquiries.services.change_status, enquiries app, Enquiry model (apps/enquiries), Enquiry statuses (seven, any to any) (+6 more)

### Community 71 - "EnquiryCreateSerializer"
Cohesion: 0.17
Nodes (5): EnquiryCreateSerializer, Meta, VisitorEnquirySerializer, Meta, VisitorViewTests

### Community 72 - "InstituteProfileSerializer"
Cohesion: 0.15
Nodes (5): InstituteProfileSerializer, Meta, InstituteProfileView, PortalContactView, ResubmitView

### Community 74 - "purge_old"
Cohesion: 0.18
Nodes (4): Command, purge_old(), purge_notifications(), PurgeTests

### Community 75 - "helpers.py"
Cohesion: 0.23
Nodes (5): get_upload_path(), get_uuid_filename(), nested_getattr(), set_instance_fields(), update_instance()

### Community 76 - "PortalTestCase"
Cohesion: 0.18
Nodes (4): EndToEndTests, PermissionMatrixTests, PortalTestCase, ResubmitTests

### Community 78 - "validate_phone_number"
Cohesion: 0.29
Nodes (4): ValidatePanVatNumberTests, ValidatePhoneNumberTests, validate_pan_vat_number(), validate_phone_number()

### Community 79 - "create_admin"
Cohesion: 0.20
Nodes (4): change_password(), create_admin(), _revoke_refresh_tokens(), set_status()

### Community 84 - "get_otp"
Cohesion: 0.31
Nodes (7): OTPPurpose, get_otp(), send_otp_email(), send_registration_otp_email(), _deliver_otp(), send_otp_email_task(), send_registration_otp_email_task()

### Community 86 - "AdminEnquiryListSerializer"
Cohesion: 0.20
Nodes (5): AdminEnquiryFilter, Meta, AdminEnquiryListSerializer, Meta, AdminEnquiryViewSet

### Community 87 - "update_admin"
Cohesion: 0.31
Nodes (3): _set_permissions(), update_admin(), StatusApiTests

### Community 99 - "InstituteCoverSerializer"
Cohesion: 0.25
Nodes (3): InstituteCoverSerializer, Meta, PortalCoverView

### Community 102 - "registry.py"
Cohesion: 0.25
Nodes (3): Channel, send(), send_notification_email()

## Ambiguous Edges - Review These
- `PRD training modes: Physical, Online, Hybrid` → `Decision: hybrid mode dropped (2026-10-13)`  [AMBIGUOUS]
  docs/Training for Merojob (PRD).md · relation: conceptually_related_to
- `PRD institute locations (several, one main office)` → `Training venue: exactly one TrainingLocation, independent of institute offices`  [AMBIGUOUS]
  docs/Training for Merojob (PRD).md · relation: conceptually_related_to
- `Notification email task (django-q2, one per row)` → `Claim: qcluster is not needed for enquiries`  [AMBIGUOUS]
  docs/enquiries-status.md · relation: conceptually_related_to
- `admin/enquiries/ read-only monitor` → `Admin enquiries monitor listed as not built`  [AMBIGUOUS]
  docs/enquiries-status.md · relation: conceptually_related_to

## Knowledge Gaps
- **23 isolated node(s):** `Dev extras: debug toolbar, django-extensions, ipdb, ipython, fabric3, pylint`, `Dependency: Django 5.2.4`, `Dependency: djangorestframework 3.16.0`, `Dependency: djangorestframework-simplejwt 5.5.1 (with PyJWT crypto)`, `Dependency: django-q2 1.8.0` (+18 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 780 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **57 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Training` connect `Training` to `.create`, `training/services.py`, `training/models.py`, `control_panel/api/v1/serializers.py`, `institutes/api/v1/views.py`, `institutes/services.py`, `control_panel/api/v1/views.py`, `EditTests`, `AdminInstituteViewSet`, `AdminInstitutesApiTests`, `FilterTests`, `AdminDashboardSummaryTests`, `PublicTrainingViewSet`, `SubmitTests`, `Enquiry`, `InstituteStatus`, `enquiries/services.py`, `AdminTrainingSerializer`, `PublicTrainingListSerializer`, `AdminTrainingsFeaturedAndReviewApiTests`, `EnquiryEventTests`, `EnquiryCreateSerializer`, `TrainingConstraintTests`, `annotate_institute_public_counts`?**
  _High betweenness centrality (0.118) - this node is a cross-community bridge._
- **Are the 56 inferred relationships involving `Training` (e.g. with `AdminTrainingFilter` and `institute_activity()`) actually correct?**
  _`Training` has 56 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Dev extras: debug toolbar, django-extensions, ipdb, ipython, fabric3, pylint`, `Dependency: Django 5.2.4`, `Dependency: djangorestframework 3.16.0` to the rest of the system?**
  _23 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `.create` be split into smaller, more focused modules?**
  _Cohesion score 0.0504828797190518 - nodes in this community are weakly interconnected._
- **Why does `Enquiry` connect `Enquiry` to `control_panel/api/v1/serializers.py`, `SubmitTests`, `institutes/services.py`, `EnquiryConstraintTests`, `control_panel/api/v1/views.py`, `EnquiryCreateSerializer`, `.url`, `institutes/api/v1/views.py`, `AdminDashboardSummaryTests`, `SubmitTests`, `PortalEnquiryViewSet`, `AdminEnquiryListSerializer`, `InstituteStatus`, `Training`, `enquiries/services.py`, `EnquiryNote`, `EnquiryEventTests`?**
  _High betweenness centrality (0.099) - this node is a cross-community bridge._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `PRD training modes: Physical, Online, Hybrid` and `Decision: hybrid mode dropped (2026-10-13)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `PRD institute locations (several, one main office)` and `Training venue: exactly one TrainingLocation, independent of institute offices`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._