# Job Board Platform

A full-stack job board application designed to connect job seekers with employers. This project focuses on a clean backend architecture using Django and Django REST Framework, with a responsive frontend built using Django Templates and Tailwind CSS.

## Features

### Candidate Features
- **Account Management**: Register and log in as a candidate.
- **Job Discovery**: Browse and search through active job listings.
- **Applications**: Apply to jobs with a resume upload (PDF/DOCX) and cover letter.
- **Tracking**: Monitor the status of submitted applications via a personal dashboard.
- **Job Saving**: Save jobs to a "Saved Jobs" list for later review.

### Employer Features
- **Job Management**: Create, edit, and delete job postings.
- **Applicant Tracking**: View a list of candidates who applied to specific jobs.
- **Status Updates**: Update application statuses (e.g., "Reviewing", "Interview Scheduled", "Hired").
- **Company Profile**: Manage company information, including description and website.

### Admin Features
- **User Moderation**: Approve or reject employer accounts.
- **Content Management**: Overview and management of all users, jobs, and applications.

### Backend & API
- **JWT Authentication**: Secure API access using JSON Web Tokens.
- **Role-Based Access Control**: Strict permission checks for candidates, employers, and admins.
- **Search & Filtering**: Filter jobs by type, location, and experience level.
- **Pagination**: Efficiently handle large lists of jobs and applications.

## User Roles
- **Candidate**: Can search, save, and apply to jobs.
- **Employer**: Can post jobs and manage applicants.
- **Admin**: Manages the platform and approves employers.

## Tech Stack
- **Backend**: Django 5.0, Django REST Framework
- **Frontend**: Django Templates, Tailwind CSS, HTMX
- **Database**: SQLite (Development)
- **Authentication**: JWT (SimpleJWT)
- **Environment**: Decoupled settings using `python-decouple`

## Installation / Setup

### 1. Environment Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configuration
Create a `.env` file from the example:
```bash
cp .env.example .env
```

### 3. Database Initialization
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 4. Run the Server
```bash
python manage.py runserver
```

## API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/token/` | Obtain JWT access and refresh tokens. |
| `GET` | `/api/jobs/` | List all active job postings. |
| `POST` | `/api/jobs/{slug}/save/` | Save a job (Candidates only). |
| `POST` | `/api/applications/` | Submit a new job application. |
| `GET` | `/api/users/me/` | Retrieve current user profile. |

## Project Structure
```text
├── job_board/           # Project settings and core configuration
├── users/               # Custom User model and authentication logic
├── jobs/                # Job listing, search, and management logic
├── applications/        # Job application and status tracking
├── core/                # Shared utilities and custom permissions
├── templates/           # HTML templates for the web interface
├── static/              # Static assets (CSS, JS)
└── tests/               # Automated test suite
```

## Why This Project Matters
This project was built to demonstrate a solid understanding of Django's ecosystem and the integration of RESTful APIs with traditional server-side rendering. It focuses on solving real-world problems like role-based access control, file handling, and state management in a multi-user environment. The code follows DRY (Don't Repeat Yourself) principles and maintains a clear separation of concerns.

## License
Distributed under the MIT License.
