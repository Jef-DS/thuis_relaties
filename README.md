# De relaties in thuis

## Inleiding
Deze applicatie analyseert de relaties in de één-serie Thuis. Hierbij wordt gebruik gemaakt van 
[de fandom website van thuis](https://nergensbeterdanthuis.fandom.com/nl/wiki/Thuis_wiki)

## Caching
Om ervoor te zorgen dat de website van de fans van thuis niet teveel belast wordt, is het een goed idee
om een *cache* te voorzien. De functies hiervoor staan in het bestand thuis_http_utils.py.

## Versies

### Versie 0.8
In thuis.ipynb code toevoegen om 
- de personagelijst te lezen in de databank 
- bestand relaties_nrs.csv maken

Fout opgelost:
- Personage Jessica bestond niet voor seizoen 1 (Gastpersonage)

### Versie 0.7
Bewaart de personagegegevens van de CSV-bestanden in een sqlite databank

### Versie 0.6
De data van de personages op de website zijn niet volledig. Soms verschillen de namen tussen een relatie en een personage (Angele ipv Angèle). Soms ontbreken er seizoenen. En soms verandert een personage (geen dead naming voor "Kaat")
- Ontbrekende gegevens van bestaande personages toegevoegd
- 29 gastpersonages manueel toegevoegd

### Versie 0.5
Informatie van hoofd- en nevenpersonages lezen en bewaren in CSV-bestanden

### Versie 0.4
Een alternatief om de HTML-bestanden te lezen met lxml (en niet met BeautifulSoup) toegevoegd in thuis_html_lxml_utils.py. Het bestand bevat dezelfde functies als thuis_html_utils.py. 

### Versie 0.3
Het bestand thuis_html_utils.py bevat een functie _extract\_relaties_ om de relaties te lezen en te bewaren in een bestand
- Er zijn 2 argumenten: de naam van het csv-bestand en de tekst van de HTML pagina met de relaties
- De functie geeft niets terug

Er zijn twee private functies aanwezig:
- \_lees\_relaties(html:str) : leest de relaties in de HTML-tekst en geeft een lijst met relatie data terug (seizoennr, naam_persoon1, naam_persoon2)
-  \_lees\_seizoen\_relatie(tag, seizoennr): leest de relaties in een seizoenstag en geeft een lijst relatie data terug (seizoennr, naam_persoon1, naam_persoon2)

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

