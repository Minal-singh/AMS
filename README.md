[![Attendance Management CI](https://github.com/Minal-singh/AMS/actions/workflows/attendance-management.yml/badge.svg)](https://github.com/Minal-singh/AMS/actions/workflows/attendance-management.yml)

# Student Attendance Management System Created Using Django

[Project Demo on YouTube]

And if you like this project, then ADD a STAR ⭐️  to this project 👆

## Features of this Project

### A. Admin Users Can
1. Register new student.
2. Manage Students (Update and Delete)
3. View Student Attendance

### B. Students Can
1. View Attendance


## 📸 ScreenShots


## How to Install and Run this project?

### Pre-Requisites:
1. Install Git Version Control
[ https://git-scm.com/ ]

2. Install Python Latest Version
[ https://www.python.org/downloads/ ]

3. Install Pip (Package Manager)
[ https://pip.pypa.io/en/stable/installing/ ]

*Alternative to Pip is Homebrew*

### Installation
**1. Create a Folder where you want to save the project**

**2. Create a Virtual Environment and Activate**

Install Virtual Environment First
```
$  pip install virtualenv
```

Create Virtual Environment

For Windows
```
$  python -m venv venv
```
For Mac
```
$  python3 -m venv venv
```
For Linux
```
$  virtualenv .
```

Activate Virtual Environment

For Windows
```
$  source venv/scripts/activate
```

For Mac
```
$  source venv/bin/activate
```

For Linux
```
$  source bin/activate
```

**3. Clone this project**
```
$  git clone 
```

Then, Enter the project
```
$  cd SAMS
```

**4. Install Requirements from 'requirements.txt'**

For Windows
```
$  pip install https://github.com/Minal-singh/dlib/blob/master/dlib-19.23.0-cp39-cp39-win_amd64.whl?raw=true
$  pip install cmake
$  pip install -r requirements.txt
```
For Linux and Mac
```python
$  pip3 install -r requirements-linux.txt
```


**5. Now Run Server**

Command for Windows:
```python
$ python manage.py makemigrations
$ python manage.py migrate
$ python manage.py runserver
```

Command for Mac:
```python
$ python3 manage.py makemigrations
$ python3 manage.py migrate
$ python3 manage.py runserver
```

Command for Linux:
```python
$ python3 manage.py makemigrations
$ python3 manage.py migrate
$ python3 manage.py runserver
```

**6. Login Credentials**

**Use Default Credentials**

*For Admin*
Email: admin@admin.com
Password: admin

*For Student*
Email: student@student.com
Password: password
