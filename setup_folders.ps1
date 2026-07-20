$dirs = @(
    "database",
    "uploads/court_receipts",
    "uploads/crime_scenes",
    "uploads/consent_scans",
    "app/services",
    "app/routes",
    "app/static/css",
    "app/static/js",
    "app/static/images",
    "app/templates/components",
    "app/templates/clinical",
    "app/templates/autopsy"
)

foreach ($dir in $dirs) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
}

$files = @(
    "run.py",
    "requirements.txt",
    "README.md",
    "app/__init__.py",
    "app/config.py",
    "app/services/__init__.py",
    "app/services/db.py",
    "app/services/auth_utils.py",
    "app/routes/__init__.py",
    "app/routes/auth.py",
    "app/routes/dashboard.py",
    "app/routes/clinical.py",
    "app/routes/autopsy.py",
    "app/routes/evidence.py",
    "app/routes/court.py",
    "app/static/css/variables.css",
    "app/static/css/layout.css",
    "app/static/css/components.css",
    "app/static/js/app.js",
    "app/static/js/charts.js",
    "app/templates/base.html",
    "app/templates/login.html",
    "app/templates/dashboard.html",
    "app/templates/components/sidebar.html",
    "app/templates/components/navbar.html",
    "app/templates/clinical/list.html",
    "app/templates/clinical/form.html",
    "app/templates/autopsy/list.html",
    "app/templates/autopsy/form.html"
)

foreach ($file in $files) {
    if (-not (Test-Path $file)) {
        New-Item -ItemType File -Path $file | Out-Null
    }
}

if (Test-Path "schema.sql") { Move-Item -Path "schema.sql" -Destination "database/schema.sql" -Force }
if (Test-Path "seed.py") { Move-Item -Path "seed.py" -Destination "database/seed.py" -Force }

Write-Host "Folder structure created successfully."
