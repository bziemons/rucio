# -*- coding: utf-8 -*-
# Copyright 2021 CERN
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Authors:
# - Cedric Serfon <cedric.serfon@cern.ch>, 2021
# - Benedikt Ziemons <benedikt.ziemons@cern.ch>, 2021

''' Add index on service column in the message table '''
import sqlalchemy as sa

from alembic import context
from alembic.op import create_index, drop_index, alter_column

# Alembic revision identifiers
revision = '30fa38b6434e'
down_revision = 'e138c364ebd0'


def upgrade():
    '''
    Upgrade the database to this revision
    '''
    if context.get_context().dialect.name in ['oracle', 'mysql', 'mariadb', 'postgresql']:
        schema = context.get_context().version_table_schema if context.get_context().version_table_schema else ''
        alter_column('messages', 'services', existing_type=sa.String(2048), type_=sa.String(256), schema=schema)
        alter_column('messages', 'event_type', existing_type=sa.String(1024), type_=sa.String(256), schema=schema)
    create_index('MESSAGES_SERVICES_IDX', 'messages', ['services', 'event_type'])


def downgrade():
    '''
    Downgrade the database to the previous revision
    '''
    drop_index('MESSAGES_SERVICES_IDX', 'messages')
    if context.get_context().dialect.name in ['oracle', 'mysql', 'mariadb', 'postgresql']:
        schema = context.get_context().version_table_schema if context.get_context().version_table_schema else ''
        alter_column('messages', 'services', existing_type=sa.String(256), type_=sa.String(2048), schema=schema)
        alter_column('messages', 'event_type', existing_type=sa.String(256), type_=sa.String(1024), schema=schema)
