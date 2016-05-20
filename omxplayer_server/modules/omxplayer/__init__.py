from queue import Queue
from time import sleep
from pyomxplayer import OMXPlayer
import threading


class thread_player(threading.Thread):
    def __init__(self, omxplayer_queue, path, *args):
        self.omxplayer_queue = omxplayer_queue
        self.path = path
        self.args = args
        threading.Thread.__init__(self)

    def run(self):
        omx = OMXPlayer(self.path, args=self.args)
        self.omxplayer_queue.put(omx)
        omx.toggle_pause()
        while True:
            sleep(1)
            if not omx.is_running():
                self.omxplayer_queue.get()
                self.omxplayer_queue.task_done()
                break


class thread_playlist(threading.Thread):
    def __init__(self, playlist_queue, omxplayer_queue):
        self.playlist_queue = playlist_queue
        self.omxplayer_queue = omxplayer_queue
        threading.Thread.__init__(self)


    def run(self):
        while True:
            path = self.playlist_queue.get()
            current_thread = thread_player(self.omxplayer_queue, path)
            current_thread.start()
            current_thread.join()
            self.playlist_queue.task_done()


class thread_controller(threading.Thread):
    def __init__(self, cmd_queue, omxplayer_queue):
        self.cmd_queue = cmd_queue
        self.omxplayer_queue = omxplayer_queue
        threading.Thread.__init__(self)

    def run(self):
        while True:
            cmd = self.cmd_queue.get()
            omx = self.omxplayer_queue.get()
            # omx.do(cmd)
            self.omxplayer_queue.put(omx)
            self.omxplayer_queue.task_done()
            self.cmd_queue.task_done()



def includeme(config):
    settings = config.registry.settings
    playlist_queue = Queue()
    cmd_queue = Queue()
    omxplayer_queue = Queue()

    settings['omxplayer_cmd_queue'] = cmd_queue
    settings['omxplayer_playlist_queue'] = playlist_queue
    settings['omxplayer_queue'] = omxplayer_queue

    playlist_thread = thread_playlist(playlist_queue, omxplayer_queue)
    controller_thread = thread_controller(cmd_queue, omxplayer_queue)

    settings['omxplayer_playlist_thread'] = playlist_thread
    settings['omxplayer_controller_thread'] = controller_thread

    playlist_thread.start()
    controller_thread.start()
