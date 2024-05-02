import re
import logging
import lxml.html
from csv import DictWriter


from thuis_typing import RelatiePersoonData

RELATIE_HEADERS = list(RelatiePersoonData.__annotations__.keys())

logger = logging.getLogger(__name__)

def extract_relaties(bestandsnaam: str, html:str) -> None:
    relaties = _lees_relaties(html)
    with open(bestandsnaam, mode='w', newline='', encoding='utf-8') as f:
        writer = DictWriter(f, delimiter=';', fieldnames=RELATIE_HEADERS)
        writer.writeheader()
        writer.writerows(relaties)

def _lees_relaties(html:str) -> list[RelatiePersoonData]:
    root = lxml.html.fromstring(html)
    seizoenen_tags = root.xpath('//div[starts-with(@id, "gallery-")]')
    logging.debug(f"{len(seizoenen_tags)} seizoenen inlezen")
    data:list[RelatiePersoonData] = []
    for seizoen_nr, seizoen_tag in enumerate(seizoenen_tags[1:],1):
        relaties = _lees_seizoen_relatie(seizoen_tag, seizoen_nr)
        data.extend(relaties)
    seizoen_nr += 1
    relaties = _lees_seizoen_relatie(seizoenen_tags[0], seizoen_nr)
    data.extend(relaties)
    return data

def _lees_seizoen_relatie(element:lxml.html.HtmlElement, seizoen_nr:int)->list[RelatiePersoonData]:
    data:list[RelatiePersoonData] = []
    b_tags = element.xpath('.//div[@class="lightbox-caption"]/b')
    for b_tag in b_tags:
        tekst = b_tag.text_content()
        persoon_1, persoon_2 = tekst.split(' en ')
        item = {'seizoen': seizoen_nr, 'persoon_1': persoon_1, 'persoon_2': persoon_2}
        data.append(item)
    logger.debug(f"{len(data)} relaties ingelezen voor seizoen {seizoen_nr}")
    return data        



if __name__ == '__main__':
    from thuis_http_utils import get_url
    logging.basicConfig(level=logging.DEBUG)
    url = "https://nergensbeterdanthuis.fandom.com/nl/wiki/Relaties"
    content = get_url(url)
    bestandsnaam = "relaties_namen.csv"
    extract_relaties(bestandsnaam, content)
