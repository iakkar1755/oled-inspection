# Import SQLAlchemy integration for Flask.
from flask_sqlalchemy import SQLAlchemy

# Create the SQLAlchemy database object.
db = SQLAlchemy()


class Inspection(db.Model):
    """
    Represents one OLED inspection result in the database.
    """

    # Database table name.
    __tablename__ = "inspections"

    # Inspection data columns.
    id = db.Column(db.Integer, primary_key=True)
    mean_brightness = db.Column(db.Float, nullable=False)
    standard_deviation = db.Column(db.Float, nullable=False)
    min_brightness = db.Column(db.Integer, nullable=False)
    max_brightness = db.Column(db.Integer, nullable=False)
    uniformity_score = db.Column(db.Float, nullable=False)
    inspection_status = db.Column(db.String(10), nullable=False)