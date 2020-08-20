import re
import os


# The regular expression for a POEM file name.
re_poem = re.compile(r'POEM_(\d{1,3})\.md')


def check_id(filename, errors):
    """ Raise AssertionError if the POEM ID is not 3 digits or the ID in the file doesn't match the one given in the filename.

    Parameters
    ----------
    filename : str
        The filename of the POEM markdown file.
    errors : list
        A list to which any errors should be appended.
    """
    # Check the ID in the filename
    match = re_poem.match(filename)
    id_filename = match.groups()[-1]
    if len(id_filename) != 3:
        errors.append('The POEM ID in the filename must be a 3 digit integer')

    with open(filename) as poem_file:
        line = poem_file.readline()
    lu = line.upper().strip()

    if not lu.startswith('POEM ID:'):
        errors.append('The first line of the POEM must contain the POEM ID as a 3 digit integer')

    id = line.split(':', 1)[-1].strip()
    if len(id) != 3:
        errors.append('The first line of the POEM must contain the POEM ID as a 3 digit integer')
    if id != id_filename:
        errors.append(f'The ID in the filename ({id_filename}) does not match the ID in the POEM file ({id}).')


def check_headers(filename, errors):
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
        if not line[:-1].endswith(r'  '):
            errors.append(f'Each line in the header must end with two spaces. - Line {i} does not.')


if __name__ == '__main__':
    errors = {}
    err_count = 0
    for filename in os.listdir(os.getcwd()):
        errors[filename] = []
        if re_poem.match(filename):
            check_headers(filename, errors[filename])
            check_id(filename, errors[filename])
            if errors[filename]:
                print(filename)
            for err in errors[filename]:
                print('    ', err)
            err_count += len(errors[filename])
    exit(err_count)
