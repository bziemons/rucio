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
# - Vincent Garonne <vgaronne@gmail.com>, 2015-2017
# - Martin Barisits <martin.barisits@cern.ch>, 2016
# - Mario Lassnig <mario.lassnig@cern.ch>, 2019-2021

""" extend request state """

from enum import Enum

import sqlalchemy
import sqlalchemy as sa
from alembic import op

# Alembic revision identifiers
revision = 'bb695f45c04'
down_revision = '3082b8cef557'


class OldRequestState(Enum):
    QUEUED = 'Q'
    SUBMITTING = 'G'
    SUBMITTED = 'S'
    FAILED = 'F'
    DONE = 'D'
    LOST = 'L'


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
    SUSPEND = 'U'


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
            postgresql_using=f'state::"{new_request_state_enum.name}"',
        )
        batch_op.add_column(sa.Column('submitter_id', sa.Integer()))

    with op.batch_alter_table('sources') as batch_op:
        batch_op.add_column(sa.Column('is_using', sa.Boolean()))


def downgrade():
    with op.batch_alter_table('requests') as batch_op:
        batch_op.alter_column(
            'state',
            type_=old_request_state_enum,
            server_default=sqlalchemy.text(f"'{OldRequestState.QUEUED.value}'"),
            existing_type=new_request_state_enum,
            existing_server_default=sqlalchemy.text(f"'{NewRequestState.QUEUED.value}'"),
            postgresql_using=f'state::"{old_request_state_enum.name}"',
        )
        batch_op.drop_column('submitter_id')

    with op.batch_alter_table('sources') as batch_op:
        batch_op.drop_column('is_using')
