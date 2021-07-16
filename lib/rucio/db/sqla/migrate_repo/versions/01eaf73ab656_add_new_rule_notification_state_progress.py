# -*- coding: utf-8 -*-
# Copyright 2019-2021 CERN
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
# - Martin Barisits <martin.barisits@cern.ch>, 2019
# - Mario Lassnig <mario.lassnig@cern.ch>, 2019-2021
# - Robert Illingworth <illingwo@fnal.gov>, 2019

''' add new rule notification state progress '''

from enum import Enum

import sqlalchemy
from alembic import op

# Alembic revision identifiers
revision = '01eaf73ab656'
down_revision = '90f47792bb76'


def load_rules(bind, schema):
    return sqlalchemy.Table(
        'rules',
        sqlalchemy.MetaData(),
        autoload_with=bind,
        schema=schema,
    )


class OldRuleNotification(Enum):
    YES = 'Y'
    NO = 'N'
    CLOSE = 'C'


def old_rule_notification_enum(metadata):
    return sqlalchemy.Enum(
        OldRuleNotification,
        name='RULES_NOTIFICATION_CHK',
        create_constraint=True,
        values_callable=lambda enum: [entry.value for entry in enum],
        metadata=metadata,
    )


class NewRuleNotification(Enum):
    YES = 'Y'
    NO = 'N'
    CLOSE = 'C'
    PROGRESS = 'P'


def new_rule_notification_enum(metadata):
    return sqlalchemy.Enum(
        NewRuleNotification,
        name='RULES_NOTIFICATION_CHK',
        create_constraint=True,
        values_callable=lambda enum: [entry.value for entry in enum],
        metadata=metadata,
    )


def upgrade():
    '''
    Upgrade the database to this revision
    '''

    rules = load_rules(bind=op.get_bind(), schema=op.get_context().version_table_schema)
    op.alter_column(
        rules.name,
        'notification',
        type_=new_rule_notification_enum(metadata=rules.metadata),
        existing_type=old_rule_notification_enum(metadata=rules.metadata),
        schema=rules.schema,
    )


def downgrade():
    '''
    Downgrade the database to the previous revision
    '''

    rules = load_rules(bind=op.get_bind(), schema=op.get_context().version_table_schema)
    op.alter_column(
        rules.name,
        'notification',
        type_=old_rule_notification_enum(metadata=rules.metadata),
        existing_type=new_rule_notification_enum(metadata=rules.metadata),
        schema=rules.schema,
    )
