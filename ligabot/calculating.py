#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import datetime
dt = datetime.datetime


def seconds_to(from_date, to_date):
    '''
    Calculates the number of seconds from 'from_date' to 'to_date'
    '''
    from_date = dt.strptime(from_date, "%d.%m.%Y %H.%M.%S")
    to_date = dt.strptime(to_date, "%d.%m.%Y %H.%M.%S")
    return int((to_date - from_date).total_seconds())


def days_to(from_date, to_date):
    '''
    Calculates the number of whole days between 'from_date' and 'to_date'
    '''
    from_date = dt.strptime(from_date, "%d.%m.%Y")
    to_date = dt.strptime(to_date, "%d.%m.%Y")
    return (to_date - from_date).days


def round_start_stop(league, round_info):
    '''
    Calculates seconds to start and stop of the current round and gives the
    live result for the last match in the round. Active matches have
    parenthesis around the score, so when that is removed after the
    'stop_seconds' run out, the round is finished.
    Is used for knowing when to start and stop the bot from watching the
    round post and updating it.
    '''
    if league:
        fulldate = dt.now().strftime('%d.%m.%Y %H.%M.%S')
        first_match = '{} {}.00'.format(round_info[0]['date'], round_info[0]['match_info_time'])
        #last_match = '{} {}.00'.format(
        #    round_info[len(round_info) - 1]['date'],
        #    round_info[len(round_info) - 1]['match_info_time'])
        start_seconds = seconds_to(fulldate, first_match)
    else:
        start_seconds = 10

    # Find out when a round should be stopped
    stop_round = ''
    if start_seconds <= 0:
        for match in round_info:
            print('status_text: {}'.format(match['status_text']))
            if '(' in match['status_text']:
                stop_round += 'x'
    print(stop_round)
    if stop_round == '':
        stop_round = True

    return {'start_seconds': start_seconds,
            'stop_round': stop_round}


if __name__ == "__main__":
    testsec_from = '01.01.2017 00.00.00'
    testsec_to = '01.01.2017 00.01.00'
    print('Number of seconds from \'{}\' to \'{}\': {}'.
          format(testsec_from, testsec_to,
                 seconds_to(testsec_from, testsec_to)))
    print('-' * 20)
    testday_from = '03.01.2017'
    testday_to = '01.01.2017'
    print('Number of days from \'{}\' to \'{}\': {}'.
          format(testday_from, testday_to,
                 days_to(testday_from, testday_to)))