import re
import sys


# The regular expression for a POEM file name.
re_poem = re.compile(r'POEM_(\d{1,3})\.md')


def check_id(filename):
    """ Raise AssertionError if the POEM ID is not 3 digits or the ID in the file doesn't match the one given in the filename.

    Parameters
    ----------
    filename : str
        The filename of the POEM markdown file.
    """
    # Check the ID in the filename
    match = re_poem.match(filename)
    id_filename = match.groups()[-1]
    assert len(id_filename) == 3, 'The POEM ID in the filename must be a 3 digit integer'

    with open(filename) as poem_file:
        line = poem_file.readline()
    lu = line.upper().strip()

    assert lu.startswith('POEM ID:'), 'The first line of the POEM must contain the POEM ID ' \
                                      'as a 3 digit integer'

    id = line.split(':', 1)[-1].strip()
    assert len(id) == 3, 'The first line of the POEM must contain the POEM ID as a ' \
                         '3 digit integer'
    assert id == id_filename, f'The ID in the filename ({id_filename}) does not match ' \
                              f'the ID in the POEM file ({id}).'


def check_headers(filename):
    """ Raise AssertionError if each line in the header doesn't end with two spaces.

    Parameters
    ----------
    filename : str
        The filename of the POEM markdown file.
    """
    with open(filename) as poem_file:
        lines = poem_file.readlines()

    for i, line in enumerate(lines):
        if len(lines[i + 1].strip()) == 0:
            break
        assert line[:-1].endswith(r'  '), f'Each line in the header must end with ' \
                                          f'two spaces. - Line {i} does not.'


if __name__ == '__main__':
    for filename in sys.argv[1:]:
        print(filename)
        if re_poem.match(filename):
            check_headers(filename)
            check_id(filename)
