import argparse
import logging

from . import testbook

def start():
    parser = argparse.ArgumentParser(description='Run TestBook')
    parser.add_argument('search_dir', default=".", nargs='?',  help='Directory to search of testbooks')
    parser.add_argument('--recursive', "-r", action='store_true', help='Recursively search for testbooks in subdirectories')
    parser.add_argument('--debug', action='store_true', help='Print debug statements')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
    testbook.run(args.search_dir, recursive=bool(args.recursive))
