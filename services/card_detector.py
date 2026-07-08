from io import BytesIO

import cv2
import numpy as np
from PIL import Image


def uploaded_file_to_cv2(uploaded_file):
    """
    Converts a Streamlit camera image into an OpenCV image.
    """
    bytes_data = uploaded_file.getvalue()
    image_array = np.frombuffer(bytes_data, np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    return image


def order_points(points):
    """
    Orders the four card corners as:
    top-left, top-right, bottom-right, bottom-left.
    """
    rect = np.zeros((4, 2), dtype="float32")

    s = points.sum(axis=1)
    rect[0] = points[np.argmin(s)]
    rect[2] = points[np.argmax(s)]

    diff = np.diff(points, axis=1)
    rect[1] = points[np.argmin(diff)]
    rect[3] = points[np.argmax(diff)]

    return rect


def four_point_transform(image, points):
    """
    Crops and straightens the detected card.
    """
    rect = order_points(points)
    top_left, top_right, bottom_right, bottom_left = rect

    width_a = np.linalg.norm(bottom_right - bottom_left)
    width_b = np.linalg.norm(top_right - top_left)
    max_width = int(max(width_a, width_b))

    height_a = np.linalg.norm(top_right - bottom_right)
    height_b = np.linalg.norm(top_left - bottom_left)
    max_height = int(max(height_a, height_b))

    destination = np.array([
        [0, 0],
        [max_width - 1, 0],
        [max_width - 1, max_height - 1],
        [0, max_height - 1]
    ], dtype="float32")

    matrix = cv2.getPerspectiveTransform(rect, destination)
    warped = cv2.warpPerspective(image, matrix, (max_width, max_height))

    return warped


def cv2_to_pil(image):
    """
    Converts OpenCV BGR image to PIL RGB image for Streamlit display.
    """
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb_image)


def cv2_to_bytes(image):
    """
    Converts OpenCV image to PNG bytes.
    """
    pil_image = cv2_to_pil(image)
    output = BytesIO()
    pil_image.save(output, format="PNG")
    output.seek(0)
    return output


def analyze_card_image(uploaded_file):
    """
    Detects whether a trading card is visible, centered, and clear enough.
    Returns an annotated image, cropped card image, and quality information.
    """
    image = uploaded_file_to_cv2(uploaded_file)

    if image is None:
        return {
            "card_found": False,
            "ready": False,
            "message": "Image could not be read.",
            "annotated_image": None,
            "cropped_image": None,
            "center_score": 0,
            "sharpness": 0,
            "brightness": 0
        }

    original = image.copy()
    height, width = image.shape[:2]

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    edges = cv2.Canny(blurred, 50, 150)

    contours, _ = cv2.findContours(
        edges,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    card_contour = None
    largest_area = 0

    for contour in contours:
        area = cv2.contourArea(contour)

        if area < 5000:
            continue

        perimeter = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)

        if len(approx) == 4 and area > largest_area:
            card_contour = approx
            largest_area = area

    annotated = original.copy()

    if card_contour is None:
        return {
            "card_found": False,
            "ready": False,
            "message": "No card shape found. Place the card on a plain background and try again.",
            "annotated_image": cv2_to_bytes(annotated),
            "cropped_image": None,
            "center_score": 0,
            "sharpness": 0,
            "brightness": 0
        }

    points = card_contour.reshape(4, 2)
    cropped = four_point_transform(original, points)

    cv2.drawContours(annotated, [card_contour], -1, (0, 255, 0), 4)

    x, y, w, h = cv2.boundingRect(card_contour)

    card_center_x = x + w / 2
    card_center_y = y + h / 2

    image_center_x = width / 2
    image_center_y = height / 2

    offset_x = abs(card_center_x - image_center_x) / width
    offset_y = abs(card_center_y - image_center_y) / height

    center_score = max(0, 100 - int((offset_x + offset_y) * 200))

    card_area_ratio = largest_area / (width * height)

    sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
    brightness = np.mean(gray)

    is_centered = center_score >= 80
    is_large_enough = card_area_ratio >= 0.18
    is_not_too_close = card_area_ratio <= 0.85
    is_clear = sharpness >= 80
    is_bright = 50 <= brightness <= 220

    ready = (
        is_centered
        and is_large_enough
        and is_not_too_close
        and is_clear
        and is_bright
    )

    if ready:
        message = "Card is centered, clear, and ready for AI identification."
    elif not is_centered:
        message = "Move the card closer to the center of the camera."
    elif not is_large_enough:
        message = "Move the camera closer to the card."
    elif not is_not_too_close:
        message = "Move the camera back slightly."
    elif not is_clear:
        message = "Image is blurry. Hold the phone steady and try again."
    elif not is_bright:
        message = "Lighting needs improvement. Avoid glare and shadows."
    else:
        message = "Try again with the card centered on a plain background."

    return {
        "card_found": True,
        "ready": ready,
        "message": message,
        "annotated_image": cv2_to_bytes(annotated),
        "cropped_image": cv2_to_bytes(cropped),
        "center_score": center_score,
        "sharpness": int(sharpness),
        "brightness": int(brightness)
    }
