# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Write directly to the app
st.title(":cup_with_straw: Customize your Smoothie! :cup_with_straw:")
st.write(
    f"""Check the fruits you want in your custom Smoothie!
    """
)
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your smoothie will be:",name_on_order)

cnx= st.connection("snowflake")
session = cnx.session()

my_dataframe = session.table("smoothies.public.fruit_options").select(col('Fruit_name'),col('search_on'))

pd_df = my_dataframe.to_pandas()
st.dataframe(pd_df)

ingredients_list = st.multiselect(
    'choose upto 5 ingredients:',
    my_dataframe   ,
    max_selections= 5
)
if ingredients_list :
    ingredients_String = ''
    for fruit_chosen in ingredients_list:
        ingredients_String += fruit_chosen +' '
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write(f'The search value for {fruit_chosen} is {search_on} .')
        url = "https://my.smoothiefroot.com/api/fruit/all"
        response = requests.get(url)
    
        if response.status_code == 200:
        all_fruit_data = response.json()  # Convert API response to JSON
        
        for fruit_chosen in ingredients_list:
            ingredients_String += fruit_chosen + ' '

            # Filter the API response to get only the selected fruit details
            fruit_data = [fruit for fruit in all_fruit_data if fruit['name'].lower() == fruit_chosen.lower()]

            if fruit_data:
                st.subheader(fruit_chosen + ' Nutrition Information')
                df = pd.DataFrame(fruit_data)  # Convert selected fruit details to DataFrame
                st.dataframe(df, use_container_width=True)
            else:
                st.error(f"Sorry, {fruit_chosen} is not found in the database.")
    else:
        st.error(f"API Request Failed! Status Code: {response.status_code}")

    
               
        st.subheader(fruit_chosen +' Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/all" + fruit_chosen )
        #st.text(smoothiefroot_response.json())
        sf_df = st.dataframe(data = smoothiefroot_response.json(), use_container_width= True)

   
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
            values ('""" +ingredients_String+"""','"""+name_on_order+"""')"""
    time_to_insert = st.button("Submit Orders")
    

    st.write(my_insert_stmt)
if time_to_insert:
    session.sql(my_insert_stmt).collect()
    st.success(f"Your smoothie is ordered !{name_on_order}", icon= "✅")
    
        
        
       
