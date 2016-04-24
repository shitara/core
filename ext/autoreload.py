
import time
import os
import sys
import logging

from core.conf import BASE_DIR, settings
from watchdog.events import FileSystemEventHandler
from watchdog.observers.polling import PollingObserver

_FILES = (
    '.yaml','.py',
    )

_has_execv = sys.platform != 'win32'

def _reload(filename):
    logging.info(
        '%s modified; restarting server' % filename)
    path_prefix = '.' + os.pathsep
    if (sys.path[0] == '' and not os.environ.get("PYTHONPATH", "").startswith(path_prefix)):
        os.environ["PYTHONPATH"] = (path_prefix + os.environ.get("PYTHONPATH", ""))
    if not _has_execv:
        subprocess.Popen([sys.executable] + sys.argv)
        sys.exit(0)
    else:
        try:
            os.execv(sys.executable, [sys.executable] + sys.argv)
        except OSError:
            os.spawnv(os.P_NOWAIT, sys.executable, [sys.executable] + sys.argv)
            os._exit(0)

class Handler(FileSystemEventHandler):

    def on_created(self, event):
        self.on_event(event)
    def on_modified(self, event):
        self.on_event(event)
    def on_deleted(self, event):
        self.on_event(event)

    def on_event(self, event):
        if os.path.splitext(event.src_path)[-1].lower() in _FILES:
            _reload(event.src_path)

if settings['debug']:
    observer = PollingObserver(timeout=.5)
    observer.schedule(
        Handler(), BASE_DIR, recursive=True)
    observer.start()

