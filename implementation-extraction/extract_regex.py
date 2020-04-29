

def rtvslo(page):
    pass

def overstock(page):
    pass

site_methods = {
    'rtvslo.si': rtvslo,
    'overstock.com': overstock,
}

def extract(site, pages):
    print(f'REGEX: {site}, {pages}')
    pages_data = []
    for page in pages:
        method = site_methods[site]
        data = method(page)

        pages_data.append(data)

    return pages_data
