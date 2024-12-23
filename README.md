# Sondae Service - Event Community Platform

A modern event management and community platform for SondaeBlu, featuring ticket sales, membership management, and indigenous-inspired design elements.

## Features

- Event Management & Ticketing
- Multi-tier Membership System
- Table Reservations & Bottle Service
- Community Engagement Tools
- Indigenous-inspired Dark Theme
- Mobile-first Design

## Tech Stack

- Flask (Backend Framework)
- SQLAlchemy (Database ORM)
- PostgreSQL (Database)
- Flask-Login (Authentication)
- Stripe (Payment Processing)
- qrcode (QR Code Generation)

## Project Structure
```
sondae-service/
├── README.md
├── requirements.txt
├── config.py
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── event.py
│   │   ├── ticket.py
│   │   ├── user.py
│   │   └── reservation.py
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   ├── templates/
│   │   ├── base.html
│   │   ├── auth/
│   │   ├── events/
│   │   ├── admin/
│   │   └── members/
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── events.py
│   │   ├── admin.py
│   │   └── members.py
│   └── utils/
│       ├── __init__.py
│       ├── decorators.py
│       └── helpers.py
└── migrations/
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

5. Run the application:
```bash
flask run
```

## Development

- Follow PEP 8 style guide
- Write tests for new features
- Update documentation as needed

## License

Copyright 2024 Sondae Service. All rights reserved.
