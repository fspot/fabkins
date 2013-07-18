Fabkins
=======

(work in progress)
Femto-jenkins based on fabfiles.

Features
--------

  - **simple, tiny and fast.**
  - no database :
    - old build logs are in plain text.
    - job configurations are short json files.
    - fabfiles are actually just fabfiles. You could use them without fabkins.
  - builds can be triggered by hand or by webhooks.
  - output of current builds can be visualized in "realtime" with websockets.

Screenshots
-----------

Installation
------------

You need a UNIX server with python >= 2.6 ; gevent and flask.
sudo apt-get install libevent-dev  # necessary for gevent
sudo pip install flask gevent gevent-websocket

Configuration and launch
------------------------

vim settings.py
python app.py
