from src.etl.config.base import _ELASTIC_SETTINGS

_ELASTIC_MAPPING = {
    "dynamic": "strict",
    "properties": {
        "uuid": {"type": "keyword"},
        "imdb_rating": {"type": "float"},
        "title": {
            "type": "text",
            "analyzer": "ru_en",
            "fields": {"raw": {"type": "keyword"}},
        },
        "description": {"type": "text", "analyzer": "ru_en"},
        "genre": {
            "type": "nested",
            "dynamic": "strict",
            "properties": {
                "uuid": {"type": "keyword"},
                "name": {"type": "text", "analyzer": "ru_en"},
            },
        },
        "directors": {
            "type": "nested",
            "dynamic": "strict",
            "properties": {
                "uuid": {"type": "keyword"},
                "full_name": {"type": "text", "analyzer": "ru_en"},
            },
        },
        "actors": {
            "type": "nested",
            "dynamic": "strict",
            "properties": {
                "uuid": {"type": "keyword"},
                "full_name": {"type": "text", "analyzer": "ru_en"},
            },
        },
        "writers": {
            "type": "nested",
            "dynamic": "strict",
            "properties": {
                "uuid": {"type": "keyword"},
                "full_name": {"type": "text", "analyzer": "ru_en"},
            },
        },
    },
}

ELASTIC_DATA = {
    "settings": _ELASTIC_SETTINGS,
    "mappings": _ELASTIC_MAPPING,
}

SQL_QUERY = """
        SELECT
            fw.id as uuid,
            fw.rating as imdb_rating,
            fw.title,
            fw.description,
            fw.modified,
            concat(
                '[', string_agg(
                    DISTINCT CASE WHEN
                        g.name IS NOT NULL THEN json_build_object(
                            'uuid', g.id, 'name', g.name
                            ) #>> '{{}}' END, ','
                    ), ']'
                ) AS genre,
            concat(
                '[', string_agg(
                    DISTINCT CASE WHEN
                        pfw.role = 'actor' THEN json_build_object(
                            'uuid', p.id, 'full_name', p.full_name
                            ) #>> '{{}}' END, ','
                    ), ']'
                ) AS actors,
            concat(
                '[', string_agg(
                    DISTINCT CASE WHEN
                        pfw.role = 'director' THEN json_build_object(
                            'uuid', p.id, 'full_name', p.full_name
                            ) #>> '{{}}' END, ','
                    ), ']'
                ) AS directors,
            concat(
                '[', string_agg(
                    DISTINCT CASE WHEN
                        pfw.role = 'writer' THEN json_build_object(
                            'uuid', p.id, 'full_name', p.full_name
                            ) #>> '{{}}' END, ','
                    ), ']'
                ) AS writers,
            GREATEST(MAX(fw.modified), MAX(g.modified), MAX(p.modified)) AS last_modified
        FROM
            content.film_work as fw
            LEFT JOIN content.genre_film_work gfm ON fw.id = gfm.film_work_id
            LEFT JOIN content.genre g ON gfm.genre_id = g.id
            LEFT JOIN content.person_film_work pfw ON fw.id = pfw.film_work_id
            LEFT JOIN content.person p ON pfw.person_id = p.id
        GROUP BY fw.id
        HAVING GREATEST(MAX(fw.modified), MAX(g.modified), MAX(p.modified)) > '{}'
        ORDER BY GREATEST(MAX(fw.modified), MAX(g.modified), MAX(p.modified)) DESC
        """
