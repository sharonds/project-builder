"""
Project Analyzer - Scans existing project and creates architecture profile.

Outputs project_profile.json containing:
- tech_stack (frontend, backend, database, auth)
- architecture (patterns, data isolation, integrations)
- conventions (naming, file structure, state management)
- schemas (extracted from code/models)
- integration_points (how components connect)
- _meta (checksums for incremental updates)
"""
from pathlib import Path
from typing import Optional
import json
import hashlib


# Frontend framework detection patterns
FRONTEND_FRAMEWORKS = {
    "next": "Next.js",
    "react": "React",
    "vue": "Vue",
    "angular": "Angular",
    "svelte": "Svelte",
    "solid-js": "Solid",
}

# Backend framework detection patterns
BACKEND_FRAMEWORKS = {
    "express": "Express.js",
    "fastify": "Fastify",
    "koa": "Koa",
    "hono": "Hono",
    "flask": "Flask",
    "fastapi": "FastAPI",
    "django": "Django",
}

# Database detection patterns
DATABASE_PATTERNS = {
    "firebase": "Firestore",
    "firebase-admin": "Firestore",
    "mongoose": "MongoDB",
    "mongodb": "MongoDB",
    "pg": "PostgreSQL",
    "mysql2": "MySQL",
    "prisma": "Prisma",
    "drizzle-orm": "Drizzle",
}

# Auth detection patterns
AUTH_PATTERNS = {
    "firebase": "Firebase Auth",
    "firebase-admin": "Firebase Auth",
    "@auth0/auth0-react": "Auth0",
    "next-auth": "NextAuth",
    "passport": "Passport.js",
}


def analyze_project(path: str, force: bool = False) -> dict:
    """
    Analyze an existing project and generate a project profile.

    Args:
        path: Path to the project root directory
        force: Force full re-analysis even if no changes detected

    Returns:
        dict: Project profile with tech_stack, architecture, conventions, etc.
    """
    project_path = Path(path)

    if not project_path.exists():
        raise ValueError(f"Project path does not exist: {path}")

    profile_path = project_path / "project_profile.json"
    existing_profile = load_existing_profile(profile_path)

    # Check if update needed
    if not force and existing_profile and not needs_update(project_path, existing_profile):
        # Return existing profile without changes
        return existing_profile

    # Build profile
    profile = {
        "tech_stack": detect_tech_stack(project_path),
        "architecture": detect_architecture_patterns(project_path),
        "conventions": detect_conventions(project_path),
        "schemas": extract_schemas(project_path),
        "integration_points": detect_integration_points(project_path),
        "_meta": {
            "checksums": compute_project_checksums(project_path),
            "incremental": existing_profile is not None
        }
    }

    # Save profile to project root
    save_profile(profile, profile_path)

    return profile


def detect_tech_stack(project_path: Path) -> dict:
    """
    Detect technology stack from config files.

    Reads:
    - package.json for JS/TS dependencies
    - requirements.txt/pyproject.toml for Python
    - firebase.json for Firebase config
    - tsconfig.json for TypeScript config
    """
    tech_stack = {
        "frontend": None,
        "backend": None,
        "database": None,
        "auth": None,
    }

    # Check package.json for JS/TS projects
    package_json = project_path / "package.json"
    if package_json.exists():
        with open(package_json) as f:
            pkg = json.load(f)

        all_deps = {}
        all_deps.update(pkg.get("dependencies", {}))
        all_deps.update(pkg.get("devDependencies", {}))

        # Detect frontend
        for dep, framework in FRONTEND_FRAMEWORKS.items():
            if dep in all_deps:
                # Prefer more specific (Next.js over React)
                if tech_stack["frontend"] is None or dep == "next":
                    tech_stack["frontend"] = framework

        # Detect backend
        for dep, framework in BACKEND_FRAMEWORKS.items():
            if dep in all_deps:
                tech_stack["backend"] = framework
                break

        # Detect database
        for dep, db in DATABASE_PATTERNS.items():
            if dep in all_deps:
                tech_stack["database"] = db
                break

        # Detect auth
        for dep, auth in AUTH_PATTERNS.items():
            if dep in all_deps:
                tech_stack["auth"] = auth
                break

    # Check requirements.txt for Python projects
    requirements_txt = project_path / "requirements.txt"
    if requirements_txt.exists():
        with open(requirements_txt) as f:
            requirements = f.read().lower()

        if "flask" in requirements:
            tech_stack["backend"] = "Flask"
        elif "fastapi" in requirements:
            tech_stack["backend"] = "FastAPI"
        elif "django" in requirements:
            tech_stack["backend"] = "Django"

    # Check pyproject.toml
    pyproject = project_path / "pyproject.toml"
    if pyproject.exists():
        with open(pyproject) as f:
            content = f.read().lower()

        if "flask" in content:
            tech_stack["backend"] = "Flask"
        elif "fastapi" in content:
            tech_stack["backend"] = "FastAPI"
        elif "django" in content:
            tech_stack["backend"] = "Django"

    # Check firebase.json
    firebase_json = project_path / "firebase.json"
    if firebase_json.exists():
        tech_stack["database"] = tech_stack["database"] or "Firestore"
        tech_stack["auth"] = tech_stack["auth"] or "Firebase Auth"

    return tech_stack


def detect_architecture_patterns(project_path: Path) -> dict:
    """
    Detect architectural patterns from directory structure and code.
    """
    architecture = {
        "pattern": None,
        "data_isolation": None,
        "ai_integration": None,
    }

    # Check for common patterns
    src_path = project_path / "src"

    if (project_path / "functions").exists() or (project_path / "firebase.json").exists():
        architecture["pattern"] = "serverless"
    elif (project_path / "services").exists():
        architecture["pattern"] = "microservices"
    elif src_path.exists():
        # Check for feature-based React/Vue structure
        has_components = (src_path / "components").exists()
        has_features = (src_path / "features").exists()
        has_services = (src_path / "services").exists()
        has_hooks = (src_path / "hooks").exists()

        if has_features or (has_components and (has_services or has_hooks)):
            architecture["pattern"] = "feature-based"
        else:
            architecture["pattern"] = "monolith"

    # Check for AI integration
    package_json = project_path / "package.json"
    if package_json.exists():
        with open(package_json) as f:
            content = f.read()
        if "anthropic" in content.lower() or "claude" in content.lower():
            architecture["ai_integration"] = "Claude API"
        elif "openai" in content.lower():
            architecture["ai_integration"] = "OpenAI"

    # Check for multi-tenant patterns
    architecture["data_isolation"] = detect_data_isolation(project_path)

    return architecture


def detect_data_isolation(project_path: Path) -> str:
    """
    Detect data isolation patterns (multi-tenant, single-tenant, etc.)
    """
    import re

    # Patterns that indicate multi-tenant architecture
    multi_tenant_patterns = [
        r'tenantId',
        r'tenant_id',
        r'organizationId',
        r'organization_id',
        r'tenants/\$\{',
        r'tenants/\{',
        r'/tenants/',
        r'getTenant',
        r'currentTenant',
        r'TenantContext',
    ]

    # Scan source files for patterns
    source_files = []
    for ext in ['*.ts', '*.tsx', '*.js', '*.jsx', '*.py']:
        source_files.extend(project_path.rglob(ext))

    # Skip node_modules and venv
    source_files = [f for f in source_files if 'node_modules' not in str(f) and 'venv' not in str(f)]

    for source_file in source_files:
        try:
            content = source_file.read_text()

            for pattern in multi_tenant_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    return "multi-tenant"

        except Exception:
            pass

    return "single-tenant"


def detect_conventions(project_path: Path) -> dict:
    """
    Detect code conventions from project structure.
    """
    conventions = {
        "naming": None,
        "file_structure": None,
        "state_management": None,
    }

    # Check file structure
    if (project_path / "src" / "features").exists():
        conventions["file_structure"] = "feature-based"
    elif (project_path / "src" / "components").exists() and (project_path / "src" / "services").exists():
        conventions["file_structure"] = "layer-based"
    elif (project_path / "src").exists():
        conventions["file_structure"] = "flat"

    # Check state management
    package_json = project_path / "package.json"
    if package_json.exists():
        with open(package_json) as f:
            content = f.read()
        if "redux" in content.lower():
            conventions["state_management"] = "Redux"
        elif "zustand" in content.lower():
            conventions["state_management"] = "Zustand"
        elif "jotai" in content.lower():
            conventions["state_management"] = "Jotai"
        elif "react" in content.lower():
            conventions["state_management"] = "React Context"

    return conventions


def extract_schemas(project_path: Path) -> dict:
    """
    Extract type definitions and schemas from code.
    """
    import re

    schemas = {}

    # Find TypeScript files
    ts_files = list(project_path.rglob("*.ts")) + list(project_path.rglob("*.tsx"))

    # Skip node_modules
    ts_files = [f for f in ts_files if "node_modules" not in str(f)]

    for ts_file in ts_files:
        try:
            content = ts_file.read_text()

            # Extract interfaces using regex
            interface_pattern = r'(?:export\s+)?interface\s+(\w+)\s*\{([^}]+)\}'
            matches = re.findall(interface_pattern, content, re.MULTILINE)

            for name, body in matches:
                # Parse fields from interface body
                fields = []
                field_pattern = r'(\w+)(?:\?)?:\s*([^;]+);'
                field_matches = re.findall(field_pattern, body)

                for field_name, field_type in field_matches:
                    fields.append(f"{field_name}: {field_type.strip()}")

                if fields:
                    schemas[name] = {"fields": fields, "source": str(ts_file.relative_to(project_path))}

        except Exception:
            pass  # Skip files that can't be read

    return schemas


def detect_integration_points(project_path: Path) -> list:
    """
    Detect how components connect to each other.
    """
    integration_points = []

    # Check for common integration patterns
    package_json = project_path / "package.json"
    if package_json.exists():
        with open(package_json) as f:
            content = f.read()

        if "firebase" in content.lower():
            integration_points.append("Firebase Auth → User Context")
            integration_points.append("Firestore → Real-time Subscriptions")

        if "axios" in content.lower() or "fetch" in content.lower():
            integration_points.append("HTTP Client → API Endpoints")

    return integration_points


def compute_file_checksum(file_path: Path) -> str:
    """Compute MD5 checksum of a file."""
    if not file_path.exists():
        return ""
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def compute_project_checksums(project_path: Path) -> dict:
    """
    Compute checksums for key configuration files.
    """
    config_files = [
        "package.json",
        "requirements.txt",
        "pyproject.toml",
        "firebase.json",
        "tsconfig.json"
    ]

    checksums = {}
    for config_file in config_files:
        file_path = project_path / config_file
        if file_path.exists():
            checksums[config_file] = compute_file_checksum(file_path)

    return checksums


def load_existing_profile(profile_path: Path) -> Optional[dict]:
    """Load existing profile if it exists."""
    if profile_path.exists():
        with open(profile_path) as f:
            return json.load(f)
    return None


def needs_update(project_path: Path, existing_profile: Optional[dict]) -> bool:
    """
    Check if profile needs to be updated based on file checksums.
    """
    if existing_profile is None:
        return True

    existing_meta = existing_profile.get("_meta", {})
    existing_checksums = existing_meta.get("checksums", {})

    current_checksums = compute_project_checksums(project_path)

    # Check if any checksum changed
    return current_checksums != existing_checksums


def save_profile(profile: dict, output_path: Path) -> None:
    """
    Save project profile to JSON file.
    """
    with open(output_path, 'w') as f:
        json.dump(profile, f, indent=2)
