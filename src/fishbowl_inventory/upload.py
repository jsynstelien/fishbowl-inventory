import os
import datetime
import glob
from typing import Optional
from firebase_admin import firestore, storage, credentials, initialize_app
from google.cloud.storage.bucket import Bucket
from google.cloud.storage.blob import Blob
import json
import base64

# ----------------------
# Firebase Initialization
# ----------------------
# Decode base64-encoded production credentials from env variable
firebase_prod_base64 = os.getenv("FIREBASE_PRODUCTION_CREDENTIALS_BASE64")
firebase_dev_base64 = os.getenv("FIREBASE_DEVELOPMENT_CREDENTIALS_BASE64")

prod_cred = credentials.Certificate(json.loads(base64.b64decode(firebase_prod_base64).decode("utf-8")))
dev_cred = credentials.Certificate(json.loads(base64.b64decode(firebase_dev_base64).decode("utf-8")))


firebase_project = initialize_app(
    credential=credentials
)

client: firestore.firestore.Client = firestore.client()
bucket: Bucket = storage.bucket()


def upload_csv_to_firebase(local_csv_path: str, cloud_file_path: str) -> Optional[str]:
    """
    Uploads a CSV file to Firebase Storage under a date-stamped folder.

    :param local_csv_path: Path to the local CSV file.
    :param algorithm: Folder name under 'Algorithms' in Firebase.
    :return: The cloud file path if uploaded successfully.
    """
    if not os.path.isfile(local_csv_path):
        print(f"❌ File not found: {local_csv_path}")
        return None

    try:
        blob: Blob = bucket.blob(cloud_path)
        blob.upload_from_filename(local_csv_path)
        print(f"✅ Uploaded {filename} to {cloud_path}")
        return cloud_path
    except Exception as e:
        print(f"❌ Failed to upload {filename}: {e}")
        return None


def main():
    """
    Main entry point for uploading today's fishbowl CSV file(s).
    Adjust glob pattern as needed.
    """
    directory = "./reports"  # Change this to your local output directory
    file_name = "daily_report"

    # Get the current date
    current_date = datetime.datetime.now()
    year = current_date.strftime("%Y")
    month = current_date.strftime("%m")
    day = current_date.strftime("%d")
    
    # Construct the cloud path with year, month, day, and relative path of the file
    cloud_file_path = f"Logs/{year}/{month}/{day}/{file_name}"
            
    # Example: upload all .csv files in the folder
    csv_files = glob.glob(os.path.join(directory, "*.csv"))

    if not csv_files:
        print("⚠️ No CSV files found for upload.")
        return

    for file_path in csv_files:
        upload_csv_to_firebase(local_csv_path=f"{directory}/{file_name}", cloud_file_path=cloud_file_path)


if __name__ == "__main__":
    main()