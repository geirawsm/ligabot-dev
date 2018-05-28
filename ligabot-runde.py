#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from bs4 import BeautifulSoup as bs
import datetime
from time import sleep
import praw
import re
import os
import html
import traceback
logging = True
logging_print = True
try:
    import syslog

    def uselog(message):
        if logging:
            if logging_print:
                print('{} {}'.format(
                    datetime.datetime.now().strftime("%d.%m.%Y %H.%M.%S"),
                    message))
            else:
                try:
                    syslog.syslog(message)
                except:
                    print('Prøvde å logge følgende feilmelding, men en ekstra feil skjedde:\n{}'.format(message))

except ImportError:
    uselog("Kunne ikke importere \'syslog\'")
    sys.exit()
try:
    from userinfo import reddit
except:
    uselog('Klarte ikke å hente filen \'userinfo.py\'. Les mer i readme:\n'
           'https://github.com/armandg/ligabot/blob/master/README.md\n'
           'Avslutter...')
    sys.exit()

filename = os.path.basename(__file__)
filedir = os.path.dirname(os.path.abspath(__file__))

nowdate = datetime.datetime.now().strftime("%d.%m.%Y")
fulldate = datetime.datetime.now().strftime("%d.%m.%Y.%H.%M.%S")


## TEMPSKRIVING ###
def skriv_runde(navn, tekst):
    write_out = open(filedir + '/testfiler/' + navn, 'w')
    write_out.write(tekst)
    write_out.close()
### TEMPSKRIVING ###


def strip_team(name):
    '''Vask av lagnavn'''
    name = name.replace(u'\xa0', '-')\
               .replace("'", '')\
               .replace(' ', '-')\
               .replace('/', '-')\
               .replace('-bk', '')\
               .replace('-tf', '')
    return name


def seconds_to(d1):
    '''Finner antall sekunder fra nå til dato i "d1"'''
    d1 = d1.split('.')
    d1.append('00')
    d2 = datetime.datetime.now().strftime("%d.%m.%Y.%H.%M.%S").split('.')
    date_1 = datetime.datetime(
        int(d1[2]), int(d1[1]), int(d1[0]),  # År, måned, dag
        int(d1[3]), int(d1[4]), int(d1[5])   # Timer, minutter, sekunder
    )
    date_2 = datetime.datetime(
        int(d2[2]), int(d2[1]), int(d2[0]),  # År, måned, dag
        int(d2[3]), int(d2[4]), int(d1[5])  # Timer, minutter, sekunder
    )
    return (date_1 - date_2).total_seconds()


def days_to(d1, d2):
    '''Finner antall dager mellom dato "d1" og "d2"'''
    d1 = d1.split('.')
    d2 = d2.split('.')
    d1 = datetime.datetime(int(d1[2]), int(d1[1]), int(d1[0]))
    d2 = datetime.datetime(int(d2[2]), int(d2[1]), int(d2[0]))
    return (d1 - d2).days


def days_count(d1, calc):
    '''Finn ny dato basert på "d1" ved å legge til eller trekke fra 4 dager'''
    d1 = d1.split('.')
    d1 = datetime.datetime(int(d1[2]), int(d1[1]), int(d1[0]))
    if calc == 'sub':
        newdate = d1 - datetime.timedelta(4)
    elif calc == 'add':
        newdate = d1 + datetime.timedelta(4)
    return newdate


def kamp_slutt_tid(fulldate, add):
    # Ta imot en dato, legg til antall sekunder, returner ny dato og tid
    fulldate = fulldate.split('.')
    fulldate = datetime.datetime(
        int(fulldate[2]), int(fulldate[1]),
        int(fulldate[0]), int(fulldate[3]),
        int(fulldate[4]), 00)
    newdate = fulldate + datetime.timedelta(0, int(add))
    return newdate


def bsify(url, table_id):
    '''Finner tabell-info fra oppgitt url på oppgitt id'''
    req = requests.get(url)
    soup = bs(req.content, 'html5lib', from_encoding="utf-8")
    table = soup.find('table', attrs={'id': table_id}).find('tbody')\
        .find_all('tr')
    return {'table': table, 'length': len(table)}


def rundebs():
    '''Finner ut hvilken runde som er nærmest i tid og henter rundens url'''
    global rundenr
    if testmodus:
        rundeurl = 'file://testfiler/runde.html'
        return {'rundenr': rundenr, 'rundeurl': rundeurl}
    else:
        termin_bs = bsify(terminliste_url, 'sd_fixtures_table')['table']
        for row in termin_bs:
            runde_cols = row.find_all('td')
            matchdate = runde_cols[0].text.strip()
            rundenr = runde_cols[1].text.strip().replace('. runde', '')
            if matchdate == "":
                matchdate = tempdate
            else:
                tempdate = matchdate
            days_to_next_round = days_to(matchdate, nowdate)
            # Hvis det er innenfor tidsrommet på 0-2 dager, gå videre
            # med scriptet
            if days_to_next_round < 0:
                    continue
            if days_to_next_round > 2:
                uselog('Neste runde starter ikke før om {} dager, den {} '
                       '. Avslutter.'.format(days_to_next_round, matchdate))
                sys.exit()
            uselog('Fant korrekt runde: {} ({})'.format(rundenr, matchdate))
            rundeurl = 'http://www.altomfotball.no/elementsCommonAja'\
                'x.do?cmd=fixturesContent&tournamentId={}&roundNo={}'\
                '&useFullUrl=false'.format(liga, rundenr)
            return {'rundenr': rundenr, 'rundeurl': rundeurl}


def createNecessaryFiles(*args):
    '''Lag filer som er nødvendige for scripet'''
    for count, filename in enumerate(args):
        wantedFile = filename
        if not os.path.exists(filedir + '/' + wantedFile):
            uselog('Filen {} eksisterer ikke. Lages...'.format(wantedFile))
            write_out = open(filedir + '/' + wantedFile, 'w').close()
            try:
                write_out = open(filedir + '/' + wantedFile, 'w')
                write_out.write(eval(filename))
                write_out.close()
            except(NameError):
                pass
        else:
            uselog('Filen {} finnes allerede.'.format(wantedFile))


def threadAlreadyCreated(subreddit):
    '''Sjekker om det allerede er laget rundetråd for runden'''
    global liganavn
    stikkord = ['Dato', 'Hjemmelag', 'Bortelag', 'TV-kanal/Streaming']
    subreddit = r.subreddit(subreddit)
    for submission in subreddit.new(limit=40):
        if rundenr in submission.title and liganavn[0] in submission.title:
            if all(word.lower() in str(submission.selftext).lower()
                for word in stikkord):
                    return submission.id
        else:
            continue

# Lag liga-fil basert på liga-input
try:
    try:
        # Hent liganr fra input
        uselog('Henter liganr fra input...')
        liga = str(sys.argv[1])
        testmodus = False
        import requests
        tabell_url = 'http://www.altomfotball.no/elementsCommonAjax.do?cmd='\
            'table&tournamentId=' + str(liga) + '&subCmd=total&live=true&'\
            'useFullUrl=false'
        terminliste_url = 'http://www.altomfotball.no/elementsCommonAjax.do?'\
            'cmd=fixturesContent&tournamentId=' + str(liga) + '&month=all&'\
            'useFullUrl=false'
    except:
        # Hvis input mangler, kjør med testverdier
        uselog('Klarte ikke å hente liganr fra input. Starter testmodus...')
        liga = 'test'
        testmodus = True
        from requests_local import requests_session as requests
        try:
            tabell_url = 'file://testfiler/tabell.html'
        except:
            uselog('Klarte ikke å hente lokale testfiler')
            sys.exit()
        rundenr = '3'
        uselog('Requests_local aktivert')
    # Sjekk om liga-fila til ligaen eksisterer, hvis ikke så lag den
    ligafil = 'liga_{}.py'.format(liga)
    createNecessaryFiles(ligafil)
    # Hent tabell fra tabellside
    har_tabell = True
    if testmodus:
        tabell_bs = bsify(tabell_url, 'sd_table_liga')['table']
    else:
        tabell_bs = bsify(tabell_url, 'sd_table_{}'.format(liga))['length']
        if tabell_bs > 22:
            har_tabell = False
            uselog('Henter ikke tabell, annen turneringsmodus')
        else:
            uselog('Henter tabell')
            tabell_bs = bsify(tabell_url, 'sd_table_{}'.format(liga))['table']
    uselog('Henter terminliste')
    terminliste_bs = bsify(terminliste_url, 'sd_fixtures_table')
except Exception as e:
    uselog('Klarte ikke å hente tabell og terminliste: {}'.format(e))
    uselog(traceback.print_exc())
    sys.exit()

# Finn liganavn
if testmodus:
    liganavn = 'Liksomligaen'
    rundenr = '3'
    reddit_post_title = liganavn + ', ' + str(rundenr) + '. runde'
else:
    liganavn_req = requests.get('http://www.altomfotball.no/element.do?cmd='
                                'tournamentTable&tournamentId={}&useFullUrl'
                                '=false'.format(liga))
    liganavn_soup = bs(liganavn_req.content, 'html5lib', from_encoding="utf-8")
    liganavn = liganavn_soup.find('div', attrs={'id': 'sd_league'})\
        .find('h1').text.split('\xa0')
    # Finner tittel til submission
    tittel_rundenr = rundebs()['rundenr']
    reddit_post_title = '{}, {}. runde'.format(liganavn[0], tittel_rundenr)
if har_tabell:
    try:
        forkortelse_fil = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
forkortelse = {'''
        # Finn info om lag i tabellen
        for liga_row in tabell_bs:
            liga_cell = liga_row.find_all('td')
            liga_lag = strip_team(liga_cell[1].text.strip())
            # Lag forkortelse av lagnavnet og sett inn i filen som skal lages
            liga_lag_forkort = liga_lag.replace('\'', '').replace('-', '')
            liga_lag_forkort = liga_lag[0:3].upper()
            if liga_lag_forkort in forkortelse_fil:
                liga_lag_forkort = liga_lag[0:4].upper()
            forkortelse_fil += '\n    \'{}\': \'{}\','.format(liga_lag, liga_lag_forkort)
        forkortelse_fil += '\n}'
        # Skriv forkortelsesinfoen til liga-fila
        write_out = open('{}/{}'.format(filedir, ligafil), 'w')
        write_out.write(forkortelse_fil)
        write_out.close()
        exec('from liga_{} import forkortelse'.format(liga))
    except Exception as e:
        uselog('Klarte ikke å lage forkortelsesfil: {}'.format(e))
        uselog(traceback.print_exc())
        sys.exit()

username = reddit['username']
subreddit = reddit['subreddit']
#subreddit = 'tippeligaensandbox'

try:
    uselog('Logger inn på reddit.')
    r = praw.Reddit(client_id=reddit['client_id'],
                    client_secret=reddit['client_secret'],
                    password=reddit['password'],
                    user_agent=reddit['useragent'],
                    username=reddit['username'])
    uselog('Går videre etter innlogging')
except Exception as e:
    uselog('Klarte ikke å autentisere mot reddit. Feilmelding: {}'.format(e))
    uselog(traceback.print_exc())

output = ""
kampvarighet = 6900
lowest_waiting = None
highest_stoptime = 0

def main():
    # Setter tomme variabler
    global highest_stoptime, reddit_post_title, form, kampvarighet, har_tabell
    runde_result = ""
    hjemme = []
    borte = []
    utsatt = []
    form = {}
    print('har_tabell: {}'.format(har_tabell))
    if har_tabell:
        # Hent plasseringer først og putt i dictionary
        global plassering
        plassering = {}
        for row in tabell_bs:
            tabell_cols = row.find_all('td')
            plass = tabell_cols[0].text.strip()
            plass = plass.replace(".", "")
            lag = strip_team(tabell_cols[1].text.strip())
            # Legg til plassering i dictionary 'plassering'
            plassering[lag] = plass

        # Henter form
        for row in tabell_bs:
            tabell_cols = row.find_all('td')
            lag = strip_team(tabell_cols[1].text.strip())
            lag = forkortelse[lag]
            form_cols = tabell_cols[10]
            kampformer = form_cols.find_all('a')
            form_lag = []
            for kampform in kampformer[-5:len(kampformer)]:
                if 'sd_draw' in kampform['class']:
                    form_lag.append(['U', kampform['title'], kampform['href']])
                elif 'sd_won' in kampform['class']:
                    form_lag.append(['S', kampform['title'], kampform['href']])
                else:
                    form_lag.append(['T', kampform['title'], kampform['href']])
            form[lag] = form_lag

    # Sett tom variabel
    tabellResult = ""
    output = ""
    uselog('---------------')

    if har_tabell:
    # Henter tabellen
        try:
            hjemme = møter_liste()['hjemme']
            borte = møter_liste()['borte']
            for row in tabell_bs:
                tabell_cols = row.find_all('td')
                # Hent palssering og fjern etterfølgende punktum
                plass = tabell_cols[0].text.strip()
                plass = plass.replace(".", "")
                lag = tabell_cols[1].text.strip()
                # Legg til plassering i dictionaryen 'plassering'
                plassering[forkortelse[strip_team(lag)]] = plass
                # Tilpass lagnavn så det er enklere å legge til lag-flair i
                # tabellen, dvs fjern skandinaviske tegn og erstatt mellomrom med
                # bindestrek
                flairlag = strip_team(lag).lower().replace('æ', 'ae')\
                    .replace('ø', 'oe')\
                    .replace('å', 'aa')
                # Finn ut hvilket lag som tabell-laget skal møte
                møter = ""
                if lag in hjemme:
                    hjemmelag = borte[hjemme.index(lag)]
                    kamp_lag = lag + ' - ' + hjemmelag
                    if kamp_lag in utsatt:
                        møter = ""
                    else:
                        if har_tabell:
                            møter = '{} hjemme'.format(hjemmelag)
                        else:
                            møter = '{} ({}) hjemme'.format(
                                hjemmelag,
                                plassering[strip_team(hjemmelag)]
                            )
                elif lag in borte:
                    bortelag = hjemme[borte.index(lag)]
                    kamp_lag = '{} - {}'.format(bortelag, lag)
                    if kamp_lag in utsatt:
                        møter = ""
                    else:
                        if har_tabell:
                            møter = '{} borte'.format(bortelag)
                        else:
                            møter = '{} ({}) borte'.format(
                                bortelag,
                                plassering[strip_team(bortelag)]
                            )
                # Hent resten av infoen for tabellen
                ant_kamper = tabell_cols[2].text.strip()
                vunnet = tabell_cols[3].text.strip()
                uavgjort = tabell_cols[4].text.strip()
                tap = tabell_cols[5].text.strip()
                målpluss = tabell_cols[6].text.strip()
                målminus = tabell_cols[7].text.strip()
                måldiff = tabell_cols[8].text.strip()
                poeng = tabell_cols[9].text.strip()
                møter = møter.replace(" ", "&nbsp;")
                # Slå sammen alle feltene i en linje med separator som er tilpasset
                # tabeller i Reddit
                tabellResult += '{}|[](/flair-{}) {}|{}|{}|{}|{}|{}|{}|{}|{}|{}\n'\
                    .format(
                        plass,
                        flairlag.lower(),
                        lag,
                        ant_kamper,
                        vunnet,
                        uavgjort,
                        tap,
                        målpluss,
                        målminus,
                        måldiff,
                        poeng,
                        møter
                    )
        except Exception as e:
            har_tabell = False
            uselog('Klarte ikke å hente tabellen: {}'.format(e))
            uselog(traceback.print_exc())
        if len(utsatt) > 0:
            output += 'Følgende kamper skulle egentlig spilles denne runden, '\
                'men har blitt utsatt:\n\n'
            for i in range(len(utsatt)):
                output += '- {}\n\n'.format(utsatt[i])
            output += "\n\n&nbsp;"
        output += "**Tabell før runden:**\n\n"
        if liga == '1':
            output += '######[](http://reddit.com#)\n'
        elif liga == '2':
            output += '#####[](http://reddit.com#)\n'
        elif liga == '3':
            output += '###[](http://reddit.com#)\n'
        output += 'Nr|Lag|K|V|U|T|M+|M-|MF|P|Møter\n'
        output += "---:|:---|:---:|---:|---:|---:|---:|---:|---:|:---|:---\n"
        output += tabellResult
        output += "\n\n&nbsp;\n\n"
    output += "**Rundens kamper:**\n\n"
    output += "Dato|Hjemmelag||Bortelag|TV-kanal/Streaming\n"
    output += ":---|---:|:---:|:---|:---\n"
    runde_result = '[](#kamper){}[](/kamper)'.format(runde_sjekk())
    output += runde_result
    output += '\n\n###[](http://reddit.com#)\nHar du forslag til endringer eller ser du feil i denne posten? [Si ifra her!](http://reddit.com/message/compose/?to={}&subject=Tips%20til%20endring/feil%20i%20runde-poster%20%28tl%29)'.format(username)
    uselog('Laga ferdig innholdet til runde-submission, prøver å poste...')

    if threadAlreadyCreated(subreddit):
        subm = r.submission(
            id=str(threadAlreadyCreated(subreddit))
        )
        subm_text = subm.selftext
        nytt_resultat = re.sub(
            '\[\]\(#kamper\)((.|\n)*)\[\]\(\/kamper\)',
            '[](#kamper){}[](/kamper)'.format(runde_sjekk()),
            subm_text,
            flags=re.MULTILINE | re.DOTALL
        )
        subm.edit(nytt_resultat)
        uselog('Tråd for {} er allerede laget. Har overskrevet kamp-tråden'
               ' med ny og korrekt info. Fortsetter med '
               'kampoppdateringene.'.format(reddit_post_title))
    else:
        uselog(
            'Fant ingen tråd som samsvarte med det nye innholder '
            'fra \'{}\'. Poster ny.'.format(reddit_post_title))
        subm = r.subreddit(subreddit).submit(reddit_post_title,  # Tittel på submission
                                             selftext=output,  # Tekst i submission
                                             send_replies=False,  # Boten skal ikke ha svar på
                                                                  # submission i innboksen sin
                                             resubmit=False  # Hvis nøyaktig samme tråd
                                                             # allerede finnes, ikke send inn
                                             )
    subm_link = 'http://redd.it/{}'.format(subm.id)

    # Oppdater rundetråd-linja
    rundetråd_info = '[{}]({})'.format(reddit_post_title, subm_link)
    sidebar = html.unescape(r.subreddit(subreddit).description)
    tråd = False
    if liga == '1':
        tråd = 'runde-elite'
    elif liga == '2':
        tråd = 'runde-obos'
    elif liga == '3':
        tråd = 'runde-topp'
    if tråd:
        new_sidebar = re.sub(
            r'\[\]\(#{tråd}\).*\[\]\(/{tråd}\)'.format(tråd=tråd),
            '[](#{tråd}){info}[](/{tråd})'.format(info=rundetråd_info, tråd=tråd),
            sidebar,
            flags=re.MULTILINE | re.DOTALL
        )
        uselog('Oppdaterer rundetråd-oversikt')
        r.subreddit(subreddit).mod.update(description=new_sidebar)

    # Starter forberedelse til kampkjøring
    uselog('Starter sleep basert på lowest_waiting: ' +
           str(kamp_slutt_tid(fulldate, lowest_waiting)))
    uselog('Scriptet slutter å gå {}'.format(
        kamp_slutt_tid(fulldate, highest_stoptime)))
    if lowest_waiting <= 5:
        uselog('lowest_waiting er lik eller under 5, fortsetter.')
    else:
        uselog('lowest_waiting er mer enn 5. venter i ' +
               str(lowest_waiting) + ' sekunder.')
        sleep(lowest_waiting - 5)
    # Hvis tråden allerede finnes, sjekk at kamp-innholdet stemmer overens med
    # det nyeste du har funnet, før runden starter
    if threadAlreadyCreated(subreddit):
        subm_text = subm.selftext
        nytt_resultat = re.sub(
            '\[\]\(#kamper\)((.|\n)*)\[\]\(\/kamper\)', '[](#kamper){}[](/kamper)'
            .format(runde_sjekk()),
            subm_text,
            flags=re.MULTILINE | re.DOTALL
        )
        subm.edit(nytt_resultat)
        uselog('Har overskrevet kamp-tråden med ny og korrekt info, siden '
               'tråden fantes allerede.')
    temp_runde_result = subm.selftext
    temp_runde_result = re.search(
        r'.*[](#kamper)((.|\n)*)[](/kamper).*', temp_runde_result).group(1)
    while highest_stoptime > 0:
        try:
            runde_result = '[](#kamper){}[](/kamper)'.format(runde_sjekk())
            if runde_result != temp_runde_result:
                uselog('Henta nytt resultat, som er annerledes enn det som '
                       'er lagra. Oppdaterer reddit-post...')
                # Sett i gang oppdatering
                subm_text = subm.selftext
                # Sett inn nytt resultat mellom kamper-taggen
                # ( [](#kamper) [](/kamper) )
                nytt_resultat = re.sub(
                    '\[\]\(#kamper\)((.|\n)*)\[\]\(\/kamper\)',
                    '[](#kamper){}[](/kamper)'.format(runde_result),
                    subm_text,
                    flags=re.MULTILINE | re.DOTALL
                )
                uselog('Fant submission id: {}'.format(subm.id))
                subm.edit(nytt_resultat)
                uselog('Endring registrert og sendt.')
                uselog('Setter ny \'temp_runde_result\'')
                temp_runde_result = runde_result
                status = 'Ferdig med nytt resultat.'
            else:
                status = 'Henta resultat, men ingen endring.'
            uselog('{} Gjenstående tid av runden er {} sekunder, og stopp er'
                   ' {}. Sover i 30 sekunder...'
                   .format(status, highest_stoptime,
                           kamp_slutt_tid(fulldate, highest_stoptime)))
            venter = 30
            sleep(int(venter))
            highest_stoptime -= int(venter)
        except Exception as e:
            uselog('Klarte ikke å kjøre runde_sjekk: {}'.format(e))
            uselog('{}'.format(traceback.print_exc()))
            sys.exit()
    uselog('Kamp-runden ferdig. Avslutter!')
    sys.exit()

def møter_liste():
    '''Henter kun hvem som møter hverandre'''
    hjemme = []
    borte = []
    for row in bsify(rundebs()['rundeurl'], 'sd_fixtures_table')['table']:
        cols = row.find_all('td')
        # Finn hjemmelaget i kampen og legg til lista 'hjemme'
        hlag = cols[3].text.strip()
        hjemme.append(hlag)
        # Finn bortelaget i kampen og legg til lista 'borte'
        blag = cols[5].text.strip()
        borte.append(blag)
    return {'hjemme': hjemme, 'borte': borte} 


def runde_sjekk():
    '''Henter rundens kamper og resultater'''
    sjekk_runde_result = ''
    hjemme = møter_liste()['hjemme']
    borte = møter_liste()['borte']
    utsatt = []
    global har_tabell
    global liga
    global forkortelse
    global kampvarighet
    global lowest_waiting
    global highest_stoptime
    # Hent plasseringer først og putt i dictionary
    global plassering
    for row in bsify(rundebs()['rundeurl'], 'sd_fixtures_table')['table']:
        cols = row.find_all('td')
        # Finn hjemmelaget i kampen og legg til lista 'hjemme'
        hlag = cols[3].text.strip()
        hjemme.append(hlag)
        # Finn bortelaget i kampen og legg til lista 'borte'
        blag = cols[5].text.strip()
        borte.append(blag)
        kamp_lag = '{}-{}'.format(hlag, blag).replace('Æ', 'AE')\
            .replace('Ø', 'OE').replace('Å', 'AA')
        if testmodus:
            matchdate = cols[0].text.strip()
            matchtime = cols[4].text.strip()
            kamp_res = cols[4].text.strip()
            kamplink = cols[4].find('a')['href']
        else:
            resultatlink = cols[4].find('a')['href']
            kamplink = 'http://www.altomfotball.no/{}'.format(resultatlink)
            kamp_req = requests.get(kamplink)
            kamp_soup = bs(kamp_req.content, "html5lib", from_encoding="utf-8")
            # Henter kampdato og setter inn forrige kampdato hvis
            # vanlig kampdato ikke er tilgjengelig
            box_small = kamp_soup.find(
                'tr', attrs={'class': 'sd_game_small'}
            )
            dateandtime = box_small.find(
                'td', attrs={'class': 'sd_game_away'}
            ).text
            matchdate = re.search(
                r'.*(\d{2}.\d{2}.\d{4}).*', str(dateandtime)
            ).group(1)
            matchtime = re.search(
                r'.*kl. (.*)$', str(dateandtime)
            ).group(1)
            kamp_res = kamp_soup.find(
                'tr', attrs={'class': 'sd_game_big'}
            ).find(
                'td', attrs={'class': 'sd_game_score'}
            ).text.strip().replace(":", ".")
        # Henter kampdato og setter inn forrige kampdato hvis vanlig
        # kampdato ikke er tilgjengelig
        if matchdate == "":
            matchdate = tempdate
        else:
            tempdate = matchdate
        secs_to_match = int(seconds_to(matchdate + '.' + matchtime))
        begge_lag = '{}-{}'.format(hlag, blag)
        uselog('{:8} avsjekk ({}.00 {} / {})'.format(begge_lag, matchdate, matchtime, kamp_slutt_tid(str(matchdate + '.' + matchtime),6900)))
        uselog('{:8} det er {} sekunder til kamp.'.format(begge_lag, secs_to_match))
        # Finn ut når siste kampen slutter
        highest_stoptime = secs_to_match
        highest_stoptime += kampvarighet
        uselog('{:8} highest_stoptime: {}'.format(begge_lag, highest_stoptime))
        # Finn ut når første kampen starter
        if kamp_res != 'Utsatt':
            if lowest_waiting is None:
                lowest_waiting = secs_to_match
            if secs_to_match < lowest_waiting:
                lowest_waiting = secs_to_match

        tv = cols[6].text.strip().replace("TV 2", "TV2").replace(" ", "&nbsp;")
        try:
            sumo_link = cols[7].find('a')['href']\
                .replace('&referrer=altomfotball.no', '')
        except:
            sumo_link = ''
        # Finner formen til lagene
        if har_tabell:
            h_form = ""
            for formkamp in form[forkortelse[strip_team(hlag)]]:
                h_form += '[{}]({}{} "{}")'.format(
                    formkamp[0],
                    kamplink,
                    formkamp[2],
                    formkamp[1]
                )
            b_form = ""
            for formkamp in reversed(form[forkortelse[strip_team(blag)]]):
                b_form += '[{}]({}{} "{}")'.format(
                    formkamp[0],
                    kamplink,
                    formkamp[2],
                    formkamp[1]
                )
        kamp_slutt = int(seconds_to(matchdate + '.' + matchtime) +
                         kampvarighet)
        uselog('{:8} kamp_slutt: {}'.format(begge_lag, kamp_slutt_tid(
            str(matchdate + '.' + matchtime), 6900)
        ))
        if -1 < kamp_slutt < kampvarighet:
            aktiv_kamp = True
            uselog('Kampen mellom ' + hlag + ' og ' + blag +
                   ' er aktiv.')
        else:
            aktiv_kamp = False
        if kamp_slutt <= 60:
            aktiv_kamp = False
        # Slå sammen alle feltene i en linje med separator som er tilpasset
        # tabeller i reddit
        if kamp_res == 'Utsatt':
            utsatt.append(hlag + ' - ' + blag)
        else:
            if aktiv_kamp:
                kamp_res = '({})'.format(kamp_res)
            else:
                kamp_res = '{}'.format(kamp_res)
            if har_tabell:
                if len(h_form) <= 0:
                    h_form = ''
                else:
                    h_form = '({})'.format(h_form)
                if len(b_form) <= 0:
                    b_form = ''
                else:
                    b_form = '({})'.format(b_form)
            if har_tabell:
                sjekk_runde_result += '{}|({})&nbsp;{}&nbsp;{}|[{}]({})|'\
                    '{}&nbsp;{}&nbsp;({})|'.format(
                        matchdate,
                        plassering[strip_team(hlag)],
                        hlag,
                        h_form,
                        kamp_res,
                        kamplink,
                        b_form,
                        blag,
                        plassering[strip_team(blag)]
                    )
            else:
                sjekk_runde_result += '{}|{}|[{}]({})|{}|'.format(
                        matchdate,
                        hlag,
                        kamp_res,
                        kamplink,
                        blag
                    )
            if tv != '':
                if tv == 'TV2&nbsp;Sumo':
                    sjekk_runde_result += '[TV2 Sumo]({})'.format(sumo_link)
                elif 'NRK' in tv:
                    sjekk_runde_result += '[{}]({})'.format(tv, 'https://tv.nrk.no')
                else:
                    if sumo_link:
                        sjekk_runde_result += ' {} / [TV2 Sumo]({})'\
                            .format(tv, sumo_link)
                    elif liga == '3':
                        sjekk_runde_result += ' {} / [Nettavisen]({})'\
                            .format(tv, 'https://pluss.nettavisen.no/norgessporten#/liga/toppserien/')
                    else:
                        sjekk_runde_result += ' {}'.format(tv)
            sjekk_runde_result += '\n'
    return sjekk_runde_result

if __name__ == "__main__":
    main()
