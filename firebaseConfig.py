import streamlit as st

config = {
  "apiKey": st.secrets['API_KEY_FIREBASE'],
  "authDomain": "streamlit-c092c.firebaseapp.com",
  "databaseURL": st.secrets['DATABASE_URL_FIREBASE'],
  "projectId": "streamlit-c092c",
  "storageBucket": "streamlit-c092c.appspot.com",
  "messagingSenderId": "761273431495",
  "appId": st.secrets['APP_ID_FIREBASE'],
  "measurementId": "G-HRX77LVPRX"
}
