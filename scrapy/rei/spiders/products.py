import scrapy
from scrapy.spiders import CrawlSpider , Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy import signals
from scrapy.signalmanager import dispatcher
from ..items import Product


# Steps for the project:
# 1. Create a new Scrapy project.
# 2. Create a new spider.
# 3. Create rules for both pages links and product links with a callback function.
# 4. Create a parse_product method to extract product information. To find out the css selector 
#    use terminal and type response.css('css selector').extract() to see the output.
#5. Run the spider and save the input in an item class object while cleaning it.
#6. Create a pipeline to store the information in a csv and json file.


class ProductsSpider(CrawlSpider):
    name = 'products'
    products_visited = 0
    allowed_domains = ['rei.com']
    start_urls = ['https://www.rei.com/c/camping-and-hiking/f/scd-deals']
   
    rules = (
        Rule(
            LinkExtractor(allow=r'page='), 
        ),
        Rule(
            LinkExtractor(allow=r'/product/'), 
            callback='parse_product', 
        )

    )

    def parse_product(self, response):
        productLoader = ItemLoader(Product(), response=response)

        productLoader.add_css('product_id', 'span#product-item-number::text')
        productLoader.add_css('product_brand', 'a#product-brand-link::text')
        brand = productLoader.get_output_value('product_brand')
        productLoader.context['brand'] = brand
        productLoader.add_css('product_name', 'h1#product-page-title::text')
        productLoader.add_css('rating', '.cdr-rating__number_15-0-0::text')
        productLoader.add_css('no_of_reviews', '.cdr-rating__count_15-0-0 > span:nth-of-type(2)::text')
        productLoader.add_css('current_price', 'span.price-value.price-value--sale::text',default=False)
        productLoader.add_css('original_price', 'span.price-component__compare--value::text',default=False )

        return productLoader.load_item()