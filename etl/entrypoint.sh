#!/bin/bash

export PYTHONPATH=$SRC_PATH

rm poetry.lock

rm pyproject.toml

cd "$APP_DIR"/

rm Dockerfile

python main.py

