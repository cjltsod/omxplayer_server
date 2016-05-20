from pyramid.view import view_config
import os


@view_config(route_name='home', renderer='templates/mytemplate.mako')
def my_view(request):
    return {'project': 'omxplayer_server'}


@view_config(route_name='play_omx', renderer='json')
def play_omx(request):
    directory = request.matchdict.get('directory', '20160410_EA')
    target_dir = '/mnt/RecordingUpload/RecordingUpload/{}'.format(directory)
    file_list = list()

    for eachFile in os.listdir(target_dir):
        if eachFile.split('.')[-1].lower() in ['mts', 'm2ts']:
            file_path = '{}/{}'.format(target_dir, eachFile)
            request.registry.settings['omxplayer_playlist_queue'].put(file_path)
            file_list.append(file_path)

    return dict(playlist=file_list)
