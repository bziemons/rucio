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
# - Ruturaj Gujar <ruturaj.gujar23@gmail.com>, 2019
# - Martin Barisits <martin.barisits@cern.ch>, 2019
# - Benedikt Ziemons <benedikt.ziemons@cern.ch>, 2021
# - Mario Lassnig <mario.lassnig@cern.ch>, 2021

''' add saml identity type '''

from alembic import context
from alembic.op import create_check_constraint, drop_constraint

from rucio.db.sqla.util import try_drop_constraint

# Alembic revision identifiers
revision = '9a1b149a2044'
down_revision = '53b479c3cb0f'


def upgrade():
    '''
    Upgrade the database to this revision
    '''

    if context.get_context().dialect.name in ['oracle']:
        try_drop_constraint('IDENTITIES_TYPE_CHK', 'identities')
        create_check_constraint(constraint_name='IDENTITIES_TYPE_CHK',
                                table_name='identities',
                                condition="identity_type in ('X509', 'GSS', 'USERPASS', 'SSH', 'SAML')")
        try_drop_constraint('ACCOUNT_MAP_ID_TYPE_CHK', 'account_map')
        create_check_constraint(constraint_name='ACCOUNT_MAP_ID_TYPE_CHK',
                                table_name='account_map',
                                condition="identity_type in ('X509', 'GSS', 'USERPASS', 'SSH', 'SAML')")

    if context.get_context().dialect.name in ['postgresql', 'mysql', 'mariadb']:
        drop_constraint('IDENTITIES_TYPE_CHK', 'identities', type_='check')
        create_check_constraint(constraint_name='IDENTITIES_TYPE_CHK',
                                table_name='identities',
                                condition="identity_type in ('X509', 'GSS', 'USERPASS', 'SSH', 'SAML')")
        drop_constraint('ACCOUNT_MAP_ID_TYPE_CHK', 'account_map', type_='check')
        create_check_constraint(constraint_name='ACCOUNT_MAP_ID_TYPE_CHK',
                                table_name='account_map',
                                condition="identity_type in ('X509', 'GSS', 'USERPASS', 'SSH', 'SAML')")


def downgrade():
    '''
    Downgrade the database to the previous revision
    '''

    if context.get_context().dialect.name in ['oracle']:
        try_drop_constraint('IDENTITIES_TYPE_CHK', 'identities')
        create_check_constraint(constraint_name='IDENTITIES_TYPE_CHK',
                                table_name='identities',
                                condition="identity_type in ('X509', 'GSS', 'USERPASS', 'SSH')")

        try_drop_constraint('ACCOUNT_MAP_ID_TYPE_CHK', 'account_map')
        create_check_constraint(constraint_name='ACCOUNT_MAP_ID_TYPE_CHK',
                                table_name='account_map',
                                condition="identity_type in ('X509', 'GSS', 'USERPASS', 'SSH')")

    elif context.get_context().dialect.name in ['postgresql', 'mysql', 'mariadb']:
        drop_constraint('IDENTITIES_TYPE_CHK', 'identities', type_='check')
        create_check_constraint(constraint_name='IDENTITIES_TYPE_CHK',
                                table_name='identities',
                                condition="identity_type in ('X509', 'GSS', 'USERPASS', 'SSH')")

        drop_constraint('ACCOUNT_MAP_ID_TYPE_CHK', 'account_map', type_='check')
        create_check_constraint(constraint_name='ACCOUNT_MAP_ID_TYPE_CHK',
                                table_name='account_map',
                                condition="identity_type in ('X509', 'GSS', 'USERPASS', 'SSH')")
        # drop_constraint('ACCOUNT_MAP_ID_TYPE_FK', 'account_map', type_='foreignkey')
        # create_foreign_key('ACCOUNT_MAP_ID_TYPE_FK', 'account_map', 'identities', ['identity', 'identity_type'], ['identity', 'identity_type'])
