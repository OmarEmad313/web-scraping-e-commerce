import scrapy
from itemloaders.processors import MapCompose , TakeFirst

def clean_data(data, str_remove=None):
    strs_to_remove = ['$', '#', 'Item',',']
    if str_remove:
        strs_to_remove.append(str_remove)
    for str in strs_to_remove:
        if str in data:
            data = data.replace(str, '')

    return data.strip()

class Product(scrapy.Item):
    product_id = scrapy.Field(input_processor=MapCompose(clean_data), output_processor=TakeFirst())
    product_brand= scrapy.Field(input_processor=MapCompose(clean_data), output_processor=TakeFirst())
    product_name= scrapy.Field(input_processor=MapCompose(lambda x, loader_context: clean_data(x, loader_context.get('brand', '')))
                               , output_processor=TakeFirst())
    rating= scrapy.Field(input_processor=MapCompose(clean_data), output_processor=TakeFirst())
    no_of_reviews= scrapy.Field(input_processor=MapCompose(clean_data), output_processor=TakeFirst())
    current_price= scrapy.Field(input_processor=MapCompose(lambda x:float(clean_data(x)) if x else None)
                                , output_processor=TakeFirst())
    original_price= scrapy.Field(input_processor=MapCompose(lambda x:float(clean_data(x)) if x else None)
                                , output_processor=TakeFirst())
    pass


