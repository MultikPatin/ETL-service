import logging
import time
from datetime import datetime

import backoff
import elasticsearch
import psycopg2

from core.configs import elastic_settings, postgres_settings
from core.utils.logger import create_logger
from etl.helpers.extractor import PostgresExtractor
from etl.helpers.loader import ElasticLoader
from etl.helpers.state import JsonFileStorage, State
from etl.helpers.transformer import Transformer
from etl.utils.connections import elastic_search_connection


@backoff.on_exception(
    wait_gen=backoff.expo, exception=(elasticsearch.exceptions.ConnectionError)
)
@backoff.on_exception(
    wait_gen=backoff.expo, exception=(psycopg2.Error, psycopg2.OperationalError)
)
def etl(
    logger: logging.Logger,
    extractor: PostgresExtractor,
    transformer: Transformer,
    state: State,
    loader: ElasticLoader,
) -> None:
    """
    ETL процесс перекачки данных из PostgresSQL в Elasticsearch
    """
    last_sync_timestamp = state.get_state("last_sync_timestamp")
    logger.info("The last sync was %s", last_sync_timestamp)
    start_timestamp = datetime.utcnow()
    for extracted_part in extractor.extract(last_sync_timestamp):
        data = transformer.transform(extracted_part)
        loader.load(data)
        state.set_state("last_sync_timestamp", str(start_timestamp))


if __name__ == "__main__":
    logger = create_logger("ETL")
    logger.info("==> START ETL ------------------------------------------ ")

    state = State(JsonFileStorage(file_path="state.json"))

    with elastic_search_connection(
        elastic_settings.get_dsn
    ) as el_conn, psycopg2.connect(
        **postgres_settings.psycopg2_connect
    ) as pg_conn:
        extractor = PostgresExtractor(
            connection=pg_conn,
            buffer_size=elastic_settings.buffer_size,
            storage_state=state,
        )
        transformer = Transformer()
        loader = ElasticLoader(el_conn)

        while True:
            etl(logger, extractor, transformer, state, loader)
            logger.info("Pause for %s seconds", elastic_settings.sleep_time)
            time.sleep(elastic_settings.sleep_time)
