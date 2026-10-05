# Import the OpenCV library
import cv2


# Open the default camera.
# Camera index 0 usually represents the built-in or primary webcam.
camera = cv2.VideoCapture(0)


# Check whether OpenCV successfully opened the camera.
if not camera.isOpened():
    print("ERROR: Could not open the camera.")
    exit()


print("Camera connected successfully.")
print("Press Q to close the camera window.")


# Continuously capture frames from the camera.
while True:

    # Read one frame from the camera.
    success, frame = camera.read()

    # Stop if OpenCV cannot capture a frame.
    if not success:
        print("ERROR: Could not read a frame.")
        break

    # Display the current camera frame.
    cv2.imshow("OLED Inspection Camera", frame)

    # Wait 1 millisecond for a keyboard input.
    # Press Q to stop the camera stream.
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


# Release the camera so other applications can use it.
camera.release()

# Close all OpenCV windows.
cv2.destroyAllWindows()

print("Camera disconnected.")