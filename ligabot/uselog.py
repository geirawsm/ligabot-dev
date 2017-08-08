#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import syslog
import datetime


def uselog(message, level=None):
    '''
    Uselog is a smarter logging function for Python scripts - for me.
    Uselog relies on two variables 'message' and 'level':
    - 'message' should contain the message that you want to log.
    - 'level' decides how the logging will be executed:
            0: Do nothing
            1: Print (default)
            2: Send to system log
            3: print and send to system log
    Example:
        import ligabot.uselog
        uselog_level = 0

        # This will print
        ligabot.uselog.uselog('test1', level=1)

        # This will not print since 'uselog_level' is 0
        ligabot.uselog.uselog('test2', level=uselog_level)

        # This will print since level 1 is default
        ligabot.uselog.uselog('test2')
    '''
    if level is None:
        import ligabot.config
        config = ligabot.config.get_config()
        level = int(config['script_settings']['uselog_level'])

    def uselog_print(message):
        print('[{}] {}'.format(
            datetime.datetime.now().strftime("%d.%m.%Y %H.%M.%S"),
            message))

    def uselog_sys(message):
        syslog.syslog(message)

    if level == 0:
        pass
    if level == 1:
        uselog_print(message)
    if level == 2:
        uselog_sys(message)
    if level == 3:
        uselog_print(message)
        uselog_sys(message)


if __name__ == "__main__":
    print('starting')
    uselog('This should print as a standard')
    uselog('This should NOT print, but go to logging', level=2)
    uselog('This should NOT print or log at all', level=0)
