import os
import glob
import sys

import extract_regex
import extract_xpath
import extract_automatic

mode_methods = {
    'A': extract_regex,
    'B': extract_xpath,
    'C': extract_automatic
}

# Mode
mode = sys.argv[1]
extraction_method = mode_methods[mode]

# Path relative to the script
script_dir = os.path.dirname(__file__)
input_dir = os.path.join(script_dir, '../input-extraction')
input_dir = os.path.abspath(input_dir)

for site in os.listdir(input_dir):
    # Skip hidden files
    if site.startswith('.'):
        continue

    site_dir = os.path.join(input_dir, site)

    # Get HTML file paths
    pages = glob.glob(os.path.join(site_dir, '*.html'))

    # Extract to standard output
    extraction_method.extract(site, pages)
