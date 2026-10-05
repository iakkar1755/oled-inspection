# Import Flask components
from flask import Flask, render_template, Response

# Import our OLED inspection function
from inspection import analyze_brightness

from models import db, Inspection

# Import OpenCV
import cv2


# Create the Flask application
app = Flask(__name__)


# Configure the SQLite database.
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///oled_inspection.db"

# Connect SQLAlchemy to the Flask application.
db.init_app(app)

# Create database tables if they do not already exist.
with app.app_context():
    db.create_all()


# Open the default camera
camera = cv2.VideoCapture(0)
# Store the most recent camera frame.
latest_frame = None

def generate_frames():
    """
    Continuously capture frames from the camera
    and stream them to the web browser.
    """
    
    global latest_frame

    while True:

        # Capture one frame from the camera
        success, frame = camera.read()
        
        # Stop if the camera cannot provide a frame
        if not success:
            break

        # Save the latest frame for inspection.
        latest_frame = frame.copy()

        # Get the frame dimensions.
        height, width = frame.shape[:2]

        # Define a centered Region of Interest (ROI).
        x1 = int(width * 0.25)
        y1 = int(height * 0.25)
        x2 = int(width * 0.75)
        y2 = int(height * 0.75)

        # Extract the ROI from the original frame.
        roi = frame[y1:y2, x1:x2]

        # Store only the ROI for inspection.
        latest_frame = roi.copy()

        # Draw the ROI rectangle on the live video.
        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),
            2
        )

    
        # Convert the OpenCV frame to JPEG format
        success, buffer = cv2.imencode(".jpg", frame)

        if not success:
            continue

        # Convert the JPEG image into bytes
        frame_bytes = buffer.tobytes()

        # Send the frame to the browser
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + frame_bytes
            + b"\r\n"
        )


@app.route("/")
def index():
    """
    Display the main OLED inspection page.
    """
    return render_template("index.html")


@app.route("/video_feed")
def video_feed():
    """
    Stream the live camera feed to the browser.
    """
    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/inspect")
def inspect():
    """
    Analyze the latest camera frame
    and save the result to the database.
    """

    # Check if a camera frame is available.
    if latest_frame is None:
        return {
            "error": "No camera frame is currently available."
        }

    # Analyze the current ROI.
    results = analyze_brightness(latest_frame)

    # Create an Inspection database object.
    inspection = Inspection(
        mean_brightness=results["mean_brightness"],
        standard_deviation=results["standard_deviation"],
        min_brightness=results["min_brightness"],
        max_brightness=results["max_brightness"],
        uniformity_score=results["uniformity_score"],
        inspection_status=results["inspection_status"]
    )

    # Add the object to the database session.
    db.session.add(inspection)

    # Save it permanently to the database.
    db.session.commit()

    # Flask automatically converts this dictionary to JSON.
    return results
    

@app.route("/history")
def history():
    """
    Return all saved inspection records.
    """

    # Read all inspection records from the database.
    inspections = Inspection.query.all()

    # Convert Inspection objects into dictionaries.
    history_data = []

    for inspection in inspections:
        history_data.append({
            "id": inspection.id,
            "mean_brightness": inspection.mean_brightness,
            "standard_deviation": inspection.standard_deviation,
            "min_brightness": inspection.min_brightness,
            "max_brightness": inspection.max_brightness,
            "uniformity_score": inspection.uniformity_score,
            "inspection_status": inspection.inspection_status
        })

    return history_data

if __name__ == "__main__":
    app.run(debug=True)