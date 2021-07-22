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
# - Martin Barisits <martin.barisits@cern.ch>, 2016-2017
# - Mario Lassnig <mario.lassnig@cern.ch>, 2019-2021
# - Robert Illingworth <illingwo@fnal.gov>, 2019
# - Benedikt Ziemons <benedikt.ziemons@cern.ch>, 2021

""" asynchronous rules and rule approval """

from enum import Enum

import sqlalchemy
from alembic import op

# Alembic revision identifiers
revision = '1d96f484df21'
down_revision = '3d9813fab443'


class OldRuleState(Enum):
    REPLICATING = 'R'
    OK = 'O'
    STUCK = 'S'
    SUSPENDED = 'U'
    WAITING_APPROVAL = 'W'
    INJECT = 'I'


old_rule_state_enum = sqlalchemy.Enum(
    OldRuleState,
    name='RULES_STATE_CHK',
    create_constraint=True,
    values_callable=lambda enum: [entry.value for entry in enum],
)


class NewRuleState(Enum):
    REPLICATING = 'R'
    OK = 'O'
    STUCK = 'S'
    SUSPENDED = 'U'
    WAITING_APPROVAL = 'W'
    INJECT = 'I'


new_rule_state_enum = sqlalchemy.Enum(
    NewRuleState,
    name='RULES_STATE_CHK',
    create_constraint=True,
    values_callable=lambda enum: [entry.value for entry in enum],
)


def upgrade():
    with op.batch_alter_table('rules') as batch_op:
        batch_op.add_column(
            sqlalchemy.Column(
                'ignore_account_limit',
                sqlalchemy.Boolean(name='RULES_IGNORE_ACCOUNT_LIMIT_CHK', create_constraint=True),
                default=False,
            )
        )
        batch_op.alter_column(
            'state',
            type_=new_rule_state_enum,
            existing_type=old_rule_state_enum,
            postgresql_using=f'state::name::"{new_rule_state_enum.name}"',
        )


def downgrade():
    with op.batch_alter_table('rules') as batch_op:
        batch_op.drop_column('ignore_account_limit')
        batch_op.alter_column(
            'state',
            type_=old_rule_state_enum,
            existing_type=new_rule_state_enum,
            postgresql_using=f'state::name::"{old_rule_state_enum.name}"',
        )
