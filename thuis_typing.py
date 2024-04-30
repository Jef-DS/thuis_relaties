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