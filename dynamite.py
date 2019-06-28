import sys
import json
import argparse
import traceback

from installer import elasticsearch
from installer import utilities


def _parse_cmdline():
    parser = argparse.ArgumentParser(
        description='Install/Configure the Dynamite Analysis Framework.'
    )
    parser.add_argument('command', metavar='command', type=str, help='An action to perform [install|start]')
    parser.add_argument('component', metavar='component', type=str,
                        help='The component to perform an action against [elasticsearch]')
    return parser.parse_args()


def install_elasticsearch():
    if not utilities.is_root():
        sys.stderr.write('[-] This script must be run as root.\n')
        sys.exit(1)

    if utilities.get_memory_available_bytes() < 6 * (1000 ** 3):
        sys.stderr.write('[-] Dynamite ElasticSearch requires at-least 6GB to run currently available [{} GB]\n'.format(
            utilities.get_memory_available_bytes()/(1024 ** 3)
        ))
        sys.exit(1)
    try:
        es_installer = elasticsearch.ElasticInstaller()
        es_installer.download_java(stdout=True)
        es_installer.extract_java(stdout=True)
        es_installer.setup_java()
        utilities.create_dynamite_user('password')
        es_installer.download_elasticsearch(stdout=True)
        es_installer.extract_elasticsearch(stdout=True)
        es_installer.setup_elasticsearch(stdout=True)
    except Exception:
        sys.stderr.write('[-] A fatal error occurred while attempting to install ElasticSearch: ')
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
    sys.stdout.write('[+] *** ElasticSearch installed successfully. ***\n')
    sys.exit(0)


if __name__ == '__main__':
    args = _parse_cmdline()
    if args.command == 'install':
        if args.component == 'elasticsearch':
            install_elasticsearch()
        else:
            sys.stderr.write('[-] Unrecognized component - {}\n'.format(args.component))
            sys.exit(1)
    elif args.command == 'start':
        if args.component == 'elasticsearch':
            sys.stdout.write('[+] Starting ElasticSearch.\n')
            started = elasticsearch.ElasticProcess().start(stdout=True)
            if started:
                sys.stdout.write('[+] ElasticSearch started successfully. Check its status at any time with: '
                                 '\'dynamite.py status elasticsearch\'.\n')
            else:
                sys.stdout.write('[-] An error occurred while attempting to start ElasticSearch.\n')
        else:
            sys.stderr.write('[-] Unrecognized component - {}\n'.format(args.component))
            sys.exit(1)
    elif args.command == 'status':
        if args.component == 'elasticsearch':
            sys.stdout.write(json.dumps(elasticsearch.ElasticProcess().status(), indent=1) + '\n')
        else:
            sys.stderr.write('[-] Unrecognized component - {}\n'.format(args.component))
            sys.exit(1)
    elif args.command == 'stop':
        if args.component == 'elasticsearch':
            sys.stdout.write('[+] Stopping ElasticSearch.\n')
            stopped = elasticsearch.ElasticProcess().stop(stdout=True)
            if stopped:
                sys.stdout.write('[+] ElasticSearch stopped successfully.\n')
            else:
                sys.stdout.write('[-] An error occurred while attempting to stop ElasticSearch.\n')
        else:
            sys.stderr.write('[-] Unrecognized component - {}\n'.format(args.component))
            sys.exit(1)
    else:
        sys.stderr.write('[-] Unrecognized command - {}\n'.format(args.command))
        sys.exit(1)