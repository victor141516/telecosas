import os
import subprocess

PART_SIZE = int(1.4 * 1024 * 1024 * 1024)

def compress(path, filename):
    if not os.path.isdir('{}/_rar'.format(path)):
        os.mkdir('{}/_rar'.format(path))
    command = 'rar a -y -v{}b "{}/_rar/{}.rar" "{}/{}"'.format(
        str(PART_SIZE), path, filename, path, filename
    )
    subprocess.check_output(command, shell=True)
    return 1+int(os.path.getsize(path) / PART_SIZE)

def must_split(path, filename):
    return os.path.getsize(path + '/' + filename) > PART_SIZE

def get_compressed_filenames(filename, nof_parts):
    return ['{}.part{}.rar'.format(filename, n) for n in range(1, nof_parts+1)]

def clean_compressed_files(path, parts_filenames):
    for f in parts_filenames:
        os.remove('{}/_rar/{}'.format(path, f))

