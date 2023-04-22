import streamlit as st
from word_parsing import WordParsing
from bs4 import BeautifulSoup
import asyncio
from pyppeteer import launch


def nutrition_calculator():
    st.subheader("Dietary Reference Intake (DRI) Calculator")
    st.write("Please input your data to calculate the required nutrition intake")
    st.text("")

    sex = st.selectbox("Your gender", ["Male", "Female"])
    age = st.selectbox("Your age", ["Birth to 6 months", "7 - 12 months", "1 - 3 years", "4 - 8 years", "9 - 13 years",
                                    "14 - 18 years", "19 - 50 years", "51 - 70 years", "71+ years"])

    pregnancy = st.selectbox("Possible pregnancy", ["No pregnant or lactating", "Pregnant", "Lactating"]) \
        if sex == "Female" and age in ["9 - 13 years", "14 - 18 years", "19 - 50 years"] else "Lactating"

    height = st.number_input("Your height in cm", min_value=1.0, max_value=300.0, step=0.1, format="%.1f")
    weight = st.number_input("Your weight in kg", min_value=1.0, max_value=600.0, step=0.1, format="%.1f")

    activity_level = st.selectbox("Activity factor",
                                  ["Little / No exercise", "Exercise 1-2 times/week", "Exercise 2-3 times/week",
                                   "Exercise 3-5 times/week", "Exercise 6-7 times/week", "Professional athlete"])

    smoke = "No" if age in ["Birth to 6 months", "7 - 12 months", "1 - 3 years", "4 - 8 years",
                            "9 - 13 years"] else st.selectbox("Are you a smoker?", ["No", "Yes"])

    if st.button("Calculate"):
        progress_text = st.empty()
        progress_text.text("Calculating... Please wait.")
        warning_text = st.empty()
        warning_text.text("If it fails, please ensure you have good Internet connection and press the button again.")

        user_info = WordParsing(sex, age, height, weight, activity_level, smoke, pregnancy)
        url = user_info.create_url()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        required_nutrient = loop.run_until_complete(get_nutrient_intake(url))
        progress_text.text("")
        warning_text.text("")
        st.subheader("Result")
        st.json(required_nutrient)
        st.text("")
        st.subheader("Website Link")
        st.write(url)


async def get_nutrient_intake(url):
    browser = await launch(handleSIGINT=False, handleSIGTERM=False, handleSIGHUP=False)
    page = await browser.newPage()
    page.setDefaultNavigationTimeout(60000)
    await page.goto(url)

    await asyncio.sleep(1)

    website_data = await page.content()
    soup = BeautifulSoup(website_data, "html.parser")

    generic_text_elements = soup.select('div.GenericText')
    nutrient_intake_table = []
    for element in generic_text_elements:
        data = element.find_all('td')
        if data:
            nutrient_intake_table.append(data)

        calorie_intake = soup.find('input', {'aria-label': 'Total daily calorie requirement '})
        result = {
            'Calorie_Per_Day': float(calorie_intake['value'].replace(',', '')),
            'Macronutrient': {},
            'Vitamin': {},
            'Micronutrient': {}
        }

    for table in nutrient_intake_table:
        for i in range(0, len(table), 2):
            key = table[i].get_text()
            value = table[i + 1].get_text()
            if key in ['Carbohydrates', 'Total fiber', 'Protein', 'Fat', 'Water']:
                if key == 'Total fiber':
                    key = 'Fiber'
                result['Macronutrient'][key] = value
            elif key.startswith('Vitamin') or key == 'Choline' or key.startswith('Biotin'):
                key = key.replace(' ', '_').replace('(', '').replace(')', '')
                key = '_'.join(key.split('_')[:2])
                subscript_mapping = {
                    "₁": "1",
                    "₂": "2",
                    "₃": "3",
                    "₄": "4",
                    "₅": "5",
                    "₆": "6",
                    "₇": "7",
                    "₈": "8",
                    "₉": "9",
                    "₀": "0",
                }
                for sub, num in subscript_mapping.items():
                    key = key.replace(sub, num)
                result['Vitamin'][key] = value
            else:
                result['Micronutrient'][key] = value
    await browser.close()
    return result


def main():
    st.set_page_config(
        page_title="Nutrition Intake Calculator"
    )
    hide_st_style = """
                    <style>
                    header {visibility: hidden;}
                    footer {visibility: hidden;}
                    </style>
                    """
    st.markdown(hide_st_style, unsafe_allow_html=True)
    st.write('<style>div.block-container{padding-top:0rem;padding-bottom:0rem;}</style>', unsafe_allow_html=True)
    nutrition_calculator()


if __name__ == '__main__':
    main()