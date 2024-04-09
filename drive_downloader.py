# import io
import pickle
import os.path
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload 
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

'''Configuration'''
# ID of the folder to be downloaded.
# ID can be obtained from the URL of the folder
FOLDER_ID = '1J57T0bbKJiaeqRsizEZMy88qfor0vShL'  # an example folder

# If modifying these scopes, delete the file token.pickle.
# SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def authenticate():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def download_all_files_in_folder_recursive_dfs(service, folder_id, folder_name):
    """Download all files in the specified folder in Google Drive."""
    page_token = None
    while True:
        # Call the Drive v3 API
        results = service.files().list(
                q=f"'{folder_id}' in parents",
                pageSize=10, fields="nextPageToken, files(id, name, mimeType)",
                pageToken=page_token).execute()
        items = results.get('files', [])

        if not items:
            print('No files found.')
        else:
            for item in items:
                # print(u'{0} ({1})'.format(item['name'], item['id']))
                # check if the file is a folder
                if(item['mimeType'] == 'application/vnd.google-apps.folder'):
                    print("Folder found: ", item['name'])
                    download_all_files_in_folder_recursive_dfs(service, item['id'], folder_name + '/' + item['name'])
                else:
                    print("File found: ", item['name'])
                    file_id = item['id']
                    # download the folder
                    request = service.files().get_media(fileId=file_id)

                    # create a files and folders as per the name: folder_name + '/' + item['name']
                    if not os.path.exists(folder_name):
                        os.makedirs(folder_name)

                    # keep only alphanumeric characters in the file name\
                    item['name'] = ''.join(e for e in item['name'] if e.isalnum() or e=='.').rstrip()
                    
                    with open(folder_name + '/' + item['name'], 'wb') as fh:
                        downloader = MediaIoBaseDownload(fh, request)
                        done = False
                        while done is False:
                            status, done = downloader.next_chunk()
                            print("Download %d%%." % int(status.progress() * 100))
                        


                # if the file is a folder, download its contents
                # if item['mimeType'] == 'application/vnd.google-apps.folder':
                #     download_all_files_in_folder_recursive_dfs(service, item['id'], folder_name + '/' + item['name'])

        page_token = results.get('nextPageToken', None)
        if page_token is None:
            break

def main():
    """Download all files in the specified folder in Google Drive."""
    creds = authenticate()

    service = build('drive', 'v3', credentials=creds)

    destination_folder = 'ARP'
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    
    with open('linkt.txt', 'r') as f:
        for line in f:
            folder_id = line.split('/')[-1].strip()
            # get the name of the folder
            try:
                request = service.files().get(fileId=folder_id)
                folder_name = request.execute()['name']
                print("Downloading folder: ", folder_name)
                download_all_files_in_folder_recursive_dfs(service, folder_id, destination_folder + '/' + folder_name)
            except:
                print("Folder not found")

if __name__ == '__main__':
    main()