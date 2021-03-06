#!/bin/bash
/usr/bin/tmux new-session -d -s omxplayer_server
/usr/bin/tmux set-option -g default-shell /bin/bash
/usr/bin/tmux set-option -t omxplayer_server remain-on-exit on
/usr/bin/tmux send-keys -t omxplayer_server "/bin/bash" C-m
/usr/bin/tmux send-keys -t omxplayer_server "source /home/pi/.bashrc" C-m
/usr/bin/tmux send-keys -t omxplayer_server "while ! ping -c1 staff.mecpro.com.tw &>/dev/null; do :; done" C-m
/usr/bin/tmux send-keys -t omxplayer_server "cd /home/pi/omxplayer_server && pipenv install" C-m
/usr/bin/tmux send-keys -t omxplayer_server "cd /home/pi/omxplayer_server && pipenv run pip install -e ." C-m
/usr/bin/tmux send-keys -t omxplayer_server "cd /home/pi/omxplayer_server && pipenv run pserve production.ini" C-m
/usr/bin/tmux send-keys -t omxplayer_server "cd /home/pi/omxplayer_server && pipenv run pserve production.ini" C-m
/usr/bin/tmux send-keys -t omxplayer_server "cd /home/pi/omxplayer_server && pipenv run pserve production.ini" C-m
/usr/bin/tmux send-keys -t omxplayer_server "cd /home/pi/omxplayer_server && pserve production.ini" C-m
/usr/bin/tmux send-keys -t omxplayer_server "cd /home/pi/omxplayer_server && pserve production.ini" C-m
/usr/bin/tmux send-keys -t omxplayer_server "cd /home/pi/omxplayer_server && pserve production.ini" C-m
/usr/bin/tmux send-keys -t omxplayer_server "sudo reboot" C-m
