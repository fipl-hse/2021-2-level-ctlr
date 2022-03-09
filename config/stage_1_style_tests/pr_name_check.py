# pylint: skip-file
import argparse
import sys
import re


def convert_raw_pr_name(pr_name_raw: str) -> str:
    return pr_name_raw.replace('_', ' ')


def is_matching_name(pr_name: str) -> bool:
    template = r'Laboratory Work #\d, \w+ \w+ - 20FPL\d'
    pr_name = re.search(template, pr_name)
    if not pr_name:
        print('Your Pull Request title does not confirm to the template.')
        print('Template: Laboratory work #1, Name Surname - 20FPL1\n')
        return False
    print('Your Pull Request name confirm to provided template!')
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Checks that PR name is done using the template')
    parser.add_argument('--pr-name', type=str, help='Current PR name')
    parser.add_argument('--pr-author', type=str, help='Current PR author')
    args: argparse.Namespace = parser.parse_args()

    if '[skip-name]' in args.pr_name:
        print("Skipping PR name checks.")
        sys.exit(0)

    if args.pr_author in ('demid5111', 'dmitry-uraev', 'marina-kaz'):
        print('Skipping PR name checks due to author.')
        sys.exit(0)

    pr_name_to_check = convert_raw_pr_name(args.pr_name)

    sys.exit(not is_matching_name(pr_name_to_check))
