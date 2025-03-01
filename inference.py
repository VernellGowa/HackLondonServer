#!/usr/bin/env python3
import sys
from inference_sdk import InferenceHTTPClient
import string

def group_predictions_by_row(predictions, row_tolerance=10):
    """
    Groups predictions into rows by comparing their y-coordinates.
    Any detections within row_tolerance pixels are assumed to be on the same row.
    """
    # First, sort by y-coordinate
    predictions = sorted(predictions, key=lambda p: p['y'])
    rows = []
    current_row = []
    current_y = None

    for pred in predictions:
        if current_y is None:
            current_row.append(pred)
            current_y = pred['y']
        elif abs(pred['y'] - current_y) <= row_tolerance:
            current_row.append(pred)
        else:
            rows.append(current_row)
            current_row = [pred]
            current_y = pred['y']
    if current_row:
        rows.append(current_row)
    return rows

def sort_row_by_x(row):
    """Sorts a row of predictions by their x-coordinate (left-to-right)."""
    return sorted(row, key=lambda p: p['x'])

def get_detected_text(image_path):
    """
    Runs inference on the given image and returns the detected Braille text.
    """
    client = InferenceHTTPClient(api_url="https://detect.roboflow.com",
                                 api_key="0WnL5kEsSRdVu6TUhf6A")
    result = client.infer(image_path, model_id="braille-detection/2")
    
    if 'predictions' not in result:
        print("No predictions found in the result.")
        sys.exit(1)
    
    predictions = result['predictions']
    # Group detections into rows
    rows = group_predictions_by_row(predictions, row_tolerance=10)
    
    # Process each row: sort by x-coordinate and extract the predicted letter
    text_rows = []
    for row in rows:
        sorted_row = sort_row_by_x(row)
        row_text = ''.join(pred.get('class', '') for pred in sorted_row)
        text_rows.append(row_text)
    
    # Combine rows into final text (separated by newline)
    final_text = "\n".join(text_rows)
    print("Detected Text:")
    print(final_text)
    
    # Optional: Check if the full alphabet is present
    all_letters = ''.join(final_text.split())
    expected_alphabet = set(string.ascii_uppercase)
    if expected_alphabet.issubset(set(all_letters)):
        print("\nThis image appears to contain the full Braille alphabet!")
    else:
        print("\nWarning: The detected text does not appear to cover the full alphabet.")
    
    return final_text

# When running this file directly, use command-line arguments.
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python inference.py <path_to_image>")
    else:
        get_detected_text(sys.argv[1])
