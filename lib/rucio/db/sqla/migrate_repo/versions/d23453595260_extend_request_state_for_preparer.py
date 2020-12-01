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

from alembic import context
from alembic.op import execute, create_check_constraint, drop_constraint

# Alembic revision identifiers
revision = 'd23453595260'
down_revision = '8ea9122275b1'


def upgrade():
    """
    Upgrade the database to this revision
    """

    new_enum_values = ['Q', 'G', 'S', 'D', 'F', 'L', 'N', 'O', 'A', 'U', 'W', 'M', 'P']
    update_enum(new_enum_values)


def downgrade():
    """
    Downgrade the database to the previous revision
    """

    old_enum_values = ['Q', 'G', 'S', 'D', 'F', 'L', 'N', 'O', 'A', 'U', 'W', 'M']
    update_enum(old_enum_values)


def enum_values_str(enumvals):
    return ', '.join(map(lambda x: x.join(("'", "'")), enumvals))


def update_enum(enum_values):
    schema = context.get_context().version_table_schema + '.' if context.get_context().version_table_schema else ''
    dialect = context.get_context().dialect.name
    create_check = False

    if dialect == 'oracle':
        drop_constraint('REQUESTS_STATE_CHK', 'requests', type_='check')
        create_check = True
    elif dialect == 'postgresql':
        execute('ALTER TABLE %srequests DROP CONSTRAINT IF EXISTS "REQUESTS_STATE_CHK", ALTER COLUMN state TYPE CHAR' % schema)
        execute('DROP TYPE "REQUESTS_STATE_CHK"')
        execute(f'CREATE TYPE "REQUESTS_STATE_CHK" AS ENUM({enum_values_str(enum_values)})')
        execute('ALTER TABLE %srequests ALTER COLUMN state TYPE "REQUESTS_STATE_CHK" USING state::"REQUESTS_STATE_CHK"' % schema)
    elif dialect == 'mysql' and context.get_context().dialect.server_version_info[0] == 5:
        create_check = True
    elif dialect == 'mysql' and context.get_context().dialect.server_version_info[0] == 8:
        execute('ALTER TABLE ' + schema + 'requests DROP CHECK REQUESTS_STATE_CHK')
        create_check = True
    if create_check:
        create_check_constraint(constraint_name='REQUESTS_STATE_CHK', table_name='requests',
                                condition=f'state in ({enum_values_str(enum_values)})')
