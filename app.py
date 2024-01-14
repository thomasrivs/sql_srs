import duckdb
import streamlit as st

con = duckdb.connect(database="data/my-db.duckdb", read_only=False)

with st.sidebar:
    theme = st.selectbox(
        "What would you like to review?",
        ("cross_joins", "Group By", "Windows Functions"),
        index=None,
        placeholder="Select a theme...",
    )
    st.write("You selected:", theme)

    exercise = con.execute(f"SELECT * FROM memory_state WHERE theme = '{theme}' ").df()
    st.write(exercise)

    EXERCISE_NAME = exercise.loc[0, "exercise_name"]
    with open(f"answers/{EXERCISE_NAME}.sql", "r") as f:
        answer = f.read()

    solution_df = con.execute(answer).df()

st.header("enter your code:")
query = st.text_area(label="votre code SQL ici", key="user_input")
if query:
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

tab2, tab3 = st.tabs(["Tables", "Solution"])

with tab2:
    exercise_tables = exercise.loc[0, "tables"]
    for table in exercise_tables:
        st.write(f"table: {table}")
        df_table = con.execute(f"SELECT * FROM '{table}'").df()
        st.dataframe(df_table)

with tab3:
    st.write(answer)
