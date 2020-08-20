#!/usr/bin/env python

import re
import os
import io

PASS = 0
FAIL = 1

# The regular expression for a POEM file name.
re_poem = re.compile(r'POEM_(\d{1,3})\.md')

# Match if real name was provided in parentheses
re_author_real_name = re.compile(r'\((?P<realname>.+?)\)')

# Regex to match a github usernamer
re_github_username = re.compile(r'^[a-z\d](?:[a-z\d]|-(?=[a-z\d])){0,38}$', re.I)


def strip_brackets(s):
    s = s[1:] if s.startswith('[') else s
    s = s[:-1] if s.endswith(']') else s
    return s


def format_authors(authors):
    """ Creates a table entry for the authors, with a link to their github REPO if given as @<author name>

    Parameters
    ----------
    authors : str
        The raw authors info.

    Returns
    -------
    authors : str
        Markdown-formatted authors for inclusion in the POEMs table.
    """
    author_list = []

    for entry in authors.split(';'):

        entry = strip_brackets(entry.strip())

        match = re_author_real_name.search(entry)

        if match:
            realname = match.groupdict()['realname'].strip()
            # Now the username must be whats before the first parentheses
            username = entry.split('(', 1)[0].strip()
            username = strip_brackets(username)
            # Is it a valid username?
            m = re_github_username.match(username)
            username = username if m else None
        else:
            # No explicit real name given, was a real name or a github username given?
            m = re_github_username.search(entry)
            if m:
                username = entry
                realname = username
            else:
                username = None
                realname = entry

        if username is not None:
            author_link = f'[{realname}](https://github.com/{username})'
            author_list.append(author_link)
        else:
            author_list.append(realname)

    return '; '.join(author_list)


def parse_poem(file):
    """ Parse a POEM file and return its id, title, authors, and status.

    Parameters
    ----------
    file : str
        The name of a POEM markdown file in the root of the repo.

    Returns
    -------
    entries : dict
        A dictionary containing the following keys for information about
        the POEM. ('id', 'title', 'authors', 'status')
    """
    entries = {'status': 'active'}

    with open(file, 'r') as poem:
        lines = poem.readlines()

    for line in lines:
        lu = line.upper().strip()
        if lu.startswith('POEM ID:'):
            entries['id'] = line.split(':', 1)[-1].strip()
        elif lu.startswith('TITLE:'):
            entries['title'] = line.split(':', 1)[-1].strip()
        elif lu.startswith('AUTHORS:') or lu.startswith('AUTHOR:'):
            entries['authors'] = line.split(':', 1)[-1].strip()
        if lu.startswith('- [X] ACTIVE'):
            entries['status'] = 'active'
        if lu.startswith('- [X] REQUESTING DECISION'):
            entries['status'] = 'requesting decision'
        if lu.startswith('- [X] ACCEPTED'):
            entries['status'] = 'accepted'
        if lu.startswith('- [X] REJECTED'):
            entries['status'] = 'rejected'
        if lu.startswith('- [X] INTEGRATED'):
            entries['status'] = 'integrated'

    return entries


def build_poem_table():
    """ Parse the POEM markdown files and generate a markdown table of all POEMs in the repo.

    Returns
    -------
    table : str
        The markdown table of POEMs.
    """
    table_dict = {}
    table = io.StringIO()

    # Collect the information
    for file in os.listdir(os.getcwd()):
        match = re_poem.match(file)
        if match:
            id_str = int(match.groups()[0])
            table_dict[id_str] = parse_poem(file)

    # Write the table
    print('| POEM ID | Title | Author | Status |', file=table)
    print('| ------- | ----- | ------ | ------ |', file=table)

    for id in sorted(table_dict.keys()):
        entries = table_dict[id]
        id_str = f'[{id:03}](POEM_{id:03}.md)'
        author_str = format_authors(entries['authors'])
        print(f"| {id_str} | {entries['title']} | {author_str} | {entries['status']} |",
              file=table)

    return table.getvalue()


def update_readme():
    """ Generate an updated markdown table of POEMs put it in the README.md file.

    Returns
    -------
    status : int
        0 if the operation is successful otherwise 1
    """
    print('updating README.md')

    try:
        with open('README.md', 'r') as readme:
            lines = readme.readlines()
    except IOError:
        return FAIL

    table = build_poem_table()

    try:
        with open('README.md', 'w') as readme:
            for line in lines:
                print(line, file=readme, end='')
                if line.startswith('## List of POEMs'):
                    print('', file=readme)
                    break
            print(table, file=readme)
    except IOError:
        return FAIL
    return PASS


if __name__ == '__main__':
    exit(update_readme())
