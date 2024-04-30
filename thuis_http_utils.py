import logging
import os
from csv import DictWriter, DictReader
from typing import   Optional

from thuis_typing import CacheInfoType

CACHE_DIR_NAME = '.filecachedir'
CACHE_DIR_PATH = os.path.join(os.getcwd(), CACHE_DIR_NAME)
INDEX_FILE_NAME = "index.csv"
INDEX_FILE_HEADERS = list(CacheInfoType.__annotations__.keys()) # de velden van CacheInfoTYpe zijn gelijk aan de veldnamen van index.csv

DATE_FORMAT = '%a, %d %b %Y %H:%M:%S %Z'

HTTP_OK = 200
HTTP_NOT_MODIFIED = 304



logger = logging.getLogger(__name__)

def get_url(url: str) -> str:
    """Geef de inhoud van een bestand op basis van de Thuis-url
    
    Parameters
    ----------
    url: str
         het bestand dat moet worden gedownload van de website als het recenter is, of uit de cache moet worden gehaald wanneer het niet recenter is

    Returns
    -------
    str
         de inhoud van het bestand     
    """
    logger.debug(f"in get_url om {url} op te halen")
    return ""


def _get_fileinfo(url: str) -> Optional[CacheInfoType]:
    index_file = _init()
    with open(index_file, mode='r', newline='', encoding='utf-8') as f:
        reader = DictReader(f, delimiter=";")
        for regel in reader:
            if regel['url'] == url:
                return regel
    return None

def _init() -> str:
    is_exist_dir = os.path.isdir(CACHE_DIR_PATH)
    if not is_exist_dir:
        logger.debug('filcachedir wordt gecreëerd')
        os.mkdir(CACHE_DIR_PATH)
    index_file = os.path.join(CACHE_DIR_PATH, INDEX_FILE_NAME)
    is_exist_file = os.path.isfile(index_file)
    if not is_exist_file:
        logger.debug('Cache index bestand wordt gecreëerd')
        with open(index_file, mode='w', newline='', encoding='utf-8') as f:
            writer = DictWriter(f, fieldnames=INDEX_FILE_HEADERS, delimiter=";")
            writer.writeheader()
    return index_file
    
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    resultaat = _get_fileinfo('dummy')
    print(resultaat)


