Fabkins
=======

Femto-jenkins based on fabfiles.

Features
--------

  - **simple, tiny and fast.**
  - no database :
    - old build logs are in plain text.
    - job configurations are short json files.
    - fabfiles are actually just fabfiles. You could use them without fabkins.
  - builds can be triggered by hand or by web-hooks.
  - output of current builds can be visualized in "realtime" with websockets.

Screenshots
-----------

Installation
------------

You need a UNIX server with python >= 2.6.
```bash
$ sudo apt-get install libevent-dev  # necessary for gevent
```

Install it in a virtualenv, *please*.
```bash
(venv) $ pip install fabkins
$ # if you've done that in a virtualenv, you should do that then:
$ # fabkins-patch-venv
```

Configuration and launch
------------------------

Usage:
```bash
(venv) $ fabkins -h
Usage: /home/fabkins/venv/bin/fabkins [OPTIONS]

Fabkins, a femto-jenkins based on fabfiles.

Options:
  -c, --config-file=STR   path of fabkins.ini
  --fabfile=STR           path of default fabfile.py template
  --workdir=STR           path of fabkins working directory (default: ~/workdir)
  --web-port=INT          listening http port (default: 8010)
  --web-prefix=STR        '/fabkins' if your instance is at example.com/fabkins(default: '/fabkins')
  --password=STR          the password used for log-in (sha256) (default: sha256 of "password")
  --webhook-key=STR       the password used to trigger web hooks (default: "th3w3bh00kk3y")
  --secret-key=STR
  --debug=STR
  -h, --help              Show this help

ProTip /!\ you should probably just use the "-c" option.
First, generate a "fabkins.ini" file -> "fabkins-gen-config -o ./fabkins.ini"
Edit it, and then launch fabkins -> "fabkins -c ./fabkins.ini"
```

Configuration:
```bash
(venv) $ fabkins-gen-config -o ~/fabkins.ini -p pass  # "pass" will be sha256summed
(venv) $ vim ~/fabkins.ini  # some edits
(venv) $ cat ~/fabkins.ini
[fabkins]
workdir = /home/me/workdir
web-port = 8010
web-prefix = /fabkins
password = d74ff0ee8da3b9806b18c877dbf29bbde50b5bd8e4dad7a3a725000feb82e8f1
webhook-key = th3w3bh00kk3y
```

Launch:
```bash
(venv) $ fabkins -c ~/fabkins.ini
# some output : it runs !
```

You can access the app at http://localhost:8010/fabkins, password = "pass".

Next steps : make nginx serve static content, and create an upstart job to control the service.

Security
--------

The security of this application relies only on UNIX basic rights.
Someone who can log in the webapp can do everything the user that launched the service can do.
So you should use a separate user for this service, with restricted rights. Or, be the only one who knows the password.

Dependencies
------------

  - gevent
  - gevent-websocket
  - Flask
  - Fabric
  - clize

See requirements.txt for more info about well working versions of these dependencies.


Caution
-------

Although it seems to work fine, I'm not using thread-safe stuff, so it should break.
So make backups. Do not use it for production / critical stuff.
