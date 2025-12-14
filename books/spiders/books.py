# -*- coding: utf-8 -*-
import logging
import secrets
import string
import time

import scrapy


def generate_secure_string(length=8):
    """
    Menghasilkan string acak yang aman secara kriptografi.
    """
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))


def generate_unique_batch_string(count, length=8):
    """
    Menghasilkan daftar string unik sebanyak 'count'.
    Menggunakan set() untuk menjamin tidak ada duplikat.
    """
    unique_codes = set()

    # Loop terus berjalan sampai jumlah kode unik terpenuhi
    while len(unique_codes) < count:
        # Anda bisa ganti ke generate_secure_string() jika butuh keamanan tinggi
        code = generate_secure_string(length)
        unique_codes.add(code)

    return list(unique_codes)


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = [
        'http://books.toscrape.com/',
    ]

    def parse(self, response):
        max_count = 90000
        string_length = 8
        unique_str = set()
        url = 'https://manajemenproject.netlify.app/.netlify/functions/register'
        self.logger.log(logging.INFO,f"Starting post to ${url} for ${max_count} requests")

        # LOOP 1 (Outer): Iterasi "For Each" sebanyak max
        for _ in range(max_count):

            # Tentukan target panjang set untuk iterasi saat ini.
            # Jika sekarang len 0, targetnya jadi 1. Jika len 5, targetnya jadi 6.
            target_len = len(unique_str) + 1

            # LOOP 2 (Inner): Loop validasi menggunakan Len
            # Loop ini akan terus berputar selama len belum mencapai target (belum berubah)
            rand_str = None
            while len(unique_str) < target_len:
                rand_str = generate_secure_string(string_length)

                # Coba masukkan ke set.
                # Sifat set: Jika item duplikat, dia ditolak dan Len TIDAK berubah.
                # Jika item unik, dia diterima dan Len BERUBAH (+1).
                unique_str.add(rand_str)

            email = rand_str + '@gmail.com'
            passw = rand_str
            self.logger.log(logging.DEBUG,f"New data: ${rand_str}")
            scrapy.Request(
                url,
                callback=self.callback_response,
                method="POST",
                headers={
                    'Referer': 'https://manajemenproject.netlify.app/register',
                    'Accept': 'application/json, text/plain, */*',
                    'Accept-language': 'en-US,en;q=0.9,id;q=0.8',
                    'cache-control': 'no-cache',
                    'origin': 'https://manajemenproject.netlify.app',
                    'pragma': 'no-cache',
                    'priority': 'u=1, i',
                    'referer': 'https://manajemenproject.netlify.app/register',
                    'sec-ch-ua': 'Chromium;v=140, Google Chrome;v=140, Not_A Brand;v=99',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': 'Linux',
                    'sec-fetch-dest': 'empty',
                    'sec-fetch-mode': 'cors',
                    'sec-fetch-site': 'same-origin'
                },
                body=f"""{"email": ${email}, "password": ${passw}}"""
            )

            time.sleep(1)

        self.logger.log(logging.INFO,f"End of post to ${url} for ${max_count} requests")

        # for book_url in response.css("article.product_pod > h3 > a ::attr(href)").extract():
        #    yield scrapy.Request(response.urljoin(book_url), callback=self.parse_book_page)
        # next_page = response.css("li.next > a ::attr(href)").extract_first()
        # if next_page:
        #    yield scrapy.Request(response.urljoin(next_page), callback=self.parse)

    def callback_response(self, response):
        item = {}
        item['body'] = response.body()
        yield item

    def parse_book_page(self, response):
        item = {}
        product = response.css("div.product_main")
        item["title"] = product.css("h1 ::text").extract_first()
        item['category'] = response.xpath(
            "//ul[@class='breadcrumb']/li[@class='active']/preceding-sibling::li[1]/a/text()"
        ).extract_first()
        item['description'] = response.xpath(
            "//div[@id='product_description']/following-sibling::p/text()"
        ).extract_first()
        item['price'] = response.css('p.price_color ::text').extract_first()
        yield item
