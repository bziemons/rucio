# Copyright 2013-2021 CERN
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
# - Ruturaj Gujar <ruturaj.gujar23@gmail.com>, 2019
# - Mario Lassnig <mario.lassnig@cern.ch>, 2021

""" add saml identity type """

from enum import Enum

import sqlalchemy
from alembic import op

# Alembic revision identifiers
revision = '9a1b149a2044'
down_revision = '53b479c3cb0f'


class OldIdentityType(Enum):
    X509 = 'X509'
    GSS = 'GSS'
    USERPASS = 'USERPASS'
    SSH = 'SSH'


old_identities_enum = sqlalchemy.Enum(
    OldIdentityType,
    name='IDENTITIES_TYPE_CHK',
    create_constraint=True,
    values_callable=lambda enum: [entry.value for entry in enum],
)

old_account_map_identities_enum = sqlalchemy.Enum(
    OldIdentityType,
    name='ACCOUNT_MAP_ID_TYPE_CHK',
    create_constraint=True,
    values_callable=lambda enum: [entry.value for entry in enum],
)


class NewIdentityType(Enum):
    X509 = 'X509'
    GSS = 'GSS'
    USERPASS = 'USERPASS'
    SSH = 'SSH'
    SAML = 'SAML'


new_identities_enum = sqlalchemy.Enum(
    NewIdentityType,
    name='IDENTITIES_TYPE_CHK',
    create_constraint=True,
    values_callable=lambda enum: [entry.value for entry in enum],
)

new_account_map_identities_enum = sqlalchemy.Enum(
    NewIdentityType,
    name='ACCOUNT_MAP_ID_TYPE_CHK',
    create_constraint=True,
    values_callable=lambda enum: [entry.value for entry in enum],
)


def upgrade():
    with op.batch_alter_table('identities') as batch_op:
        batch_op.alter_column(
            'identity_type',
            type_=new_identities_enum,
            existing_type=old_identities_enum,
            postgresql_using=f'identity_type::text::"{old_identities_enum.name}"',
        )

    with op.batch_alter_table('account_map') as batch_op:
        to_type = new_identities_enum if op.get_context().dialect.name == 'postgresql' else new_account_map_identities_enum
        from_type = old_identities_enum if op.get_context().dialect.name == 'postgresql' else old_account_map_identities_enum
        batch_op.alter_column(
            'identity_type',
            type_=to_type,
            existing_type=from_type,
            postgresql_using=f'identity_type::text::"{from_type.name}"',
        )


def downgrade():
    with op.batch_alter_table('identities') as batch_op:
        batch_op.alter_column(
            'identity_type',
            type_=old_identities_enum,
            existing_type=new_identities_enum,
            postgresql_using=f'identity_type::text::"{new_identities_enum.name}"',
        )

    with op.batch_alter_table('account_map') as batch_op:
        from_type = new_identities_enum if op.get_context().dialect.name == 'postgresql' else new_account_map_identities_enum
        to_type = old_identities_enum if op.get_context().dialect.name == 'postgresql' else old_account_map_identities_enum
        batch_op.alter_column(
            'identity_type',
            type_=to_type,
            existing_type=from_type,
            postgresql_using=f'identity_type::text::"{from_type.name}"',
        )
