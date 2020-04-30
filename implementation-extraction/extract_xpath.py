import re
import json
from lxml import html, etree

def inner_html(node):
    return '\n'.join([etree.tostring(child, encoding='unicode') for child in node.iterchildren()])

def rtvslo(page):
    tree = html.fromstring(page)

    title_xpath = r'//h1'
    subtitle_xpath = r'//div[@class="subtitle"]'
    lead_xpath = r'//p[@class="lead"]'
    content_xpath = r'//div[@class="article-body"]'
    author_xpath = r'//div[@class="author-name"]'
    date_xpath = r'//div[@class="publish-meta"]'

    data = {
        'title': tree.xpath(title_xpath)[0].text.strip(),
        'subtitle': tree.xpath(subtitle_xpath)[0].text.strip(),
        'lead': tree.xpath(lead_xpath)[0].text.strip(),
        'content': inner_html(tree.xpath(content_xpath)[0]).strip(),
        'author': tree.xpath(author_xpath)[0].text.strip(),
        'date': tree.xpath(date_xpath)[0].text.strip()
    }

    return data

def overstock(page):
    tree = html.fromstring(page)

    title_xpath = r'//td[@valign="top"]/a/b'
    content_xpath = r'//span[@class="normal"]'
    list_price_xpath = r'//td/s'
    price_xpath = r'//span[@class="bigred"]/b'
    save_xpath = r'//td[@align="left"]/span[@class="littleorange"]'

    saving_regex = r'(\$.+?)\s*\((.+)\)'


    xpath_list = [title_xpath, content_xpath,
                  list_price_xpath, price_xpath, save_xpath]

    xpath_elements = [tree.xpath(xpath) for xpath in xpath_list]

    items = []
    for data in zip(*xpath_elements):
        title_r, content_r, list_price_r, price_r, saving_r = data

        saving_r = re.search(saving_regex, saving_r.text)

        item = {
            'title': title_r.text,
            'content': content_r.text.strip().replace('\n', ' '),
            'list_price': list_price_r.text,
            'price': price_r.text,
            'saving': saving_r.group(1),
            'saving_percent': saving_r.group(2)
        }
        items.append(item)

    return items

def tmdb(page):
    tree = html.fromstring(page)

    title_xpath = r'//h2/a'
    year_xpath = r'//span[@class="tag release_date"]'
    certification_xpath = r'//span[@class="certification"]'
    release_xpath = r'//span[@class="release"]'
    genre_xpath = r'//span[@class="genres"]/a'
    runtime_xpath = r'//span[@class="runtime"]'
    rating_xpath = r'//div[@class="user_score_chart"]'
    tagline_xpath = r'//h3[@class="tagline"]'
    overview_xpath = r'//div[@class="overview"]/p'

    name_xpath = r'//li[@class="profile"]/p/a'
    role_xpath = r'//li[@class="profile"]/p[@class="character"]'

    # Year out of paranthesis
    year = re.search(r'\((.*?)\)', tree.xpath(year_xpath)[0].text).group(1)

    names = [n.text.strip() for n in tree.xpath(name_xpath)]
    roles = [r.text.strip() for r in tree.xpath(role_xpath)]

    data = {
        'title': tree.xpath(title_xpath)[0].text.strip(),
        'year': year,
        'certification': tree.xpath(certification_xpath)[0].text.strip(),
        'release': tree.xpath(release_xpath)[0].text.strip(),
        'genres': [res.text.strip() for res in tree.xpath(genre_xpath)],
        'runtime': tree.xpath(runtime_xpath)[0].text.strip(),
        'rating': tree.xpath(rating_xpath)[0].get('data-percent'),
        'tagline': tree.xpath(tagline_xpath)[0].text.strip(),
        'overview': tree.xpath(overview_xpath)[0].text.strip(),
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

    method = site_methods[site]

    for page in pages:
        with open(page, 'r', errors='replace') as file:
            page_html = file.read()

        data = method(page_html)
        print(f'[XPATH] {page}')
        print(json.dumps(data, indent=2, ensure_ascii=False))
