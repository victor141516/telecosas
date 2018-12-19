from config import *
import platform
import os
import subprocess
import sys
from telegramfilemanager import TelegramFileManager

tfm = TelegramFileManager(tg_session, tg_api_id, tg_api_hash)

if len(sys.argv) != 2:
    print('Usage: python telebox.py path/to/dir')
    quit()
else:
    watch_dir = sys.argv[1]

os_name = platform.system()


def upload(filename):
    if filename.split('/')[-1] in ['.DS_Store']:
        return
    if os.path.isfile(filename):
        print(filename)
        subprocess.Popen(['python', 'telegramfilemanager.py', filename], stdout=subprocess.DEVNULL)


if os_name == 'Linux':
    import inotify.adapters
    i = inotify.adapters.Inotify()
    i.add_watch(watch_dir)
    for event in i.event_gen(yield_nones=False):
        (_, type_names, path, filename) = event
        upload(filename)
elif os_name == 'Darwin':
    def callback(event):
        upload(event.name)
    from fsevents import Observer
    from fsevents import Stream
    observer = Observer()
    observer.start()
    stream = Stream(callback, watch_dir, file_events=True)
    observer.schedule(stream)
else:
    print('Not available on Windows')
    quit()
