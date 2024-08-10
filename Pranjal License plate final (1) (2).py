#!/usr/bin/env python
# coding: utf-8

# In[4]:


pytesseract.pytesseract.tesseract_cmd = 'C:\Program Files\Tesseract-OCR\\tesseract'


# In[6]:


import tkinter as tk
from tkinter import filedialog, Text, ttk
from PIL import Image, ImageTk
import cv2
import numpy as np
import pytesseract
import re


# License plate extraction function
def extract_license_plate(img_path):
    image = cv2.imread(img_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 50, 150)
    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
    plate_contour = None
    for contour in contours:
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
        if len(approx) == 4:
            plate_contour = approx
            break
    if plate_contour is not None:
        x, y, w, h = cv2.boundingRect(plate_contour)
        license_plate = image[y:y + h, x:x + w]
        return license_plate, license_plate
    else:
        return image, None


# Text recognition function
def recognize_text_from_plate(license_plate_img):
    gray_plate = cv2.cvtColor(license_plate_img, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray_plate, config='--psm 8')
    return text.strip()


# Dictionary to map state codes to state names
state_codes = {
    "AP": "Andhra Pradesh",
    "AR": "Arunachal Pradesh",
    "AS": "Assam",
    "BR": "Bihar",
    "CG": "Chhattisgarh",
    "GA": "Goa",
    "GJ": "Gujarat",
    "HR": "Haryana",
    "HP": "Himachal Pradesh",
    "JH": "Jharkhand",
    "KA": "Karnataka",
    "KL": "Kerala",
    "MP": "Madhya Pradesh",
    "MH": "Maharashtra",
    "MN": "Manipur",
    "ML": "Meghalaya",
    "MZ": "Mizoram",
    "NL": "Nagaland",
    "OR": "Odisha",
    "PB": "Punjab",
    "RJ": "Rajasthan",
    "SK": "Sikkim",
    "TN": "Tamil Nadu",
    "TS": "Telangana",
    "TR": "Tripura",
    "UP": "Uttar Pradesh",
    "UK": "Uttarakhand",
    "WB": "West Bengal",
    # Union Territories
    "AN": "Andaman and Nicobar Islands",
    "CH": "Chandigarh",
    "DN": "Dadra and Nagar Haveli",
    "DD": "Daman and Diu",
    "DL": "Delhi",
    "JK": "Jammu and Kashmir",
    "LA": "Ladakh",
    "LD": "Lakshadweep",
    "PY": "Puducherry"
}

def parse_license_plate(text):
    # Search for two consecutive alphabets (letters)
    match = re.search(r'([A-Za-z]{2})', text)

    if match:
        start_index = match.start()
        state_code = text[start_index:start_index + 2]

        # Check if there are at least 4 characters after the state code
        if len(text[start_index + 2:]) >= 4:
            district_code = text[start_index + 2:start_index + 4]
            vehicle_number = text[start_index + 4:]
            state = state_codes.get(state_code, "Unknown State")
            return f"State: {state}, District/RTO Code: {district_code}, Vehicle Number: {vehicle_number}"
        else:
            return "Invalid license plate format after state code"
    else:
        return "State code not found in license plate"


# GUI functions
def select_image():
    file_path = filedialog.askopenfilename()
    if file_path:
        image = Image.open(file_path)
        image.thumbnail((400, 400))
        photo = ImageTk.PhotoImage(image)
        for widget in image_frame.winfo_children():
            widget.destroy()
        label = tk.Label(image_frame, image=photo)
        label.image = photo
        label.pack(pady=20)
        select_image.image_path = file_path


def extract_and_recognize():
    if hasattr(select_image, 'image_path'):
        processed_image, license_plate = extract_license_plate(select_image.image_path)
        if license_plate is not None:
            license_text = recognize_text_from_plate(license_plate)
            recognized_text.set(license_text)
            plate_details.set(parse_license_plate(license_text))

            # Display the processed image
            image = Image.fromarray(cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB))
            image.thumbnail((400, 400))
            photo = ImageTk.PhotoImage(image)
            for widget in processed_image_frame.winfo_children():
                widget.destroy()
            label = tk.Label(processed_image_frame, image=photo)
            label.image = photo
            label.pack(pady=20)
        else:
            recognized_text.set("License plate not detected.")
            plate_details.set("")


# Main GUI
root = tk.Tk()
root.title("License Plate Recognition")
main_frame = ttk.Frame(root, padding="10")
main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

btn_select_image = ttk.Button(main_frame, text="Select Image", command=select_image)
btn_select_image.grid(row=0, column=0, pady=10, sticky=tk.W)

image_frame = ttk.Frame(main_frame)
image_frame.grid(row=1, column=0, pady=10)

# Frame for the processed image
processed_image_frame = ttk.Frame(main_frame)
processed_image_frame.grid(row=1, column=1, pady=10, padx=10)

btn_recognize = ttk.Button(main_frame, text="Extract & Recognize", command=extract_and_recognize)
btn_recognize.grid(row=2, column=0, pady=10)

recognized_text = tk.StringVar()
text_display = ttk.Entry(main_frame, textvariable=recognized_text, width=30, state="readonly")
text_display.grid(row=3, column=0, pady=10)

# Add a Text widget to display license plate details
plate_details = tk.StringVar()
details_display = ttk.Label(main_frame, textvariable=plate_details, wraplength=400)
details_display.grid(row=4, column=0, pady=10)

root.mainloop()


# In[ ]:




