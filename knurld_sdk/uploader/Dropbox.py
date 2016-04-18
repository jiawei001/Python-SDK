# -*- coding: utf-8 -*-
import contextlib
import datetime
import dropbox
from dropbox.exceptions import ApiError, HttpError
from dropbox.files import FileMetadata
import os
import time
import uuid

from knurld_sdk import app_globals as g

""" sample json configuration object:
{
    "DROPBOX": {
        "ACCESS_TOKEN": "eupdKs1bHloAAAAAAAAGVp8dVQcgP1y4q_UikyfwuZ0YhmWvtlAHFIv4b4s8kBQZ",
        "REMOTE_DIR": "knurld_sdk-voice-files",
        "FILE_NAME": "enrollment.wav"
        }
}
"""

# dbx_config is being read from the main config, which you can be overwritten by app-developers
dbx_config = g.config['DROPBOX']


def download(dbx, remote_file_path):
    """Download a file.
    Return the bytes of the file, or None if it doesn't exist.
    """
    while '//' in remote_file_path:
        remote_file_path = remote_file_path.replace('//', '/')
    with stopwatch('"download" file: %s' % str(remote_file_path)):
        try:
            md, res = dbx.files_download(remote_file_path)
        except (HttpError, ApiError) as err:
            print('*** HTTP/API error', err)
            return None
    data = res.content
    print(len(data), 'bytes; md:', md)
    return data


def upload(dbx, local_file_path, remote_file_path, overwrite=False):
    """Upload a file.
    Return the request response, or None in case of error.
    """
    while '//' in remote_file_path:
        remote_file_path = remote_file_path.replace('//', '/')
    mode = (dropbox.files.WriteMode.overwrite
            if overwrite
            else dropbox.files.WriteMode.add)
    mtime = os.path.getmtime(local_file_path)
    with open(local_file_path, 'rb+') as f:
        data = f.read()
        with stopwatch('"upload" %d bytes' % len(data)):
            try:
                res = dbx.files_upload(
                    data, remote_file_path, mode,
                    client_modified=datetime.datetime(*time.gmtime(mtime)[:6]),
                    mute=True)

            except (HttpError, ApiError) as err:
                print('*** Http/API error', err)
                return None
    print('uploaded as: ' + str(res.name.encode('utf8')))
    return res


def share(dbx, remote_file_path):
    """Share the file.
    Return the public url to shared file or None in case of error.
    """
    while '//' in remote_file_path:
        remote_file_path = remote_file_path.replace('//', '/')

    with stopwatch('"share" file: %s' % str(remote_file_path)):
        try:
            res = dbx.sharing_create_shared_link(remote_file_path)
            if share and res.url:
                # changing the url to the downloadable url with dl=1 param
                res.url = res.url.replace('dl=0', 'dl=1')
                return res.url
        except (HttpError, ApiError, TypeError) as err:
            print('*** Http/API error', err)

    return None


@contextlib.contextmanager
def stopwatch(message):
    """Context manager to print how long a block of code took."""
    t0 = time.time()
    try:
        yield
    finally:
        t1 = time.time()
        print('Total elapsed time for %s: %.3f' % (message, t1 - t0))


def get_dropbox_client():
    try:
        dbx = dropbox.Dropbox(dbx_config['ACCESS_TOKEN'])
        return dbx
    except ValueError as e:
        print('ACCESS_TOKEN not found error. ' + str(e))
    return None


def upload_and_share(local_file_path):
    """ example of how you can upload and share a local file in one go
    :param local_file_path: full local path of the file to be uploaded
    """

    dbx = get_dropbox_client()
    remote_path = dbx_config['REMOTE_DIR'].replace(os.path.sep, '/')
    file_id = '_standalone_' + str(uuid.uuid1())
    audio_filename = str(file_id) + dbx_config['FILE_NAME']

    remote_file_path = '/'.join(['/', remote_path, audio_filename])

    try:
        response = upload(dbx, local_file_path, remote_file_path, overwrite=True)
        if response:
            print('{} Upload Successful!'.format(remote_file_path))
            shared_url = share(dbx, remote_file_path)
            print('{} Shared Successfully!'.format(shared_url))
            return True
    except (ApiError, IOError, BufferError, FileMetadata) as e:
        print('File {} could not be uploaded or shared. {} '.format(local_file_path, e))

    return None

if __name__ == "__main__":

    file_to_upload = raw_input("Enter the full path of the file to be uploaded: ")
    success = upload_and_share(local_file_path=file_to_upload)

    print("Completed " + str("Successfully!!!" if success else "With Errors!"))
