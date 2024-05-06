import re
import logging
from bs4 import BeautifulSoup, Tag
from csv import DictWriter

from thuis_typing import RelatiePersoonData, PersonageData

RELATIE_HEADERS = list(RelatiePersoonData.__annotations__.keys())
PERSONAGE_HEADERS = list(PersonageData.__annotations__.keys())
HOOFDPERSONAGE_CSV = 'hoofdpersonages.csv'

logger = logging.getLogger(__name__)

def extract_hoofdpersonages() -> None:
    BASIS_URL = 'https://nergensbeterdanthuis.fandom.com'
    url = "https://nergensbeterdanthuis.fandom.com/nl/wiki/Hoofdpersonages"
    content = get_url(url)
    urls = lees_hoofdpersonage_urls(content)
    personage_data = []
    for url in urls:
        content = get_url(BASIS_URL+url)
        hoofdpersonage_data = lees_hoofdpersonage_details(content)
        personage_data.append(hoofdpersonage_data)
    with open(HOOFDPERSONAGE_CSV, mode='w', newline='', encoding='utf-8') as f:
        writer = DictWriter(f, delimiter=';', fieldnames=PERSONAGE_HEADERS)
        writer.writeheader()
        writer.writerows(personage_data)

def lees_hoofdpersonage_details(html:str) -> PersonageData:
    soep = BeautifulSoup(html)
    titel_tag = soep.find('span', class_='mw-page-title-main')
    naam = str(titel_tag.string)   #.string kan ook None teruggeeven
    naam_details = naam.split(' ', maxsplit=1)
    voornaam = naam_details[0]
    achternaam = naam_details[1] if len(naam_details) == 2 else 'Onbekend'   #Er zijn personages zonder achternaam
    seizoenen = []
    detail_data = soep.find('table', class_='userbox')
    td_tags = detail_data.find_all('td')
    a_tags = td_tags[1].find_all('a')    #td_tags[0] bevat het label 'seizoenen'
    for a_tag in a_tags:
        seizoen = int(a_tag.string)
        seizoenen.append(seizoen)
    return{'voornaam':voornaam, 'achternaam': achternaam, 'seizoenen':seizoenen}

def lees_hoofdpersonage_urls(html:str) -> list[str]:
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
    extract_hoofdpersonages()


    
