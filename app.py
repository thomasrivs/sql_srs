from datetime import date
from datetime import timedelta
import duckdb
import streamlit as st
import os
import logging

if "data" not in os.listdir():
    logging.error(os.listdir())
    logging.error("creating folder data")
    os.mkdir("data")

if "my-db.duckdb" not in os.listdir("data"):
    exec(open("init_db.py").read())


con = duckdb.connect(database="data/my-db.duckdb", read_only=False)


def check_users_solution(query: str) -> None:
    """
    Checks that user SQL query is correct by:
    1/ checking the columns
    2/ checking the values
    :param query: a string containing the query inserted bu the user
    """
    global result
    result = con.execute(query).df()
    st.dataframe(result)
    try:
        result = result[solution_df.columns]
        st.dataframe(result.compare(solution_df))
    except KeyError as e:
        (st.write("Some columns are missing!"))
    n_lines_difference = result.shape[0] - solution_df.shape[0]
    if n_lines_difference != 0:
        st.write(
            f"result has a {n_lines_difference} lines difference with the solution_df!"
        )


with st.sidebar:
    available_themes_df = con.execute("SELECT DISTINCT theme FROM memory_state").df()
    theme = st.selectbox(
        "What would you like to review?",
        available_themes_df["theme"].unique(),
        index=None,
        placeholder="Select a theme...",
    )
    if theme:
        st.write(f"You selected {theme}")
        select_exercise_query = f"SELECT * FROM memory_state WHERE theme = '{theme}'"
    else:
        select_exercise_query = f"SELECT * FROM memory_state"

    exercise = (
        con.execute(select_exercise_query)
        .df()
        .sort_values("last_reviewed")
        .reset_index(drop=True)
    )
    st.write(exercise)
    EXERCISE_NAME = exercise.loc[0, "exercise_name"]
    with open(f"answers/{EXERCISE_NAME}.sql", "r") as f:
        answer = f.read()

    solution_df = con.execute(answer).df()

st.header("Enter your code below:")
query = st.text_area(label="votre code SQL ici", key="user_input")

if query:
    check_users_solution(query)
else:
    result = "waiting for your input"
    st.subheader(result)

for n_days in [2, 7, 21]:
    if st.button(f"revoir dans {n_days} jours"):
        next_review = date.today() + timedelta(days=n_days)
        con.execute(
            f"UPDATE memory_state SET last_reviewed = {next_review} WHERE exercise_name='{EXERCISE_NAME}'"
        )
        st.rerun()

if st.button("Reset"):
    con.execute(f"UPDATE memory_state SET last_reviewed = '1970-01-01'")
    st.rerun()

tab2, tab3 = st.tabs(["Tables", "Solution"])

with tab2:
    exercise_tables = exercise.loc[0, "tables"]
    for table in exercise_tables:
        st.write(f"table: {table}")
        df_table = con.execute(f"SELECT * FROM '{table}'").df()
        st.dataframe(df_table)

with tab3:
    st.write(answer)

con.close()
