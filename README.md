# De relaties in thuis

## Inleiding
Deze applicatie analyseert de relaties in de één-serie Thuis. Hierbij wordt gebruik gemaakt van 
[de fandom website van thuis](https://nergensbeterdanthuis.fandom.com/nl/wiki/Thuis_wiki)

## Caching
Om ervoor te zorgen dat de website van de fans van thuis niet teveel belast wordt, is het een goed idee
om een *cache* te voorzien. De functies hiervoor staan in het bestand thuis_http_utils.py.

## Versies

### Versie 0.3
Het bestand thuis_html_utils.py bevat een functie _lees\_relaties_ om de relaties te lezen:
- Er is slechts 1 argument: de tekst van de HTML pagina met de relaties
- De functie geeft een list terug met {seizoennr, naam_persoon_1, naam_persoon_2}

### Versie 0.2
Functie get_url() uitgebreid met boolean optie *download*:
- als download False is wordt het bestand nooit gedownload (IndexError wanneer het nog niet aanwezig is in de cache)
- als download True is wordt er een connectie gemaakt met de Thuis website om te kijken of het bestand gedownload moet worden

### Versie 0.1
Het bestand thuis_http_utils.py bevat de volgende functies om een bestand te downloaden van de Fandom website van Thuis: 
- get_url(url: str) -> str : download een bestand als het nog niet in de cache zit of nieuw is en geeft de inhoud van het bestand in de cache terug
- _get_fileinfo(url: str) -> Optional\[CacheInfoType\] : private functie om informatie over een url (een bestand) in de cache op te vragen. Geeft None terug wanneer het bestand niet in de cache zit.
- _download_url(url:str, refdatum:Option\[str\]=None) -> Optional\[DownloadType\] : download een url wanneer het recenter is dan de refdatum en geeft de info terug. Wanneer er geen refdatum wordt meegegeven, wordt het bestand altijd gedownload. Wanneer het bestand op de website niet veranderd is, geeft de functie None terug
- _update_cache(info:DownloadType) -> None : bewaart gegevens van een nieuwe url in de cache of overschrijft de bestaande gegevens
- _init() -> str : initialiseert de cache en geeft de naam van het index.csv bestand terug

