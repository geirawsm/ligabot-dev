#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''Denne fila lager enkle testfiler og starter en interaktiv manuell
runde-oppdatering'''
import re
import datetime
import os
from bs4 import BeautifulSoup as bs
import sys
import random
import ligabot.uselog
import ligabot.config

uselog = ligabot.uselog.uselog
config = ligabot.config.get_config()

filedir = os.path.dirname(os.path.abspath(__file__)) + '/testfiler'
if not os.path.isdir(filedir):
    os.makedirs(filedir)

runde_text = '''<table id="sd_fixtures">
    <tbody>
        <tr class="sd_odd">
            <td class="sd_fixtures_date"><span><div class="kamp1dato"></div></span></td>
            <td class="sd_fixtures_round"><span>3. runde</span></td>
            <td class="sd_fixtures_tournament">Eliteserien</td>
            <td class="sd_fixtures_home"><div class="kamp1hlag"></div></td>
            <td class="sd_fixtures_score">
                <a href="kamp1link" class="sd_fixtures_score"><div class="kamp1stilling"></div class="kamp1stilling"></a></td>
            <td class="sd_fixtures_away">
                <div class="kamp1blag"></div></td>
            <td class="sd_fixtures_channels"><span><div class="kamp1tv"></div></span></td>
            <td class="sd_fixtures_sumo">
                <a class="Se kampen på Sumo1" href="http://www.FAKE_LINK.wtf&amp;referrer=altomfotball.no" target="_blank"></a>
            </td>
            <td class="sd_fixtures_tid"><div class="kamp1tid"></div></a></td>
        </tr>
        <tr class="sd_even">
            <td class="sd_fixtures_date"><span><div class="kamp2dato"></div></span></td>
            <td class="sd_fixtures_round"><span>3. runde</span></td>
            <td class="sd_fixtures_tournament">Eliteserien</td>
            <td class="sd_fixtures_home"><div class="kamp2hlag"></div></td>
            <td class="sd_fixtures_score">
                <a href="kamp2link" class="sd_fixtures_score"><div class="kamp2stilling"></div class="kamp2stilling"></a></td>
            <td class="sd_fixtures_away">
                <div class="kamp2blag"></div></td>
            <td class="sd_fixtures_channels"><span><div class="kamp2tv"></div></span></td>
            <td class="sd_fixtures_sumo">
                <a class="Se kampen på Sumo2" href="http://www.FAKE_LINK.wtf&amp;referrer=altomfotball.no" target="_blank"></a>
            </td>
            <td class="sd_fixtures_tid"><div class="kamp2tid"></div></a></td>
        </tr>
        <tr class="sd_odd">
            <td class="sd_fixtures_date"><span><div class="kamp3dato"></div></span></td>
            <td class="sd_fixtures_round"><span>3. runde</span></td>
            <td class="sd_fixtures_tournament">Eliteserien</td>
            <td class="sd_fixtures_home"><div class="kamp3hlag"></div></td>
            <td class="sd_fixtures_score">
                <a href="kamp3link" class="sd_fixtures_score"><div class="kamp3stilling"></div class="kamp3stilling"></a></td>
            <td class="sd_fixtures_away">
                <div class="kamp3blag"></div></td>
            <td class="sd_fixtures_channels"><span><div class="kamp3tv"></div></span></td>
            <td class="sd_fixtures_sumo">
                <a class="Se kampen på Sumo3" href="http://www.FAKE_LINK.wtf&amp;referrer=altomfotball.no" target="_blank"></a>
            </td>
            <td class="sd_fixtures_tid"><div class="kamp3tid"></div></a></td>
        </tr>
        <tr class="sd_even">
            <td class="sd_fixtures_date"><span><div class="kamp4dato"></div></span></td>
            <td class="sd_fixtures_round"><span>3. runde</span></td>
            <td class="sd_fixtures_tournament">Eliteserien</td>
            <td class="sd_fixtures_home"><div class="kamp4hlag"></div></td>
            <td class="sd_fixtures_score">
                <a href="kamp4link" class="sd_fixtures_score"><div class="kamp4stilling"></div class="kamp4stilling"></a></td>
            <td class="sd_fixtures_away">
                <div class="kamp4blag"></div></td>
            <td class="sd_fixtures_channels"><span><div class="kamp4tv"></div></span></td>
            <td class="sd_fixtures_sumo">
                <a title="Se kampen på Sumo4" href="http://www.FAKE_LINK.wtf&amp;referrer=altomfotball.no" target="_blank"></a>
            </td>
            <td class="sd_fixtures_tid"><div class="kamp3tid"></div></a></td>
        </tr>
    </tbody>
</table>'''

tabell_text = '''<table id="sd_table_liga" class="sd_table sd_sortable sd_sortabletable" border="0" summary="Tabell" cellspacing="0" cellpadding="0">
    <thead>
        <tr>
            <th class="sd_table_rank">&nbsp;</th>
            <th class="sd_table_team">Lag</th>
            <th title="Kamper">K</th>
            <th title="Vunnet">V</th>
            <th title="Uavgjorte">U</th>
            <th title="Tapte">T</th>
            <th title="M&aring;l for">+</th>
            <th title="M&aring;l mot">-</th>
            <th title="M&aring;lforskjell">+/-</th>
            <th class="sd_table_points" title="Poeng">P</th>
            <th class="sd_left">Siste Kamper</th></tr></thead>
    <tbody>
        <tr class="sd_table_up sd_odd">
            <td class="sd_table_new">1.</td>
            <td class="sd_table_team">[lag1]</td>
            <td>2</td>
            <td>2</td>
            <td>0</td>
            <td>0</td>
            <td>4</td>
            <td>0</td>
            <td>+4</td>
            <td class="sd_table_points">6</td>
            <td class="sd_left" style="padding-right: 0;">
                <div class="sd_table_trend_wrap"><a class="sd_table_trend sd_won" href="http://www.FAKE_LINK.wtf" title="13.03: S08-FKH&nbsp;0-1">&nbsp;</a> <a class="sd_table_trend sd_won" href="http://www.FAKE_LINK.wtf" title="19.03: FKH-AaFK&nbsp;3-0">&nbsp;</a></div></td></tr>
        <tr class="sd_table_none sd_even">
            <td class="sd_table_new">2.</td>
            <td class="sd_table_team">[lag2]</td>
            <td>2</td>
            <td>1</td>
            <td>1</td>
            <td>0</td>
            <td>3</td>
            <td>1</td>
            <td>+2</td>
            <td class="sd_table_points">4</td>
            <td class="sd_left" style="padding-right: 0;">
                <div class="sd_table_trend_wrap"><a class="sd_table_trend sd_won" href="http://www.FAKE_LINK.wtf" title="13.03: B/G-SOG&nbsp;2-0">&nbsp;</a> <a class="sd_table_trend sd_draw" href="http://www.FAKE_LINK.wtf" title="20.03: LSK-B/G&nbsp;1-1">&nbsp;</a></div></td></tr>
        <tr class="sd_table_none sd_odd">
            <td class="sd_table_new">3.</td>
            <td class="sd_table_team">[lag3]</td>
            <td>2</td>
            <td>1</td>
            <td>1</td>
            <td>0</td>
            <td>2</td>
            <td>0</td>
            <td>+2</td>
            <td class="sd_table_points">4</td>
            <td class="sd_left" style="padding-right: 0;">
                <div class="sd_table_trend_wrap"><a class="sd_table_trend sd_won" href="http://www.FAKE_LINK.wtf" title="14.03: VIF-VIK&nbsp;0-2">&nbsp;</a> <a class="sd_table_trend sd_draw" href="http://www.FAKE_LINK.wtf" title="20.03: VIK-S08&nbsp;0-0">&nbsp;</a></div></td></tr>
        <tr class="sd_table_none sd_even">
            <td class="sd_table_new">4.</td>
            <td class="sd_table_team">[lag4]</td>
            <td>2</td>
            <td>1</td>
            <td>1</td>
            <td>0</td>
            <td>3</td>
            <td>2</td>
            <td>+1</td>
            <td class="sd_table_points">4</td>
            <td class="sd_left" style="padding-right: 0;">
                <div class="sd_table_trend_wrap"><a class="sd_table_trend sd_draw" href="http://www.FAKE_LINK.wtf" title="13.03: MOL-TIL&nbsp;1-1">&nbsp;</a> <a class="sd_table_trend sd_won" href="http://www.FAKE_LINK.wtf" title="20.03: STB-MOL&nbsp;1-2">&nbsp;</a></div></td></tr>
        <tr class="sd_table_none sd_odd">
            <td class="sd_table_new">5.</td>
            <td class="sd_table_team">[lag5]</td>
            <td>2</td>
            <td>1</td>
            <td>1</td>
            <td>0</td>
            <td>1</td>
            <td>0</td>
            <td>+1</td>
            <td class="sd_table_points">4</td>
            <td class="sd_left" style="padding-right: 0;">
                <div class="sd_table_trend_wrap"><a class="sd_table_trend sd_won" href="http://www.FAKE_LINK.wtf" title="12.03: ODD-RBK&nbsp;1-0">&nbsp;</a> <a class="sd_table_trend sd_draw" href="http://www.FAKE_LINK.wtf" title="20.03: BRA-ODD&nbsp;0-0">&nbsp;</a></div></td></tr>
        <tr class="sd_table_none sd_even">
            <td class="sd_table_new">6.</td>
            <td class="sd_table_team">[lag6]</td>
            <td>2</td>
            <td>1</td>
            <td>0</td>
            <td>1</td>
            <td>1</td>
            <td>1</td>
            <td>0</td>
            <td class="sd_table_points">3</td>
            <td class="sd_left" style="padding-right: 0;">
                <div class="sd_table_trend_wrap"><a class="sd_table_trend sd_lost" href="http://www.FAKE_LINK.wtf" title="12.03: ODD-RBK&nbsp;1-0">&nbsp;</a><a class="sd_table_trend sd_won" href="http://www.FAKE_LINK.wtf" title="19.03: RBK-SIF&nbsp;1-0">&nbsp;</a></div></td></tr>
        <tr class="sd_table_none sd_odd">
            <td class="sd_table_new">7.</td>
            <td class="sd_table_team">[lag7]</td>
            <td>2</td>
            <td>1</td>
            <td>0</td>
            <td>1</td>
            <td>1</td>
            <td>2</td>
            <td>-1</td>
            <td class="sd_table_points">3</td>
            <td class="sd_left" style="padding-right: 0;">
                <div class="sd_table_trend_wrap"><a class="sd_table_trend sd_lost" href="http://www.FAKE_LINK.wtf" title="13.03: B/G-SOG&nbsp;2-0">&nbsp;</a><a class="sd_table_trend sd_won" href="http://www.FAKE_LINK.wtf" title="20.03: SOG-VIF&nbsp;1-0">&nbsp;</a></div></td></tr>
        <tr class="sd_table_none sd_even">
            <td class="sd_table_new">8.</td>
            <td class="sd_table_team">[lag8]</td>
            <td>2</td>
            <td>1</td>
            <td>0</td>
            <td>1</td>
            <td>1</td>
            <td>3</td>
            <td>-2</td>
            <td class="sd_table_points">3</td>
            <td class="sd_left" style="padding-right: 0;">
                <div class="sd_table_trend_wrap"><a class="sd_table_trend sd_won" href="http://www.FAKE_LINK.wtf" title="11.03: AaFK-STB&nbsp;1-0">&nbsp;</a><a class="sd_table_trend sd_lost" href="http://www.FAKE_LINK.wtf" title="19.03: FKH-AaFK&nbsp;3-0">&nbsp;</a></div></td></tr></tbody>
</table>'''

kamper = [
# Hjemmelag, bortelag, kamplink
['Sogndal' ,'Rosenborg', 'http://www.altomfotball.no/element.do?cmd=match&matchId=865785&tournamentId=1&seasonId=339&useFullUrl=false' ],
['Lillestrøm' ,'Stabæk', 'http://www.altomfotball.no/element.do?cmd=match&matchId=865786&tournamentId=1&seasonId=339&useFullUrl=false' ],
['Molde' ,'Strømsgodset', 'http://www.altomfotball.no/element.do?cmd=match&matchId=865790&tournamentId=1&seasonId=339&useFullUrl=false' ],
['Haugesund' ,'Aalesund', 'http://www.altomfotball.no/element.do?cmd=match&matchId=865789&tournamentId=1&seasonId=339&useFullUrl=false' ]
]

lag = []
for kamp in kamper:
    lag.append(kamp[0])
    lag.append(kamp[1])


def lag_runde_fil():
    filnavn = 'runde.html'
    global runde_text, config
    i = 0
    for kamp in kamper:
        i += 1
        if i == 1:
            runde_text = update(runde_text, i, 'dato', add_time(int(config['testfiler']['kamp1timer']), int(config['testfiler']['kamp1minutter']), 0)['dato'])
            runde_text = update(runde_text, i, 'hlag', kamp[0])
            runde_text = update(runde_text, i, 'link', kamp[2])
            runde_text = update(runde_text, i, 'stilling', add_time(int(config['testfiler']['kamp1timer']), int(config['testfiler']['kamp1minutter']), 0)['tid'])
            runde_text = update(runde_text, i, 'blag', kamp[1])
            runde_text = update(runde_text, i, 'tid', '({})'.format(add_time(int(config['testfiler']['kamp1timer']), int(config['testfiler']['kamp1minutter']), 0)['tid']))
        if i == 2:
            runde_text = update(runde_text, i, 'dato', add_time(int(config['testfiler']['kamp2timer']), int(config['testfiler']['kamp2minutter']), 0)['dato'])
            runde_text = update(runde_text, i, 'hlag', kamp[0])
            runde_text = update(runde_text, i, 'link', kamp[2])
            runde_text = update(runde_text, i, 'stilling', add_time(int(config['testfiler']['kamp2timer']), int(config['testfiler']['kamp2minutter']), 0)['tid'])
            runde_text = update(runde_text, i, 'blag', kamp[1])
            runde_text = update(runde_text, i, 'tid', '({})'.format(add_time(int(config['testfiler']['kamp2timer']), int(config['testfiler']['kamp2minutter']), 0)['tid']))
        if i == 3:
            runde_text = update(runde_text, i, 'dato', add_time(int(config['testfiler']['kamp3timer']), int(config['testfiler']['kamp3minutter']), 0)['dato'])
            runde_text = update(runde_text, i, 'hlag', kamp[0])
            runde_text = update(runde_text, i, 'link', kamp[2])
            runde_text = update(runde_text, i, 'stilling', add_time(int(config['testfiler']['kamp3timer']), int(config['testfiler']['kamp3minutter']), 0)['tid'])
            runde_text = update(runde_text, i, 'blag', kamp[1])
            runde_text = update(runde_text, i, 'tid', '({})'.format(add_time(int(config['testfiler']['kamp3timer']), int(config['testfiler']['kamp3minutter']), 0)['tid']))
        if i == 4:
            runde_text = update(runde_text, i, 'dato', add_time(int(config['testfiler']['kamp4timer']), int(config['testfiler']['kamp4minutter']), 0)['dato'])
            runde_text = update(runde_text, i, 'hlag', kamp[0])
            runde_text = update(runde_text, i, 'link', kamp[2])
            runde_text = update(runde_text, i, 'stilling', add_time(int(config['testfiler']['kamp4timer']), int(config['testfiler']['kamp4minutter']), 0)['tid'])
            runde_text = update(runde_text, i, 'blag', kamp[1])
            runde_text = update(runde_text, i, 'tid', '({})'.format(add_time(int(config['testfiler']['kamp4timer']), int(config['testfiler']['kamp4minutter']), 0)['tid']))
    if not os.path.exists(filedir + '/' + filnavn):
        write_out = open(filedir + '/' + filnavn, 'w').close()
    write_output(runde_text, filnavn)

def lag_tabellfil():
    filnavn = 'tabell.html'
    global tabell_text
    i = 0
    for nr_lag in lag:
        i += 1
        tabell_text  = re.sub('\[lag' + str(i) + ']', nr_lag, tabell_text, flags=re.MULTILINE | re.DOTALL)
    if not os.path.exists(filedir + '/' + filnavn):
        write_out = open(filedir + '/' + filnavn, 'w').close()
    write_output(tabell_text, filnavn)    


def write_output(out, fil):
    global filedir
    write_out = open(filedir + '/' + fil, 'w')
    write_out.write(out)
    write_out.close()


def read_output(fil):
    global filedir
    read_out = open(filedir + '/' + fil, 'r')
    read = read_out.read()
    if read == '':
        uselog('runde_texta er tom, wtf?')
        sys.exit()
    read_out.close()
    return read


def bsify_local(text_in):
    soup = bs(text_in, 'html5lib').find_all('tr')
    i = 0
    matches_out = ''
    for match in soup:
        i += 1
        cols = match.find_all('td')
        hlag = cols[3].text.strip()
        score = cols[4].text.strip()
        blag = cols[5].text.strip()
        matches_out += '{}: {} {} {}'.format(i, hlag, score, blag)
        if i != len(soup):
            matches_out += '\n'
    return matches_out


def add_time(x, y, z):
    dato = (datetime.datetime.now() + datetime.timedelta(hours=x, minutes=y, seconds=z)).strftime("%d.%m.%Y")
    tid = (datetime.datetime.now() + datetime.timedelta(hours=x, minutes=y, seconds=z)).strftime("%H.%M")
    return{'dato': dato, 'tid': tid}


def update(runde_text, i, tag, add):
    #output = re.sub('<div class="kamp{i}{tag}">[a-zA-ZæøåÆØÅ0-9 \.-]+<\/div>'.format(i=i, tag=tag),
    output = re.sub('<div class="kamp{i}{tag}">'.format(i=i, tag=tag),
                    '<div class="kamp{i}{tag}">{add}'.format(i=i, tag=tag, add=add),
                    runde_text, flags=re.DOTALL)
    return output


def update_score(no_of_matches, match_no=False, res=False):
    global filedir
    filnavn = 'runde.html'
    runde_text = read_output(filnavn)
    if match_no == 'c':
        while no_of_matches > 0:
            runde_text = re.sub('<div class="kamp{match_no}stilling">.*</div class="kamp{match_no}stilling">'.format(match_no=no_of_matches),
                                '<div class="kamp{match_no}stilling">(0-0)</div class="kamp{match_no}stilling">'.format(match_no=no_of_matches, add=res),
                                runde_text, flags=re.MULTILINE | re.DOTALL)
            no_of_matches -= 1

    if match_no == 'x' or res == 'x':
        while no_of_matches > 0:
            ran1 = random.randrange(0,4)
            ran2 = random.randrange(0,4)
            runde_text = re.sub('<div class="kamp{match_no}stilling">.*</div class="kamp{match_no}stilling">'.format(match_no=no_of_matches),
                                '<div class="kamp{match_no}stilling">{ran1}-{ran2}</div class="kamp{match_no}stilling">'.format(match_no=no_of_matches, add=res, ran1=ran1, ran2=ran2),
                                runde_text, flags=re.MULTILINE | re.DOTALL)
            no_of_matches -= 1

    if match_no == 'alle':
        while no_of_matches > 0:
            runde_text = re.sub('<div class="kamp{match_no}stilling">.*</div class="kamp{match_no}stilling">'.format(match_no=no_of_matches),
                                '<div class="kamp{match_no}stilling">{add}</div class="kamp{match_no}stilling">'.format(match_no=no_of_matches, add=res),
                                runde_text, flags=re.MULTILINE | re.DOTALL)
            no_of_matches -= 1

    runde_text = re.sub('<div class="kamp{match_no}stilling">.*</div class="kamp{match_no}stilling">'.format(match_no=match_no),
                        '<div class="kamp{match_no}stilling">{add}</div class="kamp{match_no}stilling">'.format(match_no=match_no, add=res),
                        runde_text, flags=re.MULTILINE | re.DOTALL)
    write_output(runde_text, filnavn)


try:
    oppdater_runde = str(sys.argv[1])
except IndexError:
    oppdater_runde = False
if oppdater_runde == 'nei':
    pass
else:
    lag_runde_fil()
lag_tabellfil()

# Manuell rundeoppdatering
uselog('Runden er laget.')

while True:
    # åpne fil og hent info om kamper
    round_file = bsify_local(read_output('runde.html'))
    print(round_file)
    print('Hvilken kamp ønsker du å endre resultatet til? (1-4, alle, '
          'c=start runden, x=avslutt runden)')
    match_no = input()
    if match_no == 'c':
        update_score(no_of_matches=len(round_file.split('\n')), match_no='c')
        continue
    elif match_no == 'x':
        update_score(no_of_matches=len(round_file.split('\n')), match_no='x')
        continue
    print('Hva skal settes som nytt resultat?')
    res = input()
    update_score(len(round_file.split('\n')), match_no=match_no, res=res)
