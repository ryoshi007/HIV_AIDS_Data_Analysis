import streamlit as st
from word_parsing import WordParsing
import asyncio
import requests
# import auth as auth
# import db as db
from streamlit_option_menu import option_menu
# import secret variable
from secret import secret
import firebase
from firebaseConfig import config
from http import cookies

# Instantiates a Firebase app
app = firebase.initialize_app(config)

# Firebase Authentication
auth = app.auth()

# initialize cookie
cookie = cookies.SimpleCookie()

if 'username' not in st.session_state:
    st.session_state['username'] = ""

if 'user_id' not in st.session_state:
    st.session_state['user_id'] = ""

if 'Email' not in st.session_state:
    st.session_state['Email'] = ""


def sidebar():
    # initialize the user's login state using SessionState
    if 'loggedIn' not in st.session_state:
        st.session_state['loggedIn'] = False

    if st.session_state["loggedIn"]:
        show_logout_sidebar()
    else:
        show_login_sidebar()


def create_cookie(auth_token):
    # store cookie
    cookie['user_id'] = auth_token["localId"]
    cookie['auth_token'] = auth_token["idToken"]
    cookie['expiresIn'] = auth_token["expiresIn"]
    cookie['expiresAt'] = auth_token["expiresAt"]
    cookie_string = cookie.output()
    return [('Set-Cookie', cookie_string)]


def clear_cookie():
    cookie['user_id'] = ''
    cookie['auth_token'] = ''
    cookie['expiresIn'] = ''
    cookie['expiresAt'] = ''
    cookie_string = cookie.output()
    return [('Set-Cookie', cookie_string)]


def LoggedIn_clicked(email, password):
    user = None
    try:
        auth_token = auth.sign_in_with_email_and_password(email, password)
        st.session_state["Email"] = email
        create_cookie(auth_token)
        account_info = auth.get_account_info(auth_token['idToken'])
        st.session_state["user_id"] = account_info['users'][0]['localId']
        # print(st.session_state["user_id"])
        username = account_info['users'][0]['displayName']
        # update username in session_state
        st.session_state['username'] = username
        st.success(f"Welcome, {username}!")
        print("login successful")
        st.session_state["loggedIn"] = True
    except:
        st.error("Incorrect password. Please try again.")
        print("login failed")
    return user


def createAccount_clicked(email, username, password, password_c):
    if len(password) < 8: return 'invalid password: password must be > 8 characters'
    elif password == password_c:
        try:
            auth_token = auth.create_user_with_email_and_password(email, password)
            auth.update_profile(auth_token['idToken'], display_name=username)
            st.success("Registration successful.")
            st.session_state["Email"] = email
            return "registration successful"
        except:
            st.error("Registration failed. The email has been registered.")
            return "registration failed"
    else:
        st.error("Incompatible password.")


def LoggedOut_clicked():
    clear_cookie()
    st.session_state["loggedIn"] = False


def show_login_sidebar():
    if not st.session_state['loggedIn']:
        with st.sidebar:
            st.title("Personal Nutrition Recommendation App")
            choice = st.selectbox('Login / Sign Up', ['Login', 'Sign Up'])

            if choice == 'Sign Up':
                # do not autocomplete email on sign up page
                email = st.text_input('Email')
                username = st.text_input('Username')
                sign_up_password = st.text_input('Password', type="password")
                sign_up_password_c = st.text_input('Confirm Password', type="password")
                st.button('Create Account', on_click=createAccount_clicked, args= (email, username, sign_up_password, sign_up_password_c))

            if choice == 'Login':
                # autocomplete email on login page
                email = st.text_input('Email', value=st.session_state["Email"])
                login_password = st.text_input('Password', type="password", key="login_password_key")
                st.button('Login', on_click=LoggedIn_clicked, args= (email, login_password))


def home():
    st.title("Home")
    nutrition_calculator()

def meal_recommendation():
    st.title("Meal Recommendation")
    # render meal recommendation page here

def profile():
    st.title("Profile")
    # render profile page here

def show_logout_sidebar():
    if st.session_state["loggedIn"]:
        with st.sidebar:
            st.title("My App")
            st.write("Welcome, " + st.session_state["username"])
            selected = option_menu(
                menu_title="Main Menu",
                options=["Home", "Meal Recommendation", "Profile"],
            )
            st.button("Log Out", on_click=LoggedOut_clicked)

        # navigate between pages
        if selected == "Home":
            home()
        if selected == "Meal Recommendation":
            meal_recommendation()
        if selected == "Profile":
            profile()


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

    api_key = secret['API_KEY_APIFY']
    actor_id = secret['ACTOR_IP_APIFY']

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
    response = requests.post(start_actor_url, data=values, headers=headers)

    # Get the actor result
    result = response.json()
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
    sidebar()


if __name__ == '__main__':
    main()