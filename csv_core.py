"""
csv_core.py
Functions to format and export repository lists to a fixed-width text table
with word-wrapped repository names.
"""

import textwrap
from typing import List, Tuple

# Column widths (tweak as needed)
NAME_WIDTH = 40
STATUS_WIDTH = 10
TYPE_WIDTH = 10
URL_WIDTH = 50

def _format_row(name: str, status: str, repo_type: str, url: str) -> str:
    """
    Format a single repository row with word-wrapped name.
    Returns a multi-line string for the row.
    """
    # wrap name to fit within NAME_WIDTH minus a small indent for wrapped lines
    wrap_width = NAME_WIDTH - 2
    wrapped = textwrap.wrap(name, width=wrap_width)
    if not wrapped:
        wrapped = ['']
    lines = []
    # first line contains all columns
    first_name = wrapped[0]
    lines.append(f"{first_name:<{NAME_WIDTH}}{status:<{STATUS_WIDTH}}{repo_type:<{TYPE_WIDTH}}{url:<{URL_WIDTH}}")
    # subsequent lines only show wrapped name (indented)
    for part in wrapped[1:]:
        lines.append(f"  {part:<{NAME_WIDTH-2}}")
    return "\n".join(lines)

def export_repos_to_txt(repos: List[dict], out_path: str = "repos.txt") -> None:
    """
    Given a list of GitHub repo objects (as dicts from the API),
    categorize, sort, and write a fixed-width table to out_path.
    """
    # categorize
    public_owned = []
    public_cloned = []
    private_owned = []
    private_cloned = []

    for repo in repos:
        is_private = repo.get('private', False)
        is_fork = repo.get('fork', False)
        name = repo.get('name', '') or ''
        html_url = repo.get('html_url', '') or ''
        # shorten url to owner/repo if possible
        url = html_url.replace('https://github.com/', '')
        if is_private:
            if is_fork:
                private_cloned.append((name, url))
            else:
                private_owned.append((name, url))
        else:
            if is_fork:
                public_cloned.append((name, url))
            else:
                public_owned.append((name, url))

    # sort case-insensitive by name
    for lst in (private_owned, private_cloned, public_owned, public_cloned):
        lst.sort(key=lambda x: x[0].lower())

    # write file
    with open(out_path, "w", encoding="utf-8") as fh:
        # header
        fh.write(f"{'Repository Name':<{NAME_WIDTH}}{'Status':<{STATUS_WIDTH}}{'Type':<{TYPE_WIDTH}}{'URL':<{URL_WIDTH}}\n")
        fh.write("-" * (NAME_WIDTH + STATUS_WIDTH + TYPE_WIDTH + URL_WIDTH) + "\n")

        # helper to write list
        def write_list(items, status_label, type_label):
            for name, url in items:
                fh.write(_format_row(name, status_label, type_label, url) + "\n")

        write_list(private_owned, "Private", "Owned")
        write_list(private_cloned, "Private", "Cloned")
        write_list(public_owned, "Public", "Owned")
        write_list(public_cloned, "Public", "Cloned")
