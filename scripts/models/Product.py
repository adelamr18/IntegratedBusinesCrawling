class Product:
    def __init__(self, merchant, product_id, brand_ar, brand_en, barcode, name_ar, name_en,
                 category_one_eng, category_two_eng, category_three_eng, category_four_eng,
                 category_five_eng, category_six_eng, category_seven_eng,
                 category_one_ar, category_two_ar, category_three_ar,
                 category_four_ar, category_five_ar, category_six_ar, category_seven_ar,
                 category_eight_eng="", category_nine_eng="", category_eight_ar="", category_nine_ar="",
                 price_before="", price_after="", offer_start_date="", offer_end_date="",
                 url="", image_url="", source_type="", crawled_on=""):
        self.merchant = merchant
        self.product_id = product_id
        self.brand_ar = brand_ar
        self.brand_en = brand_en
        self.barcode = barcode
        self.name_ar = name_ar
        self.name_en = name_en
        self.category_one_eng = category_one_eng
        self.category_two_eng = category_two_eng
        self.category_three_eng = category_three_eng
        self.category_four_eng = category_four_eng
        self.category_five_eng = category_five_eng
        self.category_six_eng = category_six_eng
        self.category_seven_eng = category_seven_eng
        self.category_one_ar = category_one_ar
        self.category_two_ar = category_two_ar
        self.category_three_ar = category_three_ar
        self.category_four_ar = category_four_ar
        self.category_five_ar = category_five_ar
        self.category_six_ar = category_six_ar
        self.category_seven_ar = category_seven_ar
        self.category_eight_eng = category_eight_eng
        self.category_nine_eng = category_nine_eng
        self.category_eight_ar = category_eight_ar
        self.category_nine_ar = category_nine_ar
        self.price_before = price_before
        self.price_after = price_after
        self.offer_start_date = offer_start_date
        self.offer_end_date = offer_end_date
        self.url = url
        self.image_url = image_url
        self.source_type = source_type
        self.crawled_on = crawled_on
