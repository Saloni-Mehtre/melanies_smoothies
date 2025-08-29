# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
  """Choose the fruits you want in your custom smoothie!
  """
)

import streamlit as st
cnx = st.connection("snowflake")
session = cnx.session()
name_on_order = st.text_input("Name on the smoothie:")
st.write("The name on the smoothie will be", name_on_order)

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
st.dataframe(data=my_dataframe, use_container_width=True)

# Define ingredients_string before the if block
ingredients_string = ''

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
     my_dataframe,
    max_selections= 5
)

if ingredients_list:
    ingredients_string = ''
    
    for fruit_chosen in ingredients_list:  
        ingredients_string += fruit_chosen + ' '
        
    st.write(ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients)
                values ('""" + ingredients_string.strip() + """')"""


    time_to_insert = st.button('Submit Order')
    if time_to_insert:
         session.sql(my_insert_stmt).collect()
         st.success(f'✅ Your Smoothie is ordered, {name_on_order}!')

import requests
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
#st.text(smoothiefroot_response.json())
sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
