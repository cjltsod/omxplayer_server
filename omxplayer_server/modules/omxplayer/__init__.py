from queue import Queue
from time import sleep
from urllib.request import urlopen
from urllib.parse import urlencode
from subprocess import call, check_output
import pkg_resources
import threading
import json

from pyomxplayer import OMXPlayer
from netifaces import interfaces, ifaddresses, AF_INET


class ThreadHeartbeat(threading.Thread):
    def __init__(self):
        self.version = pkg_resources.get_distribution('omxplayer_server').version
        threading.Thread.__init__(self)

    def get_ip(self):
        ip_dict = dict()
        for ifaceName in interfaces():
            addresses = [i['addr'] for i in ifaddresses(ifaceName).setdefault(AF_INET, [{'addr': None}])]
            ip_dict[ifaceName] = addresses
        return ip_dict

    def get_tv_no(self):
        output = check_output(['teamviewer', 'info']).decode('utf-8')
        tv_str = output[output.find('TeamViewer ID:') + len('TeamViewer ID:'):].strip().strip('\x1b[0m').strip()
        if tv_str.isdigit():
            return tv_str
        else:
            raise Exception('Parsing error: {}'.format(tv_str))

    def run(self):
        boot = True
        while True:
            try:
                identify = '1234567'  # self.get_tv_no()
                json_data = {
                    'tv_no': identify,
                    'ip_addr': self.get_ip(),
                    'version': self.version,
                }
                req_json = json.dumps(json_data)

                url = 'http://staff.mecpro.com.tw/omx_heartbeat/{}'.format(identify)
                url = 'http://192.168.1.103:6543/omx_heartbeat/{}'.format(identify)

                if boot:
                    url = url + '?boot=1'
                data = urlencode(dict(data=req_json)).encode('utf-8')
                response = urlopen(url, data=data)
                json_res = json.loads(response.read().decode('utf-8'))

                boot = False

                if json_res.get('update'):
                    print('pulling')
                    call(['git', 'pull'], shell=False)

                if json_res.get('reboot'):
                    print('rebooting')
                    call('reboot', shell=False)
            except:
                pass
                print('error')
            sleep(10)



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
    heartbeat_thread = ThreadHeartbeat()

    settings['omxplayer_playlist_thread'] = playlist_thread
    settings['omxplayer_controller_thread'] = controller_thread

    playlist_thread.start()
    controller_thread.start()
    heartbeat_thread.start()
