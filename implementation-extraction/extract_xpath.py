import re
import json
from lxml import html, etree
from lxml.html import clean

def inner_html(node):
    return '\n'.join([etree.tostring(child, encoding='unicode') for child in node.iterchildren()])

def rtvslo(page):
    tree = html.fromstring(page)

    title_xpath = r'//h1/text()'
    subtitle_xpath = r'//div[@class="subtitle"]/text()'
    lead_xpath = r'//p[@class="lead"]/text()'
    content_xpath = r'//div[@class="article-body"]'
    author_xpath = r'//div[@class="author-name"]/text()'
    date_xpath = r'//div[@class="publish-meta"]/text()'

    # Clean up content
    content = inner_html(tree.xpath(content_xpath)[0]).strip()
    content = clean.clean_html(content).replace('\t', '')

    data = {
        'title': tree.xpath(title_xpath)[0].strip(),
        'subtitle': tree.xpath(subtitle_xpath)[0].strip(),
        'lead': tree.xpath(lead_xpath)[0].strip(),
        'content': content,
        'author': tree.xpath(author_xpath)[0].strip(),
        'date': tree.xpath(date_xpath)[0].strip()
    }

    return data

def overstock(page):
    tree = html.fromstring(page)

    title_xpath = r'//td[@valign="top"]/a/b/text()'
    content_xpath = r'//span[@class="normal"]/text()'
    list_price_xpath = r'//td/s/text()'
    price_xpath = r'//span[@class="bigred"]/b/text()'
    save_xpath = r'//td[@align="left"]/span[@class="littleorange"]/text()'

    saving_regex = r'(\$.+?)\s*\((.+)\)'


    xpath_list = [title_xpath, content_xpath,
                  list_price_xpath, price_xpath, save_xpath]

    xpath_elements = [tree.xpath(xpath) for xpath in xpath_list]

    items = []
    for data in zip(*xpath_elements):
        title_r, content_r, list_price_r, price_r, saving_r = data

        saving_r = re.search(saving_regex, saving_r)

        item = {
            'title': title_r,
            'content': content_r.strip().replace('\n', ' '),
            'list_price': list_price_r,
            'price': price_r,
            'saving': saving_r.group(1),
            'saving_percent': saving_r.group(2)
        }
        items.append(item)

    return items

def tmdb(page):
    tree = html.fromstring(page)

    title_xpath = r'//h2/a/text()'
    year_xpath = r'//span[@class="tag release_date"]/text()'
    certification_xpath = r'//span[@class="certification"]/text()'
    release_xpath = r'//span[@class="release"]/text()'
    genre_xpath = r'//span[@class="genres"]/a/text()'
    runtime_xpath = r'//span[@class="runtime"]/text()'
    rating_xpath = r'//div[@class="user_score_chart"]/@data-percent'
    tagline_xpath = r'//h3[@class="tagline"]/text()'
    overview_xpath = r'//div[@class="overview"]/p/text()'

    name_xpath = r'//li[@class="profile"]/p/a/text()'
    role_xpath = r'//li[@class="profile"]/p[@class="character"]/text()'

    # Year out of paranthesis
    year = re.search(r'\((.*?)\)', tree.xpath(year_xpath)[0]).group(1)

    names = [n.strip() for n in tree.xpath(name_xpath)]
    roles = [r.strip() for r in tree.xpath(role_xpath)]

    data = {
        'title': tree.xpath(title_xpath)[0].strip(),
        'year': year,
        'certification': tree.xpath(certification_xpath)[0].strip(),
        'release': tree.xpath(release_xpath)[0].strip(),
        'genres': [res.strip() for res in tree.xpath(genre_xpath)],
        'runtime': tree.xpath(runtime_xpath)[0].strip(),
        'rating': tree.xpath(rating_xpath)[0].strip(),
        'tagline': tree.xpath(tagline_xpath)[0].strip(),
        'overview': tree.xpath(overview_xpath)[0].strip(),
        'people': [{'name': name, 'role': role}
                   for name, role in zip(names, roles)]
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
        print(f'[XPATH] {page}')
        print(json.dumps(data, indent=2, ensure_ascii=False))
