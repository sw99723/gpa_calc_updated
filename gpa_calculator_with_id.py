import streamlit as st
from queue import Queue
import json

USER_DATA_FILE = "user_data.json"

grade_scheme = {
    "A+": {"Grade Point": 4.0, "Percentage": (90, 100)},
    "A": {"Grade Point": 4.0, "Percentage": (85, 89)},
    "A-": {"Grade Point": 3.7, "Percentage": (80, 84)},
    "B+": {"Grade Point": 3.3, "Percentage": (77, 79)},
    "B": {"Grade Point": 3.0, "Percentage": (73, 76)},
    "B-": {"Grade Point": 2.7, "Percentage": (70, 72)},
    "C+": {"Grade Point": 2.3, "Percentage": (67, 69)},
    "C": {"Grade Point": 2.0, "Percentage": (63, 66)},
    "C-": {"Grade Point": 1.7, "Percentage": (60, 62)},
    "D+": {"Grade Point": 1.3, "Percentage": (57, 59)},
    "D": {"Grade Point": 1.0, "Percentage": (53, 56)},
    "D-": {"Grade Point": 0.7, "Percentage": (50, 52)},
    "F": {"Grade Point": 0.0, "Percentage": (0, 49)}
}

def get_grades(courses: dict) -> dict:
    """
    현재 가지고 있는 taken_courses를 코스 이름을 키로 하고
    밸류를 점수와 grade point로 하는 딕셔너리로 바꿈
    """
    updated_courses = {}

    for course_name, score in courses.items():
        if isinstance(score, int):
            for grade_value, info in grade_scheme.items():
                percentage_range = info["Percentage"]
                if int(percentage_range[0]) <= score <= int(percentage_range[1]):
                    grade_point = info["Grade Point"]
            updated_courses[course_name] = (score, grade_point)

    return updated_courses

def get_grades_point_completed_credit(courses: dict) -> (float, float):
    """
    gpa에 계산되는 grade point와 complete credits 구하기
    """
    updated_courses = get_grades(courses)
    completed_credit = 0.0
    sum_grade_point = 0.0

    for course, course_info in updated_courses.items():
        period_sign = course[6:7]
        if period_sign == 'H':
            if isinstance(course_info[1], float):
                completed_credit += 0.5
                sum_grade_point += course_info[1] * 0.5
        elif period_sign == 'Y':
            if isinstance(course_info[1], float):
                completed_credit += 1.0
                sum_grade_point += course_info[1] * 1.0

    return (sum_grade_point, completed_credit)

def get_cgpa(courses: dict):
    """
    현재 CGPA 구하기

    Grade Point * Credit (0.5 or 1.0) / Total Credit (Except CR/NCR)
    """
    sum_grade_point, completed_credit = get_grades_point_completed_credit(courses)

    if completed_credit != 0:
        current_cgpa = round(sum_grade_point / completed_credit, 2)
    else:
        current_cgpa = 0.0

    st.write(f'Current CGPA is {current_cgpa}')

def calculate_remaining_credit(courses: dict) -> (float, float):
    """
    20개 크레딧 중 몇 크레딧을 더 들어야 하는지

    (remaining credit, completed credit)
    """
    completed_credit = 0.0
    updated_courses = get_grades(courses)

    for course, course_info in updated_courses.items():
        if course[6:7] == 'H':
            if isinstance(course_info[0], int):
                if course_info[0] >= 50:
                    completed_credit += 0.5
        elif course[6:7] == 'Y':
            if isinstance(course_info[0], int):
                if course_info[0] >= 50:
                    completed_credit += 1.0

    remaining_credit = 20.0 - completed_credit

    return (remaining_credit, completed_credit)

def print_calculate_remaining_credit(courses: dict):
    remaining_credit, completed_credit = calculate_remaining_credit(courses)
    st.write(f'Remaining credit is {remaining_credit} \nComplete credit is {completed_credit}')

def remaining_cr(courses: dict):
    """
    2개의 CR/NCR 중 몇 개 사용했는지/몇 개 남았는지
    """
    total = 2.0
    used_courses = []

    for course, course_info in courses.items():
        if course_info == 'CR' or course_info == 'NCR':
            if course[6:7] == 'H':
                total -= 0.5
                used_courses.append(course)
            elif course[6:7] == 'Y':
                total -= 1.0
                used_courses.append(course)

    st.write(f'Remaining Credit/No Credit option is {total} \nYou used Credit/No Credit option for {used_courses}')

def save_user_data(username, password, courses):
    """
    사용자 정보와 점수 정보를 저장하는 함수
    """
    user_data = {
        "username": username,
        "password": password,
        "courses": courses
    }
    with open(USER_DATA_FILE, "w") as file:
        json.dump(user_data, file)

def load_user_data(username, password):
    """
    사용자 정보와 점수 정보를 불러오는 함수
    """
    try:
        with open(USER_DATA_FILE, "r") as file:
            user_data = json.load(file)
        if user_data["username"] == username and user_data["password"] == password:
            return user_data["courses"]
        else:
            st.error("Invalid username or password.")
    except FileNotFoundError:
        st.error("User data not found.")
    return {}

def create_user_account(username, password):
    # Check if the user already exists
    if user_exists(username):
        st.error("Username already exists. Please choose a different username.")
    else:
        # Create a new user account
        save_user_data(username, password, {})
        st.success("Account created successfully! You can now log in.")

def login_user(username, password):
    # Check if the user exists and the password is correct
    user_data = load_user_data(username, password)
    return bool(user_data)

def user_exists(username):
    # Check if the username already exists in your system
    try:
        with open(USER_DATA_FILE, "r") as file:
            user_data = json.load(file)
        return user_data["username"] == username
    except FileNotFoundError:
        return False

def main():
    st.title("GPA Calculator")
    st.write("Welcome to the GPA calculator!")

    # Check if the user wants to create a new account
    create_account = st.checkbox("Create New Account")

    if create_account:
        new_username = st.text_input("Enter a Username")
        new_password = st.text_input("Enter a Password", type="password")

        if st.button("Create Account"):
            # Save the new account information
            create_user_account(new_username, new_password)
            st.success("Account created successfully! You can now log in.")
    else:
        # Log in with existing account
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if username and password:
            # Check if the user exists and the password is correct
            if login_user(username, password):
                courses = load_user_data(username, password)
                taken_courses = input_grades()

                if st.button("Save Grades"):
                    save_user_data(username, password, taken_courses)

                if st.button("Calculate GPA"):
                    get_cgpa(taken_courses)

                if st.button("Calculate Remaining Credit"):
                    print_calculate_remaining_credit(taken_courses)

                if st.button("Calculate Remaining CR/NCR"):
                    remaining_cr(taken_courses)
            else:
                st.error("Invalid username or password.")
        else:
            st.warning("Please enter your username and password.")


if __name__ == "__main__":
    main()
