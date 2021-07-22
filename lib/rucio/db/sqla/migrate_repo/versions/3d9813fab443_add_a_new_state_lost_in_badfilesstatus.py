# Copyright 2013-2019 CERN for the benefit of the ATLAS collaboration.
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
# - Cedric Serfon <cedric.serfon@cern.ch>, 2015
# - Mario Lassnig <mario.lassnig@cern.ch>, 2019

""" add a new state LOST in BadFilesStatus and switch to enum type """

from enum import Enum

import sqlalchemy
from alembic import op

# Alembic revision identifiers
revision = '3d9813fab443'
down_revision = '1fc15ab60d43'


class BadFilesStatus(Enum):
    BAD = 'B'
    DELETED = 'D'
    LOST = 'L'
    RECOVERED = 'R'
    SUSPICIOUS = 'S'


bad_replica_state_enum = sqlalchemy.Enum(
    BadFilesStatus,
    name='BAD_REPLICAS_STATE_CHK',
    create_constraint=True,
    values_callable=lambda enum: [entry.value for entry in enum],
)


def upgrade():
    with op.batch_alter_table('bad_replicas') as batch_op:
        bad_replica_state_enum.create(bind=batch_op.get_bind(), checkfirst=True)
        batch_op.alter_column(
            'state',
            type_=bad_replica_state_enum,
            existing_type=sqlalchemy.String(1),
            postgresql_using=f'state::name::"{bad_replica_state_enum.name}"',
        )


def downgrade():
    with op.batch_alter_table('bad_replicas') as batch_op:
        batch_op.alter_column(
            'state',
            type_=sqlalchemy.String(1),
            existing_type=bad_replica_state_enum,
            postgresql_using=f'state::"char"',
        )
        batch_op.drop_constraint(bad_replica_state_enum.name, type_='check')
        bad_replica_state_enum.drop(bind=batch_op.get_bind(), checkfirst=True)
