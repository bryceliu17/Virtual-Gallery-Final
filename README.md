# Virtual Gallery

## Project Overview

**Virtual Gallery** is a web application developed for **IFN582 Rapid Web Development with Databases**.

This project is based on the **Art Lease** domain. Artists can upload artworks and offer them for lease at a monthly price. Customers can browse artworks, filter results, add items to cart, and lease artworks for a selected number of months. The application also includes registration, login, vendor management, checkout functionality, and an admin dashboard.

## Main Features

- User registration and login
- Artist/vendor artwork management
- Artwork upload with image support
- Browse and filter artworks
- Add artworks to cart
- Checkout and lease artworks for a specified number of months
- Admin dashboard for system management

## Project Structure

```text
.
├── run.py
├── README.md
└── project/
    ├── static/
    │   ├── css/
    │   ├── img/
    │   └── uploads/
    ├── templates/
    ├── forms.py
    ├── db.py
    ├── models.py
    ├── views.py
    ├── __init__.py
    └── database.sql

```


## Prerequisites

Before running this project, make sure the following are installed:

- Python 3.10 or above
- MySQL Server
- MySQL Workbench (recommended)
- PowerShell or another terminal

### Tested environment

- Python 3.11 / 3.12
- MySQL Workbench 8.0 Community Edition

## Database Configuration

The default MySQL configuration in `project/__init__.py` is:

```python
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'root'
MYSQL_DB = 'virtual_gallery'
UPLOAD_FOLDER = 'static/uploads'
```


## Setup Instructions (Windows PowerShell)

### 1. Open the project folder

Open PowerShell and change the directory to the project root, where `run.py` is located.

```powershell
cd "C:\Path\To\Your\Project"
```



### 2. Create and activate a virtual environment

```powershell
python -m venv venv
.\venv\Scripts\activate
```


### 3. Start MySQL Server

Before importing the database or running the application, make sure your MySQL Server is running.

#### Option A: Start MySQL from Windows Services

1. Press `Win + S`
2. Search for **Services**
3. Open the **Services** app
4. Find the MySQL service, commonly named **MySQL** or **MySQL80**
5. If it is not running, click **Start**

#### Option B: Check through MySQL Workbench

1. Open **MySQL Workbench**
2. Connect to your local MySQL instance
3. Make sure you can log in successfully with your MySQL username and password


### 4. Create the database

Create a database named `virtual_gallery`.

You can run the following SQL command in MySQL Workbench:

```sql
CREATE DATABASE virtual_gallery;
```


### 5. Import the database schema

Import the SQL file located at:

```text
project/database.sql

You can do this in MySQL Workbench:

1. Open **MySQL Workbench**
2. Connect to your local MySQL instance
3. Go to **Server > Data Import**
4. Choose **Import from Self-Contained File**
5. Select `project/database.sql`
6. Choose the target schema `virtual_gallery`
7. Click **Start Import**
```


### 6. Check database credentials

Before running the application, make sure the values of `MYSQL_USER` and `MYSQL_PASSWORD` in `project/__init__.py` match your local MySQL settings.

### 7. Run the application

```powershell
python run.py
```

### 8. Open the application in the browser

```text
http://127.0.0.1:8000
```

## Demo Accounts

The following demo accounts can be used for testing.

### Artists / Vendors

- `tanya.painter@example.com` / `pass2`
- `brunswick.gallery@example.com` / `pass3`
- `ava.alt@art.com` / `pass7`

### Customers

- `bob.buyer@example.com` / `pass4`
- `lauren@example.com` / `pass1`

### Admin

- `admin2@example.com` / `admin2`
- `admin@example.com` / `admin1`

## Error Testing

This project includes test cases for common error pages.

### 404 Error

Edit the URL to a route that does not exist.

### 500 Error

Open the following URL:

```text
http://127.0.0.1:8000/trigger_500
```

## Notes

When logged in as an admin or artist, artworks that have already been included in a completed transaction cannot be deleted. This restriction is kept for testing purposes.

The affected items are:

- Sun Yard
- Woven Sky
- Stone Form
- Desert Bloom
- Night Bridge

When inserting artworks as an artist, please use the images in `static/uploads`.