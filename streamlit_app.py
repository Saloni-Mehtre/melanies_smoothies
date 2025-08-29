# Import python packages
import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom smoothie!")

# Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Name input
name_on_order = st.text_input("Name on the smoothie:")
st.write("The name on the smoothie will be", name_on_order)

# Get fruit options from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
st.dataframe(data=my_dataframe, use_container_width=True)

# Define ingredients_string before the if block
ingredients_string = ''

# Multiselect for ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe,
    max_selections=5
)

# If fruits selected
if ingredients_list:
    ingredients_string = ''
    nutrition_data = []  # collect all fruit info

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        st.subheader(fruit_chosen + ' Nutrition Information')

        # API call
        smoothiefroot_response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/" + fruit_chosen
        )
        fruit_data = smoothiefroot_response.json()

        # Ensure fruit name is included in table
        if isinstance(fruit_data, dict):
            fruit_data["fruit"] = fruit_chosen
            nutrition_data.append(fruit_data)

    # Show nutrition table once
    if nutrition_data:
        sf_df = pd.DataFrame(nutrition_data)
        st.dataframe(data=sf_df, use_container_width=True)

    # Show selected ingredients
    st.write(ingredients_string)

    # Insert into Snowflake
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients)
                values ('""" + ingredients_string.strip() + """')"""

    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'✅ Your Smoothie is ordered, {name_on_order}!')

