Move a file from Google Drive to Telegram

# Build
```
docker build -t telecosas .
```

# Usage
First you have to [create a GCP project](https://console.cloud.google.com/projectcreate), then [enable the Google Drive API for your project](https://console.cloud.google.com/apis/library/drive.googleapis.com), and then get a [Google OAuth2 API Client](https://console.cloud.google.com/apis/credentials). On this last step you get a `credentials.json` file, save it.

Once you have that done, you have to [create a Telegram app API key](https://my.telegram.org/apps). Copy your _App api_id_ and your _App api_hash_ and save them too.

Now create a directory and copy there your `credentials.json`. Create a file with name `tg_app_credentials.py` and write there the following:

```
tg_session = 'telecosas'  # You can write whatever here
tg_api_id = Your App api_id
tg_api_hash = 'Your App api_hash'  # You have to use quotes for this one
```


Then run all this with (in the line with ###### you have to change the part between -v and : to your personal config path):

```
docker run -it --rm \
    -v path/to/your/config/directory:/app/config \  ######
    victor141516/telecosas \
    python gd2tg.py [gdrive file ID or URL]
```
