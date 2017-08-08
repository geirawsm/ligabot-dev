#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import re
import requests
from bs4 import BeautifulSoup as bs
import datetime
import ligabot.uselog
import ligabot.calculating
import ligabot.caching
import ligabot.config

config = ligabot.config.get_config()

uselog = ligabot.uselog.uselog

calculating = ligabot.calculating
caching = ligabot.caching
dt = datetime.datetime
nowdate = dt.now().strftime('%d.%m.%Y')

aof_domain = 'http://www.altomfotball.no/'


def get_linksoup(link, tag, attribute=False, attribute_name=False, instance=0):
    '''
    Get a certain tag with attributes:

    <div><span class = "tapenade">Some text</span></div>
          ^tag  ^attr.  ^attr. name

    link           =    Link that you want to get in cleartext
    tag            =    Html tag, like 'div' or 'p'
    attribute      =    Which attribute to look for
    attribute_name =    The name of the attribute
    instances      =    Which instance of 'tag' you want to get
    '''
    req = requests.get(link)
    soup = bs(req.content, 'html5lib', from_encoding="utf-8")
    if attribute is False and attribute_name is False:
        attribute = ''
        attribute_name = ''
    if instance == 0:
        info = soup.find(tag, attrs={attribute: attribute_name})
    elif instance > 0:
        try:
            info = soup.find_all(tag,
                                 attrs={attribute: attribute_name})[instance]
        except IndexError:
            print('Not enough instances of {} with {} \'{}\'. Reduce your '
                  'numbers.'.format(tag, attribute, attribute_name))
            sys.exit()
    return info


def get_raw_table(league):
    '''
    Gets the league table link and processes it. Makes
    a raw version of the table in a list
    '''
    if league is False:
        from requests_local import requests_session as requests
        link = 'file://testfiler/tabell.html'
        req = requests.get(link)
        soup = bs(req.content, 'html5lib', from_encoding="utf-8")
        table = soup.find('table').find('tbody').find_all('tr')
    else:
        global aof_domain
        table = get_linksoup(
            link='http://www.altomfotball.no/elementsCommonAjax.do?cmd=table&'
                 'tournamentId={}'.format(league),
            tag='table',
            attribute='class',
            attribute_name='sd_table').find('tbody').find_all('tr')
    # Get all the info you need for the table
    full_table = []
    temp_table = []
    for item in table:
        cols = item.find_all('td')
        place = cols[0].text.strip().replace('.', '')
        # altomfotball.no uses a no-break space some places in the team name
        # instead of a normal space
        team = cols[1].text.strip().replace(u'\xa0', ' ')
        flair = '[](/flair-{})'.format(flair_name(team))
        matches = cols[2].text.strip()
        w = cols[3].text.strip()
        d = cols[4].text.strip()
        l = cols[5].text.strip()
        plus = cols[6].text.strip()
        minus = cols[7].text.strip()
        diff = cols[8].text.strip()
        points = cols[9].text.strip()
        _form = cols[10].find_all('a')
        form = []
        for match in _form[len(_form) - 5:len(_form)]:
            form_res = match['class'][1][3:]
            form_title = match['title']
            form_link = '{}{}'.format(aof_domain, match['href'])
            form_text = ''
            if form_res == 'won':
                form_text = 'S'
            if form_res == 'draw':
                form_text = 'U'
            if form_res == 'lost':
                form_text = 'T'
            form.append('[{}]({} \'{}\')'.format(form_text, form_link,
                                                 form_title))
        temp_table = {'place': place, 'team': team, 'flair': flair,
                      'matches': matches, 'w': w, 'd': d, 'l': l,
                      'plus': plus, 'minus': minus, 'diff': diff,
                      'points': points, 'form': form, 'versus': ''}
        full_table.append(temp_table)
        temp_table = []
    return full_table


def get_table(table_input, round_input):
    table = []
    for row in table_input:
        for match in round_input:
            if row['team'] == match['home']:
                row['versus'] = '{} ({}) hjemme'.format(match['away'], match['away_table'])
                break
            elif row['team'] == match['away']:
                row['versus'] = '{} ({}) borte'.format(match['home'], match['home_table'])
                break
        table.append(row)
    return table


def get_full_round(table_input, round_input):
    '''
    Adds information about form and table placement to round info
    '''
    versus = []
    # Get the versus-info
    for round_item in round_input:
        home_team = round_item['home']
        away_team = round_item['away']
        for row in table_input:
            _form = row['form']
            form = ''
            if row['team'] == home_team:
                # Add table placement for home_team to round_item
                round_item['home_table'] = row['place']
                # Add form for home_team to round_item
                for form_item in _form:
                    form += form_item
                round_item['home_form'] = form
            if row['team'] == away_team:
                # Add table placement for away_team to round_item
                round_item['away_table'] = row['place']
                # Add form for away_team to round_item, but reversed
                for form_item in reversed(_form):
                    form += form_item
                round_item['away_form'] = form
        versus.append(round_item)
    return versus


def get_matches(league):
    '''
    Get the league name and all matches from 'league'
    '''
    if league is False:
        from requests_local import requests_session as requests
        link = 'file://testfiler/runde.html'
        req = requests.get(link)
        soup = bs(req.content, 'html5lib', from_encoding="utf-8")
        matches = soup.find('table').find_all('tr')
    else:
        global aof_domain
        matches = get_linksoup(
            link='http://www.altomfotball.no/elementsCommonAjax.do?cmd='
                 'fixturesContent&tournamentId={}'.format(league),
            tag='table',
            attribute='class',
            attribute_name='sd_fixtures').find('tbody').find_all('tr')
    all_matches = []
    temp_match = []
    for item in matches:
        cols = item.find_all('td')
        league_name = cols[2].text.strip()
        date = cols[0].text.strip()
        if date == '':
            date = temp_date
        else:
            temp_date = date
        round_no = cols[1].text.strip().replace('. runde', '')\
            .replace(u'\xa0', ' ')
        home = cols[3].text.strip().replace(u'\xa0', ' ')
        away = cols[5].text.strip().replace(u'\xa0', ' ')
        status_link = '{}{}'.format(aof_domain, cols[4].find('a')['href'])
        status_text = cols[4].text.strip().replace(u'\xa0', ' ')
        channel = cols[6].text.strip().replace(u'\xa0', ' ')
        tv2sumo = cols[7].text.strip().replace(u'\xa0', ' ')
        temp_match = {'round_no': round_no, 'date': date, 'home': home,
                      'home_table': '', 'home_form': '',
                      'status_text': status_text, 'status_link': status_link,
                      'away': away, 'away_table': '', 'away_form': '',
                      'channel': channel, 'tv2sumo': tv2sumo}
        all_matches.append(temp_match)
        temp_match = []
    return {'league_name': league_name, 'all_matches': all_matches}


def get_raw_round(league, matches, postponed_file):
    '''
    Get this round\'s matches. Returns 'round_matches' and 'active_round'
    as kwargs.
    '''
    global nowdate, uselog
    active_round = ''

    # If the round is starting within the next two days, start scraping
    for match in matches:
        _days_to = calculating.days_to(nowdate, match['date'])
        if _days_to >= 0:
            if _days_to < 3:
                active_round = match['round_no']
                break
            else:
                uselog('The next round doesn\'t start until {} days.'
                       .format(_days_to))
                sys.exit()
        else:
            uselog('The next round doesn\'t start until {} days.'
                   .format(_days_to))
            sys.exit()
    active_round = '19'
    round_matches = []
#    postponed_matches = []
#    temp_postponed_matches = []
    last_match_date = ''
    for match in matches:
        if match['round_no'] == active_round:
            match_link = match['status_link']
            # Get extra info from match page
            #match.append(match_info(match_link)['time'])
            if league is False:
                #####
                print(match)
                sys.exit()
                #####
                match['match_info_time'] = match['status_text']
            else:
                match['match_info_time'] = match_info(match_link)['time']
            match_date = '{} {}.00'.format(match['date'],
                                           match['match_info_time'])
#            # Check if the match is more than 6 days
#            # away from the last match checked
#            if last_match_date == '':
#                last_match_date = match_date
#            elif calculating.days_to(last_match_date, match_date) >= 6:
#                # If more than 6 days to match, add to postponed-file
#                _postponed_matches = read_cache(postponed_file)
#                _postponed_link = match[1][5]
#                _postponed_versus = '{} vs {}'.format(match[1][1], match[1][6])
#                print('postponing match \'{}\''.format(_postponed_versus))
#                if str(match[1]) in _postponed_matches:
#                    continue
#                else:
#                    _temp_postponed = '{}, '.format(league)
#                    for objects in match:
#                        for item in objects:
#                            _temp_postponed += '{}, '.format(item)
#                    _temp_postponed = re.sub(r', $', r'', _temp_postponed,
#                                             flags=re.MULTILINE | re.DOTALL)
#            else:
#                last_match_date = match_date
            round_matches.append(match)
    return {'round_matches': round_matches, 'active_round': active_round}


def match_info(link):
    '''Get specific info about the match only available on it's match page'''
    match_soup = get_linksoup(
        link=link,
        tag='div',
        attribute='id',
        attribute_name='sd_live')
    topbox = match_soup.find('div', attrs={'id': 'sd_header'})\
        .find('tr', attrs={'class': 'sd_game_small'})

    dateandtime = topbox.find('td', attrs={'class': 'sd_game_away'})\
        .text.strip()
    time = re.search(r'.*kl. (.*)$', dateandtime).group(1)

    stadion_tilsk = topbox.find('td', attrs={'class': 'sd_game_home'})
    stadion_tilsk = str(stadion_tilsk).replace('<td class="sd_game_home">'
                                               '\n\t\t\t\t', '')\
        .replace('</td>', '').replace(u'\xa0', '').split('<br/>')
    stadion = stadion_tilsk[0]

#    try:
#        lineup = match_soup.find('div', attrs={'id': 'aof_teamsetup'})
#        home_lineup = lineup.find('div', attrs={'class': 'homePlayers'}).find_all('tr')
#        for _player in home_lineup:
#            player = _player.find_all('td')[1].text.strip()
#            player = re.search(r'\w\. (.*)\s\(\d+\)', player).group(1)
#            print(player)
#            formation = lineup.find('div', attrs={'class': 'formationHomeTeam'}).text
#        print(str(formation).replace('Formasjon: ', ''))
#
#            #print(player[0])
#            #player = '{}'.format('test')
#    except:
#        pass

    return {'time': time, 'stadion': stadion}


def flair_name(team):
    '''Make a flairname of teamname'''
    team = team.lower().replace('æ', 'ae')\
                       .replace('ø', 'oe')\
                       .replace('å', 'aa')\
                       .replace(u'\xa0', '-')\
                       .replace("'", '')\
                       .replace(' ', '-')\
                       .replace('/', '-')\
                       .replace('-bk', '')
    return team


if __name__ == "__main__":
    print(scraping.match_info('http://www.altomfotball.no/element.do?cmd=match&matchId=865786&tournamentId=1&seasonId=339&useFullUrl=false'))