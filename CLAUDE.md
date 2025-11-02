# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**University Data Visualization Dashboard MVP**

A Django-based monolithic web application for visualizing university performance data (KPIs, publications, research funding, student enrollment). Built with speed and simplicity in mind for MVP delivery.

### Tech Stack

- **Backend**: Django (Python) with Django templates
- **Database**: PostgreSQL via Supabase
- **Frontend**: Django templates + Chart.js (no React/SPA in MVP)
- **Authentication**: Django session-based auth (JWT planned for Phase 2)
- **Data Processing**: Pandas for Excel/CSV parsing
- **Deployment**: Railway

### Key Design Principles

- **Anti-over-engineering**: Only implement features explicitly documented
- **MVP-first**: Maximize development speed through simplicity
- **Django Admin for uploads**: Leverage built-in admin instead of custom UI
- **Monolithic architecture**: No API layer in MVP (planned for Phase 2)

## Critical Architecture Decisions

### Database Architecture: Supabase-First

**IMPORTANT**: This project uses Supabase PostgreSQL with a specific migration strategy:

1. **Schema is managed by Supabase migrations** in `supabase/migrations/*.sql`
2. **Django models are read-only** (set `managed = False` in Meta)
3. **Django migrations only for built-in apps** (admin, auth, sessions)

All Django models must map to existing Supabase tables:

```python
class User(models.Model):
    class Meta:
        db_table = 'users'  # Match Supabase table name
        managed = False     # Django doesn't manage schema
```

### Data Upload Architecture

**MVP approach**: File uploads happen exclusively through Django Admin (`/admin`), not custom UI. This eliminates need for:
- Custom upload forms
- File upload API endpoints
- Complex frontend state management

Upload flow:
1. Admin accesses Django Admin panel
2. Uses built-in file field to upload Excel/CSV
3. `save_model()` override triggers Pandas parsing
4. Validation happens via custom validators
5. Bulk insert to PostgreSQL
6. Upload history logged automatically via signals

### Template Architecture

Three-layer template structure:

1. **base.html**: Global layout (meta tags, CSS/JS includes, Chart.js CDN)
2. **base_dashboard.html**: Dashboard-specific (navbar, sidebar, footer)
3. **Page templates**: Specific content in `{% block dashboard_content %}`

All pages inherit from base_dashboard.html except auth pages (login/signup) which use base_auth.html.

### Permission Architecture

Four role-based access levels:

- **admin**: Full access, can upload data and approve users
- **manager**: View all departments, cannot upload
- **viewer**: View only their own department
- **pending**: Awaiting admin approval

Access control via decorators:
```python
@login_required
@role_required(['admin', 'manager'])
def analytics_view(request):
    # Department filtering based on user role
    departments = get_accessible_departments(request.user)
```

## Environment Setup

### Local Development with Supabase

```bash
# Start Supabase local instance
supabase start

# Important ports:
# - PostgreSQL: 54322
# - Supabase Studio (GUI): http://127.0.0.1:54323
# - API Gateway: 54321

# Apply/reset database schema
supabase db reset

# Start Django dev server
python manage.py runserver
```

### Environment Variables

Required in `.env`:

```bash
# Django
SECRET_KEY=your-secret-key
DEBUG=True

# Supabase Local DB
SUPABASE_DB_HOST=127.0.0.1
SUPABASE_DB_PORT=54322
SUPABASE_DB_NAME=postgres
SUPABASE_DB_USER=postgres
SUPABASE_DB_PASSWORD=postgres

# Supabase Cloud (production)
DATABASE_URL=postgresql://...
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_ROLE_KEY=...
```

## Common Development Commands

### Database Operations

```bash
# View Supabase database in browser GUI
# Navigate to: http://127.0.0.1:54323

# Reset database (reapply all migrations)
supabase db reset

# Only run Django migrations for built-in apps
python manage.py migrate

# Create Django superuser (for /admin access)
python manage.py createsuperuser
```

### Running the Application

```bash
# Development server
python manage.py runserver

# Access points:
# - Django Admin: http://127.0.0.1:8000/admin
# - Dashboard: http://127.0.0.1:8000/dashboard
# - Supabase Studio: http://127.0.0.1:54323
```

### Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.authentication
python manage.py test apps.data_upload
```

## Project Structure

```
vmc6/
├── apps/
│   ├── core/                 # Shared utilities (decorators, validators, constants)
│   ├── authentication/       # User model, login/signup, permissions
│   ├── data_upload/          # Excel/CSV parsers, validators, admin customization
│   ├── analytics/            # Data aggregators, filters, Chart.js serializers
│   └── utils/                # Date/number formatting, chart helpers, export
├── templates/
│   ├── base/                 # base.html, base_dashboard.html, base_auth.html
│   ├── components/           # Reusable: navbar, sidebar, filter_panel, kpi_card
│   └── messages/             # Success/error message templates
├── static/
│   ├── css/                  # base.css, components.css, charts.css
│   └── js/                   # chart-config.js, filter-handler.js, utils.js
├── config/
│   ├── settings/
│   │   ├── base.py          # Shared settings
│   │   ├── local.py         # Development overrides
│   │   └── production.py    # Railway deployment settings
│   └── urls.py
├── supabase/
│   ├── migrations/          # *** Source of truth for schema ***
│   │   └── 20251102000000_initial_schema.sql
│   └── config.toml          # Supabase local configuration
└── docs/                    # Comprehensive documentation
    ├── prd.md               # Product requirements
    ├── database.md          # Schema documentation
    ├── userflow.md          # User journey flows
    └── common-modules.md    # Module architecture guide
```

## Data Models and Database

### Seven Core Tables

1. **users**: Authentication and roles
2. **upload_history**: File upload tracking
3. **department_kpi**: Department performance metrics
4. **publications**: Research paper publications
5. **research_projects**: Research project master data
6. **execution_records**: Detailed research budget spending
7. **students**: Student enrollment data

### Three Aggregate Views

- `v_project_execution_rate`: Research project execution rates
- `v_department_student_stats`: Student statistics by department
- `v_publication_stats`: Publication statistics

**Schema reference**: `supabase/migrations/20251102000000_initial_schema.sql`

**Documentation**: `docs/database.md` has complete table definitions, indexes, and query patterns

## Data Processing Pipeline

### Excel/CSV Upload Flow

1. **Upload** → Django Admin file field
2. **Parse** → `apps/data_upload/parsers.py` (Pandas-based)
3. **Validate** → `apps/data_upload/validators.py` (schema + business rules)
4. **Transform** → Data cleaning, type conversion, duplicate handling
5. **Load** → Bulk insert via `Model.objects.bulk_create()`
6. **Log** → UploadHistory record with success/failure details

### Data Type Mapping

Each upload type has dedicated parser:

- `DepartmentKPIParser`: Maps to `department_kpi` table
- `PublicationParser`: Maps to `publications` table
- `ResearchBudgetParser`: Splits into `research_projects` + `execution_records`
- `StudentParser`: Maps to `students` table

CSV column names are in Korean; parsers map them to English database columns.

## Visualization Architecture

### Chart.js Integration

All charts use Chart.js (via CDN in base.html). Common flow:

1. **Backend**: Django view queries database
2. **Aggregate**: `apps/analytics/aggregators.py` calculates stats
3. **Serialize**: `apps/analytics/serializers.py` formats for Chart.js
4. **Template**: Passes JSON data to template context
5. **Frontend**: JavaScript renders chart with `new Chart(ctx, config)`

### Standard Chart Types

- **Bar charts**: Department comparisons, student distribution
- **Line charts**: Year-over-year trends, enrollment history
- **Pie charts**: Budget allocation, journal grade distribution
- **Dual-axis**: Budget vs execution rate

Default colors and options defined in `static/js/chart-config.js`.

## User Workflows

### Role-Based Data Access

```python
# In views.py
from apps.authentication.permissions import get_accessible_departments

def analytics_view(request):
    # Automatically filters based on user role
    departments = get_accessible_departments(request.user)
    data = Model.objects.filter(department__in=departments)
```

Admin/Manager see all departments; Viewers see only their own.

### Critical User States

- **pending**: Registered, awaiting admin approval (cannot login to dashboard)
- **active**: Approved, can access dashboard
- **inactive**: Rejected or suspended (blocked from login)

State transitions only via Django Admin user management by admins.

## Development Workflow Patterns

### Adding a New Visualization Page

1. **Create view** in `apps/analytics/views.py`:
   ```python
   @login_required
   def new_analytics(request):
       # Query data with user permissions
       departments = get_accessible_departments(request.user)
       data = Model.objects.filter(department__in=departments)

       # Aggregate
       stats = YourAggregator().get_summary_stats(data)
       chart_data = to_bar_chart_data(data, 'label_field', 'value_field')

       return render(request, 'analytics/new_page.html', {
           'stats': stats,
           'chart_data': chart_data
       })
   ```

2. **Create template** inheriting from `base_dashboard.html`
3. **Include Chart.js** rendering in template
4. **Add route** to `config/urls.py`
5. **Add menu item** to `templates/components/sidebar.html`

### Adding a New Data Type Upload

1. **Add migration** to `supabase/migrations/` with new table
2. **Apply migration**: `supabase db reset`
3. **Create model** in `apps/analytics/models.py` with `managed = False`
4. **Create parser** in `apps/data_upload/parsers.py`
5. **Create validator** in `apps/data_upload/validators.py`
6. **Register in admin** at `apps/data_upload/admin.py`
7. **Add to constants** in `apps/core/constants.py`

## Testing Strategy

Focus testing on:

1. **Validators**: Data validation logic (required columns, data types, ranges)
2. **Parsers**: Excel/CSV parsing accuracy
3. **Aggregators**: Statistical calculations
4. **Permissions**: Role-based access control

Example:
```python
# apps/data_upload/tests.py
class DepartmentKPIParserTest(TestCase):
    def test_valid_file_parsing(self):
        # Test with sample Excel file
        parser = DepartmentKPIParser()
        result = parser.parse(sample_file)
        self.assertTrue(result.success)
```

## Phase 2 Roadmap (Not for MVP)

These are **explicitly out of scope** for current MVP:

- ❌ Custom file upload UI (currently uses Django Admin)
- ❌ JWT authentication (currently Django sessions)
- ❌ REST API layer (currently Django template rendering)
- ❌ React frontend (currently Django templates)
- ❌ Advanced analytics (AI insights, predictions)

If asked to implement these: refer to docs/requirements.md which states "2단계 로드맵".

## Common Gotchas

1. **Don't run `python manage.py makemigrations` for data models** — schema changes go in Supabase migrations
2. **Don't modify `managed = False` models** — this breaks Supabase sync
3. **Chart.js must load before custom chart JS** — verify CDN in base.html
4. **Django Admin is the ONLY upload interface** — don't build custom upload pages
5. **All dates in database are DATE/TIMESTAMP** — don't use strings for date fields
6. **Korean column names in CSV** — parsers handle mapping to English

## Getting Help

- **Project requirements**: `docs/requirements.md`
- **Full PRD**: `docs/prd.md` (all features, user journeys, success metrics)
- **Database schema**: `docs/database.md` (all tables, indexes, query examples)
- **User workflows**: `docs/userflow.md` (detailed user journeys with edge cases)
- **Architecture guide**: `docs/common-modules.md` (complete module design)
- **Tech stack rationale**: `docs/technical_suggestion.md`

## Quick Reference

| Task | Command/Path |
|------|-------------|
| Start local DB | `supabase start` |
| View DB in browser | http://127.0.0.1:54323 |
| Reset DB schema | `supabase db reset` |
| Start Django | `python manage.py runserver` |
| Access admin panel | http://127.0.0.1:8000/admin |
| Upload data files | Django Admin > respective model |
| Run tests | `python manage.py test` |
| Create superuser | `python manage.py createsuperuser` |
