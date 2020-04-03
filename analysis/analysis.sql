-- Export pages (without HTML)
SELECT page.id, page.site_id, page.page_type_code, page.url, page.html_content_hash, page.http_status_code, page.accessed_time, site.domain
FROM crawldb.page
LEFT JOIN crawldb.site ON page.site_id = site.id

-- Export images
SELECT * FROM crawldb.image

-- Export data
SELECT id, page_id, data_type_code, encode(data, 'escape') as url FROM crawldb.page_data

-- Export links
SELECT * FROM crawldb.link

-- Export sites
SELECT * FROM crawldb.site

