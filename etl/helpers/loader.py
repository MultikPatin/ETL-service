import json

import backoff
import elasticsearch.exceptions
from elasticsearch import Elasticsearch, helpers

from core.utils.logger import create_logger
from etl.config import ELASTIC_MAPPING, ELASTIC_SETTINGS


class ElasticLoader:
    def __init__(self, connection: Elasticsearch) -> None:
        self.__es = connection
        self.logger = create_logger("ElasticLoader")
        self.create_index("movies")

    @backoff.on_exception(
        wait_gen=backoff.expo,
        exception=elasticsearch.exceptions.ConnectionError,
    )
    def create_index(self, index_name: str) -> None:
        """Создание ES индекса."""

        if not self.__es.ping():
            raise elasticsearch.exceptions.ConnectionError
        if not self.__es.indices.exists(index="movies"):
            self.__es.indices.create(
                index=index_name,
                settings=ELASTIC_SETTINGS,
                mappings=ELASTIC_MAPPING,
            )
            self.logger.info(
                "Creating an index %s with the following schemes: %s and %s",
                index_name,
                json.dumps(ELASTIC_SETTINGS, indent=2),
                json.dumps(ELASTIC_MAPPING, indent=2),
            )

    def load(self, data: list[dict]) -> None:
        """Загружаем данные пачками в ElasticSearch"""

        actions = [
            {
                "_index": "movies",
                "_id": row["id"],
                "_source": row,
            }
            for row in data
        ]

        helpers.bulk(self.__es, actions)
        self.logger.info("Loaded %s rows", len(data))
