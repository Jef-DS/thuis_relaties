import logging
import os
import urllib.parse
import requests
import urllib
from csv import DictWriter, DictReader
from datetime import datetime
from typing import   Optional
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

def get_url(url: str, download=False) -> str:
    """Geef de inhoud van een bestand op basis van de Thuis-url
    
    Parameters
    ----------
    url: str
         het bestand dat moet worden gedownload van de website als het recenter is, of uit de cache moet worden gehaald wanneer het niet recenter is
    download: boolean, default False
         False => neem nooit contact op met de thuis website (bestand moet aanwezig zijn in de cache)
         True => neem contact op met de thuis website om te controleren of het bestand gewijzigd is (en download eventueel)
         
    Returns
    -------
    str
         de inhoud van het bestand

    Raises
    ------
    IndexError
         Wanneer er en fout zit in de cache of een bestand niet wordt teruggevonden in de cache     

    """
    logger.debug(f"In get_url om {url} met download {download}")
    fileinfo = _get_fileinfo(url)
    refdatum = None
    if fileinfo is not None:
        logger.debug(f"Fileinfo {fileinfo} gevonden")
        refdatum = fileinfo['laatste_wijziging']
        url = fileinfo['redirect_url']
    elif not download:
        logger.error(f"url {url} niet in cache en mag niet downloaden")
        raise IndexError(f"url {url} niet in cache en mag niet downloaden")
    if download:
        download_data = _download_url(url, refdatum=refdatum)
        if download_data is not None:
            if fileinfo is not None:
                _update_cache(download_data, fileinfo)
            else:
                fileinfo = _add_to_cache(url, download_data)
    html_bestand = os.path.join(CACHE_DIR_PATH, fileinfo['bestandsnaam'])
    with open(html_bestand, mode='r', encoding='utf-8') as f:
        content = f.read()
    return content

def _add_to_cache(url:str, download_data: DownloadType) -> CacheInfoType:
    logger.debug(f"{url} toevoegen aan cache met ")
    index_file = _init()
    cachedir = os.path.dirname(index_file)
    laatste_wijziging = download_data['laatste_wijziging']
    redirect_url = download_data['url']
    logger.debug(f"met redirect url {redirect_url} en laatste wijziging {laatste_wijziging}")
    url_path = urllib.parse.unquote( urllib.parse.urlparse(redirect_url).path)
    bestandsnaam  = url_path[url_path.rfind('/')+1:] + '.html'
    fileinfo:CacheInfoType = {'url': url, 'redirect_url':redirect_url, 'laatste_wijziging':laatste_wijziging, 'bestandsnaam':bestandsnaam}
    with open(index_file, mode='r', newline='', encoding='utf-8') as f:
        reader = DictReader(f, delimiter=';')
        data=[]
        for rij in reader:
            if rij['url'] == fileinfo['url']:
                logger.error(f"url {fileinfo['url']} bestaat al: rij['url]")
                raise IndexError(f"url {fileinfo['url']} bestaat al: rij['url]")
            data.append(rij)
    html_bestand = os.path.join(cachedir, bestandsnaam)
    logger.debug(f"bestand {html_bestand} bewaren in cache")
    with open(html_bestand, mode='wb') as f:
        f.write(download_data['content'])
    data.append(fileinfo)
    logger.debug(f"Index bewaren met {fileinfo}")
    _write_index(data)
    return fileinfo
    
def _update_cache(download_data: DownloadType, fileinfo:CacheInfoType) -> None:
    logger.debug(f"update cache voor {fileinfo['bestandsnaam']}")
    index_file = _init()
    cachedir = os.path.dirname(index_file)
    url = fileinfo['url']
    laatste_wijziging = download_data['laatste_wijziging']
    bestandsnaam = os.path.join(cachedir, fileinfo['bestandsnaam'])
    data = _read_index()
    logger.debug(f'{len(data)} indexrecords gelezen')
    gevonden_records = [ rij for rij in data if rij['url'] == url]
    aantal_records = len(gevonden_records)
    if aantal_records == 1:
        logger.debug(f"Index record updaten met laatste wijziging {laatste_wijziging}")
        gevonden_records[0]['laatste_wijziging'] = laatste_wijziging
        with open(bestandsnaam, mode='wb') as f:
            f.write(download_data['content'])
        _write_index(data)
    else:
        logger.error(f'{aantal_records} gevonden bij _update_cache voor url {url}')
        raise IndexError(f'{aantal_records} gevonden bij _update_cache voor url {url}')

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
    data = _read_index()
    for regel in data:
        if regel['url'] == url:
            return regel
    return None

def _write_index(data:list[CacheInfoType]) -> None:
    index_file = _init()
    with open(index_file, mode='w', newline='', encoding='utf-8') as f:
        writer = DictWriter(f, delimiter=';', fieldnames=INDEX_FILE_HEADERS)
        writer.writeheader()
        writer.writerows(data)

def _read_index() -> list[CacheInfoType]:
    index_file = _init()
    with open (index_file, mode='r', newline='', encoding='utf-8') as f:
        reader = DictReader(f, delimiter=";")
        data = []
        for rij in reader:
            data.append(rij)
    return data

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
    url = 'https://nergensbeterdanthuis.fandom.com/nl/wiki/C%C3%A9dric'
    content = get_url(url)

        


