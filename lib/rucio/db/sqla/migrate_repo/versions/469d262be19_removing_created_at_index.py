# -*- coding: utf-8 -*-
# Copyright 2015-2021 CERN
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
# - Vincent Garonne <vincent.garonne@cern.ch>, 2015-2017
# - Martin Barisits <martin.barisits@cern.ch>, 2016
# - Mario Lassnig <mario.lassnig@cern.ch>, 2019
# - Benedikt Ziemons <benedikt.ziemons@cern.ch>, 2021

''' removing created_at index '''

from alembic import context
from alembic.op import create_index, drop_index


revision = '469d262be19'
down_revision = '16a0aca82e12'


def upgrade():
    '''
    Upgrade the database to this revision
    '''

    if context.get_context().dialect.name in ['oracle', 'mysql', 'mariadb', 'postgresql']:
        create_index('UPDATED_DIDS_SCOPERULENAME_IDX', 'updated_dids', ['scope', 'rule_evaluation_action', 'name'])
        drop_index('CREATED_AT_IDX', 'updated_dids')


def downgrade():
    '''
    Downgrade the database to the previous revision
    '''

    if context.get_context().dialect.name in ['oracle', 'mysql', 'mariadb', 'postgresql']:
        drop_index('UPDATED_DIDS_SCOPERULENAME_IDX', 'updated_dids')
        create_index('CREATED_AT_IDX', 'updated_dids', ['created_at'])
