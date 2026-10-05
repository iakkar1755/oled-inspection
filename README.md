# OLED Display Vision Inspection System

A computer vision-based inspection system for analyzing OLED displays using a live camera feed.

The project demonstrates a full-stack automation and machine vision workflow using Python, OpenCV, Flask, SQLAlchemy, SQLite, JavaScript, and a web-based operator dashboard.

## Current Features

- Live camera streaming using OpenCV
- Flask-based web application
- Real-time camera display in the browser
- Region of Interest (ROI) extraction
- Brightness analysis using NumPy
- Mean brightness calculation
- Standard deviation calculation
- Minimum and maximum brightness detection
- Experimental uniformity score
- Automatic PASS / FAIL decision
- SQLite inspection database
- SQLAlchemy ORM integration
- Inspection history
- Web-based operator dashboard

## System Architecture

```text
Physical Camera
      ↓
OpenCV
      ↓
Camera Frame
      ↓
Region of Interest (ROI)
      ↓
Image Inspection
      ↓
Brightness / Uniformity Analysis
      ↓
PASS / FAIL
      ↓
Flask Backend
      ↓
SQLAlchemy
      ↓
SQLite Database
      ↓
JSON API
      ↓
JavaScript
      ↓
Operator Dashboard
```

## Project Structure

```text
oled-inspection/
│
├── app.py
├── camera_test.py
├── inspection.py
├── models.py
│
├── templates/
│   └── index.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── dashboard.js
│
├── .gitignore
└── README.md
```

## Technologies

- Python
- OpenCV
- NumPy
- Flask
- Flask-SQLAlchemy
- SQLite
- HTML
- CSS
- JavaScript

## Inspection Pipeline

The camera continuously captures image frames using OpenCV.

A Region of Interest (ROI) is extracted from the camera frame and used for inspection.

The current inspection algorithm converts the ROI to grayscale and calculates:

- Mean brightness
- Standard deviation
- Minimum brightness
- Maximum brightness
- Uniformity score

The calculated measurements are compared with experimental thresholds to determine the inspection result:

```text
PASS
or
FAIL
```

Each inspection result is stored in the SQLite database and displayed in the inspection history table on the operator dashboard.

## Current Development Status

The current version implements the basic camera-to-database inspection pipeline.

Planned development includes:

- Redis integration
- Flask-SSE live event streaming
- SciPy-based image processing
- Advanced defect detection
- Code modularization
- GitLab / CI workflow
- Automated testing with pytest
- Docker containerization
- Linux deployment
- Optional FastAPI services
- Optional machine learning-based defect detection

## Important Note

The current PASS / FAIL thresholds and uniformity calculations are experimental and are intended for development and demonstration purposes.

They are not official OLED manufacturing specifications.
