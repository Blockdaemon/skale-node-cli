#   -*- coding: utf-8 -*-
#
#   This file is part of skale-node-cli
#
#   Copyright (C) 2019 SKALE Labs
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import logging
from shutil import copyfile
from urllib.parse import urlparse

from core.resources import save_resource_allocation_config

from configs import (DEPENDENCIES_SCRIPT, ADMIN_PORT,
                     DEFAULT_URL_SCHEME, NODE_DATA_PATH,
                     SKALE_DIR, CONTAINER_CONFIG_PATH, CONTRACTS_PATH,
                     NODE_CERTS_PATH, SGX_CERTS_PATH, REDIS_DATA_PATH,
                     SCHAINS_DATA_PATH, LOG_PATH, MYSQL_BACKUP_FOLDER)
from configs.cli_logger import LOG_DATA_PATH
from configs.resource_allocation import (DISK_MOUNTPOINT_FILEPATH,
                                         SGX_SERVER_URL_FILEPATH)

from core.helper import safe_load_texts
from tools.helper import run_cmd

TEXTS = safe_load_texts()

logger = logging.getLogger(__name__)


def install_host_dependencies():
    env = {
        **os.environ,
        'SKALE_CMD': 'host_deps'
    }
    run_cmd(["sudo", "bash", DEPENDENCIES_SCRIPT], env=env)
    # todo: check execution status


def fix_url(url):
    try:
        result = urlparse(url)
        if not result.scheme:
            url = f'{DEFAULT_URL_SCHEME}{url}'
        if not url.endswith(str(ADMIN_PORT)):
            return f'{url}:{ADMIN_PORT}'
        return url
    except ValueError:
        return False


def get_flask_secret_key():
    secret_key_filepath = os.path.join(NODE_DATA_PATH, 'flask_db_key.txt')
    with open(secret_key_filepath) as key_file:
        return key_file.read().strip()


def prepare_host(env_filepath, disk_mountpoint, sgx_server_url):
    logger.info(f'Preparing host started, disk_mountpoint: {disk_mountpoint}')
    make_dirs()
    save_env_params(env_filepath)
    save_disk_mountpoint(disk_mountpoint)
    save_sgx_server_url(sgx_server_url)
    save_resource_allocation_config()


def is_node_inited():
    return os.path.isdir(NODE_DATA_PATH)


def make_dirs():
    for dir_path in (
            SKALE_DIR, NODE_DATA_PATH, CONTAINER_CONFIG_PATH,
            CONTRACTS_PATH, NODE_CERTS_PATH, MYSQL_BACKUP_FOLDER,
            SGX_CERTS_PATH, SCHAINS_DATA_PATH, LOG_PATH, REDIS_DATA_PATH
    ):
        safe_mk_dirs(dir_path)


def save_disk_mountpoint(disk_mountpoint):
    logger.info(f'Saving disk_mountpoint option to {DISK_MOUNTPOINT_FILEPATH}')
    with open(DISK_MOUNTPOINT_FILEPATH, 'w') as f:
        f.write(disk_mountpoint)


def save_sgx_server_url(sgx_server_url):
    logger.info(f'Saving disk_mountpoint option to {SGX_SERVER_URL_FILEPATH}')
    with open(SGX_SERVER_URL_FILEPATH, 'w') as f:
        f.write(sgx_server_url)


def save_env_params(env_filepath):
    copyfile(env_filepath, os.path.join(SKALE_DIR, '.env'))


def init_logs_dir():
    safe_mk_dirs(LOG_DATA_PATH)


def init_data_dir():
    safe_mk_dirs(NODE_DATA_PATH)


def safe_mk_dirs(path):
    if os.path.exists(path):
        return
    msg = f'Creating {path} directory...'
    logger.info(msg), print(msg)
    os.makedirs(path, exist_ok=True)
