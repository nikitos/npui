"""Initial revision

Revision ID: dc3035eac910
Revises: 
Create Date: 2017-09-25 16:24:04.787272

"""

# revision identifiers, used by Alembic.
revision = 'dc3035eac910'
down_revision = None
branch_labels = ('bills',)
depends_on = ['2e190ad964b4', '075de24b065d']

from alembic import op
import sqlalchemy as sa
from sqlalchemy import FetchedValue
from netprofile.db import ddl as npd
from netprofile.db import fields as npf

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('bills_serials',
    sa.Column('bsid', npf.UInt32(), npd.Comment('Bill serial counter ID'), nullable=False, default=sa.Sequence('bills_serials_bsid_seq')),
    sa.Column('name', sa.Unicode(length=255), npd.Comment('Bill serial counter name'), nullable=False),
    sa.Column('value', npf.UInt32(), npd.Comment('Bill serial counter value'), nullable=False),
    sa.PrimaryKeyConstraint('bsid', name=op.f('bills_serials_pk')),
    mysql_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.set_table_comment('bills_serials', 'Bill serial counters')
    op.create_index('bills_serials_u_name', 'bills_serials', ['name'], unique=True)
    op.create_table('bills_types',
    sa.Column('btypeid', npf.UInt32(), npd.Comment('Bill type ID'), nullable=False, default=sa.Sequence('bills_types_btypeid_seq')),
    sa.Column('bsid', npf.UInt32(), npd.Comment('Bill serial counter ID'), server_default=sa.text('NULL'), nullable=True),
    sa.Column('name', sa.Unicode(length=255), npd.Comment('Bill type name'), nullable=False),
    sa.Column('prefix', sa.Unicode(length=48), npd.Comment('Bill number prefix'), server_default=sa.text('NULL'), nullable=True),
    sa.Column('cap', npf.ASCIIString(length=48), npd.Comment('Capability to create bills of this type'), server_default=sa.text('NULL'), nullable=True),
    sa.Column('issuer', npf.UInt32(), npd.Comment('Issuer entity ID'), server_default=sa.text('NULL'), nullable=True),
    sa.Column('siotypeid', npf.UInt32(), npd.Comment('Stash I/O type generated when paid'), server_default=sa.text('NULL'), nullable=True),
    sa.Column('docid', npf.UInt32(), npd.Comment('Bill document ID'), server_default=sa.text('NULL'), nullable=True),
    sa.Column('template', npf.JSONData(), npd.Comment('Bill parts template'), server_default=sa.text('NULL'), nullable=True),
    sa.Column('mutable', npf.NPBoolean(), npd.Comment('Is template mutable?'), server_default=npf.npbool(True), nullable=False),
    sa.Column('descr', sa.UnicodeText(), npd.Comment('Bill type description'), server_default=sa.text('NULL'), nullable=True),
    sa.ForeignKeyConstraint(['bsid'], ['bills_serials.bsid'], name='bills_types_fk_bsid', onupdate='CASCADE', ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['cap'], ['privileges.code'], name='bills_types_fk_cap', onupdate='CASCADE', ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['docid'], ['docs_def.docid'], name='bills_types_fk_docid', onupdate='CASCADE', ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['issuer'], ['entities_def.entityid'], name='bills_types_fk_issuer', onupdate='CASCADE', ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['siotypeid'], ['stashes_io_types.siotypeid'], name='bills_types_fk_siotypeid', onupdate='CASCADE', ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('btypeid', name=op.f('bills_types_pk')),
    mysql_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.set_table_comment('bills_types', 'Bill types')
    op.create_index('bills_types_i_bsid', 'bills_types', ['bsid'], unique=False)
    op.create_index('bills_types_i_cap', 'bills_types', ['cap'], unique=False)
    op.create_index('bills_types_i_docid', 'bills_types', ['docid'], unique=False)
    op.create_index('bills_types_i_issuer', 'bills_types', ['issuer'], unique=False)
    op.create_index('bills_types_i_siotypeid', 'bills_types', ['siotypeid'], unique=False)
    op.create_index('bills_types_u_name', 'bills_types', ['name'], unique=True)
    op.create_table('bills_def',
    sa.Column('billid', npf.UInt32(), npd.Comment('Bill ID'), nullable=False, default=sa.Sequence('bills_def_billid_seq')),
    sa.Column('btypeid', npf.UInt32(), npd.Comment('Bill type ID'), nullable=False),
    sa.Column('serial', npf.UInt32(), npd.Comment('Bill serial number'), server_default=sa.text('NULL'), nullable=True),
    sa.Column('entityid', npf.UInt32(), npd.Comment('Entity ID'), nullable=False),
    sa.Column('stashid', npf.UInt32(), npd.Comment('Stash ID'), nullable=False),
    sa.Column('currid', npf.UInt32(), npd.Comment('Currency ID'), server_default=sa.text('NULL'), nullable=True),
    sa.Column('sum', npf.Money(precision=20, scale=8), npd.Comment('Total amount to be paid'), nullable=False),
    sa.Column('state', npf.DeclEnumType(name='BillState', values=['C', 'S', 'P', 'R']), npd.Comment('Created / Sent / Paid / Recalled'), server_default=sa.text("'C'"), nullable=False),
    sa.Column('title', sa.Unicode(length=255), npd.Comment('Bill title'), server_default=sa.text('NULL'), nullable=True),
    sa.Column('adate', sa.Date(), npd.Comment('Accounting date'), server_default=sa.text('NULL'), nullable=True),
    sa.Column('ctime', sa.TIMESTAMP(), npd.Comment('Creation timestamp'), server_default=FetchedValue(), nullable=True),
    sa.Column('mtime', sa.TIMESTAMP(), npd.Comment('Last modification timestamp'), server_default=npd.CurrentTimestampDefault(on_update=True), nullable=False),
    sa.Column('ptime', sa.TIMESTAMP(), npd.Comment('Payment timestamp'), server_default=FetchedValue(), nullable=True),
    sa.Column('cby', npf.UInt32(), npd.Comment('Created by'), server_default=sa.text('NULL'), nullable=True),
    sa.Column('mby', npf.UInt32(), npd.Comment('Modified by'), server_default=sa.text('NULL'), nullable=True),
    sa.Column('pby', npf.UInt32(), npd.Comment('Marked as paid by'), server_default=sa.text('NULL'), nullable=True),
    sa.Column('parts', npf.JSONData(), npd.Comment('Bill parts'), server_default=sa.text('NULL'), nullable=True),
    sa.Column('descr', sa.UnicodeText(), npd.Comment('Bill description'), server_default=sa.text('NULL'), nullable=True),
    sa.ForeignKeyConstraint(['btypeid'], ['bills_types.btypeid'], name='bills_def_fk_btypeid', onupdate='CASCADE'),
    sa.ForeignKeyConstraint(['cby'], ['users.uid'], name='bills_def_fk_cby', onupdate='CASCADE', ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['currid'], ['currencies_def.currid'], name='bills_def_fk_currid', onupdate='CASCADE'),
    sa.ForeignKeyConstraint(['entityid'], ['entities_def.entityid'], name='bills_def_fk_entityid', onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['mby'], ['users.uid'], name='bills_def_fk_mby', onupdate='CASCADE', ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['pby'], ['users.uid'], name='bills_def_fk_pby', onupdate='CASCADE', ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['stashid'], ['stashes_def.stashid'], name='bills_def_fk_stashid', onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('billid', name=op.f('bills_def_pk')),
    mysql_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.set_table_comment('bills_def', 'Bills')
    op.create_trigger('netprofile_bills', 'bills_def', 'before', 'insert', 'dc3035eac910')
    op.create_trigger('netprofile_bills', 'bills_def', 'before', 'update', 'dc3035eac910')
    op.create_trigger('netprofile_bills', 'bills_def', 'after', 'insert', 'dc3035eac910')
    op.create_trigger('netprofile_bills', 'bills_def', 'after', 'update', 'dc3035eac910')
    op.create_trigger('netprofile_bills', 'bills_def', 'after', 'delete', 'dc3035eac910')
    op.create_index('bills_def_i_btypeid', 'bills_def', ['btypeid'], unique=False)
    op.create_index('bills_def_i_cby', 'bills_def', ['cby'], unique=False)
    op.create_index('bills_def_i_currid', 'bills_def', ['currid'], unique=False)
    op.create_index('bills_def_i_entityid', 'bills_def', ['entityid'], unique=False)
    op.create_index('bills_def_i_mby', 'bills_def', ['mby'], unique=False)
    op.create_index('bills_def_i_pby', 'bills_def', ['pby'], unique=False)
    op.create_index('bills_def_i_stashid', 'bills_def', ['stashid'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('bills_def_i_stashid', table_name='bills_def')
    op.drop_index('bills_def_i_pby', table_name='bills_def')
    op.drop_index('bills_def_i_mby', table_name='bills_def')
    op.drop_index('bills_def_i_entityid', table_name='bills_def')
    op.drop_index('bills_def_i_currid', table_name='bills_def')
    op.drop_index('bills_def_i_cby', table_name='bills_def')
    op.drop_index('bills_def_i_btypeid', table_name='bills_def')
    op.drop_table('bills_def')
    op.drop_index('bills_types_u_name', table_name='bills_types')
    op.drop_index('bills_types_i_siotypeid', table_name='bills_types')
    op.drop_index('bills_types_i_issuer', table_name='bills_types')
    op.drop_index('bills_types_i_docid', table_name='bills_types')
    op.drop_index('bills_types_i_cap', table_name='bills_types')
    op.drop_index('bills_types_i_bsid', table_name='bills_types')
    op.drop_table('bills_types')
    op.drop_index('bills_serials_u_name', table_name='bills_serials')
    op.drop_table('bills_serials')
    # ### end Alembic commands ###
