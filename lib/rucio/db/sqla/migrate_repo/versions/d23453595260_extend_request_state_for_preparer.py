# -*- coding: utf-8 -*-
# Copyright 2020 CERN
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
# - Benedikt Ziemons <benedikt.ziemons@cern.ch>, 2020

"""
Add PREPARING state to Request model.
"""

from enum import Enum

import sqlalchemy
from alembic import op

# Alembic revision identifiers
revision = 'd23453595260'
down_revision = '8ea9122275b1'


class OldRequestState(Enum):
    QUEUED = 'Q'
    SUBMITTING = 'G'
    SUBMITTED = 'S'
    FAILED = 'F'
    DONE = 'D'
    LOST = 'L'
    NO_SOURCES = 'N'
    ONLY_TAPE_SOURCES = 'O'
    SUBMISSION_FAILED = 'A'
    MISMATCH_SCHEME = 'M'
    SUSPEND = 'U'
    WAITING = 'W'


old_request_state_enum = sqlalchemy.Enum(
    OldRequestState,
    name='REQUESTS_STATE_CHK',
    create_constraint=True,
    values_callable=lambda enum: [entry.value for entry in enum],
)


class NewRequestState(Enum):
    QUEUED = 'Q'
    SUBMITTING = 'G'
    SUBMITTED = 'S'
    FAILED = 'F'
    DONE = 'D'
    LOST = 'L'
    NO_SOURCES = 'N'
    ONLY_TAPE_SOURCES = 'O'
    SUBMISSION_FAILED = 'A'
    MISMATCH_SCHEME = 'M'
    SUSPEND = 'U'
    WAITING = 'W'
    PREPARING = 'P'


new_request_state_enum = sqlalchemy.Enum(
    NewRequestState,
    name='REQUESTS_STATE_CHK',
    create_constraint=True,
    values_callable=lambda enum: [entry.value for entry in enum],
)


def upgrade():
    with op.batch_alter_table('requests') as batch_op:
        batch_op.alter_column(
            'state',
            type_=new_request_state_enum,
            server_default=sqlalchemy.text(f"'{NewRequestState.QUEUED.value}'"),
            existing_type=old_request_state_enum,
            existing_server_default=sqlalchemy.text(f"'{OldRequestState.QUEUED.value}'"),
            postgresql_using=f'state::name::"{new_request_state_enum.name}"',
        )


def downgrade():
    with op.batch_alter_table('requests') as batch_op:
        batch_op.alter_column(
            'state',
            type_=old_request_state_enum,
            server_default=sqlalchemy.text(f"'{OldRequestState.QUEUED.value}'"),
            existing_type=new_request_state_enum,
            existing_server_default=sqlalchemy.text(f"'{NewRequestState.QUEUED.value}'"),
            postgresql_using=f'state::name::"{old_request_state_enum.name}"',
        )
