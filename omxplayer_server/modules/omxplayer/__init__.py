from queue import Queue
from time import sleep
from pyomxplayer import OMXPlayer
import threading


class ThreadPlayer(threading.Thread):
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


class ThreadPlaylist(threading.Thread):
    def __init__(self, playlist_queue, omxplayer_queue):
        self.playlist_queue = playlist_queue
        self.omxplayer_queue = omxplayer_queue
        threading.Thread.__init__(self)

    def run(self):
        while True:
            path = self.playlist_queue.get()
            current_thread = ThreadPlayer(self.omxplayer_queue, path)
            current_thread.start()
            current_thread.join()
            self.playlist_queue.task_done()


class ThreadController(threading.Thread):
    def __init__(self, cmd_queue, playlist_queue, omxplayer_queue):
        self.cmd_queue = cmd_queue
        self.omxplayer_queue = omxplayer_queue
        self.playlist_queue = playlist_queue
        threading.Thread.__init__(self)

    def run(self):
        while True:
            cmd = self.cmd_queue.get()
            omx = self.omxplayer_queue.get()
            if cmd == 'pause':
                omx.toggle_pause()
            elif cmd == 'next':
                if not self.playlist_queue.empty():
                    omx.stop()
            elif cmd == 'stop':
                try:
                    while not self.playlist_queue.empty():
                        self.playlist_queue.get_nowait()
                        self.playlist_queue.task_done()
                except:
                    pass
                omx.stop()
            elif cmd == 'mute':
                omx.toggle_mute()
            elif cmd == 'inc_vol':
                omx.inc_vol()
            elif cmd == 'dec_vol':
                omx.dec_vol()
            elif cmd == 'back_30':
                omx.back_30()
            elif cmd == 'back_600':
                omx.back_600()
            elif cmd == 'forward_30':
                omx.forward_30()
            elif cmd == 'forward_600':
                omx.forward_600()
            elif cmd == 'inc_speed':
                omx.inc_speed()
            elif cmd == 'dec_speed':
                omx.dec_speed()
            else:
                pass
                # unknown command

            self.omxplayer_queue.put(omx)
            self.omxplayer_queue.task_done()
            self.cmd_queue.task_done()



def includeme(config):
    settings = config.registry.settings
    playlist_queue = Queue()
    cmd_queue = Queue()
    omxplayer_queue = Queue()

    config.add_route('omx_play', '/play/{directory}')
    config.add_route('omx_cmd', '/cmd/{cmd}')
    config.add_route('omx_panel', '/')

    settings['omxplayer_cmd_queue'] = cmd_queue
    settings['omxplayer_playlist_queue'] = playlist_queue
    settings['omxplayer_queue'] = omxplayer_queue

    playlist_thread = ThreadPlaylist(playlist_queue, omxplayer_queue)
    controller_thread = ThreadController(cmd_queue, playlist_queue, omxplayer_queue)

    settings['omxplayer_playlist_thread'] = playlist_thread
    settings['omxplayer_controller_thread'] = controller_thread

    playlist_thread.start()
    controller_thread.start()
