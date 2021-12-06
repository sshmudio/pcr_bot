from PIL import Image, ImageDraw,ImageFont
import random

class PcrGenerator:
    font_dir = '/System/Library/Fonts/'
    font_collor = '#000000'
    template_image = "pcrtemplate.png"

    def __init__(self, name, dob, age, gender, collected_date, date_of_completion):
        self.name = name
        self.dob = dob
        self.age = age
        self.gender = gender
        self.collected_date = collected_date
        self.date_of_completion = date_of_completion

    def generate(self):
        with Image.open(self.template_image).convert("RGBA") as base:
            txt = Image.new("RGBA", base.size, (255,255,255,0))
            fnt = ImageFont.truetype(f'{self.font_dir}helr65w.ttf', 60)
            d = ImageDraw.Draw(txt)
            d.text((816,1385), self.name, font=fnt, fill=self.font_collor) # First and last name
            d.text((780,1510), self.dob, font=fnt, fill=self.font_collor) # DOB
            d.text((1728,1510), self.age, font=fnt, fill=self.font_collor) # Age
            d.text((2350,1510), self.gender, font=fnt, fill=self.font_collor) # Gender
            d.text((1780,1260), self.collected_date, font=fnt, fill=self.font_collor) # Collected data
            d.text((1200,4800), self.date_of_completion, font=fnt, fill=self.font_collor) # Date of completion
            out = Image.alpha_composite(base, txt)
            name_document_string = f'{self.name}-{random.randrange(0, 100)}.png'
            out.save(name_document_string)
            return name_document_string

