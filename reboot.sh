#!/bin/bash
source /home/pi/.bash_profile
/usr/bin/tmux new-session -d -s omxplayer_server
/usr/bin/tmux send-keys -t omxplayer_server "cd /home/pi/omxplayer_server && $VENV/bin/pserve production.ini" C-m
/usr/bin/tmux set-option -t omxplayer_server remain-on-exit on
