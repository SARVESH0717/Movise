import streamlit as st
import pandas as pd
from utils import get_poster, display_images, fetch_trailer
from db import init_db, add_user, check_user
import re # Import regex for password validation

# Read The Data
movie = pd.read_csv(r'C:\Users\Admin\Desktop\Sarvesh\Projects\Movise\src\Dataset\tmdb_5000_credits.csv')

def pagination():
    st.set_page_config(
        page_title="Movise",
        page_icon="🎬",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

# --- Password Validation Function ---
def validate_password(password):
    """
    Validates the password based on specific requirements:
    - At least 6 letters
    - At least 1 number
    - At least 1 special character (!@#$%^&*()-+?_=,<>/)
    """
    if len(password) < 6:
        return "Password must be at least 6 characters long."
    if not re.search(r"[a-zA-Z]", password):
        return "Password must contain at least one letter."
    if not re.search(r"\d", password):
        return "Password must contain at least one number."
    if not re.search(r"[!@#$%^&*()-+?_=,<>/\[\]\{\}\|;:'\"`~]", password):
        return "Password must contain at least one special character (e.g., !@#$%^&*)."
    return None # Return None if validation passes

def get_poster_url_from_movie_title(movie_title):
    try:
        movie_id = movie[movie['title'] == movie_title]['movie_id'].iloc[0]
        return get_poster(movie_id)[1]
    except Exception:
        return "https://via.placeholder.com/150?text=No+Poster"

def show_recommendation(title):
    with st.spinner('Recommendation is processing...'):
        from recomendor import get_recomend
        recommendation = get_recomend(title)
        x = recommendation['id'].to_list()
        poster = [get_poster(i) for i in x]
        display_images(*poster)

def section_display_movies(section_title, section_description, movie_titles_list):
    st.markdown("---")
    st.subheader(section_title)
    st.write(section_description)
    if not movie_titles_list:
        st.info("No movies to display right now. Please check back later!")
        return
    num_columns = 5
    cols = st.columns(num_columns)
    for i, title in enumerate(movie_titles_list):
        poster_url = get_poster_url_from_movie_title(title)
        with cols[i % num_columns]:
            with st.container():
                st.image(poster_url, caption=title, use_container_width=True)

def main():
    pagination()
    init_db()
    st.title('Movise📺')

    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if "active_tab" not in st.session_state:
        st.session_state["active_tab"] = "Home"
    if "show_login" not in st.session_state:
        st.session_state["show_login"] = False

    if not st.session_state["authenticated"]:
        tab_names = ["Home"]
    else:
        tab_names = ["Home", "Recommend", "About", "Contact Us"]

    selected = st.radio("Navigation", tab_names, index=tab_names.index(st.session_state["active_tab"]), horizontal=True)

    if selected == "Home":
        st.header("Welcome to Movise!")
        if not st.session_state["authenticated"]:
            if not st.session_state["show_login"]:
                st.subheader("Sign Up")
                signup_email = st.text_input("Email", key="signup_email")
                signup_password = st.text_input("Password", type="password", key="signup_password")
                
                # --- Display Password Requirements ---
                st.info("Password must be at least 6 characters long and contain at least one letter, one number, and one special character (e.g., !@#$%^&*).")

                if st.button("Sign Up"):
                    validation_error = validate_password(signup_password)
                    if validation_error:
                        st.error(validation_error)
                    else:
                        if add_user(signup_email, signup_password):
                            st.session_state["authenticated"] = True
                            st.session_state["active_tab"] = "Recommend"
                            st.rerun()
                        else:
                            st.error("Email already exists. Please login or use a different email.")
                if st.button("Already have an account? Log In"):
                    st.session_state["show_login"] = True
                    st.rerun()
            else:
                st.subheader("Login")
                login_email = st.text_input("Email", key="login_email")
                login_password = st.text_input("Password", type="password", key="login_password")
                if st.button("Login"):
                    if check_user(login_email, login_password):
                        st.session_state["authenticated"] = True
                        st.session_state["active_tab"] = "Recommend"
                        st.rerun()
                    else:
                        st.error("Invalid email or password.")
                if st.button("Don't have an account? Sign Up"):
                    st.session_state["show_login"] = False
                    st.rerun()
        else:
            st.success("You are already logged in!")
            st.write("Please select a movie to get recommendations.")
            if st.button("Logout"):
                st.session_state["authenticated"] = False
                st.session_state["active_tab"] = "Home"
                st.session_state["show_login"] = False
                st.info("You have been logged out.")
                st.rerun()

    elif selected == "Recommend":
        # Only show content if authenticated
        if st.session_state["authenticated"]:
            with st.container():
                title = st.selectbox('Please Select Movie', movie['title'].to_list())
                if st.button('Recommend'):
                    show_recommendation(title)
            trending_movie_titles_example = movie['title'].sample(n=10, random_state=42).to_list()
            section_display_movies("🔥 Trending Now", "Check out what's hot and happening!", trending_movie_titles_example)
            new_release_movie_titles_example = movie['title'].sample(n=10, random_state=10).to_list()
            section_display_movies("✨ New Releases", "Fresh out of the oven! Don't miss these.", new_release_movie_titles_example)
        else:
            st.warning("Please login or sign up to view movie recommendations.")
            # Optionally redirect to home or show login directly
            if st.button("Go to Home / Login"):
                st.session_state["active_tab"] = "Home"
                st.session_state["show_login"] = True
                st.rerun()


    elif selected == "About":
        # Only show content if authenticated
        if st.session_state["authenticated"]:
            st.markdown("""
            **Movise: It's a web platform where you can discover your next cinematic masterpiece.**

            ### About Our Movie Recommender 🎬✨

            **Your Personal Movie Guru:**
            We help you find your next favorite film.

            **Smart Suggestions:**
            Powered by algorithms that understand your taste.

            **Beyond the Blockbusters:**
            Discover hidden gems and expand your watchlist.

            **Effortless Discovery:**
            Less searching, more watching.

            _Simply choose a movie to start!_
            """)
        else:
            st.warning("Please login or sign up to view this content.")
            if st.button("Go to Home / Login"):
                st.session_state["active_tab"] = "Home"
                st.session_state["show_login"] = True
                st.rerun()


    elif selected == "Contact Us":
        # Only show content if authenticated
        if st.session_state["authenticated"]:
            st.markdown("""
            For any queries, please contact us at: [sarveshdangar01@gmail.com]

            Connect with us on [LinkedIn](https://www.linkedin.com/in/sarvesh-dangar-6913682b1/)

            follow us on [GitHub](https://github.com/SARVESH0717)

            or visit our [Portfolio](https://sarvesh0717.github.io/Portfolio-Website/).
            """)
            st.markdown("Made by Sarvesh Dangar")
            st.markdown("© 2025 Movise. All rights reserved.")
        else:
            st.warning("Please login or sign up to view this content.")
            if st.button("Go to Home / Login"):
                st.session_state["active_tab"] = "Home"
                st.session_state["show_login"] = True
                st.rerun()


if __name__ == "__main__":
    main()
