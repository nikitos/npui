"""Initial revision

Revision ID: 21e3f826ac55
Revises: 
Create Date: 2017-09-25 15:29:49.208307

"""

# revision identifiers, used by Alembic.
revision = '21e3f826ac55'
down_revision = None
branch_labels = ('networks',)
depends_on = '92c966fd43d9'

from alembic import op
import sqlalchemy as sa
from sqlalchemy import FetchedValue
from netprofile.db import ddl as npd
from netprofile.db import fields as npf

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('nets_groups',
    sa.Column('netgid', npf.UInt32(), npd.Comment('Network group ID'), nullable=False, default=sa.Sequence('nets_groups_netgid_seq')),
    sa.Column('name', sa.Unicode(length=255), npd.Comment('Network group name'), nullable=False),
    sa.Column('descr', sa.UnicodeText(), npd.Comment('Network group description'), server_default=sa.text('NULL'), nullable=True),
    sa.PrimaryKeyConstraint('netgid', name=op.f('nets_groups_pk')),
    mysql_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.set_table_comment('nets_groups', 'Network groups')
    op.create_index('nets_groups_u_name', 'nets_groups', ['name'], unique=True)
    op.create_table('nets_hltypes',
    sa.Column('hltypeid', npf.UInt32(), npd.Comment('Networks-hosts linkage type ID'), nullable=False, default=sa.Sequence('nets_hltypes_hltypeid_seq', start=101, increment=1)),
    sa.Column('name', sa.Unicode(length=255), npd.Comment('Networks-hosts linkage type name'), nullable=False),
    sa.Column('unique', npf.NPBoolean(), npd.Comment('Is unique per network?'), server_default=npf.npbool(False), nullable=False),
    sa.PrimaryKeyConstraint('hltypeid', name=op.f('nets_hltypes_pk')),
    mysql_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.set_table_comment('nets_hltypes', 'Networks-hosts linkage types')
    op.create_index('nets_hltypes_u_name', 'nets_hltypes', ['name'], unique=True)
    op.create_table('rt_def',
    sa.Column('rtid', npf.UInt32(), npd.Comment('Routing table ID'), nullable=False, default=sa.Sequence('rt_def_rtid_seq')),
    sa.Column('name', sa.Unicode(length=255), npd.Comment('Routing table name'), nullable=False),
    sa.PrimaryKeyConstraint('rtid', name=op.f('rt_def_pk')),
    mysql_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.set_table_comment('rt_def', 'Routing tables')
    op.create_index('rt_def_u_name', 'rt_def', ['name'], unique=True)
    op.create_table('rt_bits',
    sa.Column('rtbid', npf.UInt32(), npd.Comment('Routing table bit ID'), nullable=False, default=sa.Sequence('rt_bits_rtbid_seq')),
    sa.Column('rtid', npf.UInt32(), npd.Comment('Routing table ID'), nullable=False),
    sa.Column('net', npf.IPv4Address(), npd.Comment('Network address'), nullable=False),
    sa.Column('cidr', npf.UInt8(), npd.Comment('Network CIDR'), server_default=sa.text('24'), nullable=False),
    sa.Column('rtr', npf.UInt32(), npd.Comment('Next hop host ID'), server_default=sa.text('NULL'), nullable=True),
    sa.ForeignKeyConstraint(['rtid'], ['rt_def.rtid'], name='rt_bits_fk_rtid', onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['rtr'], ['hosts_def.hostid'], name='rt_bits_fk_hostid', onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('rtbid', name=op.f('rt_bits_pk')),
    mysql_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.set_table_comment('rt_bits', 'IPv4 routing table entries')
    op.create_index('rt_bits_i_rtid', 'rt_bits', ['rtid'], unique=False)
    op.create_index('rt_bits_i_rtr', 'rt_bits', ['rtr'], unique=False)
    op.create_table('nets_def',
    sa.Column('netid', npf.UInt32(), npd.Comment('Network ID'), nullable=False, default=sa.Sequence('nets_def_netid_seq')),
    sa.Column('name', sa.Unicode(length=255), npd.Comment('Network name'), nullable=False),
    sa.Column('domainid', npf.UInt32(), npd.Comment('Domain ID'), nullable=False),
    sa.Column('netgid', npf.UInt32(), npd.Comment('Network group ID'), server_default=sa.text('NULL'), nullable=True),
    sa.Column('mgmtdid', npf.UInt32(), npd.Comment('Management device ID'), server_default=sa.text('NULL'), nullable=True),
    sa.Column('enabled', npf.NPBoolean(), npd.Comment('Is network enabled?'), server_default=npf.npbool(True), nullable=False),
    sa.Column('public', npf.NPBoolean(), npd.Comment('Is network visible to outsiders?'), server_default=npf.npbool(True), nullable=False),
    sa.Column('ipaddr', npf.IPv4Address(), npd.Comment('Network IPv4 address'), server_default=sa.text('NULL'), nullable=True),
    sa.Column('ip6addr', npf.IPv6Address(length=16), npd.Comment('Network IPv6 address'), server_default=sa.text('NULL'), nullable=True),
    sa.Column('cidr', npf.UInt8(), npd.Comment('Network CIDR number'), server_default=sa.text('24'), nullable=False),
    sa.Column('cidr6', npf.UInt8(), npd.Comment('Network CIDRv6 number'), server_default=sa.text('64'), nullable=False),
    sa.Column('vlanid', npf.UInt16(), npd.Comment('Network VLAN ID'), server_default=sa.text('0'), nullable=False),
    sa.Column('rtid', npf.UInt32(), npd.Comment('Routing table ID'), server_default=sa.text('NULL'), nullable=True),
    sa.Column('gueststart', npf.UInt16(), npd.Comment('Start of IPv4 guest allocation area'), server_default=sa.text('NULL'), nullable=True),
    sa.Column('guestend', npf.UInt16(), npd.Comment('End of IPv4 guest allocation area'), server_default=sa.text('NULL'), nullable=True),
    sa.Column('gueststart6', npf.IPv6Offset(precision=39, scale=0), npd.Comment('Start of IPv6 guest allocation area'), server_default=sa.text('NULL'), nullable=True),
    sa.Column('guestend6', npf.IPv6Offset(precision=39, scale=0), npd.Comment('End of IPv6 guest allocation area'), server_default=sa.text('NULL'), nullable=True),
    sa.Column('descr', sa.UnicodeText(), npd.Comment('Network description'), server_default=sa.text('NULL'), nullable=True),
    sa.ForeignKeyConstraint(['domainid'], ['domains_def.domainid'], name='nets_def_fk_domainid', onupdate='CASCADE'),
    sa.ForeignKeyConstraint(['mgmtdid'], ['devices_network.did'], name='nets_def_fk_mgmtdid', onupdate='CASCADE', ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['netgid'], ['nets_groups.netgid'], name='nets_def_fk_netgid', onupdate='CASCADE', ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['rtid'], ['rt_def.rtid'], name='nets_def_fk_rtid', onupdate='CASCADE', ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('netid', name=op.f('nets_def_pk')),
    mysql_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.set_table_comment('nets_def', 'Networks')
    op.create_trigger('netprofile_networks', 'nets_def', 'after', 'insert', '21e3f826ac55')
    op.create_trigger('netprofile_networks', 'nets_def', 'after', 'update', '21e3f826ac55')
    op.create_trigger('netprofile_networks', 'nets_def', 'after', 'delete', '21e3f826ac55')
    op.create_index('nets_def_i_domainid', 'nets_def', ['domainid'], unique=False)
    op.create_index('nets_def_i_mgmtdid', 'nets_def', ['mgmtdid'], unique=False)
    op.create_index('nets_def_i_netgid', 'nets_def', ['netgid'], unique=False)
    op.create_index('nets_def_i_rtid', 'nets_def', ['rtid'], unique=False)
    op.create_index('nets_def_u_ip6addr', 'nets_def', ['ip6addr'], unique=True)
    op.create_index('nets_def_u_ipaddr', 'nets_def', ['ipaddr'], unique=True)
    op.create_index('nets_def_u_name', 'nets_def', ['name'], unique=True)
    op.create_table('nets_hosts',
    sa.Column('nhid', npf.UInt32(), npd.Comment('Network-host linkage ID'), nullable=False, default=sa.Sequence('nets_hosts_nhid_seq')),
    sa.Column('netid', npf.UInt32(), npd.Comment('Network ID'), nullable=False),
    sa.Column('hostid', npf.UInt32(), npd.Comment('Host ID'), nullable=False),
    sa.Column('hltypeid', npf.UInt32(), npd.Comment('Network-host linkage type'), nullable=False),
    sa.ForeignKeyConstraint(['hltypeid'], ['nets_hltypes.hltypeid'], name='nets_hosts_fk_hltypeid', onupdate='CASCADE'),
    sa.ForeignKeyConstraint(['hostid'], ['hosts_def.hostid'], name='nets_hosts_fk_hostid', onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['netid'], ['nets_def.netid'], name='nets_hosts_fk_netid', onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('nhid', name=op.f('nets_hosts_pk')),
    mysql_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.set_table_comment('nets_hosts', 'Networks-hosts linkage')
    op.create_index('nets_hosts_i_hltypeid', 'nets_hosts', ['hltypeid'], unique=False)
    op.create_index('nets_hosts_i_hostid', 'nets_hosts', ['hostid'], unique=False)
    op.create_index('nets_hosts_u_nhl', 'nets_hosts', ['netid', 'hostid', 'hltypeid'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('nets_hosts_u_nhl', table_name='nets_hosts')
    op.drop_index('nets_hosts_i_hostid', table_name='nets_hosts')
    op.drop_index('nets_hosts_i_hltypeid', table_name='nets_hosts')
    op.drop_table('nets_hosts')
    op.drop_index('nets_def_u_name', table_name='nets_def')
    op.drop_index('nets_def_u_ipaddr', table_name='nets_def')
    op.drop_index('nets_def_u_ip6addr', table_name='nets_def')
    op.drop_index('nets_def_i_rtid', table_name='nets_def')
    op.drop_index('nets_def_i_netgid', table_name='nets_def')
    op.drop_index('nets_def_i_mgmtdid', table_name='nets_def')
    op.drop_index('nets_def_i_domainid', table_name='nets_def')
    op.drop_table('nets_def')
    op.drop_index('rt_bits_i_rtr', table_name='rt_bits')
    op.drop_index('rt_bits_i_rtid', table_name='rt_bits')
    op.drop_table('rt_bits')
    op.drop_index('rt_def_u_name', table_name='rt_def')
    op.drop_table('rt_def')
    op.drop_index('nets_hltypes_u_name', table_name='nets_hltypes')
    op.drop_table('nets_hltypes')
    op.drop_index('nets_groups_u_name', table_name='nets_groups')
    op.drop_table('nets_groups')
    # ### end Alembic commands ###
