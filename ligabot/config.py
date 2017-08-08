#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import configparser
import sys
import os

filename = 'userinfo.ini'


def get_config():
    '''
    Setting up path and getting config file
    '''
    config = configparser.ConfigParser()
    if os.path.exists('{}/ligabot/'.format(sys.path[0])):
        config.read('{}/ligabot/{}'.format(sys.path[0], filename))
    else:
        line = '/'
        for i in sys.path[0][1:len(sys.path[0]) - 1]:
            line += '{}/'.format(i)
        config.read('{}/{}'.format(sys.path[0], filename))

    if config == []:
        print('Couldn\'t open the file \'{}\'. Read more about thi'
              's config file in the readme:\nhttps://github.com/armandg/liga'
              'bot/blob/master/README.md\n'.format(filename))
        sys.exit()
    else:
        return config


if __name__ == "__main__":
    print(get_config().sections())
