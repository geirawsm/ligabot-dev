#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import re
import ligabot.uselog
import ligabot.config

config = ligabot.config.get_config()

uselog = ligabot.uselog.uselog


def create_necessary_file(filename):
    '''
    If a file does not exist, make it
    '''
    if not os.path.exists(filename):
        uselog('The file {} does not exist. Creating...'.format(filename))
        open(filename, 'w').close()
        try:
            write_cache('', filename)
        except(NameError):
            pass


def append_cache(info, file):
    '''
    Append 'info' to 'file'
    '''
    create_necessary_file(file)
    cache = open(file, 'a')
    cache.write('{}\n'.format(info))
    cache.close()


def write_cache(info, file):
    '''
    Write 'info' to 'file'
    '''
    create_necessary_file(file)
    cache = open(file, 'w')
    cache.write('{}\n'.format(info))
    cache.close()


def read_cache(file):
    '''
    Read from 'file'
    '''
    create_necessary_file(file)
    read_out = open(file, 'r')
    read = read_out.read()
    read_out.close()
    return read


def clean_cache(file):
    '''
    Clean out things we don't want in a file
    '''
    read = read_cache(file)
    regex_clean = [[r'^\s{1,100}', ''],
                   [r'\s{1,100}$', ''],
                   [r'\n{2,100}', '\n'],
                   [r'\n$(?![\r\n])', '']
                   ]
    for regex in regex_clean:
        read = re.sub(regex[0],
                      regex[1],
                      read,
                      flags=re.MULTILINE | re.DOTALL
                      )
        write_cache(read, file)
