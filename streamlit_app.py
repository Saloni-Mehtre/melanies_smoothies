# Import python packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col

# -------------------------
# Streamlit UI
# -------------------------
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom smoothie!"""
)

# -------------------------
# Snowflake Connection
# -------------------------
cnx = st.connection("snowflake")
session = cnx.session()

# Name input
name_on_order = st.text_input("Name on the smoothie:")
st.write("The name on the smoothie will be", name_on_order)

# Get fruit options from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
st.dataframe(data=my_dataframe, use_container_width=True)

# -------------------------
# Fruit selection
# -------------------------
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe,
    max_selections=5
)

ingredients_string = ''  # will hold selected fruits

# -------------------------
# Show Nutrition Information
# -------------------------
if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)

    nutrition_data = []  # collect all nutrition info

    for fruit_chosen in ingredients_list:
        st.subheader(fruit_chosen + ' Nutrition Information')

        # API call for nutrition info
        smoothiefroot_response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/" + fruit_chosen
        )

        # Add the JSON response to list
        fruit_data = smoothiefroot_response.json()
        nutrition_data.append(fruit_data)

        # Show each fruit's data (optional)
        st.json(fruit_data)

    st.write("Your chosen ingredients:", ingredients_string)

    # -------------------------
    # Save order in Snowflake
    # -------------------------
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients)
        VALUES ('{ingredients_string.strip()}')
    """

    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'✅ Your Smoothie is ordered, {name_on_order}!')
