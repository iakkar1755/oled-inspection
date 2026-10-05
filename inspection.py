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