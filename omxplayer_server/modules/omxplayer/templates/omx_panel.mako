<!DOCTYPE html>
<html lang="${request.locale_name}">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="omxplayer control panel">
    <meta name="author" content="Blessingsoft Corp.">
    <link rel="shortcut icon" href="${request.static_url('omxplayer_server:static/pyramid-16x16.png')}">

    <title>Control Panel</title>

    <!-- Bootstrap core CSS -->
    <link href="//oss.maxcdn.com/libs/twitter-bootstrap/3.0.3/css/bootstrap.min.css" rel="stylesheet">
    <link href="//maxcdn.bootstrapcdn.com/font-awesome/4.6.3/css/font-awesome.min.css" rel="stylesheet">

    <!-- Custom styles for this scaffold -->
    <link href="${request.static_url('omxplayer_server:static/theme.css')}" rel="stylesheet">

    <!-- HTML5 shim and Respond.js IE8 support of HTML5 elements and media queries -->
    <!--[if lt IE 9]>
      <script src="//oss.maxcdn.com/libs/html5shiv/3.7.0/html5shiv.js"></script>
      <script src="//oss.maxcdn.com/libs/respond.js/1.3.0/respond.min.js"></script>
    <![endif]-->
  </head>

  <body>

    <div class="">
      <div class="container">
        <div class="row">
              <p class="lead">
                <form class="form-inline">
                <div class="form-group">
                  <select class="form-control" id="playlist">
                    % for each in available_dir:
                    <option>${each}</option>
                    % endfor
                  </select>
                  <button type="button" class="btn btn-default btn-lg" onclick="add_to_playlist()"><i class="fa fa-plus" title="Add to playlist"></i></button>
                </div>
                </form>
              </p>
              <p class="lead">
                <div class="btn-group" role="group">
                % for each_cmd in available_cmd:
                <button class="btn btn-default btn-lg" href="#" onclick="execute_cmd('${each_cmd['cmd']}')"><i class="fa ${each_cmd['icon']}" title="${each_cmd['description']}"></i> </button>
                % endfor
                </div>
              </p>
        </div>
        <div class="row">
          <div class="copyright">
            Copyright &copy; Blessing Software
          </div>
        </div>
      </div>
    </div>

    <!-- Bootstrap core JavaScript
    ================================================== -->
    <!-- Placed at the end of the document so the pages load faster -->
    <script src="//oss.maxcdn.com/libs/jquery/1.10.2/jquery.min.js"></script>
    <script src="//oss.maxcdn.com/libs/twitter-bootstrap/3.0.3/js/bootstrap.min.js"></script>
    <script>
        function execute_cmd(cmd) {
            url = "${request.route_url('omx_cmd', cmd='__cmd__')}";
            url = url.replace('__cmd__', cmd);
            $.get(url, function(data) {
                if(data.status != 'OK') {
                    alert('Failed to do ' + cmd + ', \nResult:\n' + data.status);
                }
            });
        }
        function add_to_playlist() {
            url = "${request.route_url('omx_play', directory='__playlist__')}";
            url = url.replace('__playlist__', $('#playlist').val());
            $.get(url, function(data) {
                if(data.status == 'OK') {
                    alert('Successful add following video into playlist:\n' + data.playlist.join('\n'));
                }
                else {
                    alert('Failed to add into playlist:\n' + data.detail);
                }
            });
        }
    </script>
  </body>
</html>
