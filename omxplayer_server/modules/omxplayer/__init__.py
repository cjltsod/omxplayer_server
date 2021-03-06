from queue import Queue
from time import sleep
from urllib.request import urlopen
from urllib.parse import urlencode
from subprocess import call, check_output
import pkg_resources
import threading
import json
import sys
import time
import os
import signal

from pyomxplayer import OMXPlayer
from netifaces import interfaces, ifaddresses, AF_INET
from pyramid.events import ApplicationCreated


def update():
    call(['git', 'checkout', '--', '.'], shell=False)
    call(['git', 'pull'], shell=False)
    call(['chmod', 'u+x', 'reboot.sh'], shell=False)


class ThreadHeartbeat(threading.Thread):
    def __init__(self, server):
        self.version = pkg_resources.get_distribution('omxplayer_server').version
        self.server = server
        threading.Thread.__init__(self)

    def get_git_version(self):
        return check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('utf-8').strip()

    def get_ip(self):
        ip_dict = dict()
        for ifaceName in interfaces():
            addresses = [i['addr'] for i in ifaddresses(ifaceName).setdefault(AF_INET, [{'addr': None}])]
            ip_dict[ifaceName] = addresses
        return ip_dict

    def get_tv_no(self):
        output = check_output(['sudo', 'teamviewer', 'info']).decode('utf-8')
        tv_str = output[output.find('TeamViewer ID:') + len('TeamViewer ID:'):].strip().split()[-1]
        if not tv_str.isdigit():
            tv_str = output[output.find('TeamViewer ID:') + len('TeamViewer ID:'):].split('\n')[0].split()[-1]

        if tv_str.isdigit():
            return tv_str
        else:
            raise Exception('Parsing error: {}'.format(tv_str))

    def get_temp(self):
        output = check_output(['/opt/vc/bin/vcgencmd', 'measure_temp']).decode('utf-8')
        temp = output.strip().strip('temp=').strip('\'C')
        return temp

    def test_self_connect(self):
        try:
            response = urlopen('http://127.0.0.1:8080')
            return True
        except:
            return False

    def run(self):
        boot = True
        time.sleep(5)
        if not self.test_self_connect():
            print('Exception happend when self connect.')
            os.kill(os.getpid(), signal.SIGKILL)
            sys.exit(1)

        while True:
            short_sleep = False
            try:
                identify = self.get_tv_no()
                json_data = {
                    'tv_no': identify,
                    'ip_addr': self.get_ip(),
                    'version': self.get_git_version(),
                    'temperature': self.get_temp(),
                }
                req_json = json.dumps(json_data)

                url = self.server + '{}'.format(identify)

                if boot:
                    url = url + '?boot=1'
                data = urlencode(dict(data=req_json)).encode('utf-8')
                response = urlopen(url, data=data)
                json_res = json.loads(response.read().decode('utf-8'))

                boot = False

                if json_res.get('update'):
                    update()

                if json_res.get('reboot'):
                    call(['sudo', 'reboot'], shell=False)
            except:
                print('Exception happened when hearbeat.')
                short_sleep = True

            if short_sleep:
                sleep(5)
            else:
                sleep(60)


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
        last_postition = 0
        wait_time = 10
        while True:
            sleep(1)
            if not omx.is_running():
                self.omxplayer_queue.get()
                self.omxplayer_queue.task_done()
                break
            elif not omx.paused and omx.position == last_postition:
                wait_time = wait_time - 1
                if wait_time <= 0:
                    omx.stop()
            else:
                last_postition = omx.position


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
            if cmd not in ['reboot', 'update']:
                omx = self.omxplayer_queue.get()
            else:
                omx = None

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
            elif cmd == 'reboot':
                call(['sudo', 'reboot'], shell=False)
            elif cmd == 'update':
                update()
            else:
                pass
                # unknown command

            if omx:
                self.omxplayer_queue.put(omx)
                self.omxplayer_queue.task_done()
            self.cmd_queue.task_done()


def application_created_callback(event):
    settings = event.app.registry.settings

    settings['omxplayer_playlist_thread'].start()
    settings['omxplayer_controller_thread'].start()
    settings['omxplayer_heartbeat_thread'].start()


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
    heartbeat_thread = ThreadHeartbeat(server=settings['omx_heartbeat.server'])

    settings['omxplayer_playlist_thread'] = playlist_thread
    settings['omxplayer_controller_thread'] = controller_thread
    settings['omxplayer_heartbeat_thread'] = heartbeat_thread

    config.add_subscriber(application_created_callback, ApplicationCreated)

