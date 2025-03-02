#!/usr/bin/env python3
import sys
from ultralytics import YOLO
import numpy as np

def annotate_image(image_path):
    """
    Runs inference on the given image and returns the detected Braille text.
    """
    file_name = image_path.split("/")[-1]

    # Load trained model
    model = YOLO("runs/detect/train4/weights/best.pt")
    results = model(image_path)

    for result in results:
        result.save(filename=f'braille/{file_name}')

def get_detected_text(image_path):
    """
    Runs inference on the given image and returns the detected Braille text.
    """
    file_name = image_path.split("/")[-1]

    # Load trained model
    model = YOLO("runs/detect/train4/weights/best.pt")
    results = model(image_path)
    # Load class names from the model
    class_names = model.names  # Dictionary mapping class indices to names

    detections = []

    for result in results:
        for box in result.boxes:
            class_id = int(box.cls)  # Get class ID
            label = class_names[class_id]  # Get class name
            confidence = box.conf.item()  # Confidence score
            x_min = box.xyxy[0][0].item()  # Left X coordinate
            y_min = box.xyxy[0][1].item()  # Top Y coordinate

            detections.append((x_min, y_min, label, confidence))

        result.save(filename=f'braille/{file_name}')

    # Convert detections to NumPy array for sorting
    detections = np.array(detections, dtype=object)

    # Sort by Y-coordinate first
    detections = detections[detections[:, 1].argsort()]

    # Group by rows using a Y threshold (to cluster letters in the same row)
    y_threshold = 20  # Adjust if needed
    rows = []
    current_row = [detections[0]]

    for i in range(1, len(detections)):
        if abs(detections[i, 1] - current_row[-1][1]) < y_threshold:
            current_row.append(detections[i])
        else:
            rows.append(sorted(current_row, key=lambda x: x[0]))  # Sort row by X-coordinates
            current_row = [detections[i]]

    # Append last row
    if current_row:
        rows.append(sorted(current_row, key=lambda x: x[0]))

    # Flatten sorted rows into the final ordered text
    ordered_text = "".join([char[2] for row in rows for char in row])
    return ordered_text

# When running this file directly, use command-line arguments.
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python inference.py <path_to_image>")
    else:
        get_detected_text(sys.argv[1])
