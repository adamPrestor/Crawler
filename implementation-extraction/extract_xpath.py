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

site_methods = {
    'rtvslo.si': rtvslo,
    'overstock.com': overstock,
}

def extract(site, pages):

    method = site_methods[site]

    for page in pages:
        with open(page, 'r', errors='replace') as file:
            page_html = file.read()

        data = method(page_html)
        print(f'[XPATH] {page}')
        print(json.dumps(data, indent=2, ensure_ascii=False))
