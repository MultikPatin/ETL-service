from src.etl.config.base import _ELASTIC_SETTINGS

_ELASTIC_MAPPING = {
    "dynamic": "strict",
    "properties": {
        "uuid": {"type": "keyword"},
        "name": {"type": "text", "analyzer": "ru_en"},
        "description": {"type": "text", "analyzer": "ru_en"},
    },
}

ELASTIC_DATA = {
    "settings": _ELASTIC_SETTINGS,
    "mappings": _ELASTIC_MAPPING,
}

SQL_QUERY = """
        SELECT
            g.id as uuid,
            g.name,
            g.description,
            g.modified
        FROM content.genre as g
        WHERE g.modified > '{}'
        GROUP BY g.id
        ORDER BY g.modified DESC
        """
