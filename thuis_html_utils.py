import re
import logging
from bs4 import BeautifulSoup, Tag
from csv import DictWriter

from thuis_typing import RelatiePersoonData, PersonageData

RELATIE_HEADERS = list(RelatiePersoonData.__annotations__.keys())
PERSONAGE_HEADERS = list(PersonageData.__annotations__.keys())
HOOFDPERSONAGE_CSV = 'hoofdpersonages.csv'
NEVENPERSONAGE_CSV = 'nevenpersonages.csv'

logger = logging.getLogger(__name__)

def extract_nevenpersonages() -> None:
    """Leest nevenpersonagedata en bewaart ze in nevenpersonages.csv
    
    """
    BASIS_URL = 'https://nergensbeterdanthuis.fandom.com'
    url = "https://nergensbeterdanthuis.fandom.com/nl/wiki/Nevenpersonages"
    content = get_url(url)
    urls = _lees_nevenpersonage_urls(content)
    personage_data = []
    for url in urls:
        content = get_url(BASIS_URL+url)
        nevenpersonage_data = _lees_personage_details(content)
        personage_data.append(nevenpersonage_data)
    print(personage_data)
    

def extract_hoofdpersonages() -> None:
    """Leest hoofdpersonagedata en bewaart ze in hoofdpersonages.csv
    
    """
    BASIS_URL = 'https://nergensbeterdanthuis.fandom.com'
    url = "https://nergensbeterdanthuis.fandom.com/nl/wiki/Hoofdpersonages"
    content = get_url(url)
    urls = _lees_hoofdpersonage_urls(content)
    personage_data = []
    for url in urls:
        content = get_url(BASIS_URL+url)
        hoofdpersonage_data = _lees_personage_details(content)
        personage_data.append(hoofdpersonage_data)
    with open(HOOFDPERSONAGE_CSV, mode='w', newline='', encoding='utf-8') as f:
        writer = DictWriter(f, delimiter=';', fieldnames=PERSONAGE_HEADERS)
        writer.writeheader()
        writer.writerows(personage_data)


def _lees_personage_details(html:str) -> PersonageData:
    soep = BeautifulSoup(html, 'lxml')
    titel_tag = soep.find('span', class_='mw-page-title-main')
    naam = str(titel_tag.string)   #.string kan ook None teruggeeven
    naam_details = naam.split(' ', maxsplit=1)
    voornaam = naam_details[0]
    achternaam = naam_details[1] if len(naam_details) == 2 else 'Onbekend'   #Er zijn personages zonder achternaam
    seizoenen = []
    detail_data = soep.find('table', class_='userbox')
    td_tags = detail_data.find_all('td')
    if td_tags is not None:
        a_tags = td_tags[1].find_all('a')    #td_tags[0] bevat het label 'seizoenen'
        for a_tag in a_tags:
            seizoen = int(a_tag.string)
            seizoenen.append(seizoen)
    else:
        seizoen = _verwerk_nevenpersonage_details_uitzonderingen(voornaam, achternaam)
    return{'voornaam':voornaam, 'achternaam': achternaam, 'seizoenen':seizoenen}

def _verwerk_nevenpersonage_details_uitzonderingen(voornaam:str, achternaam:str) -> list[int]:
    if voornaam == 'Nand' and achternaam=='Reimers':
        return [10, 11, 12, 13]
    logger.error(f"Geen seizoensdata voor {voornaam} {achternaam}")
    raise Exception(f"Geen seizoensdata voor {voornaam} {achternaam}")

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

def extract_relaties(bestandsnaam: str, html:str) -> None:
    relaties = _lees_relaties(html)
    with open(bestandsnaam, mode='w', newline='', encoding='utf-8') as f:
        writer = DictWriter(f, delimiter=';', fieldnames=RELATIE_HEADERS)
        writer.writeheader()
        writer.writerows(relaties)

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
        item = {'seizoen': seizoen_nr, 'persoon_1': persoon_1, 'persoon_2': persoon_2}
        data.append(item)
    logger.debug(f"{len(data)} relaties ingelezen voor seizoen {seizoen_nr}")
    return data

if __name__ == '__main__':
    from thuis_http_utils import get_url
    logging.basicConfig(level=logging.DEBUG)
    url = "https://nergensbeterdanthuis.fandom.com/nl/wiki/Hoofdpersonages"
    BASIS_URL = 'https://nergensbeterdanthuis.fandom.com'
    extract_nevenpersonages()


    
