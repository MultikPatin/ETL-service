from collections.abc import Iterator
from datetime import datetime

from psycopg2.extensions import connection as _connection

from core.utils.logger import create_logger


class PostgresExtractor:
    __cursor = None

    def __init__(
        self, connection: _connection, buffer_size: int, storage_state
    ) -> None:
        self.__buffer_size = buffer_size
        self.__connection = connection
        self.state = storage_state
        self.logger = create_logger("PostgresExtractor")

    def extract(self, extract_timestamp: datetime) -> Iterator:
        """
        Метод чтения данных пачками.
        Ищем строки, удовлетворяющие условию - при нахождении записываем
        в хранилище состояния id
        """
        self.__cursor = self.__connection.cursor()

        stmt = f"""
                SELECT
                    fw.id,
                    fw.rating as imdb_rating,
                    json_agg(DISTINCT g.name) as genre,
                    fw.title,
                    fw.description,
                    fw.modified,
                    string_agg(DISTINCT CASE WHEN pfw.role = 'director' THEN p.full_name ELSE '' END, ',') AS director,
                    array_remove(COALESCE(array_agg(DISTINCT CASE WHEN pfw.role = 'actor' THEN p.full_name END) FILTER (WHERE p.full_name IS NOT NULL)), NULL) AS actors_names,
                    array_remove(COALESCE(array_agg(DISTINCT CASE WHEN pfw.role = 'writer' THEN p.full_name END) FILTER (WHERE p.full_name IS NOT NULL)), NULL) AS writers_names,
                    concat('[', string_agg(DISTINCT CASE WHEN pfw.role = 'actor' THEN json_build_object('id', p.id, 'name', p.full_name) #>> '{{}}' END, ','), ']') AS actors,
                    concat('[', string_agg(DISTINCT CASE WHEN pfw.role = 'writer' THEN json_build_object('id', p.id, 'name', p.full_name) #>> '{{}}' END, ','), ']') AS writers,
                    GREATEST(MAX(fw.modified), MAX(g.modified), MAX(p.modified)) AS last_modified
                FROM
                    content.film_work as fw
                    LEFT JOIN content.genre_film_work gfm ON fw.id = gfm.film_work_id
                    LEFT JOIN content.genre g ON gfm.genre_id = g.id
                    LEFT JOIN content.person_film_work pfw ON fw.id = pfw.film_work_id
                    LEFT JOIN content.person p ON pfw.person_id = p.id
                GROUP BY fw.id
                HAVING GREATEST(MAX(fw.modified), MAX(g.modified), MAX(p.modified)) > '{str(extract_timestamp)}'
                ORDER BY GREATEST(MAX(fw.modified), MAX(g.modified), MAX(p.modified)) DESC;
                """
        self.__cursor.execute(stmt)

        while True:
            rows = self.__cursor.fetchmany(self.__buffer_size)
            if rows:
                self.logger.info("Extracted %s rows", len(rows))
                yield rows
            else:
                self.logger.info("No changes found")
                self.__cursor.close()
                break
