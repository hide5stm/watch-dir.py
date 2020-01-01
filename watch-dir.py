'''
https://notify2.readthedocs.io/en/latest/_modules/notify2.html
https://www.flaticon.com/free-icon/download_179383
'''

import os
import signal
from threading import Event

import gi
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import GdkPixbuf
import notify2
from pyinotify import IN_MOVED_TO, IN_MOVED_FROM, \
    ProcessEvent, WatchManager, ThreadedNotifier


class Message:
    def __init__(self):
        notify2.init("Watch")
        self._pixbuf = GdkPixbuf.Pixbuf.new_from_file('download.png')

    def send(self, path, name):
        message = "{}, {}".format(path, name)
        n = notify2.Notification("Download", message)
        n.set_icon_from_pixbuf(self._pixbuf)
        n.show()


class Handler(ProcessEvent):
    def __init__(self):
        self._message = Message()

    def process_IN_MOVED_TO(self, event):
        self._message.send(event.path, event.name)


class Loop():
    def __init__(self):
        signal.signal(signal.SIGINT, self._sig_handler)
        self._is_exit = Event()

    def _sig_handler(self, signum, frame):
        self._is_exit.set()

    def do_loop(self):
        while not self._is_exit.is_set():
            self._is_exit.wait()


def main(dirs):
    if not dirs:
        dirs = '{}/Downloads'.format(os.environ['HOME'])

    wm = WatchManager()
    watch_dirs = wm.add_watch(dirs, IN_MOVED_TO | IN_MOVED_FROM)

    notifier = ThreadedNotifier(wm, Handler())
    notifier.start()
    Loop().do_loop()
    notifier.stop()

    wm.rm_watch(watch_dirs.values())


if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
