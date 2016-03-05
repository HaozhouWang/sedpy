import argparse
import fileinput
from . import Sed


def main(args, help):
    sed = Sed(args.script, quiet=args.quiet)
    for line in fileinput.input(args.files):
        sed.parseString(line)


if __name__ == '__main__':
    parser = argparse.ArgumentParser('sedpy')
    parser.add_argument('script')
    parser.add_argument('files', nargs='*')
    parser.add_argument('-n', '--quiet', action="store_true", default=False)
    main(parser.parse_args(), parser.print_help)
