import requests

# Numerical calculations
import numpy as np

# Computer vision
import cv2


def analyze_brightness(frame):
    """
    Analyze the brightness and uniformity of an image.

    Parameters:
        frame: OpenCV BGR image

    Returns:
        Dictionary containing brightness statistics.
    """

    # Convert the color image to grayscale.
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Calculate the average pixel brightness.
    mean_brightness = np.mean(gray)

    # Calculate brightness variation.
    standard_deviation = np.std(gray)

    # Find minimum and maximum brightness values.
    min_brightness = np.min(gray)
    max_brightness = np.max(gray)

    # Simple experimental uniformity score.
    # Lower standard deviation means the image is more uniform.
    uniformity_score = 100 - min(standard_deviation, 100)

    # Define temporary inspection thresholds.
    min_mean_brightness = 80
    max_mean_brightness = 220
    min_uniformity_score = 50

    # Determine whether the image passes the inspection.
    if (
    min_mean_brightness <= mean_brightness <= max_mean_brightness
    and uniformity_score >= min_uniformity_score
    ):
        inspection_status = "PASS"
    else:
        inspection_status = "FAIL"

    return {
    "mean_brightness": round(float(mean_brightness), 2),
    "standard_deviation": round(float(standard_deviation), 2),
    "min_brightness": int(min_brightness),
    "max_brightness": int(max_brightness),
    "uniformity_score": round(float(uniformity_score), 2),
    "inspection_status": inspection_status
    }


    # Google Cloud FastAPI endpoint through the SSH tunnel
CLOUD_API_URL = "http://localhost:8000/api/inspections"


def send_inspection_to_cloud(result):
    """
    Send a completed OLED inspection result to Google Cloud.
    """
    try:
        response = requests.post(
            CLOUD_API_URL,
            json=result,
            timeout=10
        )
        response.raise_for_status()

        saved_inspection = response.json()
        print(
            f"Cloud inspection saved: "
            f"ID={saved_inspection['id']}, "
            f"Status={saved_inspection['inspection_status']}"
        )
        return saved_inspection

    except requests.RequestException as error:
        print(f"Cloud upload failed: {error}")
        return None

def upload_inspection_image(inspection_id, frame):
    image_url = (
        f"http://localhost:8000/api/inspections/"
        f"{inspection_id}/image"
    )

    success, encoded_image = cv2.imencode(
        ".jpg",
        frame,
        [cv2.IMWRITE_JPEG_QUALITY, 85]
    )

    if not success:
        print("JPEG encoding failed")
        return False

    try:
        response = requests.post(
            image_url,
            files={
                "image": (
                    "capture.jpg",
                    encoded_image.tobytes(),
                    "image/jpeg"
                )
            },
            timeout=15
        )

        response.raise_for_status()
        print(f"Image uploaded: Inspection ID={inspection_id}")
        return True

    except requests.RequestException as error:
        print(f"Image upload failed: {error}")
        return False