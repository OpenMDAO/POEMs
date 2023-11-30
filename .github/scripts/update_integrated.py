#!/usr/bin/env python

import sys
import update_readme


PASS = 0
FAIL = 1


def update_integrated(poem_id):
    """
    Modify a POEM markdown file to indicate that it's status is 'Integrated'.

    Parameters
    ----------
    poem_id : int
        The id of a POEM markdown file in the root of the repo.

    Returns
    -------
    status : int
        0 if the operation is successful otherwise 1
    """
    filename = f'POEM_{poem_id:0>3}.md'

    print(f'updating {filename}')

    try:
        with open(filename, 'r') as poem_md:
            lines = poem_md.readlines()
    except IOError:
        return FAIL

    in_status = False
    success = False

    try:
        with open(filename, 'w') as poem_md:
            for line in lines:
                lu = line.upper().strip()
                if lu.startswith('STATUS:'):
                    in_status = True
                    print(line, file=poem_md, end='')
                elif in_status and '[' in line:
                    left = line[:line.find('[')]
                    right = line[line.find(']'):]
                    if left and right:
                        if lu.endswith('INTEGRATED'):
                            print(f'{left}[x{right}', file=poem_md, end='')
                            in_status = False
                            success = True
                        else:
                            print(f'{left}[ {right}', file=poem_md, end='')
                    else:
                        print(line, file=poem_md, end='')
                else:
                    print(line, file=poem_md, end='')
    except IOError:
        return FAIL

    if success:
        print(f"Updated status in '{poem_md}' to Integrated")
        return update_readme.update_readme()
    else:
        return FAIL


if __name__ == '__main__':
    exit(update_integrated(sys.argv[1]))
