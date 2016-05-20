import os

from pyramid.view import view_config


@view_config(route_name='omx_play', renderer='json')
def omx_play(request):
    directory = request.matchdict.get('directory', '20160410_EA')
    target_dir = os.path.join('/mnt/RecordingUpload/RecordingUpload', directory)
    play_list = list()
    _return = dict()

    try:
        file_list = os.listdir(target_dir)
        file_list.sort()

        for eachFile in file_list:
            if eachFile.split('.')[-1].lower() in ['mp4', 'mts', 'm2ts']:
                file_path = os.path.join(target_dir, eachFile)
                request.registry.settings['omxplayer_playlist_queue'].put(file_path)
                play_list.append(os.path.join(directory, eachFile))
        _return['status'] = 'OK'
        _return['playlist'] = play_list
    except:
        _return['playlist'] = list()
        _return['status'] = 'Not Found'
        _return['detail'] = 'Unable to find directory'

    return _return


@view_config(route_name='omx_cmd', renderer='json')
def omx_cmd(request):
    cmd = request.matchdict.get('cmd')
    available_command_list = [
        'pause', 'next', 'stop',
        'mute', 'inc_vol', 'dec_vol',
        'back_30', 'back_600', 'forward_30', 'forward_600',
        'inc_speed', 'dec_speed',
    ]

    _return = dict()
    if cmd in available_command_list:
        request.registry.settings['omxplayer_cmd_queue'].put(cmd)
        _return['status'] = 'OK'
    else:
        _return['status'] = 'Unknown'
        _return['available_command'] = available_command_list

    return _return


@view_config(route_name='omx_panel', renderer='templates/omx_panel.mako')
def omx_panel(request):
    available_command = [
        {'cmd': 'pause', 'description': 'Pause','icon': 'fa-pause'},
        {'cmd': 'next', 'description': 'Next Video', 'icon': 'fa-step-forward'},
        {'cmd': 'stop', 'description': 'Stop all', 'icon': 'fa-stop'},
        {'cmd': 'mute', 'description': 'Mute', 'icon': 'fa-volume-off'},
        {'cmd': 'inc_vol', 'description': 'Increase Volume', 'icon': 'fa-volume-up'},
        {'cmd': 'dec_vol', 'description': 'Decrease Volume', 'icon': 'fa-volume-down'},
        {'cmd': 'back_600', 'description': 'Backward 10 minutes', 'icon': 'fa-fast-backward'},
        {'cmd': 'back_30', 'description': 'Backward 30 seconds', 'icon': 'fa-backward'},
        {'cmd': 'forward_30', 'description': 'Forward 30 seconds', 'icon': 'fa-forward'},
        {'cmd': 'forward_600', 'description': 'Forward 10 minutes', 'icon': 'fa-fast-forward'},
        {'cmd': 'inc_speed', 'description': 'Speed slow', 'icon': 'fa-angle-right'},
        {'cmd': 'dec_speed', 'description': 'Speed fast', 'icon': 'fa-angle-double-right'},
    ]

    try:
        target_dir = '/mnt/RecordingUpload/RecordingUpload/'
        file_list = os.listdir(target_dir)
        onlydirs = [ f for f in file_list if os.path.isdir(os.path.join(target_dir ,f))]
        onlydirs.sort()
    except:
        onlydirs = ['20160101_FAKE']

    return dict(available_cmd=available_command, available_dir=onlydirs)