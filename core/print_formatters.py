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

import json
import os
import datetime
import texttable
from dateutil import parser

import inspect

from configs import LONG_LINE
from tools.texts import Texts

TEXTS = Texts()


def print_err_response(error_payload):
    if isinstance(error_payload, list):
        error_msg = '\n'.join(error_payload)
    else:
        error_msg = error_payload

    print('Command failed with following errors:')
    print(LONG_LINE)
    print(error_msg)
    print(LONG_LINE)


def print_wallet_info(wallet):
    print(inspect.cleandoc(f'''
        {LONG_LINE}
        Address: {wallet['address'].lower()}
        ETH balance: {wallet['eth_balance']} ETH
        SKALE balance: {wallet['skale_balance']} SKALE
        {LONG_LINE}
    '''))


def get_tty_width():
    tty_size = os.popen('stty size 2> /dev/null', 'r').read().split()
    if len(tty_size) != 2:
        return 0
    _, width = tty_size
    return int(width)


class Formatter(object):
    def table(self, headers, rows):
        table = texttable.Texttable(max_width=get_tty_width())
        table.set_cols_dtype(['t' for h in headers])
        table.add_rows([headers] + rows)
        table.set_deco(table.HEADER)
        table.set_chars(['-', '|', '+', '-'])

        return table.draw()


def format_date(date):
    return date.strftime("%b %d %Y %H:%M:%S")


def print_containers(containers):
    headers = [
        'Name',
        'Status',
        'Started At',
        'Image'
    ]
    rows = []
    for container in containers:
        date = parser.parse(container["state"]["StartedAt"])
        status = container["state"]["Status"].capitalize()

        if not container['state']['Running']:
            finished_date = parser.parse(container["state"]["FinishedAt"])
            status = f'{status} ({format_date(finished_date)})'

        rows.append([
            container['name'],
            status,
            format_date(date),
            container['image']
        ])
    print(Formatter().table(headers, rows))


def print_schains(schains):
    headers = [
        'Name',
        'Owner',
        'Size',
        'Lifetime',
        'Created At',
        'Deposit'
    ]
    rows = []
    for schain in schains:
        date = datetime.datetime.fromtimestamp(schain['startDate'])
        rows.append([
            schain['name'],
            schain['owner'],
            schain['partOfNode'],
            schain['lifetime'],
            format_date(date),
            schain['deposit'],
        ])
    print(Formatter().table(headers, rows))


def print_dkg_statuses(statuses):
    headers = [
        'sChain Name',
        'DKG Status',
        'Added At',
        'sChain Status'
    ]
    rows = []
    for status in statuses:
        date = datetime.datetime.fromtimestamp(status['added_at'])
        schain_status = 'Deleted' if status['is_deleted'] else 'Active'
        rows.append([
            status['name'],
            status['dkg_status_name'],
            format_date(date),
            schain_status
        ])
    print(Formatter().table(headers, rows))


def print_schains_healthchecks(schains):
    headers = [
        'sChain Name',
        'Data directory',
        'DKG',
        'Config file',
        'Volume',
        'Container',
        'IMA',
        'Firewall'
    ]
    rows = []
    for schain in schains:
        healthchecks = schain['healthchecks']
        rows.append([
            schain['name'],
            healthchecks['data_dir'],
            healthchecks['dkg'],
            healthchecks['config'],
            healthchecks['volume'],
            healthchecks['container'],
            healthchecks['ima_container'],
            healthchecks['firewall_rules']
        ])
    print(Formatter().table(headers, rows))


def print_logs(logs):
    print('Base logs\n')
    print_log_list(logs['base'])
    print(f'\n{LONG_LINE}')
    print('\nsChains logs\n')
    print_schains_logs(logs['schains'])


def print_schains_logs(schains_logs):
    for name in schains_logs:
        print(f'\n{name} \n')
        print_log_list(schains_logs[name]['logs'])


def print_log_list(logs):
    headers = [
        'Name',
        'Size',
        'Created At'
    ]
    rows = []
    for log in logs:
        date = datetime.datetime.fromtimestamp(log['created_at'])
        rows.append([
            log['name'],
            log['size'],
            format_date(date)
        ])
    print(Formatter().table(headers, rows))


def print_dict(title, rows, headers=['Key', 'Value']):
    print(title)
    print(Formatter().table(headers, rows))


def print_exit_status(exit_status_info):
    headers = [
        'Schain name',
        'Status'
    ]
    logs = exit_status_info['data']
    node_exit_status = exit_status_info['status'].lower()
    rows = [[log['name'], log['status'].lower()] for log in logs]
    print(f'\n{Formatter().table(headers, rows)}\n')
    status_info = TEXTS['exit']['status'][node_exit_status]
    print(f'\n{status_info}\n')
    if node_exit_status == 'wait_for_rotations':
        exit_time = exit_status_info['exit_time']
        exit_time_utc = datetime.datetime.utcfromtimestamp(exit_time)
        print(f'Rotation finish time: {exit_time_utc}')


def print_firewall_rules(rules, raw=False):
    if len(rules) == 0:
        print('No allowed endpoints')
        return
    if raw:
        print(json.dumpes(rules))
    headers = [
        'Port',
        'Ip'
    ]
    rows = []
    for rule in sorted(rules, key=lambda r: r['port']):
        rows.append([
            rule['port'],
            rule['ip']
        ])
    print(Formatter().table(headers, rows))
