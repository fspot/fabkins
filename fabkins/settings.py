#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os, pwd

TCP_PORT = 58010
TCP_CLIENT_TIMEOUT = 5
CONFIG_SECTION = 'fabkins'

class default_params(object):
    DEFAULT_FABFILE = None  # it means "default_fabfile.py" !
    WORKDIR = "/home/%s/workdir" % pwd.getpwuid(os.getuid())[0]
    WEB_PORT = 8010
    WEB_PREFIX = "/fabkins"

    # next three have to be secrets !
    # in bash: echo -n "password" | sha256sum
    # in python: import hashlib; print hashlib.sha256("password").hexdigest()
    PASSWORD = "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"
    WEBHOOK_KEY = "th3w3bh00kk3y" # used to prevent malicious webhook triggering
    SECRET_KEY = os.urandom(24)   # actually, you do not need to know it

    DEBUG = False


def _geto(config, option, section=CONFIG_SECTION, cls=None):
    method = config.get
    if cls == int:  method = config.getint
    if cls == bool: method = config.getboolean
    if config.has_option(section, option):
        return method(section, option)

def _seto(config, attr, option, cls=None):
    option_value = _geto(config, option, cls=cls)
    if option_value is not None:
        setattr(default_params, attr, option_value)

def read_config_file(configfile):
    import ConfigParser
    config = ConfigParser.RawConfigParser()
    config.read(configfile)
    _seto(config, 'DEFAULT_FABFILE', 'default-fabfile')
    _seto(config, 'WORKDIR', 'workdir')
    _seto(config, 'WEB_PORT', 'web-port', cls=int)
    _seto(config, 'WEB_PREFIX', 'web-prefix')
    _seto(config, 'PASSWORD', 'password')
    _seto(config, 'WEBHOOK_KEY', 'webhook-key')
    _seto(config, 'SECRET_KEY', 'secret-key')
    _seto(config, 'DEBUG', 'debug', cls=bool)


def write_config_file(configfile, password):
    import ConfigParser
    config = ConfigParser.RawConfigParser()
    params = [
        ('workdir', default_params.WORKDIR),
        ('web-port', default_params.WEB_PORT),
        ('web-prefix', default_params.WEB_PREFIX),
        ('password', password),
        ('webhook-key', default_params.WEBHOOK_KEY),
    ]
    config.add_section(CONFIG_SECTION)
    for option, value in params:
        config.set(CONFIG_SECTION, option, value)
    with open(configfile, 'wb') as conf_file:
        config.write(conf_file)


def get_default_fabfile_content():
    if default_params.DEFAULT_FABFILE is None:
        try:
            import fabkins
            fabfile = os.path.join(fabkins.__path__[0], 'default_fabfile.py')
        except:
            # fabkins is not installed via setup.py install
            fabfile = os.path.join(os.path.dirname(os.path.realpath(__file__)), "default_fabfile.py")
    else:
        fabfile = default_params.DEFAULT_FABFILE
    return open(fabfile, 'r').read()

def add_fab_to_env_path():
    # check that we are in a good virtualenv:
    try:
        import os, sys, fabric, os.path
        if hasattr(sys, 'real_prefix'):
            os.environ["PATH"] += ':' + os.path.join(sys.prefix, 'bin')
    except:
        pass
