# ☕ MeroCoffee - Creator Support Platform

<div align="center">

**A modern, full-stack platform that enables content creators to receive support from their community through donations, memberships, and subscriptions.**

[![Python](https://img.shields.io/badge/Python-3.13+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2+-092E20?style=flat&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](license)

</div>

---

## 🌟 Overview

**MeroCoffee** is a comprehensive creator support platform built with Django that allows content creators to monetize their work through one-time donations ("buy me a coffee"), recurring memberships, and direct supporter engagement. The platform features a robust payment system, creator dashboards, KYC verification, and enterprise-grade security.

---

## ✨ Key Features

### 🎨 Creator Features
- **Customizable Creator Profiles** - Personalized public pages with bio, avatar, pricing, and branding
- **Multi-tier Support System** - Accept one-time donations with custom "coffee prices"
- **Membership & Subscriptions** - Offer recurring membership tiers with custom benefits
- **Comprehensive Dashboard** - Real-time analytics, earnings overview with Chart.js visualizations
- **Supporter Management** - View and manage all supporters with transaction history
- **Withdrawal System** - Request payouts to multiple payment methods with tracking
- **Profile Settings** - Full control over page appearance and settings

### 💳 Payment & Finance
- **Multiple Payment Gateways**:
  - eSewa (Nepal)
  - Khalti (Nepal)
  - Bank Transfer
  - Stripe (International)
  - PayPal (International)
- **Flexible Payment Tracking** - Complete transaction logs and payment history
- **Withdrawal Management** - Support for multiple withdrawal methods with status tracking
- **Earnings Analytics** - Total, pending, withdrawn, and available balance tracking

### 👥 User Management
- **Role-Based Access Control** - Super Admin, Admin, Manager, Merchant, Support, Creator, Supporter
- **Email Verification** - Secure account activation with token-based verification
- **KYC System** - Full identity verification with document uploads (ID cards, selfies)
- **Password Reset** - Secure password recovery with email confirmation
- **User Authentication** - JWT-style token authentication with session management

### 📧 Communication
- **Email Template System** - Database-driven, customizable email templates
- **Newsletter Integration** - Subscribe and manage newsletter subscribers with verification
- **Transactional Emails**:
  - Registration confirmation
  - Payment receipts (for both creators and supporters)
  - Password reset
  - Newsletter verification

### 🔒 Security Features
- **Django Defender** - Brute-force protection with automatic IP-based lockout
- **Admin Honeypot** - Fake admin login at `/admin/` to catch malicious attempts (real admin at `/dashboardx/`)
- **Rate Limiting** - Configurable rate limits on sensitive endpoints
- **CIDR Network Control** - IP whitelist/blacklist support
- **Cloudflare Turnstile** - Bot protection on forms
- **Sentry Integration** - Real-time error tracking and monitoring
- **CSRF Protection** - Django's built-in CSRF middleware
- **Secure File Storage** - Private media storage for KYC documents

### 🎨 UI/UX
- **Interactive Components** - Dynamic charts, dropdowns, mobile menus
- **Component Architecture** - Reusable Django View Components
- **Modern Admin Interface** - Customized with Django Jazzmin
- **Real-time Updates** - Live dashboard statistics
- **Browser Reload** - Hot reload during development

### 🚀 Developer Experience
- **Async Task Processing** - Celery with Redis for background jobs
- **Caching** - Redis-backed caching for performance
- **Docker Support** - Production-ready containerization
- **CI/CD Ready** - Pre-commit hooks, linting (Ruff), formatting (djlint)
- **Multiple Environments** - Development, testing, staging, and production configs
- **Location Support** - Cities/countries database with django-cities-light

---

## 🛠️ Tech Stack

### Backend
- **Django 5.2+** - Modern Python web framework
- **Python 3.13+** - Latest Python features
- **PostgreSQL** - Primary database (SQLite for development)
- **Redis** - Caching and message broker
- **Celery** - Distributed task queue
- **Flower** - Celery monitoring tool

### Frontend
- **Django Templates** - Server-side rendering
- **Chart.js** - Interactive data visualizations
- **Django View Component** - Component-based architecture
- **JavaScript** - Interactive UI behaviors

### Infrastructure & DevOps
- **Docker & Docker Compose** - Containerization
- **WhiteNoise** - Static file serving
- **Gunicorn** - WSGI HTTP server
- **Nginx** - Reverse proxy
- **Sentry** - Error tracking and monitoring

### Security & Authentication
- **Django Defender** - Brute-force protection
- **Django Admin Honeypot** - Security monitoring
- **Cloudflare Turnstile** - CAPTCHA alternative
- **django-ratelimit** - Request rate limiting

### Integrations
- **Stripe** - International payments
- **PayPal** - Alternative payment method
- **eSewa/Khalti** - Nepal payment gateways
- **Sentry** - Error monitoring

---

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- Redis (for caching and Celery)
- PostgreSQL (optional, SQLite used by default)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/PublisherName/MeroCoffee.git
   cd MeroCoffee
   ```

2. **Install uv package manager** (if not installed)
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Install dependencies**
   ```bash
   uv sync --frozen --extra development
   ```

4. **Configure environment variables**
   ```bash
   cp .env.dev.example .env
   # Edit .env with your configuration
   ```

5. **Run database migrations**
   ```bash
   uv run python manage.py migrate
   ```

6. **Seed initial data**
   ```bash
   uv run manage.py seed_groups
   uv run python manage.py seed_payment_gateways
   uv run python manage.py loaddata fixtures/nepal_cities_light.json
   uv run python manage.py seed_email_templates
   ```

7. **Install and start Redis** (Linux - Arch-based)
   ```bash
   sudo pacman -S redis
   sudo systemctl start redis
   ```
   For other systems, see [Redis installation guide](https://redis.io/docs/getting-started/installation/)

8. **Create a superuser** (optional)
   ```bash
   uv run python manage.py createsuperuser
   ```

9. **Start the development server**
    ```bash
    uv run python manage.py runserver
    ```

10. **Access the application**
    - Application: `http://localhost:8000`
    - Admin Panel: `http://localhost:8000/dashboardx/`

---

## 🐳 Docker Setup

MeroCoffee includes production-ready Docker support for all environments.

### Prerequisites
- Docker Engine 20.10+
- Docker Compose V2

### Quick Docker Start

1. **Create external network**
   ```bash
   docker network create external-services
   ```

2. **Choose environment**

   **Development/Testing:**
   ```bash
   ln -sf docker/docker-compose.dev.yml docker-compose.yml
   cp .env.dev.example .env
   ```

   **Production/Staging:**
   ```bash
   ln -sf docker/docker-compose.prod.yml docker-compose.yml
   cp .env.prod.example .env
   ```

3. **Configure environment variables**
   ```bash
   # Edit .env with your actual values
   nano .env
   ```

4. **Start external services** (PostgreSQL, Redis)
   ```bash
   ln -sf docker/external_services.yml external_services.yml
   docker compose -f external_services.yml up -d
   ```

5. **Create database** (if using PostgreSQL)
   ```bash
   docker exec db psql -U postgres -c 'CREATE DATABASE merocoffee;'
   ```

6. **Start application**
   ```bash
   docker compose up -d
   ```

7. **Create superuser**
   ```bash
   docker compose exec server ./manage.py createsuperuser
   ```

8. **Access the application**
   - Application: `http://localhost:8000`
   - Real Admin: `http://localhost:8000/dashboardx/`
   - Fake Admin (Honeypot): `http://localhost:8000/admin/`

### Docker Commands Reference

```bash
# View logs
docker compose logs -f

# View specific service logs
docker compose logs -f server

# Rebuild after code changes
docker compose build

# Run migrations
docker compose exec server ./manage.py migrate

# Collect static files
docker compose exec server ./manage.py collectstatic --noinput

# Access shell
docker compose exec server ./manage.py shell

# Stop all services
docker compose down

# Stop and remove volumes (⚠️ deletes data)
docker compose down -v
```

---


## 📁 Project Structure

```
MeroCoffee/
├── apps/                    # Django applications
│   ├── accounts/          # User authentication & KYC
│   ├── core/              # Core functionality & utilities
│   ├── creators/          # Creator profiles & management
│   ├── dashboard/         # Creator dashboard views
│   ├── emails/            # Email templates & sending
│   ├── newsletter/        # Newsletter subscriptions
│   └── payments/          # Payment processing & withdrawals
│
├── components/            # Reusable UI components
│   ├── email_input/
│   ├── password_input/
│   ├── image_upload/
│   ├── turnstile_input/
│   └── ...
│
├── root/                  # Project configuration
│   ├── settings.py        # Django settings
│   ├── urls.py            # URL routing
│   ├── celery.py          # Celery configuration
│   ├── middleware.py      # Custom middleware
│   └── storage.py         # File storage configuration
│
├── templates/             # HTML templates
├── static/                # Static files (CSS, JS, images)
├── public/                # Public media files
├── private/               # Private media files (KYC docs)
│
├── docker/                # Docker configuration files
├── nginx/                 # Nginx configuration
├── terraform/             # Infrastructure as Code
├── fixtures/              # Database fixtures
│
├── manage.py              # Django management script
├── pyproject.toml         # Python dependencies (uv)
├── Dockerfile             # Docker image definition
└── docker-compose.yml     # Docker Compose configuration
```

---

## 🔒 Security

MeroCoffee implements multiple layers of security to protect both creators and supporters.

### Admin Security

**Admin Honeypot** - Decoy admin login to catch malicious attempts:
- **Fake Admin**: `/admin/` → Logs all unauthorized login attempts
- **Real Admin**: `/dashboardx/` → Actual Django admin interface

View honeypot logs at: `/dashboardx/admin_honeypot/loginattempt/`

### Brute-Force Protection

**Django Defender** automatically locks out users/IPs after failed login attempts:
- Configurable lockout duration (default: 60 minutes)
- IP and username-based blocking
- Redis-backed for performance
- Tracks both IP and username combinations

### Rate Limiting

- Configurable rate limits on sensitive endpoints
- Production default: 3 requests per 30 minutes
- Disabled in development for easier testing
- Custom lockout view for better UX

### Additional Security Measures

- **CSRF Protection** - All forms protected against cross-site attacks
- **Cloudflare Turnstile** - Bot protection on registration/login forms
- **CIDR Network Control** - IP whitelist/blacklist support
- **Secure File Storage** - Private media storage for KYC documents
- **Password Requirements** - Django's built-in password validation
- **HTTPS Enforcement** - Automatic HTTPS redirect in production
- **Sentry Monitoring** - Real-time error tracking and alerting

### Best Practices

1. Always use strong passwords for admin accounts
2. Enable 2FA for admin users (via third-party package)
3. Regularly review honeypot login attempts
4. Keep dependencies updated
5. Use environment variables for sensitive data
6. Configure proper ALLOWED_HOSTS in production
7. Enable Sentry in production for error monitoring

---

## ⚙️ Environment Variables

Key environment variables to configure:

### Required
```bash
# Server Configuration
SERVER_ENVIRONMENT=development  # development|testing|staging|production
DJANGO_SECRET_KEY=your-secret-key-here
SITE_BASE_URL=http://localhost:8000
SITE_NAME=MeroCoffee

# Database
DATABASE_URL=sqlite:///db.sqlite3  # or postgresql://user:pass@host:port/dbname

# Cache & Celery
CACHE_URL=redis://localhost:6379/0
```

### Payment Gateways
```bash
# eSewa
ESEWA_MERCHANT_ID=your-merchant-id
ESEWA_SECRET_KEY=your-secret-key

# Khalti
KHALTI_SECRET_KEY=your-secret-key

# Stripe
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...

# PayPal
PAYPAL_CLIENT_ID=your-client-id
PAYPAL_SECRET=your-secret
```

### Email Configuration
```bash
EMAIL_URL=smtp://user:password@smtp.gmail.com:587
DEFAULT_FROM_EMAIL=noreply@example.com
```

### Security
```bash
# Cloudflare Turnstile
TURNSTILE_SITE_KEY=your-site-key
TURNSTILE_SECRET_KEY=your-secret-key

# Sentry (Error Tracking)
SENTRY_DSN=https://...@sentry.io/...

# Rate Limiting (production)
RATELIMIT_RATE=3/30m
```

### Production Settings
```bash
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
ALLOWED_CIDR_NETS=192.168.1.0/24,10.0.0.0/8
```

See `.env.dev.example`, `.env.test.example`, and `.env.prod.example` for complete configuration examples.

---

## 📚 Usage Guide

### For Supporters

1. **Browse Creators** - Visit the homepage to discover content creators
2. **Select Amount** - Choose how many "coffees" to buy (custom amounts)
3. **Leave a Message** - Add an optional message of support
4. **Choose Payment** - Select from eSewa, Khalti, Bank Transfer, Stripe, or PayPal
5. **Complete Payment** - Follow the payment gateway flow
6. **Get Confirmation** - Receive email confirmation of your support

### For Creators

1. **Sign Up** - Register and verify your email
2. **Complete Profile** - Add bio, avatar, and set your coffee price
3. **Set Up Payments** - Configure payment methods for withdrawals
4. **Share Your Page** - Share your creator URL with your audience
5. **Track Earnings** - Monitor support through your dashboard
6. **Request Withdrawals** - Cash out your earnings when ready
7. **Complete KYC** - Submit identity verification (required for withdrawals)

### For Administrators

1. **Access Admin** - Navigate to `/dashboardx/`
2. **Manage Users** - Review and manage user accounts
3. **Process KYC** - Approve or reject identity verifications
4. **Handle Withdrawals** - Process creator payout requests
5. **Monitor Security** - Review honeypot logs and failed login attempts
6. **Configure Gateways** - Set up and manage payment gateways
7. **Email Templates** - Customize transactional email templates

---

## 🧑‍💻 Development

### Running Tests

```bash
# Run all tests
uv run python manage.py test

# Run specific app tests
uv run python manage.py test apps.accounts

# Run with coverage
uv run coverage run --source='.' manage.py test
uv run coverage report
```

### Code Quality

```bash
# Format code with Ruff
uv run ruff format .

# Lint code
uv run ruff check .

# Format templates with djlint
uv run djlint templates/ --reformat

# Run pre-commit hooks
uv run pre-commit run --all-files
```

### Database Management

```bash
# Create migrations
uv run python manage.py makemigrations

# Apply migrations
uv run python manage.py migrate

# Create database backup
uv run python manage.py dumpdata > backup.json

# Load fixtures
uv run python manage.py loaddata fixtures/nepal_cities_light.json
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork the Repository**
2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make Your Changes**
   - Follow existing code style
   - Add tests for new features
   - Update documentation as needed
4. **Run Tests & Linting**
   ```bash
   uv run ruff check .
   uv run python manage.py test
   ```
5. **Commit Your Changes**
   ```bash
   git commit -m "feat: add amazing feature"
   ```
   Follow [Conventional Commits](https://www.conventionalcommits.org/)
6. **Push to Your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Open a Pull Request**
   - Provide clear description
   - Link any related issues
   - Wait for review

### Development Guidelines

- Write clear, self-documenting code
- Add docstrings to functions and classes
- Keep functions small and focused
- Write tests for new features
- Update README for significant changes
- Follow Django best practices
- Use type hints where appropriate

---

## 📝 Roadmap

### Planned Features

- [ ] Recurring membership subscriptions
- [ ] Creator analytics dashboard (detailed insights)
- [ ] Mobile app (React Native/Flutter)
- [ ] Multi-language support (i18n)
- [ ] Social media integration
- [ ] Creator collaboration tools
- [ ] Advanced reporting and exports
- [ ] Webhook support for integrations
- [ ] Two-factor authentication
- [ ] Custom domain for creator pages

---

## 🐛 Known Issues

- Celery worker must be running for email sending
- Some payment gateways require specific IP whitelisting

See [Issues](https://github.com/PublisherName/MeroCoffee/issues) for more details.

---

## 💫 FAQ

**Q: Can I use this for commercial purposes?**
A: Yes! This project is MIT licensed and free to use commercially.

**Q: Which payment gateways are supported?**
A: eSewa, Khalti (Nepal), Stripe, PayPal, and Bank Transfer.

**Q: Is this production-ready?**
A: Yes, with proper configuration. Ensure you set up Sentry, configure all security settings, and use PostgreSQL for production.

**Q: How do I add a new payment gateway?**
A: Create a new payment gateway in the admin panel and implement the payment flow in `apps/payments/`.

**Q: Can creators have custom URLs?**
A: Currently, creators use username-based URLs (`/creator/{username}`). Custom domains are on the roadmap.

---

## 📜 License

This project is licensed under the **MIT License** - see the [license](license) file for details.

You are free to:
- ✅ Use commercially
- ✅ Modify
- ✅ Distribute
- ✅ Private use

---

## 📧 Contact & Support

- **Email**: coffee@subashghimire.info.np
- **Issues**: [GitHub Issues](https://github.com/PublisherName/MeroCoffee/issues)
- **Discussions**: [GitHub Discussions](https://github.com/PublisherName/MeroCoffee/discussions)

---

## 🚀 Deployment

### Recommended Stack

- **Application**: Docker + Gunicorn
- **Database**: PostgreSQL (managed service recommended)
- **Cache/Queue**: Redis (managed service recommended)
- **Static Files**: WhiteNoise + CDN (optional)
- **Hosting**: AWS, DigitalOcean, Heroku, or Render
- **Monitoring**: Sentry for errors, Flower for Celery

### Environment Checklist

Before deploying to production:

- [ ] Set `SERVER_ENVIRONMENT=production`
- [ ] Generate strong `DJANGO_SECRET_KEY`
- [ ] Configure `DJANGO_ALLOWED_HOSTS`
- [ ] Set up PostgreSQL database
- [ ] Configure Redis for caching
- [ ] Set up email service (SMTP/SendGrid/AWS SES)
- [ ] Configure payment gateway credentials
- [ ] Set up Sentry for error tracking
- [ ] Enable HTTPS and set `SECURE_SSL_REDIRECT=True`
- [ ] Configure Cloudflare Turnstile
- [ ] Set up automated backups
- [ ] Configure CIDR network restrictions
- [ ] Review and test all security settings

---

## ⭐ Show Your Support

If you find this project useful, please consider:

- ⭐ Starring the repository
- 🐛 Reporting bugs
- 💡 Suggesting new features
- 🤝 Contributing to the codebase
- 💬 Sharing with others

---

<div align="center">

**Built with ❤️ by the MeroCoffee Team**

[Report Bug](https://github.com/PublisherName/MeroCoffee/issues) · [Request Feature](https://github.com/PublisherName/MeroCoffee/issues) · [Documentation](https://github.com/PublisherName/MeroCoffee/wiki)

</div>
