import argparse
import logging

from . import testbook

def start():
    parser = argparse.ArgumentParser(description='Run TestBook')
    parser.add_argument('search_dir', default=".", nargs='?',  help='Directory to search of testbooks')
    parser.add_argument('--recursive', "-r", action='store_true', help='Recursively search for testbooks in subdirectories')
    parser.add_argument('--debug', default=0, type=int, help='Print debug statements')
    args = parser.parse_args()

    if args.debug == 1:
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
    elif args.debug == 2:
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
    
    testbook.run(args.search_dir, recursive=bool(args.recursive))
