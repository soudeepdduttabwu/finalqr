import os
import cv2
import pandas as pd
import logging
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS


app = Flask(__name__)
CORS(app)  

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


google_sheet_url = 'https://docs.google.com/spreadsheets/d/1EK721MaoRZw_qJoop9nA6iIOXoYwDWK_/export?format=csv'     


def match_qr_data(data):
    logging.info("Matching QR code data...")
    try:
        
        sheet_data = pd.read_csv(google_sheet_url)

        logging.info("Data fetched successfully from Google Sheet.")
        
       
        user_row = sheet_data[sheet_data['qr_data'] == data]
        
       
        if not user_row.empty:
            logging.info("Match found.")
            return user_row.iloc[0]['name'] 
        else:
            logging.warning("No match found in the database.")
            return None
    except Exception as e:
        logging.error(f"Error: {e}")
        return None


def read_qr_from_image(image_path):
    logging.info(f"Reading QR code from image: {image_path}")
    
    detector = cv2.QRCodeDetector()
    img = cv2.imread(image_path)
    if img is None:
        logging.error("Error: Unable to load the image. Please check the file path.")
        return "Error: Unable to load the image. Please check the file path."

    data, bbox, _ = detector.detectAndDecode(img)
    if data:
        logging.info(f"QR code data: {data}")
        user = match_qr_data(data)
        if user:
            logging.info(f"User '{user}' found.")
            return f"User '{user}' is present!"
        else:
            logging.warning("No match found for the QR code in the database.")
            return "No match found in the database."
    else:
        logging.warning("No QR Code detected in the image.")
        return "No QR Code detected in the image."


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'qr_image' not in request.files:
        logging.warning("No file uploaded.")
        return jsonify({'message': 'No file uploaded'}), 400

    file = request.files['qr_image']
    if file.filename == '':
        logging.warning("No file selected.")
        return jsonify({'message': 'No file selected'}), 400

    logging.info(f"File selected: {file.filename}")

 
    file_path = os.path.join('uploads', file.filename)
    file.save(file_path)
    logging.info(f"File saved at {file_path}.")

   
    result = read_qr_from_image(file_path)
    logging.info(f"Processing result: {result}")

    os.remove(file_path)
    logging.info(f"File {file_path} removed after processing.")

    return jsonify({'result': result})

if __name__ == "__main__":

    os.makedirs('uploads', exist_ok=True)
    logging.info("Starting Flask app...")

 
    app.run(host='0.0.0.0', debug=True)
