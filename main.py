import streamlit as st
from word_parsing import WordParsing
import asyncio
import requests
import time


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
        required_nutrient = get_apify_result(url)
        progress_text.text("")
        warning_text.text("")
        st.subheader("Result")
        st.json(required_nutrient)
        st.text("")
        st.subheader("Website Link")
        st.write(url)


def get_apify_result(url):

    api_key = st.secrets['api_key']
    actor_id = st.secrets['actor_id']

    # Start the actor
    start_actor_url = f"https://api.apify.com/v2/acts/{actor_id}/run-sync-get-dataset-items?token={api_key}"
    values = f"""
      {{
        "start_urls": [
          {{
            "url": "{url}"
          }}
        ],
        "max_depth": 1
      }}
    """
    headers = {
        'Content-Type': 'application/json'
    }
    st.write(values)
    response = requests.post(start_actor_url, data=values, headers=headers)
    time.sleep(20)

    # Get the actor result
    result = response.json()
    print(result)

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