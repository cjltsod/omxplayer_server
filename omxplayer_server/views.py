from pyramid.view import view_config
import os


@view_config(route_name='home', renderer='templates/mytemplate.mako')
def my_view(request):
    return {'project': 'omxplayer_server'}


@view_config(route_name='play_omx', renderer='json')
def play_omx(request):
    directory = request.matchdict.get('directory', '20160410_EA')
    target_dir = '/mnt/RecordingUpload/RecordingUpload/{}'.format(directory)
    play_list = list()
    file_list = os.listdir(target_dir)
    file_list.sort()

    for eachFile in file_list:
        if eachFile.split('.')[-1].lower() in ['mts', 'm2ts']:
            file_path = '{}/{}'.format(target_dir, eachFile)
            request.registry.settings['omxplayer_playlist_queue'].put(file_path)
            play_list.append(file_path)

    return dict(playlist=play_list)


@view_config(route_name='cmd_omx', renderer='json')
def cmd_omx(request):
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
