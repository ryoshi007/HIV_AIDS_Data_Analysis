class WordParsing:
    def __init__(self, sex, age, height, weight, activity, smoke="No", pregnancy="Lactating"):
        self.sex = self.get_gender(sex)
        self.age = self.get_age_range(age)
        self.pregnancy = self.get_pregnancy(pregnancy)
        self.height = height
        self.weight = weight
        self.activity = self.get_activity_factor(activity)
        self.smoke = self.get_smoke(smoke)

    @staticmethod
    def get_gender(response):
        if response == "Female":
            return 1
        elif response == "Male":
            return 0

    @staticmethod
    def get_age_range(response):
        if response == "Birth to 6 months":
            return 0
        elif response == "7 - 12 months":
            return 1
        elif response == "1 - 3 years":
            return 2
        elif response == "4 - 8 years":
            return 3
        elif response == "9 - 13 years":
            return 4
        elif response == "14 - 18 years":
            return 5
        elif response == "19 - 50 years":
            return 6
        elif response == "51 - 70 years":
            return 7
        elif response == "71+ years":
            return 8

    @staticmethod
    def get_pregnancy(response):
        if response == "Not pregnant or lactating":
            return 0
        elif response == "Pregnant":
            return 396
        elif response == "Lactating":
            return 365

    @staticmethod
    def get_activity_factor(response):
        if response == "Little / No exercise":
            return 1.2
        elif response == "Exercise 1-2 times/week":
            return 1.4
        elif response == "Exercise 2-3 times/week":
            return 1.6
        elif response == "Exercise 3-5 times/week":
            return 1.75
        elif response == "Exercise 6-7 times/week":
            return 2.0
        elif response == "Professional athlete":
            return 2.3

    @staticmethod
    def get_smoke(response):
        if response == "Yes":
            return 35
        elif response == "No":
            return 0

    def create_url(self):
     return f"https://www.omnicalculator.com/health/dri?c=MYR&v=height:{self.height}!cm,pregnancy:{self.pregnancy},sex:{self.sex},weight:{self.weight}!kg,age:{self.age},activity_factor:{self.activity},smoker:{self.smoke}"