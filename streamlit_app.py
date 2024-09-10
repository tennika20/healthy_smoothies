# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd
import streamlit.components.v1 as components

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie!
    """)

name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))
# st.dataframe(data=my_dataframe, use_container_width=True)
# st.stop()

# Convert the Snowflake Dataframe to a Pandas Dataframe so we can use the LOC function
pd_df = my_dataframe.to_pandas()
# st.dataframe(pd_df)


ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:'
    , my_dataframe
    , max_selections=5
    )

if ingredients_list:

    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        # st.write('The search value for ', fruit_chosen,' is', search_on, '.')
        
        st.subheader(fruit_chosen + ' Nurition Information (Serving Per 100g)')
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + search_on)
        
       # a = []
       # a.append(fruityvice_response.json())
       # st.write(fruityvice_response.json())
       # st.write(a)
       # fv = pd.DataFrame(a, columns = ['nutritions'])
        fvv = pd.DataFrame(fruityvice_response.json(), columns = ['nutritions'])
        
       # st.write(fv)
       # st.write(fvv)
        components.html(fvv.to_html(header=False))
       # st.write(pd.json_normalize(a["nutritions"]))
       # fv_nut = pd.json_normalize(fv["labels"])
       # st.write(fv_nut)
        
       # fv_2=fv.drop(columns=['family'])
       # fv_df_2 = st.dataframe(data=fv_nut, use_container_width=True)
        

    #st.write(ingredients_string)

    my_insert_stmt = """insert into smoothies.public.orders(ingredients, name_on_order)
            values ('""" + ingredients_string + """', '""" + name_on_order + """')"""

    #st.write(my_insert_stmt)
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        #success_message =  st.write('Your Smoothie is ordered, ', name_on_order, '!')
        st.success('''Your Smoothie is ordered, '''  + name_on_order + '''!''',  icon="✅")
