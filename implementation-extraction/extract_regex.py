import re
import json
from lxml.html import clean

def rtvslo(page):
    title_regex = r'<h1>(.+)</h1>'
    subtitle_regex = r'<div class="subtitle">(.+)</div>'
    lead_regex = r'<p class="lead">(.+)</p>'
    content_regex = r'<div class="article-body">\s*([\s\S]+?\s*</article>)'
    author_regex = r'<div class="author-name">(.+)</div>'
    date_regex = r'<div class="publish-meta">\s*(.*)\s*<br>'

    data = {
        'title': re.search(title_regex, page).group(1),
        'subtitle': re.search(subtitle_regex, page).group(1),
        'lead': re.search(lead_regex, page).group(1),
        'content': clean.clean_html(re.search(content_regex, page).group(1).replace('\t', '')),
        'author': re.search(author_regex, page).group(1),
        'date': re.search(date_regex, page).group(1)
    }

    return data

def overstock(page):
    title_regex = r'<a.+PAGE=PROFRAME.+?PROD_ID=\d+[^<]*><b>(.+)</b>'
    content_regex = r'<span class="normal">([\S\s]+?\s*</a>\s*)</span>'
    content_regex_nolink = r'<span class="normal">([\S\s]+?)\s*<br>'

    list_price_regex = r'List Price:.+<s>(.+)</s>'
    price_regex = r'Price:.+<b>(.+)</b>'
    save_regex = r'You Save:.+(\$.+?)\s*\((.+)\)'

    regex_list = [title_regex, content_regex_nolink,
                  list_price_regex, price_regex, save_regex]

    regex_iters = [re.finditer(regex, page) for regex in regex_list]

    items = []
    for data in zip(*regex_iters):
        title_r, content_r, list_price_r, price_r, saving_r = data

        item = {
            'title': title_r.group(1),
            'content': content_r.group(1).replace('\n', ' '),
            'list_price': list_price_r.group(1),
            'price': price_r.group(1),
            'saving': saving_r.group(1),
            'saving_percent': saving_r.group(2)
        }
        items.append(item)

    return items

def tmdb(page):
    title_regex = r'<div class="title[\S\s]+?>(.+)</a>'
    year_regex = r'<span class="tag release_date">\((\d+)\)</span>'
    certification_regex = r'<span class="certification">\s*(.+)\s*</span>'
    release_regex = r'<span class="release">\s*(.+)\s*</span>'
    genre_regex = r'<a href="/genre/.*?/movie">\s*(.*?)\s*</a>'
    runtime_regex = r'<span class="runtime">\s*(.*?)\s*</span>'
    rating_regex = r'data-percent="(.*?)"'
    tagline_regex = r'<h3 class="tagline" dir="auto">\s*(.*?)\s*</h3>'
    overview_regex = r'<div class="overview" dir="auto">\s*<p>\s*(.*)\s*</p>\s*</div>'
    profile_regex = r'<li class="profile">[\s\S]*?<a href="/person/.*>(.*)</a>[\s\S]*?<p class="character">(.*)</p>'

    data = {
        'title': re.search(title_regex, page).group(1),
        'year': re.search(year_regex, page).group(1),
        'certification': re.search(certification_regex, page).group(1),
        'release': re.search(release_regex, page).group(1),
        'genres': [res.group(1) for res in re.finditer(genre_regex, page)],
        'runtime': re.search(runtime_regex, page).group(1),
        'rating': re.search(rating_regex, page).group(1),
        'tagline': re.search(tagline_regex, page).group(1),
        'overview': re.search(overview_regex, page).group(1),
        'people': [{'name': res.group(1), 'role': res.group(2)}
                   for res in re.finditer(profile_regex, page)]
    }

    return data


site_methods = {
    'rtvslo.si': rtvslo,
    'overstock.com': overstock,
    'themoviedb.org': tmdb,
}

def extract(site, pages):
    if site not in site_methods:
        print(f'[REGEX] Extraction for site "{site}" not imlemented.')
        return

    method = site_methods[site]

    for page in pages:
        with open(page, 'r', errors='replace') as file:
            page_html = file.read()

        data = method(page_html)
        print(f'[REGEX] {page}')
        print(json.dumps(data, indent=2, ensure_ascii=False))
