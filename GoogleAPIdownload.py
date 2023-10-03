import os
import time
import io
import httplib2
import ssl
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# CONFIGURATION

CLIENT_SECRET_FILE = 'example.apps.googleusercontent.com.json'  # --- ENTER SECRETS FILE NAME HERE ---
ROOT_ID = 'rootIDfromURLhere'  # --- ENTER FILE/FOLDER ROOT ID HERE ---
DEST_FILENAME = 'example.zip'  # --- ENTER FILE NAME HERE (ignored if root_id is a folder) ---

CHUNK_SIZE = 5 * 1024 * 1024  # 50 MB -- increase or decrease depending on typical file sizes

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCOPES = ['https://www.googleapis.com/auth/drive']
TOKEN_FILE = 'token.json'

# CONFIGURATION


def initialize_drive_api():
    try:
        with open(TOKEN_FILE, 'r') as token:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    except FileNotFoundError:
        creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return build('drive', 'v3', credentials=creds)


def download_file(service, file_id, dest_filename, chunk_size):
    file_metadata = service.files().get(fileId=file_id, fields='size,mimeType').execute()
    
    mimeType = file_metadata.get('mimeType', '')
    
    export_format = {
        'application/vnd.google-apps.document': 'application/pdf',
        'application/vnd.google-apps.spreadsheet': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.google-apps.presentation': 'application/pdf'
    }
    
    if 'google-apps' in mimeType:
        request = service.files().export_media(fileId=file_id, mimeType=export_format.get(mimeType, 'application/pdf'))
        print("Starting download of a Google Editor file.")
    else:
        request = service.files().get_media(fileId=file_id)
        total_file_size = int(file_metadata.get('size', '0'))  # Default to '0' if 'size' is not available
        total_chunks_needed = -(-total_file_size // chunk_size)
        print(f"Starting download with chunk size: {chunk_size / (1024 * 1024)} MB. {total_chunks_needed} chunks will be downloaded.")
    
    fh = io.FileIO(dest_filename, 'wb')
    downloader = MediaIoBaseDownload(fh, request, chunksize=chunk_size)
    
    total_time = 0
    chunks_downloaded = 0
    done = False
    retry_count = 0
    
    while not done:
        try:
            start_time = time.time()
            status, done = downloader.next_chunk()
            end_time = time.time()
            elapsed_time = end_time - start_time

            total_time += elapsed_time
            chunks_downloaded += 1
            avg_time = total_time / chunks_downloaded
            time_difference = elapsed_time - avg_time

            print(f"Chunk {chunks_downloaded}. Took {elapsed_time:.2f}s, {time_difference:.2f}s from average ({(chunk_size / (1024 * 1024)) / elapsed_time:.2f} MB/s)")

            retry_count = 0
        
        except (httplib2.HttpLib2Error, IOError, ssl.SSLEOFError) as e:
            print(f"An error occurred: {e}")
            retry_count += 1
            print(f"Retrying in 5 seconds... (Attempt: {retry_count})")
            time.sleep(5)
        except Exception as e:  # Catch-all for other exceptions
            print(f"An unexpected error occurred: {e}")
            retry_count += 1
            print(f"Retrying in 5 seconds... (Attempt: {retry_count})")
            time.sleep(5)



def list_folder(service, folder_id):
    query = f"'{folder_id}' in parents"
    results = service.files().list(q=query).execute()
    return results.get('files', [])


def download_folder(service, folder_id, local_folder_path):
    os.makedirs(local_folder_path, exist_ok=True)
    items = list_folder(service, folder_id)
    
    for item in items:
        item_name = item['name']
        item_id = item['id']
        item_type = item.get('mimeType')
        
        local_path = os.path.join(local_folder_path, item_name)
        
        if item_type == 'application/vnd.google-apps.folder':
            download_folder(service, item_id, local_path)
        else:
            if 'google-apps' in item_type:
                local_path += '.pdf'
            download_file(service, item_id, local_path, CHUNK_SIZE)
     
     
def main():
    os.chdir(SCRIPT_DIR)
    print("Initializing Google Drive API...")
    service = initialize_drive_api()
    print("Drive API client built successfully.")
    
    if not ROOT_ID or not DEST_FILENAME or not CLIENT_SECRET_FILE:
        raise Exception("Configuration variables cannot be empty!")
  
    item_metadata = service.files().get(fileId=ROOT_ID, fields='mimeType,name').execute()
    item_type = item_metadata.get('mimeType')
    item_name = item_metadata.get('name')
    
    if item_type == 'application/vnd.google-apps.folder':
        print(f"Found a folder with name {item_name}. Starting folder download.")
        download_folder(service, ROOT_ID, item_name)
    else:
        print(f"Found a file with name {item_name}. Starting file download.")
        download_file(service, ROOT_ID, DEST_FILENAME, CHUNK_SIZE)
        
    input("Done! Enter to exit")

if __name__ == '__main__':
    main()
