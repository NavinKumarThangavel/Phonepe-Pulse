import streamlit as st
import sqlite3
import pandas as pd
import json
import os

st.set_page_config(
    page_title="Phonepe Pulse",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded")

st.header('📊:violet[ Phonepe Pulse Data Visualization and Exploration:]')
conn = sqlite3.connect('phonepeplus.db')

# with st.container():
st.subheader('About Pulse:')
st.text('''
The Indian digital payments story has truly captured the world's imagination. 
        
From the largest towns to the remotest villages, there is a payments revolution being driven by
the penetration of mobile phones and data.  
          
PhonePe Pulse is your window to the world of how India transacts with interesting trends, 
deep insights and in-depth analysis based on our data put together by the PhonePe team.''')

#Intialize variable
root_path = "pulse/data/"
root_directory_list = os.listdir(root_path)
transaction_state = {'State': [], 'Year': [], 'Quarter': [], 'Transactiontype': [], 'Transactioncount': [],
                     'Transactionamount': []}
user_state = {'State': [], 'Year': [], 'Quarter': [], 'RegisteredUsers': [], 'AppOpens': []}
user_brand_state = {'State': [], 'Year': [], 'Quarter': [], 'Brand': [], 'Count': [], 'Percentage': []}
insurance_state = {'State': [], 'Year': [], 'Quarter': [], 'Name': [], 'Count': [], 'Amount': []}
transaction_distict = {'State': [], 'Year': [], 'Quarter': [], 'DistrictName': [], 'Count': [], 'Amount': []}
user_distict = {'State': [], 'Year': [], 'Quarter': [], 'DistrictName': [], 'RegisteredUsers': [], 'AppOpens': []}
insurance_distict = {'State': [], 'Year': [], 'Quarter': [], 'DistrictName': [], 'Count': [], 'Amount': []}
transaction_top_district = {'State': [], 'Year': [], 'Quarter': [], 'DistrictName': [], 'Count': [], 'Amount': []}
transaction_top_pincodes = {'State': [], 'Year': [], 'Quarter': [], 'Pincodes': [], 'Count': [], 'Amount': []}
user_top_district = {'State': [], 'Year': [], 'Quarter': [], 'DistrictName': [], 'RegisteredUsers': []}
user_top_pincodes = {'State': [], 'Year': [], 'Quarter': [], 'Pincodes': [], 'RegisteredUsers': []}
insurance_top_district = {'State': [], 'Year': [], 'Quarter': [], 'DistrictName': [], 'Count': [], 'Amount': []}
insurance_top_pincodes = {'State': [], 'Year': [], 'Quarter': [], 'Pincodes': [], 'Count': [], 'Amount': []}


def transaction_state_wise(info, state, year, quarter):
    for z in info['data']['transactionData']:
        transaction_state['Transactiontype'].append(z['name'])
        transaction_state['Transactioncount'].append(z['paymentInstruments'][0]['count'])
        transaction_state['Transactionamount'].append(z['paymentInstruments'][0]['amount'])
        transaction_state['State'].append(state)
        transaction_state['Year'].append(year)
        transaction_state['Quarter'].append(quarter)


def users_state_wise(info, state, year, quarter):
    user_state['RegisteredUsers'].append(info['data']['aggregated']['registeredUsers'])
    user_state['AppOpens'].append(info['data']['aggregated']['appOpens'])
    user_state['State'].append(state)
    user_state['Year'].append(year)
    user_state['Quarter'].append(quarter)
    if info['data']['usersByDevice'] != None:
        for info in info['data']['usersByDevice']:
            user_brand_state['Brand'].append(info['brand'])
            user_brand_state['Count'].append(info['count'])
            user_brand_state['Percentage'].append(info['percentage'])
            user_brand_state['State'].append(state)
            user_brand_state['Year'].append(year)
            user_brand_state['Quarter'].append(quarter)


def insurance_state_wise(info, state, year, quarter):
    for z in info['data']['transactionData']:
        insurance_state['Name'].append(z['name'])
        insurance_state['Count'].append(z['paymentInstruments'][0]['count'])
        insurance_state['Amount'].append(z['paymentInstruments'][0]['amount'])
        insurance_state['State'].append(state)
        insurance_state['Year'].append(year)
        insurance_state['Quarter'].append(quarter)


def transaction_district_wise(info, state, year, quarter):
    for z in info['data']['hoverDataList']:
        transaction_distict['DistrictName'].append(z['name'].replace('district', ''))
        transaction_distict['Count'].append(z['metric'][0]['count'])
        transaction_distict['Amount'].append(z['metric'][0]['amount'])
        transaction_distict['State'].append(state)
        transaction_distict['Year'].append(year)
        transaction_distict['Quarter'].append(quarter)


def users_district_wise(info, state, year, quarter):
    for z in info['data']['hoverData'].keys():
        user_distict['DistrictName'].append(z.replace('district', ''))
        user_distict['RegisteredUsers'].append(info['data']['hoverData'][z]['registeredUsers'])
        user_distict['AppOpens'].append(info['data']['hoverData'][z]['appOpens'])
        user_distict['State'].append(state)
        user_distict['Year'].append(year)
        user_distict['Quarter'].append(quarter)


def insurance_district_wise(info, state, year, quarter):
    for z in info['data']['hoverDataList']:
        insurance_distict['DistrictName'].append(z['name'].replace('district', ''))
        insurance_distict['Count'].append(z['metric'][0]['count'])
        insurance_distict['Amount'].append(z['metric'][0]['amount'])
        insurance_distict['State'].append(state)
        insurance_distict['Year'].append(year)
        insurance_distict['Quarter'].append(quarter)


def transaction_pincode_wise(info, state, year, quarter):
    for z in info['data']['districts']:
        transaction_top_district['DistrictName'].append(z['entityName'])
        transaction_top_district['Count'].append(z['metric']['count'])
        transaction_top_district['Amount'].append(z['metric']['amount'])
        transaction_top_district['State'].append(state)
        transaction_top_district['Year'].append(year)
        transaction_top_district['Quarter'].append(quarter)
    if "pincodes" in info['data']:
        for z in info['data']['pincodes']:
            transaction_top_pincodes['Pincodes'].append(z['entityName'])
            transaction_top_pincodes['Count'].append(z['metric']['count'])
            transaction_top_pincodes['Amount'].append(z['metric']['amount'])
            transaction_top_pincodes['State'].append(state)
            transaction_top_pincodes['Year'].append(year)
            transaction_top_pincodes['Quarter'].append(quarter)


def users_pincode_wise(info, state, year, quarter):
    for z in info['data']['districts']:
        user_top_district['DistrictName'].append(z['name'])
        user_top_district['RegisteredUsers'].append(z['registeredUsers'])
        user_top_district['State'].append(state)
        user_top_district['Year'].append(year)
        user_top_district['Quarter'].append(quarter)
    if "pincodes" in info['data']:
        for z in info['data']['pincodes']:
            user_top_pincodes['Pincodes'].append(z['name'])
            user_top_pincodes['RegisteredUsers'].append(z['registeredUsers'])
            user_top_pincodes['State'].append(state)
            user_top_pincodes['Year'].append(year)
            user_top_pincodes['Quarter'].append(quarter)


def insurance_pincode_wise(info, state, year, quarter):
    for z in info['data']['districts']:
        insurance_top_district['DistrictName'].append(z['entityName'])
        insurance_top_district['Count'].append(z['metric']['count'])
        insurance_top_district['Amount'].append(z['metric']['amount'])
        insurance_top_district['State'].append(state)
        insurance_top_district['Year'].append(year)
        insurance_top_district['Quarter'].append(quarter)
    if "pincodes" in info['data']:
        for z in info['data']['pincodes']:
            insurance_top_pincodes['Pincodes'].append(z['entityName'])
            insurance_top_pincodes['Count'].append(z['metric']['count'])
            insurance_top_pincodes['Amount'].append(z['metric']['amount'])
            insurance_top_pincodes['State'].append(state)
            insurance_top_pincodes['Year'].append(year)
            insurance_top_pincodes['Quarter'].append(quarter)

def mapping_state_name(state):
    state = state.replace('-', ' ').title()
    if (state == 'Arunachal Pradesh'):
        state = 'Arunanchal Pradesh'
    elif (state == 'Delhi'):
        state = 'NCT of Delhi'
    elif (state == 'Andaman & Nicobar Islands'):
        state = 'Andaman & Nicobar Island'
    elif (state == 'Ladakh'):
        state = 'Daman & Diu'
    return state


def readfile_store(root_path):
    for i in root_directory_list:
        p_i = root_path + i + "/"
        category_directory_list = os.listdir(p_i)
        for j in category_directory_list:
            subfolder = "/hover" if i == 'map' and j in ['transaction', 'user', 'insurance'] else ''
            p_j = p_i + j + subfolder + "/country/india/state/"
            Agg_state_list = os.listdir(p_j)
            for k in Agg_state_list:
                p_k = p_j + k + "/"
                Agg_year_list = os.listdir(p_k)
                for l in Agg_year_list:
                    p_l = p_k + l + "/"
                    Agg_file_list = os.listdir(p_l)
                    for m in Agg_file_list:
                        p_m = p_l + m
                        Data = open(p_m, 'r')
                        n = int(m.strip('.json'))
                        json_data = json.load(Data)
                        if i == 'aggregated':
                            if j == 'transaction':
                                transaction_state_wise(json_data, k, l, n)
                            elif j == 'user':
                                users_state_wise(json_data, k, l, n)
                            else:
                                insurance_state_wise(json_data, k, l, n)
                        elif i == 'map':
                            if j == 'transaction':
                                transaction_district_wise(json_data, k, l, n)
                            elif j == 'user':
                                users_district_wise(json_data, k, l, n)
                            else:
                                insurance_district_wise(json_data, k, l, n)
                        else:
                            if j == 'transaction':
                                transaction_pincode_wise(json_data, k, l, n)
                            elif j == 'user':
                                users_pincode_wise(json_data, k, l, n)
                            else:
                                insurance_pincode_wise(json_data, k, l, n)

if st.button(label=":orange[Extract Data]", type="primary"):
    readfile_store(root_path)

    #converting Dictionary to Dataframe
    agg_trans = pd.DataFrame(transaction_state)
    agg_trans['State'] = agg_trans['State'].apply(lambda x: mapping_state_name(x))
    agg_user = pd.DataFrame(user_state)
    agg_user['State'] = agg_user['State'].apply(lambda x: mapping_state_name(x))
    agg_user_brand = pd.DataFrame(user_brand_state)
    agg_user_brand['State'] = agg_user_brand['State'].apply(lambda x: mapping_state_name(x))
    agg_insurance = pd.DataFrame(insurance_state)
    agg_insurance['State'] = agg_insurance['State'].apply(lambda x: mapping_state_name(x))
    map_trans = pd.DataFrame(transaction_distict)
    map_users = pd.DataFrame(user_distict)
    map_insurance = pd.DataFrame(insurance_distict)
    top_insurance_pincode = pd.DataFrame(insurance_top_pincodes)
    top_user_pincode = pd.DataFrame(user_top_pincodes)
    top_trans_pincode = pd.DataFrame(transaction_top_pincodes)
    top_insurance_district = pd.DataFrame(insurance_top_district)
    top_user_district = pd.DataFrame(user_top_district)
    top_trans_district = pd.DataFrame(transaction_top_district)

    #Dataframe inside into table
    agg_trans.to_sql(name='Transaction_State', con=conn, if_exists='replace', index=False)
    agg_user.to_sql(name='User_state', con=conn, if_exists='replace', index=False)
    agg_user_brand.to_sql(name='User_Brand_State', con=conn, if_exists='replace', index=False)
    agg_insurance.to_sql(name='Insurance_State', con=conn, if_exists='replace', index=False)
    map_trans.to_sql(name='Transaction_District', con=conn, if_exists='replace', index=False)
    map_users.to_sql(name='User_District', con=conn, if_exists='replace', index=False)
    map_insurance.to_sql(name='Insurance_District', con=conn, if_exists='replace', index=False)
    top_insurance_pincode.to_sql(name='Top_Insurance_Pincode', con=conn, if_exists='replace', index=False)
    top_trans_pincode.to_sql(name='Top_Transaction_Pincode', con=conn, if_exists='replace', index=False)
    top_user_pincode.to_sql(name='Top_User_Pincode', con=conn, if_exists='replace', index=False)
    top_insurance_district.to_sql(name='Top_Insurance_District', con=conn, if_exists='replace', index=False)
    top_trans_district.to_sql(name='Top_Transaction_District', con=conn, if_exists='replace', index=False)
    top_user_district.to_sql(name='Top_User_District', con=conn, if_exists='replace', index=False)

st.caption('Update New information Every Quarter through this Button 👆')
st.sidebar.page_link("pages/Insight.py", label=":orange[🎯Business Insight]")
