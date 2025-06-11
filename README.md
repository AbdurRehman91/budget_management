Budget_management System:

    This system helps an ad agency manage brands, campaigns, and track ad spend, 
    using Django, Celery, Redis, and PostgreSQL, all containerized with Docker Compose
    The pseudo_code is in pseudo_code.txt

Key Features:
    
    Budget Management: Tracks daily/monthly ad spend and automatically turns campaigns on/off based on budgets.
    Dayparting: Campaigns run only during specified hours.
    Automated Resets: Daily and monthly budgets reset automatically.
    API for Impressions: Records ad impressions via an API endpoint.
    Admin UI: Manage brands, campaigns, and view impressions via Django Admin.

Technologies

    Django: Web framework
    Celery: Task queue for background jobs
    Redis: Celery's message broker
    PostgreSQL: Database
    Docker Compose: For easy setup and orchestration

Getting Started

Prerequisites

Ensure you have Docker and Docker Compose installed.
Setup & Run

    Clone the project and navigate into it.
    git https://github.com/AbdurRehman91/budget_management.git
    cd project
    Prepare environment files and dependencies.
    Create a .env file from .env.example and update it. Ensure requirements.txt, Dockerfile, and docker-compose.yml are in place (as per previous instructions).
    Build and start all services.
    docker-compose up --build -d
    Create a Django superuser (after services are up).
    docker-compose exec django python manage.py createsuperuser

Usage

    Django Admin: Access http://localhost:8000/admin/ to create/manage Brands and Campaigns, and view Ad Impressions.
    Record Impressions: Send a POST request to http://localhost:8000/api/ads/record-impression/ with example {"campaign_id": 1, "cost": "0.15"}.
    Background Tasks: Celery automatically handles daily/monthly budget resets and periodic campaign status checks. View logs with docker-compose logs -f celery_worker or celery_beat.
    Type Checking: Run docker-compose exec django mypy ads/ to verify types.
Stopping Services

To stop all containers and remove them:

    docker-compose down

To also remove database data volumes:

    docker-compose down --volumes