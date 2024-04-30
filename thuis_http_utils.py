import logging
import os
import requests
from csv import DictWriter, DictReader
from datetime import datetime
from typing import   Optional, cast
from zoneinfo import ZoneInfo

from thuis_typing import CacheInfoType, DownloadType

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
    fileinfo = _get_fileinfo(url)
    refdatum = None
    if fileinfo is not None:
        refdatum = fileinfo['refdatum']

    return ""

def _download_url(url: str, refdatum:Optional[str]=None) -> Optional[DownloadType]:
    if refdatum is None:
        refdatum = datetime(2000, 1, 1).astimezone(tz=ZoneInfo('GMT')).strftime(DATE_FORMAT)
    logger.debug(f'download {url} met refdatum {refdatum}')
    headers = {'Accept-Encoding': 'br', 'If-Modified-Since': refdatum}
    try:
        response = requests.get(url, headers=headers)
        logger.debug(f'Response met status {response.status_code}')
        if response.status_code == HTTP_NOT_MODIFIED:
            logger.debug(f"{url} is niet gedownload (not modified)")
            return None
        if response.status_code == HTTP_OK:
            url = response.url
            content = response.content
            laatste_wijziging = response.headers["Last-Modified"]
            logger.debug(f"{url} gedownload met datum {laatste_wijziging}")
            return {'url': url, 'content': content, 'laatste_wijziging': laatste_wijziging}
        response.raise_for_status()
        logger.error(f'Reponse met onverwachte status {response.status_code}')
        raise(Exception(f'Reponse met onverwachte status {response.status_code}'))
    except requests.exceptions.ConnectionError as conn_err:
        url = conn_err.request.url
        logger.error(f'Connection error {conn_err.strerror} voor url {url}')
        raise(conn_err)
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error {http_err.response.status_codee}")
        raise(http_err)
    
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
    url = 'https://nergensbeterdanthuis.fandom.com/nl/wiki/Relaties'
    resultaat = _download_url(url, refdatum='Mon, 29 Apr 2024 06:06:18 GMT')
    if resultaat is not None:
        print(resultaat['laatste_wijziging'])
        print(resultaat['url'])
    else:
        print("bestand is niet gedownload")


