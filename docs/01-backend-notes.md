# Employee Directory: Backend Notes (Django + DRF + SQLite)

> Notes for a MERN developer learning Django. They cover everything built so far:
> setup, project structure, models, migrations, admin, the ORM and the REST API.
> Each section shows **what** we wrote, **why**, and **what it maps to in MERN**.

---

## Table of Contents

1. [The Big Picture](#1-the-big-picture)
2. [Environment Setup (venv + pip)](#2-environment-setup-venv--pip)
3. [Creating the Project and App](#3-creating-the-project-and-app)
4. [Folder Structure Explained](#4-folder-structure-explained)
5. [settings.py: Configuration](#5-settingspy-configuration)
6. [models.py: Database Tables](#6-modelspy-database-tables)
7. [Migrations: Changing the Database](#7-migrations-changing-the-database)
8. [admin.py: Free Admin Panel](#8-adminpy-free-admin-panel)
9. [The ORM: Querying with Python](#9-the-orm-querying-with-python)
10. [serializers.py: Validation + JSON](#10-serializerspy-validation--json)
11. [views.py: API Controllers](#11-viewspy-api-controllers)
12. [urls.py: Routing](#12-urlspy-routing)
13. [The Complete Request Flow](#13-the-complete-request-flow)
14. [API Endpoints Reference](#14-api-endpoints-reference)
15. [Python Syntax Used in This Project](#15-python-syntax-used-in-this-project)
16. [Common Errors and Fixes](#16-common-errors-and-fixes)
17. [Daily Commands Cheat Sheet](#17-daily-commands-cheat-sheet)
18. [Quiz Review (Q&A)](#18-quiz-review-qa)

---

## 1. The Big Picture

### What we're building
An **Employee Directory** (a mini HRMS):
- **Departments** (Engineering, HR, Sales)
- **Employees**, each belonging to one department
- **Leave Requests**, each belonging to one employee, with an approve/reject workflow

### Architecture
```
┌──────────────────┐        HTTP / JSON         ┌──────────────────────────┐
│  React (Vite)    │  ───────────────────────►  │  Django + DRF            │
│  frontend/       │  ◄───────────────────────  │  backend/                │
│  localhost:5173  │                            │  127.0.0.1:8000          │
└──────────────────┘                            └────────────┬─────────────┘
                                                             │ ORM
                                                      ┌──────▼──────┐
                                                      │ db.sqlite3  │
                                                      │ (one file)  │
                                                      └─────────────┘
```
Backend and frontend are **two separate apps** that only talk over HTTP, the same as Express + React.

### MERN → Django translation table

| MERN | Django world | Notes |
|---|---|---|
| Node.js | Python | The language/runtime |
| `npm` | `pip` | Package manager |
| `package.json` (deps) | `requirements.txt` | Must be regenerated manually with `pip freeze` |
| `node_modules/` | `venv/` | Per-project packages. Must be **activated**. |
| Express | Django | The web framework |
| `server.js` / `app.js` | `config/` (settings + urls) | Project-level setup |
| Feature folder (routes + controller + model) | A Django **app** (`employees/`) | One folder per feature |
| `app.use(middleware)` | `MIDDLEWARE` list in settings | Runs in order on every request |
| `express.Router()` | `urls.py` + DRF `DefaultRouter` | |
| Controller functions | **Views** / **ViewSets** | |
| Mongoose schema/model | **Model** (`models.py`) | |
| Joi / manual validation + `res.json()` | **Serializer** | One class does both |
| MongoDB | SQLite | SQL, relational, single file |
| `ref: 'Department'` + `.populate()` | `ForeignKey` + `select_related()` | Enforced by the database |
| *(no equivalent)* | **Migrations** | Versioned schema changes |
| Build your own admin UI | **Django Admin** | Free, ~25 lines |
| `nodemon server.js` | `python manage.py runserver` | Auto-reloads on save |
| `cors` package | `django-cors-headers` | |

---

## 2. Environment Setup (venv + pip)

Run from: `D:\Projects\employee-directory\backend`

### 2.1 Create a virtual environment
```bash
python -m venv venv
```
- `python -m venv` runs Python's built-in **venv** module (`-m` = "run a module").
- The last `venv` is the **folder name** to create.
- **Why:** by default `pip install` installs globally for your whole machine. A venv is a private,
  per-project Python plus packages folder. Node does this automatically with `node_modules`, but Python doesn't.

### 2.2 Activate it (once per terminal window)
```bash
.\venv\Scripts\Activate.ps1
```
- Your prompt changes to `(venv) PS ...>`
- Now `python` and `pip` point to the venv's copies.
- **If PowerShell blocks it** ("running scripts is disabled"), run this once:
  ```bash
  Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
  ```
- To leave the venv: `deactivate`

> ⚠️ **Rule:** no `(venv)` in your prompt = Django is invisible = "No module named django".

### 2.3 Install packages
```bash
pip install django djangorestframework django-cors-headers
```
| Package | What it is | MERN equivalent |
|---|---|---|
| `django` | Web framework + ORM + admin | Express + Mongoose + an admin panel |
| `djangorestframework` (DRF) | Toolkit for building JSON APIs | The JSON/REST part of Express |
| `django-cors-headers` | Lets the browser call the API from another port | `cors` npm package |

### 2.4 Save the dependency list
```bash
pip freeze > requirements.txt
```
- `pip freeze` lists all installed packages with exact versions. `>` writes that list to a file.
- **Unlike npm, this is NOT automatic.** Re-run it after every `pip install`.
- Someone cloning the project runs:
  ```bash
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  pip install -r requirements.txt
  ```

Our `requirements.txt`:
```
asgiref==3.13.0
Django==6.1.2
django-cors-headers==4.9.0
djangorestframework==3.18.3
sqlparse==0.6.0
tzdata==2026.5
```
(`asgiref`, `sqlparse` and `tzdata` are Django's own dependencies and were installed automatically.)

### 2.5 VS Code tip
`Ctrl+Shift+P` → **Python: Select Interpreter** → choose the one inside `backend\venv`.
This fixes red squiggles under `import django`.

### 2.6 .gitignore (project root)
```gitignore
# Python
venv/
__pycache__/
*.pyc
db.sqlite3

# Node
node_modules/
```
- `venv/`: like `node_modules`, never commit it
- `__pycache__/`, `*.pyc`: Python's auto-generated compiled files
- `db.sqlite3`: your local data (a fresh clone runs `migrate` to create its own)

> ⚠️ `.gitignore` comments must be on their **own line** starting with `#`.
> `venv/   # comment` on one line does NOT work: git treats the whole line as the pattern.

---

## 3. Creating the Project and App

### 3.1 Create the project (ONE TIME ONLY)
```bash
django-admin startproject config .
```
- `django-admin` is Django's global CLI.
- `config` is the name of the settings package.
- `.` means "create it **here**". Without it you'd get a nested `config/config/` folder.

> ⚠️ **Never run `startproject` again.** After this, always use `python manage.py ...`.

### 3.2 Create an app
```bash
python manage.py startapp employees
```
- **Project** = the whole website (settings, main routes).
- **App** = one feature module (its own models, views, URLs).
- A big HR system might have apps like `employees`, `payroll` and `attendance`. We need only one.

> ⚠️ A new app does nothing until it's added to `INSTALLED_APPS` (see §5).

### `django-admin` vs `python manage.py`
| | `django-admin` | `python manage.py` |
|---|---|---|
| Knows your project's settings? | ❌ No | ✅ Yes (points Django at `config.settings`) |
| When to use | `startproject` only, once | **Everything else** |

---

## 4. Folder Structure Explained

```
employee-directory/
├── .gitignore
├── docs/
│   └── 01-backend-notes.md     ← this file
├── frontend/                   ← React + Vite (next chunk)
└── backend/
    ├── venv/                   ← packages (never commit)
    ├── manage.py               ← project CLI: runserver, migrate, shell...
    ├── requirements.txt        ← dependency list
    ├── db.sqlite3              ← THE DATABASE (a single file)
    │
    ├── config/                 ← PROJECT level
    │   ├── __init__.py         ← empty file marking this folder as an importable "package"
    │   ├── settings.py         ← ALL configuration
    │   ├── urls.py             ← main router: /admin/ and /api/
    │   ├── asgi.py             ← production server entry point (async). Ignore for now.
    │   └── wsgi.py             ← production server entry point (sync). Ignore for now.
    │
    └── employees/              ← APP level (our feature)
        ├── __init__.py
        ├── models.py           ← database tables          (Mongoose schemas)
        ├── serializers.py      ← validation + JSON         (Joi + res.json)       [we created]
        ├── views.py            ← request handlers          (controllers)
        ├── urls.py             ← app routes                (express.Router)       [we created]
        ├── admin.py            ← admin panel registration
        ├── apps.py             ← app config (rarely touched)
        ├── tests.py            ← tests
        └── migrations/         ← DB schema history (auto-generated, DO commit)
            ├── __init__.py
            └── 0001_initial.py
```

---

## 5. settings.py: Configuration

File: `backend/config/settings.py`. Think of it as `.env` plus all your `app.use()` setup in one place.

### 5.1 INSTALLED_APPS: what Django loads
```python
INSTALLED_APPS = [
    'django.contrib.admin',         # admin panel
    'django.contrib.auth',          # users, groups, permissions
    'django.contrib.contenttypes',  # internal: tracks model types
    'django.contrib.sessions',      # login sessions
    'django.contrib.messages',      # flash messages
    'django.contrib.staticfiles',   # CSS/JS for the admin
    # Third-party
    'rest_framework',               # DRF
    'corsheaders',                  # CORS
    # Our apps
    'employees',
]
```
> 🔑 **Django completely ignores apps not listed here.** Their models won't migrate and their
> admin won't show. This is the #1 beginner bug.

### 5.2 MIDDLEWARE: runs on every request, top to bottom
```python
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',   # ← we added this, FIRST
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```
- Same idea as `app.use(cors())`, `app.use(express.json())` and so on.
- CORS goes near the top so it can add headers before anything else responds.

### 5.3 CORS: who may call the API from a browser
```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',   # Vite (React) dev server
]
```
Same as `app.use(cors({ origin: 'http://localhost:5173' }))`.

### 5.4 DATABASES: SQLite (default, we didn't change it)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```
- No connection string, no `mongoose.connect()`, no database server to start.
- SQLite is just a file. Django reads and writes it directly.
- `BASE_DIR / 'db.sqlite3'` means "the `backend` folder + `db.sqlite3`" (`/` joins paths here).
- Switching to PostgreSQL later means changing only this block. Models and queries stay the same.

### 5.5 Other important settings
| Setting | Meaning |
|---|---|
| `DEBUG = True` | Detailed error pages. **Must be `False` in production** (otherwise it leaks routes and settings). |
| `SECRET_KEY` | Used for signing sessions and tokens. Keep it secret in production. |
| `ALLOWED_HOSTS = []` | Which domains may serve the app. Empty is fine with DEBUG on. |
| `TIME_ZONE = 'UTC'` / `USE_TZ = True` | Datetimes are stored in UTC |

---

## 6. models.py: Database Tables

File: `backend/employees/models.py`

### 6.1 Relationships (the key mental shift from MongoDB)
```
Department 1 ────< many  Employee  1 ────< many  LeaveRequest
```
- In MongoDB you might **embed** leave requests inside an employee document.
- In SQL, **each entity is its own table**, linked by **foreign keys**: a column holding the `id`
  of a row in another table. The **database enforces** that the linked row exists.

### 6.2 The full code
```python
from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Employee(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    job_title = models.CharField(max_length=100)
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name='employees',
    )
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    date_joined = models.DateField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class LeaveRequest(models.Model):
    class LeaveType(models.TextChoices):
        SICK = 'SICK', 'Sick Leave'
        CASUAL = 'CASUAL', 'Casual Leave'
        ANNUAL = 'ANNUAL', 'Annual Leave'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='leave_requests',
    )
    leave_type = models.CharField(max_length=10, choices=LeaveType.choices)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField(blank=True)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee} - {self.leave_type} ({self.status})"
```

### 6.3 Line-by-line concepts

**`class Department(models.Model):`**
- Inheriting from `models.Model` turns this class into a database table.
- Table name: `<app>_<model>` → `employees_department`.
- It inherits `.save()`, `.delete()` and `.objects` (the query manager) for free.

**No `id` field?**
Django adds `id` automatically: an auto-incrementing integer primary key (1, 2, 3...). Like Mongo's `_id`, but a number.

**`def __str__(self):`**
How the object displays as text in the admin, the shell and dropdowns. Like overriding `toString()`.
Without it you'd see `Employee object (1)` instead of `Asha Rao`.

**`class Meta:`**
A nested class for **table-level options** (not columns).
- `ordering = ['name']` → default sort A→Z
- `ordering = ['-created_at']` → the `-` means **descending** (newest first)

### 6.4 Field types → Mongoose

| Django field | Mongoose equivalent | Notes |
|---|---|---|
| `CharField(max_length=100)` | `{ type: String, maxlength: 100 }` | `max_length` is **required** |
| `TextField()` | `String` | Long text, no limit |
| `EmailField()` | `String` + email regex | Validates the format |
| `DecimalField(max_digits=10, decimal_places=2)` | (none built in) | **Exact** money values. Up to 99,999,999.99 |
| `DateField()` | `Date` | Date only (`2026-11-03`) |
| `DateTimeField()` | `Date` | Date + time |
| `BooleanField(default=True)` | `{ type: Boolean, default: true }` | |
| `ForeignKey(Model, ...)` | `{ type: ObjectId, ref: 'Model' }` | Enforced by the database |

> 💡 Why `DecimalField` for salary? Floats can't represent money exactly
> (`85000 * 1.1 = 93500.00000000001`). Decimals can.

### 6.5 Field options

| Option | Meaning | Gotcha |
|---|---|---|
| `unique=True` | No two rows can share this value (enforced by the database) | |
| `blank=True` | Field is **optional** in validation and forms | **Fields are REQUIRED by default**, the opposite of Mongoose |
| `null=True` | The database column can store NULL | Mostly for non-text fields. For text, use `blank=True` (empty string). |
| `default=...` | Value used when none is given | |
| `auto_now_add=True` | Set automatically on **create** | Like `timestamps: true` (createdAt) |
| `auto_now=True` | Set automatically on **every save** | Like updatedAt (we didn't use it) |
| `choices=...` | Restrict to a fixed list of values | Renders as a dropdown |

### 6.6 ForeignKey in depth
```python
department = models.ForeignKey(
    Department,                 # which table it points to
    on_delete=models.PROTECT,   # what happens when that department is deleted
    related_name='employees',   # name of the reverse lookup
)
```
- In the database this column is called `department_id` and stores an integer.
- In Python, `employee.department` gives you the full `Department` object.
- `employee.department_id` gives you just the number.

**`on_delete` options:** SQL forces you to decide what happens to the "children".

| Option | When the parent is deleted... | We used it for |
|---|---|---|
| `PROTECT` | ❌ Refuse. Raises `ProtectedError` | Employee → Department (can't delete a department that has staff) |
| `CASCADE` | 🗑️ Delete the children too | LeaveRequest → Employee (an employee's leaves go with them) |
| `SET_NULL` | Set the FK to NULL (needs `null=True`) | |
| `SET_DEFAULT` | Set the FK to its default | |

**`related_name`: the reverse direction**
The FK lives on `Employee`, but `related_name='employees'` lets you go from department to employees:
```python
asha.department          # forward:  Employee → Department
eng.employees.all()      # reverse:  Department → all its Employees
asha.leave_requests.all()  # reverse: Employee → all their LeaveRequests
```
In Mongoose you'd need a second query or a virtual populate.

### 6.7 TextChoices (enums)
```python
class Status(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    #  ↑ name     ↑ stored in DB   ↑ human label (shown in admin/forms)
```
- The database stores `'PENDING'`, and the UI shows `Pending`.
- In code, use `LeaveRequest.Status.APPROVED` instead of the raw string `'APPROVED'` (catches typos).
- `choices=Status.choices` → Django rejects any value not in the list.
- Like a Mongoose `enum: ['PENDING', 'APPROVED', 'REJECTED']`, with labels added.

---

## 7. Migrations: Changing the Database

MongoDB has no fixed schema, so it never needed migrations. **SQL tables have a fixed structure**,
so every model change needs a migration.

### 7.1 The workflow (memorize this)
```
1. Edit models.py
        ↓
2. python manage.py makemigrations   → WRITES a migration file (a plan). Database untouched.
        ↓
3. python manage.py migrate          → APPLIES the plan to db.sqlite3
```

### 7.2 Commands
```bash
python manage.py makemigrations          # generate migration files from model changes
python manage.py migrate                 # apply pending migrations
python manage.py showmigrations          # list migrations, [X] = applied
python manage.py sqlmigrate employees 0001   # show the actual SQL for a migration
```

### 7.3 What happened in our project
- **First `migrate`** (before we had any models) created tables for Django's built-in apps:
  `auth_user`, `auth_group`, `django_session`, `django_admin_log`, and so on.
  These apps ship with their own models and migrations.
- **`makemigrations`** after writing our models created `employees/migrations/0001_initial.py`:
  ```
  + Create model Department
  + Create model Employee
  + Create model LeaveRequest
  ```
- **`migrate`** created `employees_department`, `employees_employee` and `employees_leaverequest`.

### 7.4 Rules
- ✅ **Commit migration files to git.** They're how every developer and server ends up with the same schema.
- ❌ Don't edit applied migrations by hand.
- 🐛 "**no such column**" / "**no such table**" error → you forgot `makemigrations` + `migrate`.

---

## 8. admin.py: Free Admin Panel

File: `backend/employees/admin.py`
```python
from django.contrib import admin

from .models import Department, Employee, LeaveRequest


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'department', 'job_title', 'is_active']
    list_filter = ['department', 'is_active']
    search_fields = ['first_name', 'last_name', 'email']


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ['employee', 'leave_type', 'start_date', 'end_date', 'status']
    list_filter = ['status', 'leave_type']
```

| Piece | Meaning |
|---|---|
| `from .models import ...` | `.` = same folder. Like `require('./models')` |
| `@admin.register(Department)` | **Decorator**: "show this model in the admin, with these settings" |
| `admin.ModelAdmin` | Base class with all the admin behaviour |
| `list_display` | Columns in the list view |
| `list_filter` | Filter sidebar |
| `search_fields` | Search box. Searches these columns. |

**Create a login:**
```bash
python manage.py createsuperuser
```
(The password is invisible while you type. That's normal.)

**Open:** http://127.0.0.1:8000/admin/

What you get for free: list, create, edit, delete, search, filter, dropdowns for ForeignKeys and
choices, validation, and a history log. In MERN this would take days to build.

---

## 9. The ORM: Querying with Python

Open an interactive shell connected to the database:
```bash
python manage.py shell
```
(Django 6 auto-imports your models. Type `exit()` to quit.)

### 9.1 `Model.objects`: the manager
Every query starts from `Model.objects`, like calling static methods on a Mongoose model.

### 9.2 CREATE
```python
from datetime import date

eng = Department.objects.create(name="Engineering", description="Builds the product")

Employee.objects.create(
    first_name="Asha", last_name="Rao", email="asha@co.com",
    job_title="Backend Developer", department=eng,      # ← pass the OBJECT
    salary=85000, date_joined=date(2023, 3, 1),
)
```

### 9.3 READ
```python
Employee.objects.all()                       # everything
Employee.objects.get(email="asha@co.com")    # exactly ONE (or crash)
Employee.objects.filter(department=eng)      # list (possibly empty)
Employee.objects.exclude(is_active=False)    # NOT matching
Employee.objects.order_by("-salary")         # sort desc
Employee.objects.filter(department=eng).count()
Employee.objects.values("first_name", "salary")   # plain dicts, selected fields
```

**`.get()` vs `.filter()`**

| | `.get()` | `.filter()` |
|---|---|---|
| Returns | One object | A QuerySet (list-like) |
| 0 matches | 💥 `DoesNotExist` | Empty QuerySet |
| 2+ matches | 💥 `MultipleObjectsReturned` | All of them |

### 9.4 Field lookups: the double underscore `__`
Pattern: `field__lookup=value`
```python
filter(salary__gte=80000)           # >=      Mongo: { salary: { $gte: 80000 } }
filter(salary__lt=60000)            # <
filter(first_name__icontains="ri")  # contains, case-insensitive   Mongo: /ri/i
filter(first_name__startswith="A")
filter(id__in=[1, 2, 3])            # Mongo: { $in: [...] }
filter(date_joined__year__lt=2024)  # lookups can chain
filter(phone="")                    # exact match (default)
```

### 9.5 Following relationships (automatic JOINs)
```python
# Employees whose department's name is Engineering  → SQL INNER JOIN
Employee.objects.filter(department__name="Engineering")

# Through TWO relationships: leave → employee → department
LeaveRequest.objects.filter(status="PENDING", employee__department__name="Engineering")

asha.department.name       # forward
eng.employees.all()        # reverse (related_name)
asha.leave_requests.all()  # reverse
```

### 9.6 UPDATE
```python
# One object
asha.salary = 90000
asha.save()                 # ← without .save(), NOTHING is written

# Bulk, one SQL query (like updateMany)
Employee.objects.filter(department=eng).update(is_active=True)   # returns the row count
```

### 9.7 DELETE
```python
obj.delete()
Employee.objects.filter(is_active=False).delete()
hr.delete()   # 💥 ProtectedError if HR has employees (on_delete=PROTECT)
```

### 9.8 Aggregation (the SQL version of `$group`)
```python
from django.db.models import Count, Avg

# annotate = add a calculated field to EACH row
Department.objects.annotate(
    headcount=Count("employees"),
    avg_salary=Avg("employees__salary"),
).values("name", "headcount", "avg_salary")

# aggregate = ONE result for the whole table
Employee.objects.aggregate(total=Sum("salary"))   # (import Sum)
```

### 9.9 See the SQL
```python
print(Employee.objects.filter(department__name="Engineering").query)
```

### 9.10 Cheat sheet

| Mongoose | Django ORM |
|---|---|
| `Model.create({...})` | `Model.objects.create(...)` |
| `Model.find({})` | `Model.objects.all()` |
| `Model.find({ a: 1 })` | `Model.objects.filter(a=1)` |
| `Model.findOne({ a: 1 })` | `Model.objects.get(a=1)` |
| `Model.findById(id)` | `Model.objects.get(pk=id)` |
| `{ age: { $gte: 18 } }` | `filter(age__gte=18)` |
| `{ name: { $ne: "x" } }` | `exclude(name="x")` |
| `.sort({ age: -1 })` | `.order_by("-age")` |
| `.limit(10)` | `[:10]` |
| `.countDocuments()` | `.count()` |
| `.select('a b')` | `.values('a', 'b')` |
| `.populate('dept')` | `.select_related('department')` |
| `doc.x = 1; await doc.save()` | `obj.x = 1; obj.save()` |
| `updateMany(filter, update)` | `.filter(...).update(...)` |
| `deleteOne()` | `obj.delete()` |
| `aggregate([{ $group }])` | `.annotate()` / `.aggregate()` |

---

## 10. serializers.py: Validation + JSON

File: `backend/employees/serializers.py` (we created this file)

### 10.1 What a serializer does
```
OUTGOING:  Model object ──serializer──► Python dict ──► JSON response
INCOMING:  JSON request ──serializer──► validate ──► .save() ──► Model object
```
In Express you'd write Joi validation **and** `res.json(doc)` separately. A serializer does both.

### 10.2 The code
```python
from rest_framework import serializers

from .models import Department, Employee, LeaveRequest


class DepartmentSerializer(serializers.ModelSerializer):
    employee_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'employee_count', 'created_at']


class EmployeeSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = Employee
        fields = [
            'id', 'first_name', 'last_name', 'email', 'phone', 'job_title',
            'department', 'department_name', 'salary', 'date_joined', 'is_active',
        ]


class LeaveRequestSerializer(serializers.ModelSerializer):
    employee_name = serializers.StringRelatedField(source='employee', read_only=True)

    class Meta:
        model = LeaveRequest
        fields = [
            'id', 'employee', 'employee_name', 'leave_type', 'start_date',
            'end_date', 'reason', 'status', 'created_at',
        ]
        read_only_fields = ['status']

    def validate(self, data):
        start = data.get('start_date', getattr(self.instance, 'start_date', None))
        end = data.get('end_date', getattr(self.instance, 'end_date', None))
        if start and end and end < start:
            raise serializers.ValidationError({'end_date': 'End date cannot be before start date.'})
        return data
```

### 10.3 Concepts

**`ModelSerializer`** reads the model and auto-generates fields **and validation rules**:
- `max_length`, `unique=True`, `EmailField` format, `choices`, required vs `blank=True`
- You never repeat these rules. The model is the single source of truth.

**`class Meta: fields = [...]`** is a **whitelist**.
- Only these fields are read or written through the API.
- Security benefit: a new sensitive model field stays hidden until you add it here.

**Extra read-only fields (output only):**

| Field | Output | Why |
|---|---|---|
| `department` (auto) | `1` | React **sends** this ID when creating or updating |
| `department_name = CharField(source='department.name', read_only=True)` | `"Engineering"` | React **displays** this without a second request |
| `employee_name = StringRelatedField(source='employee', read_only=True)` | `"Asha Rao"` | Uses the model's `__str__` |
| `employee_count = IntegerField(read_only=True)` | `3` | Not a model field. Computed by `annotate()` in the view. |

`source='department.name'` means "follow the FK and read `.name`", a lightweight `.populate()`.

**`read_only_fields = ['status']`**
- Clients **cannot** set the status on create or update. It's silently ignored.
- A new leave is always `PENDING` (the model default).
- The status changes **only** via the `/approve/` and `/reject/` endpoints, so the business rule is enforced by the API.

**`def validate(self, data)`**: custom cross-field validation
- Runs **after** the field-level checks pass.
- `data` = the incoming, already-cleaned values (a dict).
- `self.instance` = the existing object when updating, `None` when creating.
- `getattr(obj, 'attr', default)` = `obj?.attr ?? default` in JavaScript.
- **Why the fallback?** A PATCH might send only `{"reason": "Flu"}` with no dates, so we compare
  against the dates already saved.
- `raise ValidationError({...})` → DRF returns **400**:
  `{"end_date": ["End date cannot be before start date."]}`
- **Must `return data`** at the end.

**Validation levels in DRF:**

| Level | How | Example |
|---|---|---|
| Model-derived | Automatic | `email` already exists, `max_length` exceeded |
| Single field | `def validate_<field>(self, value):` | `validate_salary`: must be > 0 |
| Cross-field | `def validate(self, data):` | end_date ≥ start_date |

---

## 11. views.py: API Controllers

File: `backend/employees/views.py`
```python
from django.db.models import Count, ProtectedError
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Department, Employee, LeaveRequest
from .serializers import DepartmentSerializer, EmployeeSerializer, LeaveRequestSerializer


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.annotate(employee_count=Count('employees'))
    serializer_class = DepartmentSerializer

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {'detail': 'Cannot delete a department that still has employees.'},
                status=status.HTTP_400_BAD_REQUEST,
            )


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.select_related('department')
    serializer_class = EmployeeSerializer


class LeaveRequestViewSet(viewsets.ModelViewSet):
    queryset = LeaveRequest.objects.select_related('employee')
    serializer_class = LeaveRequestSerializer

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        leave = self.get_object()
        leave.status = LeaveRequest.Status.APPROVED
        leave.save()
        return Response(self.get_serializer(leave).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        leave = self.get_object()
        leave.status = LeaveRequest.Status.REJECTED
        leave.save()
        return Response(self.get_serializer(leave).data)
```
> Note: your file also has `from django.shortcuts import render` at the top (from the template).
> It's unused and safe to delete.

### 11.1 `ModelViewSet`: full CRUD in two lines
Set `queryset` (which rows) and `serializer_class` (how to convert them), and you get:

| HTTP | URL | ViewSet method | Express equivalent you'd write by hand |
|---|---|---|---|
| GET | `/employees/` | `list` | `Employee.find()` |
| POST | `/employees/` | `create` | validate + `Employee.create()` → 201 |
| GET | `/employees/1/` | `retrieve` | `findById()` + 404 check |
| PUT | `/employees/1/` | `update` | validate all fields + update |
| PATCH | `/employees/1/` | `partial_update` | validate sent fields + update |
| DELETE | `/employees/1/` | `destroy` | `findByIdAndDelete()` → 204 |

Each built-in method can be **overridden**, as we did with `destroy`.

### 11.2 `select_related()` and the N+1 problem
`EmployeeSerializer` reads `department.name` for every employee.
- ❌ **Without** `select_related`: 1 query for the employees + 1 query **per employee** for their department
  → 100 employees = **101 queries**
- ✅ **With** `select_related('department')`: one SQL `JOIN` → **1 query**

> 🔑 **Rule:** if a serializer reads through a ForeignKey, add `select_related` for it.
> The API works without it, just slower. That's why it's easy to miss.

(For reverse or many-to-many relations, the equivalent is `prefetch_related`.)

### 11.3 `annotate()` in the queryset
`Count('employees')` adds `employee_count` to every department. The serializer's
`employee_count = IntegerField(read_only=True)` then outputs it.

### 11.4 Overriding `destroy` for a friendly error
- Without it: deleting a department that has employees → `ProtectedError` → **500 Server Error**
- With it: a clean **400** + a message React can display
- `super().destroy(...)` = "run the parent's normal delete logic" (like `super.method()` in JS)
- `try / except` = `try / catch`
- `*args, **kwargs` = accept and pass along any extra positional and keyword arguments (like `...args`)
- `status.HTTP_400_BAD_REQUEST` is a readable constant for `400`

### 11.5 `@action`: custom endpoints beyond CRUD
```python
@action(detail=True, methods=['post'])
def approve(self, request, pk=None):
```
- `detail=True` → acts on **one** record → URL `/leave-requests/<pk>/approve/`
  (`detail=False` would give `/leave-requests/approve/` for collection-level actions)
- `methods=['post']` → only POST is allowed
- `self.get_object()` → fetch by `pk`, automatic **404** if not found
- `self.get_serializer(leave).data` → convert to a dict → `Response(...)` sends JSON
- The REST-friendly way to model **workflow actions** (approve, reject, archive...)

---

## 12. urls.py: Routing

### 12.1 App router: `backend/employees/urls.py` (we created this)
```python
from rest_framework.routers import DefaultRouter

from .views import DepartmentViewSet, EmployeeViewSet, LeaveRequestViewSet

router = DefaultRouter()
router.register('departments', DepartmentViewSet)
router.register('employees', EmployeeViewSet)
router.register('leave-requests', LeaveRequestViewSet)

urlpatterns = router.urls
```
- `DefaultRouter` **generates every URL** for each ViewSet (list, detail and `@action`s).
- `DefaultRouter` also creates the API root page at `/api/` listing all endpoints.
- `urlpatterns` is the variable name Django looks for in every `urls.py` (like `module.exports`).

### 12.2 Main router: `backend/config/urls.py`
```python
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('employees.urls')),
]
```
- `include('employees.urls')` = mount the app's routes under `/api/`
- Same as `app.use('/api', employeeRoutes)`

### 12.3 Why `/` gives a 404
Only `admin/` and `api/` are defined. Visiting `http://127.0.0.1:8000/` matches nothing.
That's expected. (The rocket welcome page only shows while a project has no routes of its own.)

---

## 13. The Complete Request Flow

Example: `POST /api/leave-requests/` with `{"employee": 1, "leave_type": "SICK", "start_date": "2026-11-03", "end_date": "2026-11-04"}`

```
Browser / React
   │  POST /api/leave-requests/
   ▼
MIDDLEWARE (top → bottom)            ← CORS check, security, sessions, auth...
   ▼
config/urls.py                       ← matches 'api/' → include('employees.urls')
   ▼
employees/urls.py (router)           ← matches 'leave-requests/' + POST → LeaveRequestViewSet.create
   ▼
LeaveRequestViewSet.create()         ← (built into ModelViewSet)
   ▼
LeaveRequestSerializer(data=...)
   ├─ field validation               ← employee exists? leave_type in choices? valid dates?
   ├─ validate()                     ← end_date >= start_date?
   │     └─ ❌ fails → 400 {"end_date": [...]}
   └─ ✅ .save()                      ← status ignored (read-only) → default PENDING
   ▼
Model → ORM → INSERT INTO employees_leaverequest ... → db.sqlite3
   ▼
Serializer converts the saved object → dict
   ▼
Response → 201 Created + JSON
```

Express equivalent:
```js
app.use(cors());
app.use('/api', router);
router.post('/leave-requests', async (req, res) => {
  const { error } = schema.validate(req.body);          // serializer: field validation
  if (error) return res.status(400).json(error);
  if (req.body.end_date < req.body.start_date) ...       // serializer: validate()
  const leave = await LeaveRequest.create({ ...req.body, status: 'PENDING' });
  res.status(201).json(leave);                          // serializer: output
});
```

---

## 14. API Endpoints Reference

Base URL: `http://127.0.0.1:8000/api/`

| Method | Endpoint | Purpose | Success |
|---|---|---|---|
| GET | `/api/` | API root (lists resources) | 200 |
| GET | `/api/departments/` | List departments (+ `employee_count`) | 200 |
| POST | `/api/departments/` | Create a department | 201 |
| GET | `/api/departments/<id>/` | Get one | 200 |
| PUT / PATCH | `/api/departments/<id>/` | Full / partial update | 200 |
| DELETE | `/api/departments/<id>/` | Delete (400 if it has employees) | 204 |
| GET | `/api/employees/` | List employees (+ `department_name`) | 200 |
| POST | `/api/employees/` | Create an employee | 201 |
| GET / PUT / PATCH / DELETE | `/api/employees/<id>/` | Get / update / delete one | 200 / 204 |
| GET | `/api/leave-requests/` | List leaves (newest first) | 200 |
| POST | `/api/leave-requests/` | Create a leave (always PENDING) | 201 |
| GET / PUT / PATCH / DELETE | `/api/leave-requests/<id>/` | Get / update / delete one | 200 / 204 |
| POST | `/api/leave-requests/<id>/approve/` | Set status → APPROVED | 200 |
| POST | `/api/leave-requests/<id>/reject/` | Set status → REJECTED | 200 |

### Example JSON

**GET `/api/employees/1/`**
```json
{
  "id": 1,
  "first_name": "Asha",
  "last_name": "Rao",
  "email": "asha@co.com",
  "phone": "",
  "job_title": "Backend Developer",
  "department": 1,
  "department_name": "Engineering",
  "salary": "85000.00",
  "date_joined": "2023-03-01",
  "is_active": true
}
```
> Note: `salary` comes back as a **string** (`"85000.00"`). DRF does this for Decimals to avoid
> float rounding. In React, use `Number(salary)` when you need to do maths with it.

**POST `/api/leave-requests/`** (request body)
```json
{ "employee": 1, "leave_type": "SICK", "start_date": "2026-11-03", "end_date": "2026-11-04", "reason": "Fever" }
```

**Validation error (400)**
```json
{ "end_date": ["End date cannot be before start date."] }
```
```json
{ "email": ["employee with this email already exists."] }
```
DRF errors are always shaped `{ "field_name": ["message", ...] }`. Handy for showing errors under form inputs in React.

### Browsable API
Open any endpoint in a browser to get a clickable UI with forms (POST, PUT, DELETE buttons), like Postman built in.

---

## 15. Python Syntax Used in This Project

| Python | JavaScript | Notes |
|---|---|---|
| `x = 5` | `let x = 5` | No `let`/`const`, no semicolons |
| `True` / `False` / `None` | `true` / `false` / `null` | Capitalized |
| `# comment` | `// comment` | |
| `"""docstring"""` | `/** ... */` | |
| `f"Hi {name}"` | `` `Hi ${name}` `` | f-strings |
| `[1, 2, 3]` | `[1, 2, 3]` | list |
| `{"a": 1}` / `d["a"]` | `{a: 1}` / `o.a` | dict, **brackets only** |
| `len(x)` | `x.length` | |
| Indentation + `:` | `{ }` | Indentation **is** the syntax |
| `if / elif / else` | `if / else if / else` | |
| `and`, `or`, `not` | `&&`, `\|\|`, `!` | |
| `for x in items:` | `for (const x of items)` | |
| `def f(a, b=1):` | `function f(a, b = 1)` | |
| `f(b=2)` | `f({ b: 2 })` | Keyword arguments, used **everywhere** in Django |
| `class A(B):` | `class A extends B` | Inheritance |
| `def __init__(self):` | `constructor()` | |
| `self` | `this` | Must be the first parameter of methods |
| `super().method()` | `super.method()` | |
| `def __str__(self):` | `toString()` | |
| `Obj()` | `new Obj()` | No `new` |
| `from x import y` | `import { y } from 'x'` | |
| `from .models import X` | `require('./models')` | `.` = this folder |
| `@decorator` | (wrapper / HOF) | Modifies the function or class below |
| `try: ... except Err:` | `try {} catch (e) {}` | |
| `raise Error(...)` | `throw new Error(...)` | |
| `*args, **kwargs` | `...args` | Positional / keyword rest params |
| `getattr(o, 'a', d)` | `o?.a ?? d` | |
| `d.get('k', default)` | `d.k ?? default` | Safe dict access |
| `[x*2 for x in xs if x > 1]` | `xs.filter(x => x > 1).map(x => x*2)` | List comprehension |

---

## 16. Common Errors and Fixes

| Error | Cause | Fix |
|---|---|---|
| `can't open file '...\manage.py'` | Wrong folder | `cd D:\Projects\employee-directory\backend` |
| `'.\venv\Scripts\Activate.ps1' is not recognized` | Wrong folder | `cd` into `backend` first |
| `running scripts is disabled on this system` | PowerShell policy | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` (once) |
| `django-admin is not recognized` / `No module named django` | venv not active | `.\venv\Scripts\Activate.ps1` → check `(venv)` |
| `no such column` / `no such table` | Model changed without migrating | `makemigrations` then `migrate` |
| App's models don't show / don't migrate | App not in `INSTALLED_APPS` | Add it in `settings.py` |
| 404 at `http://127.0.0.1:8000/` | No route for `/` | Use `/api/` or `/admin/` |
| `ProtectedError` | Deleting a parent with `PROTECT` children | Delete or reassign the children first (the API returns 400) |
| `DoesNotExist` | `.get()` found nothing | Use `.filter()`, or check that the value exists |
| `MultipleObjectsReturned` | `.get()` found more than one | Use `.filter()` or a unique field |
| Changed a field value but the DB didn't change | Forgot `.save()` | `obj.save()` |
| `IndentationError` | Missing or inconsistent indentation | Use 4 spaces per level |
| Browser CORS error (soon) | Frontend origin not allowed | Check `CORS_ALLOWED_ORIGINS` |

> 🧭 **"Where am I?" checklist:** (1) Is the folder in the prompt correct? (2) Is `(venv)` showing?

> ⚠️ Never re-run `django-admin startproject`. It's a one-time command.

---

## 17. Daily Commands Cheat Sheet

```bash
# Start working (every new terminal)
cd D:\Projects\employee-directory\backend
.\venv\Scripts\Activate.ps1
python manage.py runserver              # http://127.0.0.1:8000  (Ctrl+C to stop)

# After changing models.py
python manage.py makemigrations
python manage.py migrate

# Explore data with Python
python manage.py shell                  # exit() to quit

# Admin user
python manage.py createsuperuser

# Packages
pip install <package>
pip freeze > requirements.txt           # always after installing!
pip install -r requirements.txt         # fresh setup

# Diagnostics
python manage.py check                  # config sanity check
python manage.py showmigrations
python manage.py sqlmigrate employees 0001
```

| URL | What |
|---|---|
| http://127.0.0.1:8000/admin/ | Admin panel |
| http://127.0.0.1:8000/api/ | API root (browsable) |

---

## 18. Quiz Review (Q&A)

**Setup**
- **Q: What two commands give a teammate the same packages?**
  A: `python -m venv venv` (then activate it), then `pip install -r requirements.txt`.
- **Q: A new terminal, no activation, `python -m django --version`. What happens?**
  A: `No module named django`. Django only exists inside the venv.
- **Q: Commit `venv/` and `db.sqlite3`?**
  A: No. `venv/` is like `node_modules` (recreate it from requirements.txt), and `db.sqlite3` is local data.

**Project structure**
- **Q: New app `leaves` and Django ignores it. Why?**
  A: It wasn't added to `INSTALLED_APPS`.
- **Q: `django-admin` vs `python manage.py`?**
  A: `django-admin` is global and doesn't know your settings, so you use it only for `startproject`. `manage.py` knows the project, so you use it for everything else.
- **Q: Why did the first `migrate` create tables before we wrote any models?**
  A: Built-in apps (auth, admin, sessions, contenttypes) ship with their own models and migrations.

**Models & migrations**
- **Q: Added a field and the admin says "no such column". What did you forget?**
  A: `makemigrations`, then `migrate`.
- **Q: `makemigrations` vs `migrate`?**
  A: `makemigrations` **writes** the plan (a migration file). `migrate` **applies** it to the database.
- **Q: Delete an employee. What happens to their leaves? What if it were `PROTECT`?**
  A: `CASCADE` deletes them too. `PROTECT` would block the delete with a `ProtectedError`.
- **Q: All employees in HR, given `dept`?**
  A: `dept.employees.all()` (via `related_name`).

**ORM**
- **Q: All Sales employees earning under 60000?**
  A: `Employee.objects.filter(department__name="Sales", salary__lt=60000)`
- **Q: `.get()` vs `.filter()`?**
  A: `.get()` returns one object and crashes on 0 or 2+ matches. `.filter()` returns a QuerySet and never crashes on the count.
- **Q: `asha.salary = 100000`, then close the shell. Saved?**
  A: No. Only `asha.save()` writes to the database.

**API**
- **Q: The two jobs of a serializer?**
  A: Convert model ⇄ JSON, and validate incoming data.
- **Q: Where did "email already exists" come from?**
  A: `unique=True` on the model. `ModelSerializer` turns it into a validator automatically.
- **Q: Why can't a client create a leave with `"status": "APPROVED"`?**
  A: `status` is in `read_only_fields`, so it's ignored on input and the default `PENDING` is used.
- **Q: Remove `select_related('department')`. Does it still work?**
  A: Yes, but it causes N+1 queries (1 + one per employee), which is slower as the data grows.

---

## What's Next

**Chunk 6: the React frontend**
- Create a Vite + React app in `frontend/`
- Fetch from `http://127.0.0.1:8000/api/...` (CORS is already configured)
- Build: employee list, add-employee form (showing DRF validation errors), leave approval screen
