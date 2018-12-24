from apiclient import errors
from apiclient.http import MediaIoBaseDownload
from googleapiclient.discovery import build
from googleapiclient import errors
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from httplib2 import Http
import json
from oauth2client import file, client, tools
import os
import pickle
import re
import sys

ID_REGEX = re.compile('^([a-zA-Z0-9-_]{33}|[a-zA-Z0-9-_]{28})$')
URL_REGEX = re.compile('^https:\/\/drive.google.com\/file\/d\/([a-zA-Z0-9-_]{33}|[a-zA-Z0-9-_]{28})')


class GD2TGException(ValueError):
    pass

def fetch_credentials():
    SCOPES = [
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/drive.appdata',
        'https://www.googleapis.com/auth/drive.apps.readonly',
        'https://www.googleapis.com/auth/drive.photos.readonly'
    ]

    if not os.path.exists('config/credentials.dat'):
        flow = InstalledAppFlow.from_client_secrets_file('config/credentials.json', SCOPES)
        flow.redirect_uri = 'http://localhost:8080/'
        print(flow.authorization_url()[0])
        code = input('Enter the authorization code: ')
        flow.fetch_token(code=code)
        credentials = flow.credentials

        with open('config/credentials.dat', 'wb') as credentials_dat:
            pickle.dump(credentials, credentials_dat)
    else:
        with open('config/credentials.dat', 'rb') as credentials_dat:
            credentials = pickle.load(credentials_dat)

    return credentials


def copy_copy_get_link(original_file_id):
    service = build('drive', 'v2', credentials=fetch_credentials())

    try:
        original_shared = service.files().get(fileId=original_file_id).execute()
    except errors.HttpError as e:
        if 'File not found' in e.content.decode('utf-8'):
            raise GD2TGException('File with ID ' + original_file_id + ' does not exists')
        else:
            raise e

    try:
        shared_copy = service.files().copy(fileId=original_file_id, body={
            'title': '_',
            'parents': [{'id': 'root'}]}).execute()
    except errors.HttpError as e:
        if 'This file cannot be copied' in e.content.decode('utf-8'):
            raise GD2TGException('File with ID ' + original_file_id + ' cannot be copied')
        else:
            raise e

    shared_copy_copy = service.files().copy(fileId=shared_copy['id'], body={
        'title': original_shared['title'],
        'parents': [{'id': 'root'}]}).execute()

    download_url = 'https://drive.google.com/file/d/{}/view'.format(shared_copy_copy['id'])

    service.files().delete(fileId=shared_copy['id']).execute()

    return download_url


def get_id(url_or_id):
    id_regex_result = ID_REGEX.match(url_or_id)
    url_regex_result = URL_REGEX.match(url_or_id)
    if id_regex_result:
        return id_regex_result.group(1)
    elif url_regex_result:
        return url_regex_result.group(1)
    else:
        raise ValueError(url_or_id + ' is not a valid URL nor ID')

def download_file(file_id):
    service = build('drive', 'v3', credentials=fetch_credentials())
    name = service.files().get(fileId=file_id).execute()['name']
    request = service.files().get_media(fileId=file_id)
    if not os.path.isdir('tmp'):
        os.mkdir('tmp')
    fh = open('tmp/' + name, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download " + name + " %d%%." % int(status.progress() * 100), end='\r')

    return name

def delete_file(file_id):
    service = build('drive', 'v2', credentials=fetch_credentials())
    return service.files().delete(fileId=file_id).execute()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        ids = []
        for each in sys.argv[1:]:
            ids.append(get_id(each))
        ids = list(set(ids))
        for each in ids:
            try:
                print(copy_copy_get_link(each))
            except GD2TGException as e:
                print(e)
    else:
        print('Usage: python copy_gdrive.py [List of Drive URLs/IDs]')
        quit()
