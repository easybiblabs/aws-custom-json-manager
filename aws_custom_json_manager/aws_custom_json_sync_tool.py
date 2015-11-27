#!/usr/bin/env python2
"""aws-custom-json-sync-tool

Tool for managing AWS OpsWorks custom-JSON stack-settings.

Usage:
    sync_tool [-y|--yes] pull <filename>
    sync_tool [-y|--yes] push <filename>

Options:
    --version   - Print the version-number and exit.
    -h|--help   - Print this help and exit.
    -y|--yes    - Automatically opt-in to questions.

Arguments:
    <filename>  - Path to the stack-file. All stack-files are JSON files containing the following
                  format:

                    {
                        "stack-id": <uuid>,
                        "custom-json": <json>
                    }
"""

import sys
import json
import boto3
import logging
from docopt import docopt

__version__ = '0.1.4'
__author__ = 'Brian Wiborg <brian.wiborg@imagineeasy.com>'

logger = logging.getLogger('sync-tool')


def configure_logging():
    """Helper function for logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(name)-24s %(levelname)-8s %(message)s",
    )


def die(severity, message, exit_code=1):
    """Print an error and exit.

    :param severity: str    - The severity is basically the log-level and used as bold prefix of
                              the printed error message.
    :param message: str     - An arbitrary message describing the error or possible causes.
    :param exit_code: int   - Use this as the program's exit-code.
    """

    severities = ['debug', 'info', 'warning', 'critical', 'fatal']

    if severity not in severities:
        raise ValueError("Unknown severity, use one of: {}".format(severities))

    log_func = getattr(logger, severity)
    log_func("{}: {}".format(severity.upper(), message))

    sys.exit(exit_code)


def read_stack_file(path):
    """Read a stack-file.

    :param path: str                - Path to stack-file.
    :return: dict                   - JSON object:
                                        {
                                            u'stack-id': u'<UUID>',
                                            u'custom-json': <custom-json>,
                                        }
    :raise: IOError                 - If the format of the stack-file is broken.
    """

    logger.info("Loading stack-file: {}".format(path))

    stack_file_handler = open(path, 'r')
    stack_json = json.load(stack_file_handler)
    stack_file_handler.close()

    if u'stack-id' not in stack_json:
        raise IOError("Format broken, can not find: stack-id")

    if u'custom-json' not in stack_json:
        stack_json[u'custom-json'] = {}

    return stack_json


def write_stack_file(path, stack_file_json):
    """Write a stack-file.

    :param path: str                - Path to stack-file.
    :param stack_file_json: dict    - JSON object.
    """

    logger.info("Saving stack-file: {}".format(path))

    stack_file_handler = open(path, 'w')
    json.dump(stack_file_json, stack_file_handler, indent=2)
    stack_file_handler.close()


def get_opsworks_stack_settings_custom_json(stack_id):
    """Pull a custom JSON from the stack-settings of an OpsWorks stack in AWS.

    :param stack_id: str    - OpsWorksID of desired stack.
    :return: dict           - Loaded JSON object.
    """

    logger.info("Use boto3 to get custom JSON from AWS-API...")

    opsworks = boto3.resource('opsworks', 'us-east-1')
    stack = opsworks.Stack(stack_id)
    return json.loads(stack.custom_json)


def set_opsworks_stack_settings_custom_json(stack_id, custom_json_str):
    """Push a custom JSON to the stack-settings of an OpsWorks stack in AWS.

    :param stack_id: str        - OpsWorksID of desired stack.
    :param custom_json_str: str - Custom JSON.
    :raise TypeError            - If Custom JSON is not of type str.
    """

    logger.info("Use boto3 to set custom JSON via AWS-API...")

    if not isinstance(custom_json_str, str):
        raise TypeError("Must be of type str: {}".format(custom_json_str))

    opsworks = boto3.client('opsworks', 'us-east-1')
    opsworks.update_stack(StackId=stack_id, CustomJson=custom_json_str)


def opt_in(prompt):
    do_it = raw_input(prompt + ' [y|N] : ')
    if do_it and do_it.lower()[0] == 'y':
        return True

    return False


def main():
    configure_logging()

    # Parse shell-arguments.
    args = docopt(__doc__, version=__version__)

    # Get file contents.
    try:
        stack_json = read_stack_file(args['<filename>'])
    except IOError as e:
        return die('critical', e.message)

    stack_id = stack_json[u'stack-id']

    # Select and run workflow.
    if args['pull']:
        prompt = "Do you really want to overwrite your local custom JSON?"
        do_it = not stack_json[u'custom-json'] or args['-y'] or args['--yes'] or opt_in(prompt)
        if do_it is not True:
            logger.info("Aborted.")

        else:
            custom_json = get_opsworks_stack_settings_custom_json(stack_json[u'stack-id'])
            new_stack_json = {
                u'stack-id': stack_id,
                u'custom-json': custom_json,
            }
            write_stack_file(args['<filename>'], new_stack_json)
            logger.info("Done.")

    elif args['push']:
        prompt = "Do you really want to overwrite the OpsWorks stack-settings custom JSON?"
        do_it = args['-y'] or args['--yes'] or opt_in(prompt)
        if do_it is not True:
            logger.info("Aborted.")

        else:
            custom_json_str = json.dumps(stack_json[u'custom-json'], indent=2)
            set_opsworks_stack_settings_custom_json(stack_id, custom_json_str)
            logger.info("Done.")


if __name__ == '__main__':
    main()
