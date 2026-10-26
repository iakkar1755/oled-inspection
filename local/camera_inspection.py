
import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk

from inspection import (
    analyze_brightness,
    send_inspection_to_cloud,
    upload_inspection_image
)

CAMERA_INDEX = 0

camera = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)

if not camera.isOpened():
    raise RuntimeError("Cannot open camera")

root = tk.Tk()
root.title("OLED Manual Inspection")
root.geometry("850x700")

video_label = ttk.Label(root)
video_label.pack(pady=10)

status_label = ttk.Label(
    root,
    text="Ready for inspection",
    font=("Arial", 16)
)
status_label.pack(pady=10)

latest_frame = None


def update_camera():
    global latest_frame

    success, frame = camera.read()

    if success:
        latest_frame = frame.copy()

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(rgb)
        image.thumbnail((800, 500))

        photo = ImageTk.PhotoImage(image=image)
        video_label.configure(image=photo)
        video_label.image = photo

    root.after(30, update_camera)


def inspect_frame():
    if latest_frame is None:
        status_label.configure(text="No camera frame available")
        return

    frame = latest_frame.copy()

    # Analyze camera image
    result = analyze_brightness(frame)

    # Save inspection metrics to SQLite through FastAPI
    saved = send_inspection_to_cloud(result)

    if not saved:
        status_label.configure(text="Cloud inspection save failed")
        return

    inspection_id = saved["id"]

    # Upload JPEG using the same inspection ID
    image_uploaded = upload_inspection_image(
        inspection_id,
        frame
    )

    if image_uploaded:
        status_label.configure(
            text=f"Inspection {inspection_id}: Image uploaded"
        )
    else:
        status_label.configure(
            text=f"Inspection {inspection_id}: Image upload failed"
        )


inspect_button = ttk.Button(
    root,
    text="INSPECT",
    command=inspect_frame
)
inspect_button.pack(pady=15)


def on_close():
    camera.release()
    root.destroy()


root.protocol("WM_DELETE_WINDOW", on_close)

update_camera()
root.mainloop()
