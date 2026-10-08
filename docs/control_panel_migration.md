# Control Panel App Migration - Summary

## Overview
Created a dedicated `control_panel` app that consolidates all admin-related functionality previously scattered across `users`, `institutes`, `training`, and `common` apps. This provides a single entry point for admin operations under `/api/v1/admin/`.

## What Was Done

### 1. Created New App Structure
```
apps/control_panel/
├── api/v1/
│   ├── users/
│   │   ├── serializers.py    # AdminSerializer (moved from users app)
│   │   └── views.py          # AdminViewSet (moved from users app)
│   ├── institutes/
│   │   ├── serializers.py    # AdminInstituteSerializer, DocumentReviewSerializer, etc.
│   │   └── views.py          # AdminInstituteViewSet, AdminDocumentView, AdminDocumentDownloadView
│   ├── training/
│   │   ├── serializers.py    # AdminTrainingListSerializer, AdminTrainingSerializer, TrainingReasonSerializer
│   │   └── views.py          # AdminTrainingViewSet
│   ├── filters.py            # AdminTrainingFilter (moved from training app)
│   └── urls.py               # Unified admin URL routing
├── apps.py
├── models.py                 # Empty (no new models)
└── admin.py                  # Empty (uses existing admin)
```

### 2. Consolidated Admin Endpoints

| Previous Location | New Location (under `/admin/`) |
|-------------------|--------------------------------|
| `/user/admins/` → `apps.users.api.v1.views.AdminViewSet` | `/admin/users/admins/` → `apps.control_panel.api.v1.users.views.AdminViewSet` |
| `/admin/institutes/` → `apps.institutes.api.v1.views.AdminInstituteViewSet` | `/admin/institutes/` → `apps.control_panel.api.v1.institutes.views.AdminInstituteViewSet` |
| `/admin/institutes/{id}/documents/` → `apps.institutes.api.v1.views.AdminDocumentView` | `/admin/institutes/{id}/documents/` → `apps.control_panel.api.v1.institutes.views.AdminDocumentView` |
| `/admin/trainings/` → `apps.training.api.v1.views.AdminTrainingViewSet` | `/admin/trainings/` → `apps.control_panel.api.v1.training.views.AdminTrainingViewSet` |
| `/admin/categories/` → `apps.common.api.v1.views.AdminCategoryViewSet` | `/admin/categories/` → `apps.control_panel.api.v1.views.AdminCategoryViewSet` |

### 3. Backward Compatibility
- `/user/admins/` still works (mapped to same `AdminViewSet` in control_panel)
- Old admin URLs in individual apps are removed

## Files Modified

### Core Configuration
| File | Change |
|------|--------|
| `config/settings/base.py` | Added `"apps.control_panel"` to `LOCAL_APPS` |

### Main URL Routing
| File | Change |
|------|--------|
| `apps/api/v1/urls.py` | Replaced 3 separate `admin/` includes with single `include("apps.control_panel.api.v1.urls")`; added backward compat route for `/user/admins/` |

### Users App
| File | Change |
|------|--------|
| `apps/users/api/v1/urls/users.py` | Removed `AdminViewSet` router registration (no longer owns admin management) |
| `apps/users/api/v1/views.py` | Removed `AdminViewSet` class; imports `AdminSerializer` from control_panel |

### Control Panel App - Users
| File | Change |
|------|--------|
| `apps/control_panel/api/v1/users/serializers.py` | Added `from apps.users import services` import; fixed `services.create_admin` / `services.update_admin` calls |
| `apps/control_panel/api/v1/users/views.py` | Unchanged (already correct) |

### Control Panel App - Training
| File | Change |
|------|--------|
| `apps/control_panel/api/v1/training/views.py` | Changed `from apps.common import services` → `from apps.training import services`; added `from apps.training.api.v1.views import CHILDREN` |
| `apps/control_panel/api/v1/training/serializers.py` | Unchanged |

### Control Panel App - Institutes
| File | Change |
|------|--------|
| `apps/control_panel/api/v1/institutes/views.py` | Changed `from apps.common import services` → `from apps.institutes import services`; added `AdminDocumentSerializer` import; fixed `AdminDocumentView.patch()` to pass serializer context |
| `apps/control_panel/api/v1/institutes/serializers.py` | Fixed import: `from rest_framework import serializers` instead of `from apps.common import serializers` |

### Control Panel App - URLs
| File | Change |
|------|--------|
| `apps/control_panel/api/v1/urls.py` | **New file** - unified router with all admin viewsets: `AdminCategoryViewSet`, `AdminViewSet`, `AdminInstituteViewSet`, `AdminTrainingViewSet` + document endpoints |

### Common App
| File | Change |
|------|--------|
| `apps/common/api/v1/urls/admin.py` | Removed (admin categories moved to control_panel) |

### Training App
| File | Change |
|------|--------|
| `apps/training/api/v1/urls/admin.py` | Removed (admin trainings moved to control_panel) |

### Institutes App
| File | Change |
|------|--------|
| `apps/institutes/api/v1/urls/admin.py` | Removed (admin institutes moved to control_panel) |

## Testing
- All 339 existing tests pass
- 1 pre-existing flaky test (`test_the_sixth_registration_in_an_hour_is_throttled`) unrelated to this migration
- Django system check passes with no warnings

## Benefits
1. **Single admin entry point**: All admin operations under `/api/v1/admin/`
2. **Clear separation**: Admin logic isolated from public/portal APIs
3. **Easier maintenance**: Admin permissions, throttling, and docs in one place
4. **Consistent patterns**: All admin viewsets follow same structure (ReadOnlyViewSet + action decorators)