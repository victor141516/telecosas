import copy_gdrive
import os
import split
import subprocess
import sys

def download_and_upload(gdrive_link):
    gdrive_link = sys.argv[1]
    gdrive_id = copy_gdrive.get_id(gdrive_link)
    new_gdrive_link = copy_gdrive.copy_copy_get_link(gdrive_id)
    new_gdrive_id = copy_gdrive.get_id(new_gdrive_link)
    filename = copy_gdrive.download_file(new_gdrive_id)
    path = 'tmp'

    if split.must_split(path, filename):
        print('\n\nMust split, compressing\n\n')
        nof_parts = split.compress(path, filename)
        print('\n\nCompression completed')
        print('\n\nParts: {}'.format(str(nof_parts)))
        dest_filenames = split.get_compressed_filenames(filename, nof_parts)
        must_split = True
    else:
        print('\n\nSmall file, skipping compression')
        dest_filenames = [filename]
        must_split = False

    for f in dest_filenames:
        print('\n\nUploading {}\n\n'.format(f))
        porcess_out = subprocess.Popen('python telegramfilemanager.py "{}"'.format(
            path + ('/_rar/' if must_split else '/') + f
        ), shell=True)
        if porcess_out.wait() != 0:
            print('\n\nError uploading your file:\n--STDERR')
            print(porcess_out.stderr)
            print('\n\n--\n\n--STDOUT')
            print(porcess_out.stdout)
            print('\n\n--')
            quit()
        print('Uploaded {}'.format(f))

    if must_split:
        split.clean_compressed_files(path, dest_filenames)

    os.remove(path + '/' + filename)

    copy_gdrive.delete_file(new_gdrive_id)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Syntax: python gdrive_to_telegram.py [gdrive link]')
        quit()
    else:
        download_and_upload(sys.argv[1])

