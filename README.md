# ligabot-dev
> Developer repo for ligabot (github.com/armandg/ligabot)

(Alle kodehenvisninger skal ha egen link til linje/linjer)

### Kort gjennomgang av hva ligabot gjør i dag
- Script kjøres på faste intervaller gjennom dagen som en cron job på en linux boks.
- Den henter informasjon om neste runde fra altomfotball.no
- Hvis neste runde er to dager unna (eller mindre), så skal det lages en rundetråd [(eksempel)](http://redd.it/6ram8b).
- Når rundetråd lages skal det sjekkes om det allerede eksisterer en lignende rundetråd fra før av. Dette sjekkes i funksjonen `threadAlreadyCreated` ([ligabot](https://github.com/armandg/ligabot/blob/master/ligabot-runde.py#L231-L242)) / `thread_already_created` ([ligabot-dev](https://github.com/armandg/ligabot-dev/blob/master/ligabot/posting.py#L119-L131)).
- Når rundetråd lages, oppdateres "rundetråd"-linja øverst på subreddit med info om korrekt runde. Dette er egentlig tekst i sidebar som har blitt flytta ved hjelp av css. Tekst som skal erstattes velges ved å lete etter korrekt "kode" ved hjelp av regex. Teksten ser slik ut:
```##Rundetråder: [](#runde-elite)[Eliteserien, 18. runde](http://redd.it/6ram8b)[](/runde-elite) - [](#runde-obos)[OBOS-ligaen, 18. runde](http://redd.it/6ram8c)[](/runde-obos) - [](#runde-topp)[Toppserien, 12. runde](http://redd.it/6k6p69)[](/runde-topp)```
- Rundetråden skal oppdateres ca hvert minutt når kamper er aktive, og oppdatere nåværende resultat. Den skal kun endre kampresultatene, ikke tabellplasseringene som puttes i samme post.
- Rundetråden skal ikke oppdateres lenger når siste kamp er ferdig.

### Mer spesifikt om rundetråder:
- Når rundetråd er laget på subredditen ligger den i bero inntil man begynner å sjekke kampresultater.
- Resultater skal begynne å sjekkes når første kamp starter. Intervall er per 60. sekund.
- Hver rundetråd har en "skjult" link som brukes for å erstatte kun en enkelt del av teksten i en submission. Denne er lik som for rundetråder og ser slik ut: `[](#kamper)` og `[](/kamper)`.
- Jeg har forsøkt å også sette det opp sånn at hvis `ligabot-runde.py` ikke kjøres med et liganummer, så vil den kjøres i testmodus. Fila `testfiler.py` lager  automatisk runde- og tabell-fil i mappa `testfiler` som kan brukes til testing av selve koden uten å måtte vente på at nye runder/kamper starter live på altomfotball.no. Denne får jeg ikke helt til å funke som ønskelig, så skrik ut de som har lyst til å prøve å forbedre den.

### Litt om praw og testing
- Bruker OAuth for innlogging som script istedet for bruker/pass
- [Les mer her](https://github.com/armandg/ligabot#oauth) for å finne ut av hvordan du kan skaffe OAuth-nøkler så du får kjørt eget script
- Kan maks oppdatere mot reddit hvert 2. sekund, så eventuelle API-henvendelser må ta hensyn til det
- Jeg bruker [/r/tippeligaensandbox](tippeligaensandbox.reddit.com) til testing. Si ifra hvis du ønsker mod-tilgang der for å teste kjøring av scriptet.
- 

### Ønsker om forbedringer
1. Forbedring av fil- og kodestruktur
Per nå er etter min mening `dev` forbedret en god del når det kommer til å få vekk mange av funksjonene fra hovedfila som gjorde koding veldig uoversiktlig. Men er dette godt nok eller kan det gjøres enda bedre?

2. Enkeltvise kamp-kommentarer med info
- Fra posten har blitt laget og fram til kampen, skal scriptet også kunne hente spesifikk info om kampen fra kampsiden:
  - Dommer
  - Lagoppstillinger
  - (Eventuelle) skader
  - (Eventuelle) suspensjoner pga kort og/eller hvem som er i fare for å få suspensjon.
  - Tilskuere
- All infoen blir en liten tekst som postes som en egen kommentar i rundetråden. Eksempel:

```
[Aalesund - Brann](link til kampinfoside)
Kampstart: 20.00
Dommer: En kar
Tilskuere: [oppdateres når tilgjengelig på kampside]
```
&nbsp;

Etter at kampen har startet legges det til kampinfo i samme kommentar. Eksempel:

&nbsp;

```
[Aalesund - Brann](link til kampinfoside)
Kampstart: 20.00
Dommer: En kar
Tilskuere: [oppdateres når tilgjengelig på kampside]

10' Mål Brann (Jakob Orlov, assist Vidar Jónsson)
12' Mål Brann (Kristoffer Barmen)
18' Gult kort Aalesund (Vebjørn Hoff)
```
