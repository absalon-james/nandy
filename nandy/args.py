"""
Module for parsing arguments from the command line.

Import parser from this module.

"""
import argparse

import meta
import utils


def parse_date(s):
    """Parse a string from a date argument.

    :param s: String should be in format of YYYY-mm-dd
    :returns: datetime
    """
    try:
        return utils.date_from_string(s)
    except ValueError:
        raise argparse.ArgumentTypeError(
            "Not a valid date: '{0}'. Should be YYYY-mm-dd.".format(s)
        )


description = "Tool for creating usage reports"
parser = argparse.ArgumentParser(description=description)

# Argument for configuration file
parser.add_argument('--config-file', type=str,
                    help="Configuration file location",
                    default="/etc/nandy/nandy.yaml")

# Argument for version
parser.add_argument('--version', action='version',
                    version='%(prog)s ' + str(meta.version))

subparsers = parser.add_subparsers(
    help='sub-command help',
    dest="subcommand"
)

# ################## Report sub command ########################
parser_report = subparsers.add_parser(
    'report',
    help='One time report between two dates.'
)

# Collect default dates
default_start, default_end = utils.get_date_interval()

parser_report.add_argument(
    '--tenant_id', type=str, default=None,
    help="Isolate report to one tenant if provided."
)

# Report start date
parser_report.add_argument(
    '--start', type=parse_date,
    help='Start date in YYYY-MM-DD. Defaults to today',
    default=default_start.date().isoformat()
)
# Report end date
parser_report.add_argument(
    '--end', type=parse_date,
    help='End date in YYYY-MM-DD. Defaults to tomorrow',
    default=default_end.date().isoformat()
)

# ################## Agent sub command #########################
parser_report = subparsers.add_parser(
    'agent',
    help='Generates timeseries data on active resource usage.'
)
