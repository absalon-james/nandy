"""Main entry point to nandy. Run a one time report or start an agent."""
from args import parser as argparser
import config
from db import ActiveLocalStorageGB
from db import ActiveMemoryMB
from db import ActiveVCPUS
from db import db as database
from db import Tenant
from keystoneauth1 import loading
from keystoneauth1 import session
from novaclient import client as novaclient
from report import UsageReport
import time
import utils


def get_nova(conf):
    """Get nova client.

    :param conf: Dictionary configuration
    :returns: novaclient.client.Client
    """
    loader = loading.get_plugin_loader('password')
    auth = loader.load_from_options(
        auth_url=conf.get('auth_url'),
        username=conf.get('username'),
        password=conf.get('password'),
        project_id=conf.get('project_id')
    )
    sess = session.Session(auth=auth)
    return novaclient.Client('2.1', session=sess)


def report(args):
    """Run a one time report.

    Reports usage in resource hours as well as current active stats.

    :param args: argparse args
    """
    conf = config.load(args.config_file)
    nova = get_nova(conf)

    usages = nova.usage.list(args.start, args.end, detailed=True)
    r = UsageReport(usages)

    tenant = args.tenant_id if args.tenant_id else 'all tenants'
    title = "Report {0} to {1} for {2}:".format(args.start, args.end, tenant)

    print ("\n\n{0}".format(title))
    print ("VCPU Hours:\t{0}".format(
        r.total_vcpu_usage(tenant_id=args.tenant_id)
    ))

    print ("Ram MB Hours:\t{0}".format(
        r.total_memory_mb_usage(tenant_id=args.tenant_id)
    ))

    print ("Disk GB Hours:\t{0}".format(
        r.total_local_gb_usage(tenant_id=args.tenant_id)
    ))

    v, m, s = r.active_stats(tenant_id=args.tenant_id)
    print ("\nActive stats:")
    print ("VCPUS:\t\t{0}".format(v))
    print ("Memory:\t\t{0} MB".format(m))
    print ("Storage:\t{0} GB".format(s))
    exit()


def agent(args):
    """Run a long running polling agent.

    Periodically updates the database with timeseries active stat data.

    :param args: argparse args
    """
    conf = config.load(args.config_file)
    nova = get_nova(conf)
    database.get_engine(conf.get('db', {}))

    detailed = True

    # Special all tenant.
    all_tenant_id = '0' * 32

    # Init last poll time to 0 to trigger first poll
    last_polled = 0

    while True:
        if time.time() - last_polled > conf.get('polling_interval', 120):
            with database.session_scope() as session:
                start, end = utils.get_date_interval()

                # Grab usage results
                usages = nova.usage.list(start, end, detailed=detailed)
                r = UsageReport(usages)

                # Get datetime for time value
                now = utils.get_now()

                # Iterate over all tenants
                for tenant_usage in usages:

                    # Ensure tenant is in tenant table
                    tenant_id = tenant_usage.tenant_id
                    tenant = Tenant.get_or_create(session, tenant_id)
                    session.commit()

                    # Get tenant stats and add to session
                    v, m, s = r.active_stats(tenant_id=tenant_id)
                    session.add(ActiveVCPUS(
                        value=v, time=now, tenant_id=tenant.id
                    ))
                    session.add(ActiveMemoryMB(
                        value=m, time=now, tenant_id=tenant.id
                    ))
                    session.add(ActiveLocalStorageGB(
                        value=s, time=now, tenant_id=tenant.id
                    ))

                # Save all tenant stats
                v, m, s = r.active_stats()
                print ("Active vcpus", v)
                print ("Active memory MB", m)
                print ("Active storage GB", s)
                all_tenant = Tenant.get_or_create(session, all_tenant_id)
                session.commit()
                session.add(ActiveVCPUS(
                    value=v, time=now, tenant_id=all_tenant.id
                ))
                session.add(ActiveMemoryMB(
                    value=m, time=now, tenant_id=all_tenant.id
                ))
                session.add(ActiveLocalStorageGB(
                    value=s, time=now, tenant_id=all_tenant.id
                ))

            last_polled = time.time()
            print ("Updating polling interval")
        time.sleep(1)
    exit()


# Parse arguments and then take action.
args = argparser.parse_args()
if args.subcommand == 'report':
    report(args)

elif args.subcommand == 'agent':
    agent(args)
