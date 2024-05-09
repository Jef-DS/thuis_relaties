import re
import logging
from bs4 import BeautifulSoup, Tag
from csv import DictWriter
from thuis_http_utils import get_url

from thuis_typing import RelatiePersoonData, PersonageData

RELATIE_HEADERS = list(RelatiePersoonData.__annotations__.keys())
PERSONAGE_HEADERS = list(PersonageData.__annotations__.keys())
HOOFDPERSONAGE_CSV = 'hoofdpersonages.csv'
NEVENPERSONAGE_CSV = 'nevenpersonages.csv'
RELATIES_NAMEN_CSV = 'relaties_namen.csv'
GASTPERSONAGE_CSV  = 'gastpersonages.csv'

BASIS_URL = 'https://nergensbeterdanthuis.fandom.com'
RELATIE_URL = BASIS_URL + "/nl/wiki/Relaties"
HOOFDPERSONAGES_URL = BASIS_URL + "/nl/wiki/Hoofdpersonages"
NEVENERSONAGES_URL = BASIS_URL + "/nl/wiki/Nevenpersonages"

logger = logging.getLogger(__name__)

def extract_gastpersonages() -> None:
    """Bewaart gastpersonages in gastpersonages.csv
    
    """
    personages = [
        {'voornaam': 'Adam', 'achternaam': 'Kiabaté', 'seizoenen': [22]},
        {'voornaam': 'Alex', 'achternaam': 'Walters', 'seizoenen': [8,9]},         #onbekend personage
        {'voornaam': 'Amber', 'achternaam': ' Van Gistel', 'seizoenen': [12,13]},
        {'voornaam': 'André', 'achternaam': 'Versteven', 'seizoenen': [16,17,18,19,20,21]},
        {'voornaam': 'Axel', 'achternaam': 'Verstraeten', 'seizoenen': [17]},
        {'voornaam': 'Bert', 'achternaam': 'Onbekend', 'seizoenen': [7]},
        {'voornaam': 'Bonnie', 'achternaam': 'Declerck', 'seizoenen': [11,12]},
        {'voornaam': 'Chiara', 'achternaam': 'Giampicollo', 'seizoenen': [22]},
        {'voornaam': 'Dirk', 'achternaam': 'Onbekend', 'seizoenen': [1]},
        {'voornaam': 'Eline', 'achternaam': 'Eelen', 'seizoenen': [16]},
        {'voornaam': 'Elke', 'achternaam': 'Vervust', 'seizoenen': [1]},
        {'voornaam': 'Filip', 'achternaam': 'Lamote', 'seizoenen': [15],},
        {'voornaam': 'Floris', 'achternaam': 'Onbekend', 'seizoenen': [23,24,25]},
        {'voornaam': 'François', 'achternaam': 'Chevalier', 'seizoenen': [2,3]},
        {'voornaam': 'Gaby', 'achternaam': 'Fontaine', 'seizoenen': [28]},
        {'voornaam': 'Hanne', 'achternaam': 'Goris', 'seizoenen': [15]},
        {'voornaam': 'Jean-Marie', 'achternaam': 'Onbekend', 'seizoenen': [15]},
        {'voornaam': 'Jef', 'achternaam': 'Van Hout', 'seizoenen': [26,27]},
        {'voornaam': 'Jessica', 'achternaam': 'Onbekend', 'seizoenen': [1]},
        {'voornaam': 'John', 'achternaam': 'De Brabander', 'seizoenen': [1]},
        {'voornaam': 'Leon', 'achternaam': 'Raemaeckers', 'seizoenen': [1]},
        {'voornaam': 'Margot', 'achternaam': 'Onbekend', 'seizoenen': [12]},   #Onbekedn personage
        {'voornaam': 'Martha', 'achternaam': 'Onbekend', 'seizoenen': [17]},
        {'voornaam': 'Max', 'achternaam': 'Maertens', 'seizoenen': [16,17]},
        {'voornaam': 'Nona', 'achternaam': 'Sareno', 'seizoenen': [12,13,14]},
        {'voornaam': 'Renée', 'achternaam': 'Coppens', 'seizoenen': [21,22,23]},
        {'voornaam': 'Sindi', 'achternaam': 'Onbekend', 'seizoenen': [12]},
        {'voornaam': 'Thomas', 'achternaam': 'Onbekend', 'seizoenen': [19]},   #Onbekend personage
        {'voornaam': 'Wim', 'achternaam': 'Daniels', 'seizoenen': [11,12]},
        {'voornaam': 'Zosiane', 'achternaam': 'Pelckmans', 'seizoenen': [10]}
    ]
    with open(GASTPERSONAGE_CSV, mode='w', newline='', encoding='utf-8') as f:
        writer = DictWriter(f, delimiter=";",fieldnames=PERSONAGE_HEADERS)
        writer.writeheader()
        writer.writerows(personages)

def extract_nevenpersonages(download=False) -> None:
    """Leest nevenpersonagedata en bewaart ze in nevenpersonages.csv

    Parameters
    ----------
    download: bool, optional
              Moet er contact worden opgenomen met de website om te controleren of het bestand gewijzigd is
    
    Raises
    ------
    IndexError
         Wanneer er en fout zit in de cache of een bestand niet wordt teruggevonden in de cache
    
    """
    content = get_url(NEVENERSONAGES_URL, download)
    urls = _lees_nevenpersonage_urls(content)
    personage_data = []
    for url in urls:
        content = get_url(BASIS_URL+url, download)
        nevenpersonage_data = _lees_personage_details(content)
        personage_data.append(nevenpersonage_data)
    with open(NEVENPERSONAGE_CSV, mode='w', newline='', encoding='utf-8') as f:
        writer = DictWriter(f, delimiter=';', fieldnames=PERSONAGE_HEADERS)
        writer.writeheader()
        writer.writerows(personage_data)    

def extract_hoofdpersonages(download=False) -> None:
    """Leest hoofdpersonagedata en bewaart ze in hoofdpersonages.csv

    Parameters
    ----------
    download: bool, optional
              Moet er contact worden opgenomen met de website om te controleren of het bestand gewijzigd is
    
    Raises
    ------
    IndexError
         Wanneer er en fout zit in de cache of een bestand niet wordt teruggevonden in de cache
    
    """
    content = get_url(HOOFDPERSONAGES_URL, download)
    urls = _lees_hoofdpersonage_urls(content)
    personage_data = []
    for url in urls:
        content = get_url(BASIS_URL+url, download)
        hoofdpersonage_data = _lees_personage_details(content)
        personage_data.append(hoofdpersonage_data)
    with open(HOOFDPERSONAGE_CSV, mode='w', newline='', encoding='utf-8') as f:
        writer = DictWriter(f, delimiter=';', fieldnames=PERSONAGE_HEADERS)
        writer.writeheader()
        writer.writerows(personage_data)

def extract_relaties(download=False) -> None:
    """Leest relaties en bewaart ze in relaties_namen.csv

    Parameters
    ----------
    download: bool, optional
              Moet er contact worden opgenomen met de website om te controleren of het bestand gewijzigd is
    
    Raises
    ------
    IndexError
         Wanneer er en fout zit in de cache of een bestand niet wordt teruggevonden in de cache
    
    """
    content = get_url(RELATIE_URL, download)
    relaties = _lees_relaties(content)
    with open(RELATIES_NAMEN_CSV, mode='w', newline='', encoding='utf-8') as f:
        writer = DictWriter(f, delimiter=';', fieldnames=RELATIE_HEADERS)
        writer.writeheader()
        writer.writerows(relaties)

def _lees_personage_details(html:str) -> PersonageData:
    soep = BeautifulSoup(html, 'lxml')
    titel_tag = soep.find('span', class_='mw-page-title-main')
    naam = str(titel_tag.string)   #.string kan ook None teruggeeven
    seizoenen = []
    detail_data = soep.find('table', class_='userbox')
    if detail_data is not None:
        td_tags = detail_data.find_all('td')
        a_tags = td_tags[1].find_all('a')    #td_tags[0] bevat het label 'seizoenen'
        for a_tag in a_tags:
            seizoen = int(a_tag.string)
            seizoenen.append(seizoen)
    personage_details = _verwerk_personage_details_uitzonderingen(naam, seizoenen)
    return personage_details

def _verwerk_personage_details_uitzonderingen(naam:str, seizoenen:list[int]) -> PersonageData:
    naam_details = naam.split(' ', maxsplit=1)
    voornaam = naam_details[0]
    achternaam = naam_details[1] if len(naam_details) == 2 else 'Onbekend'   #Er zijn personages zonder achternaam
    if voornaam =='Nand' and achternaam == 'Reimers':
        seizoenen = [10, 11, 12, 13]
    if voornaam == 'Stijn' and achternaam == 'De Belder':
        seizoenen = [16, 17]
    if voornaam == 'Tim' and achternaam == 'Cremers':  #relatie met Katrien begint in seizoen 13
        seizoenen.insert(0, 13)
    if voornaam == 'Claire' and achternaam == 'Bastiaens':
        seizoenen.append(15)
    if voornaam == 'Britney' : voornaam = 'Britt'
    if voornaam == 'Angele': voornaam = 'Angèle'
    if voornaam == 'Rogerke': voornaam = 'Roger'
    if voornaam == 'Kazàn' : voornaam = 'Kasper'
    return {'voornaam':voornaam, 'achternaam':achternaam, 'seizoenen':seizoenen}
    

def _verwerk_nevenpersonage_urls_uitzonderingen(urls:list[str], url:str) -> list[str]:
    if url == '/nl/wiki/Pips': 
        logger.debug(f"Uitzondering voor url Pips")
        return urls  #Pips heeft geen detailspagina
    urls.append(url)
    return urls

def _lees_nevenpersonage_urls(html:str) -> list[str]:
    data = []
    soep = BeautifulSoup(html, 'lxml')
    huidige_nevenpersonages_tag = soep.find(id='gallery-0')
    personage_tags = huidige_nevenpersonages_tag.find_all(class_='wikia-gallery-item')    
    for personage_tag in personage_tags:
        a_tag = personage_tag.find('a')
        url = a_tag['href']
        data = _verwerk_nevenpersonage_urls_uitzonderingen(data, url)
    vorige_nevenpersonages_tag = soep.find('table', class_='sortable')  #class=jquery-tablesorter zit niet in source
    tr_tags = vorige_nevenpersonages_tag.find_all('tr')
    for tr_tag in tr_tags[1:]:              #header overslaan
        td_tags = tr_tag.find_all('td')
        a_tag = td_tags[2].find('a')
        url = a_tag['href']
        data = _verwerk_nevenpersonage_urls_uitzonderingen(data, url)
    return data    

def _lees_hoofdpersonage_urls(html:str) -> list[str]:
    """Geeft de urls terug van de detailpagina's van de hoofdpersonages
    
    Parameters
    ----------
    html: str
          de tekst van de HTML-pagina met de urls
    
    Returns
    -------
    list[str]:
          de lijst met de urls van de detailpagina's
    """
    data = []
    soep = BeautifulSoup(html, 'lxml')
    #Er zijn twee reeksen van personages, namelijk id='gallery-0' en id='gallery-1'
    hoofdpersonage_tags = soep.find_all(id=re.compile(r'^gallery-[01]$'))
    for hoofdpersonage_tag in hoofdpersonage_tags:
        personage_tags = hoofdpersonage_tag.find_all(class_='wikia-gallery-item')
        for personage_tag in personage_tags:
            a_tag = personage_tag.find('a')
            url = a_tag['href']
            data.append(url)
    return data   


def _lees_relaties(html:str) -> list[RelatiePersoonData]:
    """Leest de relaties van de HTML-tekst van de Relaties-pagina van de Thuis website

    Parameters
    ----------
    html: str
         De tekst met de HTML-data van de relatiepagina
    
    Returns
    -------
    list[RelatiePersoonData]:
         De relatiegegevens onder de vorm van een lijst met seizoennr, persoon_1 en persoon2
    """
    soep = BeautifulSoup(html, 'lxml')
    seizoenen_tags = soep.find_all(id= re.compile(r'^gallery-[1-9][0-9]?'))
    logging.debug(f"{len(seizoenen_tags)} vorige seizoenen inlezen")
    data:list[RelatiePersoonData] = []
    for seizoen_nr, seizoen_tag in enumerate(seizoenen_tags, 1):
        relaties = _lees_seizoen_relatie(seizoen_tag, seizoen_nr)
        data.extend(relaties)
    laatste_seizoen_tag = soep.find(id='gallery-0')
    seizoen_nr += 1
    relaties = _lees_seizoen_relatie(laatste_seizoen_tag, seizoen_nr)
    data.extend(relaties)
    return data

def _lees_seizoen_relatie(tag:Tag, seizoen_nr:int ) -> list[RelatiePersoonData]:
    data:list[RelatiePersoonData] = []
    b_tags = tag.find_all('b')
    for b_tag in b_tags:
        tekst = str(b_tag.string)
        persoon_1, persoon_2 = tekst.split(" en ")
        item = _verwerk_lees_seizoen_relatie_uitzondering(seizoen_nr, persoon_1, persoon_2)
        data.append(item)
    logger.debug(f"{len(data)} relaties ingelezen voor seizoen {seizoen_nr}")
    return data

def _verwerk_lees_seizoen_relatie_uitzondering(seizoen_nr:int, persoon_1:str, persoon_2:str) -> RelatiePersoonData:
    if persoon_1 == 'Angele': persoon_1 = 'Angèle'
    if persoon_2 == 'Angele': persoon_2 = 'Angèle'
    if persoon_1 == 'Aisha' : persoon_1 = 'Aïsha'
    if persoon_2 == 'Aisha' : persoon_2 = 'Aïsha'
    if persoon_1 == 'Franky' : persoon_1 = 'Kaat'   #Geen dead naming
    if persoon_2 == 'Franky' : persoon_2 = 'Kaat'

    return {'seizoen': seizoen_nr, 'persoon_1': persoon_1, 'persoon_2': persoon_2}

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    extract_gastpersonages()


    
