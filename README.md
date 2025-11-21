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

---

## Tech Stack

- **Django (Python)** — Backend web framework
- **Django Templates + Tailwind CSS** — Frontend UI and responsive styling
  - Tailwind CDN for utility classes
  - Custom CSS files for semantic component styles
  - Separated CSS architecture for maintainability
- **Chart.js** — Interactive earnings chart on dashboard
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
    uv sync --frozen
    ```
3. Copy .env.example -> .env
    ```bash
    cp .env.example .env
    ```
4. Run migrations:
    ```
    uv run python manage.py migrate
    ```

5. Seed default payment gateways (eSewa, Khalti):
    ```bash
    uv run python manage.py seed_payment_gateways
    ```

5. Create a superuser for admin access (optional):
    ```
    uv run python manage.py createsuperuser
    ```

6. Start the development server:
    ```
    uv run python manage.py runserver
    ```

7. Access the app at `http://127.0.0.1:8000`

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

For questions or feedback, contact the maintainer at `event@subashghimire.info.np`

---
