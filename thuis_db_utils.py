import sqlite3
import logging
import json


DB_BESTAND ="thuis.db"
TBL_PERSONAGE = "PERSONAGE"
SQL_CREATE_TBL_PERSONAGE = \
f"""CREATE TABLE IF NOT EXISTS {TBL_PERSONAGE}(
         ID INTEGER PRIMARY KEY AUTOINCREMENT,
         VOORNAAM VARCHAR(255) NOT NULL,
         ACHTERNAAM VARCHAR(255) NULL  ,
         SEIZOENEN BLOB NULL   
)"""
SQL_CREATE_IDX_PERSONAGE = f"CREATE INDEX idx_voornaam ON {TBL_PERSONAGE} (VOORNAAM)"

SQL_DROP_TBL_PERSONAGE = f"DROP TABLE IF EXISTS {TBL_PERSONAGE}"

SQL_INSERT_PERSONAGE = \
f"""INSERT INTO {TBL_PERSONAGE} (VOORNAAM, ACHTERNAAM, SEIZOENEN)
VALUES (:voornaam, :achternaam, :seizoenen)
"""
SQL_SELECT_PERSONAGE_LIJST = f"SELECT ID, VOORNAAM, ACHTERNAAM, SEIZOENEN FROM {TBL_PERSONAGE}"

SQL_SELECT_PERSONAGE_VOORNAAM = SQL_SELECT_PERSONAGE_LIJST + " WHERE VOORNAAM = :voornaam"

logger = logging.getLogger(__name__)
def adapt_to_blob(lijst):
    if lijst is None or len(lijst) == 0: return None
    return json.dumps(lijst)

def convert_to_list(blob):
    return json.loads(blob)

sqlite3.register_converter('blob', convert_to_list)
sqlite3.register_adapter(list, adapt_to_blob)

def lees_personages_voornaam(voornaam):
    personages = []
    try:
        conn:sqlite3.Connection = sqlite3.connect(DB_BESTAND, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES, autocommit=False) # type: ignore
        cursor = conn.cursor();
        cursor.execute(SQL_SELECT_PERSONAGE_VOORNAAM, {'voornaam':voornaam})
        for row in cursor:
            personage = {
                'id': row[0],
                'voornaam' : row[1],
                'achternaam' : row[2],
                'seizoenen' : row[3]
            }
            personages.append(personage)
        
        return personages

    except (sqlite3.Error) as error:
        logger.error(error)
        if personage is not None:
            logger.error("error treedt op bij %", personage )
    finally:
        if conn is not None:
            conn.close()
            logger.info("lees_personages: Databank afgesloten")

def lees_personages():
    personages = []
    try:
        conn:sqlite3.Connection = sqlite3.connect(DB_BESTAND, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES, autocommit=False) # type: ignore
        cursor = conn.cursor();
        cursor.execute(SQL_SELECT_PERSONAGE_LIJST)
        for row in cursor:
            personage = {
                'id': row[0],
                'voornaam' : row[1],
                'achternaam' : row[2],
                'seizoenen' : row[3]
            }
            personages.append(personage)
        
        return personages
    except (sqlite3.Error) as error:
        logger.error(error)
        if personage is not None:
            logger.error("error treedt op bij %", personage )
    finally:
        if conn is not None:
            conn.close()
            logger.info("lees_personages: Databank afgesloten")

def bewaar_personage_lijst(lijst):
    personage = None
    try:
        conn:sqlite3.Connection = sqlite3.connect(DB_BESTAND, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES, autocommit=False) # type: ignore
        cursor = conn.cursor();
        for personage in lijst:
            id = _bewaar_personage(cursor, personage)
            logger.debug("personage toegevoegd met id %d", id)
            personage['id'] = id
        personage = None
        conn.commit()
    except (sqlite3.Error) as error:
        logger.error(error)
        if personage is not None:
            logger.error("error treedt op bij %", personage )
    finally:
        if conn is not None:
            conn.close()
            logger.debug("bewaar_personage_lijst: Databank afgesloten")

def init_db():
    try:
        conn = sqlite3.connect(DB_BESTAND, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES, autocommit=False) # type: ignore
        logger.info("verbonden met databank %s", DB_BESTAND)
        cur = conn.execute(SQL_DROP_TBL_PERSONAGE)
        logger.info("Databank is leeggemaakt")
        cur.execute(SQL_CREATE_TBL_PERSONAGE)
        cur.execute(SQL_CREATE_IDX_PERSONAGE)
        conn.commit()
        logger.info("Databank opnieuw gecreëerd")
    except (sqlite3.Error) as error:
        logger.error(error)
    finally:
        if conn is not None:
            conn.close()
            logger.debug("init_db: Databank afgesloten")


def _bewaar_personage(cursor, personage):
    data={}
    data['voornaam'] = personage['voornaam']
    data['achternaam'] = personage['achternaam']
    data['seizoenen'] = personage['seizoenen']
    logger.debug(f"insert {data}")
    cursor.execute(SQL_INSERT_PERSONAGE, personage)
    last_id = cursor.lastrowid
    return int(last_id)