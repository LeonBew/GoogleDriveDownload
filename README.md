## Download files from Google Drive with the free [Google Cloud Console](https://cloud.google.com/)

Use this script to efficiently download from your own Google Drive or shared folders. It uses the Google Cloud Console, for which no trial or additional account is needed. Key additions:

1. Download error recovery! The script can recover from errors — either on your end or Google's. The script saves its progress into chunks and retries every 5s indefinitely. This is key for large downloads which would otherwise be interrupted. Just leave it running overnight.
2. No file size limits! (that I've found)

--- 

- Download chunk size can be modified to account for many small files vs. few/one large file(s).
- Folders are supported and are downloaded recursively.
- Google Apps files (Google docs/sheets/slides) are supported and will be saved as `.pdf`.
- Download speeds through the API are faster than through a browser.
- The API has a 1TB download limit / month.
- Progress % and estimated download time included.

# 1: Set Up a Google Cloud Console Project
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project.
3. Go to "APIs and Services", then under the "Enabled APIs and Services" tab (in the sidebar), click "Enable APIs and Services" above the graphs. Search for `Google Drive` and enable the Google Drive API.
4. Under  the "Credentials" tab (in the sidebar), create a OAuth client ID with the application type `Desktop App`. Download the JSON after it is created and place it in the folder where the script is.
5. Under  the "OAuth consent screen" tab (in the sidebar), set up as basic of a consent screen as you want, add your Gmail as a test user. *No* need to Publish App. Note that no other users will have access to your cloud console project unless you add their Gmail to the testers list.

# 2: Initial setup
1. Have Python installed. Run `pip install --upgrade google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client httplib2 oauth2client`.
2. Download the script and enter the config variables into the top of the script. The `CLIENT_SECRET_FILE` is the .json downloaded before. The `ROOT_ID` is the ID contained in the link of the file/folder you want to download. Examples: `https://drive.google.com/drive/folders/exampleidhere`, `https://drive.google.com/file/d/1exampleidhere/view`.
3. When you first run the script, it will open the OAuth consent screen previously created in 1. Click through it. Whether your project has been tested by Google is irrelevant, you can just click continue. The authentication window will not pop up again and your access will be saved in `token.json`.
4. Depending on the size of the file(s) you want to download, increase or decrease the chunk size in the script. Fewer chunks will mean less api calls and faster downloads for large files. For 100GB+ files, a 500 MB chunk size works well.


From now on, you can change the `ROOT_ID` and `DEST_FILENAME` to any other files/folders too.
