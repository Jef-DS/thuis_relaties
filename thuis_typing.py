from typing import TypedDict

class DownloadType(TypedDict):
    url: str
    content: bytes
    laatste_wijziging: str

class CacheInfoType(TypedDict):
    url: str
    bestandsnaam: str
    laatste_wijziging: str
    redirect_url: str

class RelatiePersoonData(TypedDict):
    seizoen: int
    persoon_1: str
    persoon_2: str

class PersonageData(TypedDict):
    voornaam: str
    achternaam: str
    seizoenen: list[int]