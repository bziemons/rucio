# -*- coding: utf-8 -*-
# Copyright 2016-2021 CERN
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
# - Vincent Garonne <vincent.garonne@cern.ch>, 2016-2017
# - Martin Barisits <martin.barisits@cern.ch>, 2017
# - Mario Lassnig <mario.lassnig@cern.ch>, 2019
# - Benedikt Ziemons <benedikt.ziemons@cern.ch>, 2021

''' add third_party_copy column to rse_protocols '''

import sqlalchemy as sa

from alembic import context
from alembic.op import add_column, drop_column


# Alembic revision identifiers
revision = 'fe8ea2fa9788'
down_revision = '0437a40dbfd1'


def upgrade():
    '''
    Upgrade the database to this revision
    '''

    if context.get_context().dialect.name in ['oracle', 'mysql', 'mariadb', 'postgresql']:
        schema = context.get_context().version_table_schema if context.get_context().version_table_schema else ''
        add_column('rse_protocols', sa.Column('third_party_copy', sa.Integer, server_default='0'), schema=schema)


def downgrade():
    '''
    Downgrade the database to the previous revision
    '''

    if context.get_context().dialect.name in ['oracle', 'mysql', 'mariadb', 'postgresql']:
        schema = context.get_context().version_table_schema if context.get_context().version_table_schema else ''
        drop_column('rse_protocols', 'third_party_copy', schema=schema)
