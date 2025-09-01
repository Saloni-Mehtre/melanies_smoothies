# Import required packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# App title and description
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom smoothie!")

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Input for smoothie name
name_on_order = st.text_input("Name on the smoothie:")
st.write("The name on the smoothie will be", name_on_order)

# Load fruit options from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()

# Display fruit options
st.dataframe(pd_df)

# Create a list of fruit names for selection
fruit_list = pd_df['FRUIT_NAME'].tolist()

# Multiselect for ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_list,
    max_selections=5
)

# Initialize ingredients string
ingredients_string = ''

# If fruits are selected
if ingredients_list:
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        
        
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        #st.write('The search value for ', fruit_chosen,' is ', search_on, '.')


        st.subheader(f"{fruit_chosen} Nutrition Information")
        fruityvice_response = requests.get( f"https://fruityvice.com/api/fruit/"+search_on)
        fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)


        # Check API response
        if fruityvice_response.status_code == 200:
            st.dataframe(data=fruityvice_response.json(), use_container_width=True)
        else:
            st.error(f"Could not fetch data for {fruit_chosen}. Please check the SEARCH_ON value.")

    # Show final ingredients string
    st.write("Your smoothie will contain:", ingredients_string.strip())

    # Prepare SQL insert statement
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients)
        VALUES ('{ingredients_string.strip()}')
    """

    # Submit button
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'✅ Your Smoothie is ordered, {name_on_order}!')
