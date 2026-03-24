# Videoflix

**Videoflix** is a video streaming platform where users can register, log in, watch videos, and manage their accounts. Built with **Django**, **Django REST Framework**, and **Redis**, it provides secure user authentication, email verification, and password reset functionality.
Videos can be uploaded via the admin panel only.

> ⚠️ A frontend is required for full project usage — placeholder for future GitHub repo.

---

## 📋 Project Overview

Videoflix enables:

* **Users** to register, log in/out, reset passwords, and stream videos
* **Admins** to manage users, videos, and system activity via the Django admin panel
* **Email notifications** for user activation and password reset

### Key Features

* 🔐 User registration and login/logout
* 📧 Email-based account activation
* 🔑 Password reset via email
* 🎬 Video streaming
* 📦 Dockerized backend with Redis and PostgreSQL
* 🚀 Development with Python virtual environments or `uv`

---

## 🚀 Setup Option 1 — using `uv` (uv Toolchain)

This option uses **uv** to manage your virtual environment and run your Django app.

### 🛠️ Prerequisites

Make sure **uv** is installed and available in your shell. Node.js ≥ 22 is required for frontend development (optional).

### 📦 Install Dependencies

```bash
uv sync
```

### 📁 Activate Environment

```bash
source .venv/bin/activate     # macOS / Linux
.venv\Scripts\activate         # Windows
```

### 🔐 Environment Configuration

Create your environment file from the template:

```bash
cp .env.template .env
```

Generate a Django secret key at [https://djecrety.ir/](https://djecrety.ir/) and add it:

```
SECRET_KEY=your-generated-secret-key-here
```

Configure email and database credentials in `.env`.
Set DEBUG variable to False on production, otherwise True.

### 🐳 Using Docker

Build and start all services with:

```bash
docker-compose up --build
```

This will start:

* PostgreSQL database
* Redis server
* Django backend

The backend will be available at:

```
http://127.0.0.1:8000/
```
---

## 👥 User Types & Permissions

### Regular Users

* Register, log in/out
* Reset password via email
* Stream videos

### Admin/Staff

* Full access via admin panel
* Manage users, videos, and system configurations

---

## 🔒 Security & Validation

### Authentication

* JWT token-based authentication via `djangorestframework-simplejwt`
* Secure password hashing with Django default

### Email Verification & Password Reset

* Activation email sent upon registration
* Password reset emails with secure links

### Permissions

* Role-based access (User, Admin)
* Protected endpoints require authentication

---

## 📝 Data Models

### User

* Default Django User with email, username, password
* Status: active/inactive (activation email required)

### Video

* Fields: title, description, thumbnail, category, original_file, hls_ready
* Streamable to authenticated users

### Password Reset Tokens

* Secure token management via Django’s built-in system

---

## 🧪 Testing

Run tests:

```bash
python manage.py test
```

---

## 📌 Notes

### 🔐 Environment Variables

* `.env` contains sensitive data (`SECRET_KEY`, email credentials, database info)
* **Do not commit `.env`** to version control

### 🗄️ Database

* PostgreSQL is used in development and production inside the Docker container

### 🧠 Frontend

* Frontend application required for full usage (to be created separately)

### 🧹 Git Ignore

* `.venv/`, media files, `.env` are ignored

### 📊 Media Files

* Stored in `/media/` directory inside the Docker container
* Configure `MEDIA_ROOT` and `MEDIA_URL` in Django settings

---

## 🛠️ Development




### Run Container

```bash
docker compose up --build
```

or

```bash
docker compose up
```

when volume already built.


### Running Tests

```bash
docker compose exec web python manage.py test
```

### Reset Container

```bash
docker compose down -v
```

---

## 📚 Quick Reference

| Step                 | Command                                            |
| -------------------- | -------------------------------------------------- |
| Create container     | `docker compose up --build`                        |
| Remove container     | `docker compose down -v   `                        |
| Configure .env       | `cp .env.template .env`                            |
| Generate SECRET_KEY  | Visit [https://djecrety.ir/](https://djecrety.ir/) |
| Access admin         | `http://127.0.0.1:8000/admin/`                     |
| Access API           | `http://127.0.0.1:8000/api/`                       |
| Access DB            | `http://127.0.0.1:5432`                            |

---

**Welcome to Videoflix!** 🎬✨

*Stream your favorite videos securely and easily.*
