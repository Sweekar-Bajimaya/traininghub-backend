# Control Panel App - Migration Notes

A record of the move, not a description of the code: where they differ, the code wins. The current layout is in
`CLAUDE.md` (Layout) and the decision is in `docs/System Design.md` (decision log, 2026-10-10).

## What changed

Every admin endpoint now lives in one app, `apps/control_panel`, under `/api/v1/admin/`. Before, the admin side was
spread over four apps (`users`, `common`, `institutes`, `training`), each with its own `urls/admin.py` and an `Admin*`
viewset and serializer next to its public and portal code.

`control_panel` has no models and no migrations. It only exposes the other apps' services over HTTP; the rules stay
where they were (`users/services.py`, `common/services.py`, `institutes/services.py`, `training/services.py`).

## Structure

```
apps/control_panel/
├── apps.py, __init__.py
├── models.py, admin.py, migrations/    empty (no models)
├── tests.py                            routing: admin API root, admin/users/admins/, the old path is gone
└── api/v1/
    ├── serializers.py                  every admin serializer
    ├── views.py                        every admin view
    ├── filters.py                      AdminCategoryFilter, AdminTrainingFilter
    └── urls.py                         one DefaultRouter + the two document routes
```

`api/v1/` is deliberately flat for now (one file each). `serializers.py` and `views.py` are grouped by comment headers in
the same order: admins, categories, institutes, trainings. If a file grows too large, split it per resource then.

## Where each endpoint came from

| Endpoint (under `/api/v1/`) | Permission | Was in |
|---|---|---|
| `admin/users/admins/` (list, create, retrieve, patch) | `users.manage_admins` | `users` (`user/admins/`, now a 404) |
| `admin/categories/` (list, create, retrieve, patch) | `users.manage_categories` | `common` |
| `admin/institutes/` and `{id}/{approve,reject,request-info,suspend,reinstate}/` | `users.manage_institutes` | `institutes` |
| `admin/institutes/{id}/documents/{doc}/` (PATCH) and `.../download/` | `users.manage_institutes` | `institutes` |
| `admin/trainings/` and `{id}/{approve,request-changes,reject}/` | `users.manage_trainings` | `training` |

`GET admin/` is the DRF API root and lists the four groups (`users/admins`, `categories`, `institutes`, `trainings`).

Only the admin-team path changed. The category, institute and training admin URLs are the same as before the move.

## The old admins path

`user/admins/` was dropped with no alias: it answers 404 now, and the frontend must call `admin/users/admins/`.
`PATCH user/users/{id}/status/` (suspend / activate) did not move; it is still in `users`.

## Files touched outside `control_panel`

| File | Change |
|---|---|
| `config/settings/base.py` | `"apps.control_panel"` added to `LOCAL_APPS` |
| `apps/api/v1/urls.py` | one `admin/` include of `control_panel` |
| `apps/users/api/v1/{serializers,views}.py`, `urls/users.py` | `AdminSerializer` and `AdminViewSet` removed |
| `apps/common/api/v1/{serializers,views,filters}.py` | `AdminCategory*` removed |
| `apps/institutes/api/v1/{serializers,views}.py` | `Admin*` serializers and views, `ReasonSerializer`, `DocumentReviewSerializer` removed |
| `apps/training/api/v1/{serializers,views,filters}.py` | `Admin*` serializers, viewset and filter, `TrainingReasonSerializer` removed |
| `apps/{common,institutes,training}/api/v1/urls/admin.py` | deleted |

Import direction: `control_panel` imports from `users`, `common`, `institutes` and `training`; nothing imports it except
`apps/api/v1/urls.py`. The one cross-view import is `with_content` (training) and `private_file_response` (institutes).

## Merge with `main-v2` (2026-10-10)

`main-v2` changed the same training files that the move emptied. The merge was finished by hand:

- `AdminTrainingSerializer` takes the flat `overview`, `eligibility`, `certification`, `skills` and `contact_*` fields
  (`TrainingContentFields`), and `AdminTrainingViewSet` loads them with `with_content()` (the detail and contact rows plus
  the children), as `main-v2` did in `training/api/v1`.
- The portal `cover` and `summary` actions had been deleted along with the admin viewset that followed them; they are back
  in `PortalTrainingViewSet`.
- `main-v2`'s `DefaultRouter` change is followed in `control_panel/api/v1/urls.py`.
- The two reason serializers (`ReasonSerializer` and `TrainingReasonSerializer`, both just `reason`) are one
  `ReasonSerializer`.

## Testing

`python manage.py test`: 355 tests pass (352 from `main-v2` plus 3 in `apps/control_panel/tests.py`).
`python manage.py check` and `python manage.py makemigrations --check --dry-run` are clean. The admin endpoints keep
being tested with their resource (`apps/users/tests.py`, `apps/common/tests/`, `apps/institutes/tests/`,
`apps/training/tests/`); they hit the URLs, so the move needed no test changes.
