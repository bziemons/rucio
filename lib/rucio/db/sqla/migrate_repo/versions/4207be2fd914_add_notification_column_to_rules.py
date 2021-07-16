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
# - Mario Lassnig <mario.lassnig@cern.ch>, 2019-2020
# - Benedikt Ziemons <benedikt.ziemons@cern.ch>, 2021

""" add notification column to rules """

from enum import Enum

import sqlalchemy
from alembic import op

# Alembic revision identifiers
revision = '4207be2fd914'
down_revision = '14ec5aeb64cf'


class RuleNotification(Enum):
    YES = 'Y'
    NO = 'N'
    CLOSE = 'C'


rule_notification_enum = sqlalchemy.Enum(
    RuleNotification,
    name='RULES_NOTIFICATION_CHK',
    create_constraint=True,
    values_callable=lambda enum: [entry.value for entry in enum],
)


def upgrade():
    '''
    Upgrade the database to this revision
    '''

    op.add_column(
        'rules',
        sqlalchemy.Column('notification', rule_notification_enum),
    )


def downgrade():
    '''
    Downgrade the database to the previous revision
    '''

    with op.batch_alter_table('rules') as batch_op:
        batch_op.drop_column('notification')
        rule_notification_enum.drop(bind=batch_op.get_bind(), checkfirst=True)
