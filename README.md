# MeroCoffee - Fullstack Creator Support Platform

Welcome to **MeroCoffee**, a fullstack web application built with Django and Tailwind CSS that enables content creators to connect with supporters through donations and manage their creator profiles via a feature-rich dashboard.

---

## Features

- **User Authentication**: Registration, Login, Password Reset, Email Verification
- **Creator Profiles**: Public creator pages with bio, coffee price, avatar, monthly earnings, and supporter count
- **Supporters**: Fans can browse creators, select donation amounts, leave messages, and choose payment methods (eSewa, Khalti, Bank)
- **Dashboard**: Creator-specific dashboard with overview, detailed earnings, supporters list, page settings, and withdrawal functionality
- **Responsive Navbar & Sidebar**: Active navigation links and user profile dropdown with logout via secure POST form
- **Real-time UI Interaction**: Mobile menu toggling, dropdown menus, and interactive charts (via Chart.js)
- **Customizable Coffee Price**
- **Security Features**:
  - **Django Defender**: Protects against brute-force login attempts with automatic account lockout
  - **Admin Honeypot**: Fake admin login at `/admin/` to catch and log malicious login attempts (real admin at `/dashboardx/`)

---

## Tech Stack

- **Django (Python)** — Backend web framework
- **Django Templates + Tailwind CSS** — Frontend UI and responsive styling
  - Tailwind CDN for utility classes
  - Custom CSS files for semantic component styles
  - Separated CSS architecture for maintainability
- **Chart.js** — Interactive earnings chart on dashboard
- **Django Admin Honeypot** — Fake admin login at `/admin/` to catch and log malicious login attempts (real admin at `/dashboardx/`)
- **Django Defender** — Protects against brute-force login attempts with automatic account lockout
- **Django Jazzmin** — Customizable admin interface with modern design

- **PostgreSQL or SQLite** — Database (adjustable)
- **JavaScript** — UI behaviors (menu toggles, dropdowns)

---

## Installation & Setup

1. Clone repository:
    ```
    git clone https://github.com/PublisherName/MeroCoffee.git
    cd merocoffee
    ```

2. Create virtual environment and install dependency:
    ```
    uv sync --frozen --extra development
    ```

    Install uv if not installed:
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

3. Copy .env.dev.example -> .env
    ```bash
    cp .env.dev.example .env
    ```
4. Run migrations:
    ```
    uv run python manage.py migrate
    ```

5. Seed default payment gateways (eSewa, Khalti):
    ```bash
    uv run python manage.py seed_payment_gateways
    ```

6. Install tailwind dependency
   ```bash
   uv run python manage.py tailwind install
   ```

7. Build tailwind css and assets
   ```bash
   uv run python manage.py tailwind build
   ```

8. Install redis-server if not installed
      ```bash
      sudo pacman -S redis
      ```

9. Create a superuser for admin access (optional):
    ```
    uv run python manage.py createsuperuser
    ```

10. Start the development server:
    ```
    uv run python manage.py tailwind dev
    ```

11. Access the app at `http://127.0.0.1:8000`
---

## Docker Setup

MeroCoffee includes Docker support for development, testing, and production environments.

### Prerequisites

- Docker installed on your system
- Docker Compose V2 (`docker compose` command)

### Setup Steps

1. **Create external services network:**
   ```bash
   docker network create external-services
   ```

2. **Create symlink for docker-compose file:**

   For **development/testing**:
   ```bash
   ln -s docker/docker-compose.dev.yml docker-compose.yml
   ```

   For **staging/production**:
   ```bash
   ln -s docker/docker-compose.prod.yml docker-compose.yml
   ```

3. **Create `.env` file:**

   Copy the appropriate example file and configure required environment variables:
   ```bash
   # For development
   cp .env.dev.example .env

   # For production
   cp .env.prod.example .env
   ```

   Edit `.env` and set appropriate values as explained in the example file.

4. **Setup external services (optional):**

   If you need PostgreSQL or Redis, create a symlink and start the services:
   ```bash
   ln -s docker/external_services.yml external_services.yml
   docker compose -f external_services.yml up -d
   ```

   To start only specific services:
   ```bash
   # Start only PostgreSQL
   docker compose -f external_services.yml up -d db

   # Start only Redis
   docker compose -f external_services.yml up -d redis
   ```

5. **Create database (if using PostgreSQL):**

   If you've configured a database other than SQLite3, create the database:
   ```bash
   docker exec db psql -U postgres -c 'CREATE DATABASE merocoffee;'
   ```
   Replace `merocoffee` with your actual database name from `.env`.

6. **Start the server:**
   ```bash
   # Start all services (server + celery worker)
   docker compose up -d

   # Start server only
   docker compose up -d server
   ```

   > **Note**: Celery worker is required for background tasks.

7. **Create superuser (first time setup):**
   ```bash
   docker compose exec server sh
   ./manage.py createsuperuser
   exit
   ```

8. **Access the application:**
   - Application: `http://localhost:8000`
   - Admin panel: `http://localhost:8000/admin`

### Useful Docker Commands

```bash
# View logs
docker compose logs -f

# Rebuild images after code changes
docker compose build

# View running containers
docker compose ps

# Stop all services
docker compose down

# Stop and remove volumes
docker compose down -v

# Execute commands in running container
docker compose exec server ./manage.py migrate
```

---

## Tailwind

1. Install tailwind css dependency

```bash
uv run python manage.py tailwind install
```
2. Start development server ( django + Tailwind )

```bash
uv run python manage.py tailwind dev
```

3. Start only the tailwind watcher

```bash
uv run python manage.py tailwind start
```

4. Building for production

```bash
uv run python manage.py tailwind build
```

---

## Security

### Admin Honeypot

MeroCoffee uses **django-admin-honeypot** to protect the admin panel from unauthorized access attempts:

- **Fake Admin**: `/admin/` - This is a decoy login page that logs all login attempts
- **Real Admin**: `/dashboardx/` - This is the actual Django admin panel

All login attempts to `/admin/` are logged in the database and can be reviewed in the real admin panel at `/dashboardx/admin_honeypot/loginattempt/`. This helps identify potential security threats and malicious actors trying to access your admin panel.

---

## Usage

- Visit the homepage to browse creators or learn how the platform works.
- Register or login to start creating your own creator page or support others.
- Use the dashboard to view earnings, manage your profile, update page settings, or request withdrawals.
- Mobile-friendly navigation ensures usability on phones and tablets.

---

## Contributing

Contributions are welcome! Please fork the repo and open pull requests with descriptive titles and details.

---

## License

This project is licensed under the MIT License.

---

## Contact

For questions or feedback, contact the maintainer at `coffee@subashghimire.info.np`

---
