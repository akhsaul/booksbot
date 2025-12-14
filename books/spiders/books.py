# -*- coding: utf-8 -*-
import json
import logging
import secrets
import string
import random
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

    while len(unique_codes) < count:
        code = generate_secure_string(length)
        unique_codes.add(code)

    return list(unique_codes)


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["manajemenproject.netlify.app"]
    start_urls = [
        'https://manajemenproject.netlify.app',
    ]

    def parse(self, response):
        max_count = self.settings.getint("max_count", 900000)
        range_str_length  = range(8, 240)
        unique_str = set()
        url = 'https://manajemenproject.netlify.app/.netlify/functions/register'
        self.logger.log(logging.INFO,f"Starting post to {url} for {max_count} requests")

        for _ in range(max_count):

            stop_job = self.settings.getbool("STOP_JOB", False)
            if stop_job:
                self.logger.log(logging.INFO, "STOP_JOB is set to True. Stopping the spider.")
                break

            target_len = len(unique_str) + 1
            string_length = random.choice(range_str_length)

            rand_str = None
            while len(unique_str) < target_len:
                rand_str = generate_secure_string(string_length)

                # Sifat set: Jika item duplikat, dia ditolak dan Len TIDAK berubah.
                # Jika item unik, dia diterima dan Len BERUBAH (+1).
                unique_str.add(rand_str)

            email = rand_str + '@gmail.com'
            passw = rand_str
            self.logger.log(logging.DEBUG, f"New data: {rand_str}")
            yield scrapy.Request(
                url,
                callback=self.callback_response,
                method="POST",
                headers={
                    'Referer': 'https://manajemenproject.netlify.app/register',
                    'Content-Type': 'application/json',
                    'Accept': 'application/json, text/plain, */*',
                    'Accept-language': 'en-US,en;q=0.9,id;q=0.8',
                    'cache-control': 'no-cache',
                    'origin': 'https://manajemenproject.netlify.app',
                    'pragma': 'no-cache',
                    'priority': 'u=1, i',
                    'referer': 'https://manajemenproject.netlify.app/register',
                    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
                    'sec-ch-ua': 'Chromium;v=140, Google Chrome;v=140, Not_A Brand;v=99',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': 'Linux',
                    'sec-fetch-dest': 'empty',
                    'sec-fetch-mode': 'cors',
                    'sec-fetch-site': 'same-origin'
                },
                body=json.dumps({"email": email, "password": passw}),
                errback=self.when_error
            )

            #time.sleep(0.5)

        self.logger.log(logging.INFO,f"End of post to {url} for {max_count} requests")

        # for book_url in response.css("article.product_pod > h3 > a ::attr(href)").extract():
        #    yield scrapy.Request(response.urljoin(book_url), callback=self.parse_book_page)
        # next_page = response.css("li.next > a ::attr(href)").extract_first()
        # if next_page:
        #    yield scrapy.Request(response.urljoin(next_page), callback=self.parse)

    def when_error(self, failure):
        request = getattr(failure, 'request', None)
        if request:
            self.logger.log(logging.ERROR, f"Request failed: {request.text()}")
        else:
            self.logger.log(logging.ERROR, f"Request failed: {failure}")

    def callback_response(self, response):
        yield response.text.json()

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
