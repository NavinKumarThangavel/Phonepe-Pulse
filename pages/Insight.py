import streamlit as st
import sqlite3
import pandas as pd
import json
import plotly.express as px

#It will setup tab information in browers
st.set_page_config(
    page_title="Phonepe Pulse",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded")

#connecting to SQLITE DB
conn = sqlite3.connect('phonepeplus.db')

#Intialize Transaction,User,Insurance dropdown information
initial_Transaction_State = pd.read_sql(sql='SELECT * FROM Transaction_state',con=conn)
initial_User_state = pd.read_sql(sql='SELECT * FROM User_state',con=conn)
initial_Insurance_State = pd.read_sql(sql='SELECT * FROM Insurance_State',con=conn)

def get_year(category):
    if category=='Transaction':
        return initial_Transaction_State['Year'].unique()
    elif category=='User':
        return initial_User_state['Year'].unique()
    else:
        return initial_Insurance_State['Year'].unique()

def get_quarter(category,year):
    if category=='Transaction':
        return initial_Transaction_State.query(f'Year =="{year}"')['Quarter'].unique()
    elif category=='User':
        return initial_User_state.query(f'Year =="{year}"')['Quarter'].unique()
    else:
        return initial_Insurance_State.query(f'Year =="{year}"')['Quarter'].unique()

def format_cash(amount):
    def truncate_float(number, places):
        return int(number * (10 ** places)) / 10 ** places

    if amount < 1e3:
        return amount

    if 1e3 <= amount < 1e5:
        return str(truncate_float((amount / 1e5) * 100, 2)) + " K"

    if 1e5 <= amount < 1e7:
        return str(truncate_float((amount / 1e7) * 100, 2)) + " L"

    if amount > 1e7:
        return str(truncate_float(amount / 1e7, 2)) + " Cr"


india_state = json.load(open("states_india.geojson", "r"))

def load_barchart(question,input_sql):
    st.subheader(question)
    input_chart_df = pd.read_sql(sql=input_sql, con=conn)
    st.bar_chart(input_chart_df, x=input_chart_df.columns[0], y=input_chart_df.columns[1], color="#500879")

def geojson_info():
    for feature in india_state['features']:
        if feature['properties']['st_nm'] == 'Dadara & Nagar Havelli':
            feature['properties']['st_nm'] = 'Dadra & Nagar Haveli & Daman & Diu'
        # elif feature['properties']['st_nm'] == 'Daman & Diu':
        #     india_state['features'].remove(feature)


geojson_info()

st.header('📊:violet[ Phonepe Pulse Data Visualization and Exploration:]')
st.sidebar.page_link("Home.py", label=":orange[🏠Home]")
with st.sidebar:
    category = ['Transaction','User','Insurance']
    selected_category = st.selectbox(':orange[Category]', category)
    selected_year = st.selectbox(':orange[Year]', get_year(selected_category))
    selected_quarter = st.selectbox(':orange[Quarter]', ['Q'+str(i) for i in get_quarter(selected_category,selected_year)]).strip('Q')

with st.container(height=500):
    state_id_map = {}
    for feature in india_state['features']:
        feature['id'] = feature['properties']['state_code']
        state_id_map[feature['properties']['st_nm']] = feature['id']

    if selected_category == 'User':
        map_user_state = pd.read_sql(sql=f'''SELECT * 
                                             FROM User_state 
                                             WHERE Year={selected_year} 
                                             AND Quarter={selected_quarter}''', con=conn)
        map_user_state['Id'] = map_user_state['State'].apply(lambda x: state_id_map[x])
        input_df = map_user_state
        input_color = "RegisteredUsers"
    elif selected_category == 'Insurance':
        map_insurance_state= pd.read_sql(sql=f'''SELECT * 
                                                 FROM Insurance_State 
                                                 WHERE Year={selected_year} 
                                                 AND Quarter={selected_quarter}''', con=conn)
        map_insurance_state['Id'] = map_insurance_state['State'].apply(lambda x: state_id_map[x])
        input_df = map_insurance_state
        input_color = "Count"
    else:
        map_transaction_state = pd.read_sql(sql=f'''SELECT * 
                                                    FROM Transaction_state
                                                    WHERE Year={selected_year} 
                                                    AND Quarter={selected_quarter}''', con=conn)
        map_transaction_state['Id'] = map_transaction_state['State'].apply(lambda x: state_id_map[x])
        input_df = map_transaction_state
        input_color = "Transactioncount"

    st.subheader(f''':violet[{selected_category} {selected_year} Q{selected_quarter}]''')
    fig = px.choropleth(input_df, locations='Id', geojson=india_state, color=f'{input_color}',
                        color_continuous_scale="Magma",
                        hover_name="State")
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout( height=400, width=900, margin=dict(
                          l=0,
                          r=0,
                          b=0,
                          t=0
                      ))
    st.plotly_chart(fig,use_container_width=True,theme=None)

with st.container(height=500):
    col1, col2 = st.columns([0.50, 0.50], gap='small')
    if selected_category == 'User':
        with col1:
            st.header(body=":violet[Users]", divider='rainbow')
            User_detail = pd.read_sql(sql=f'''SELECT sum(RegisteredUsers)RegisteredUsers,
                                                     sum(AppOpens)AppOpens 
                                              FROM User_state
                                              WHERE Year<"{selected_year}" or (Year="{selected_year}" 
                                              AND Quarter<={selected_quarter})''', con=conn)
            st.subheader(f''':violet[Registered PhonePe users till {'Q' + selected_quarter} {selected_year}]''')
            st.subheader(User_detail['RegisteredUsers'].iloc[0])
            st.subheader(f''':violet[PhonePe app opens in {'Q' + selected_quarter} {selected_year}]''')
            st.subheader(User_detail['AppOpens'].iloc[0])

        with col2:
            col1, col2, col3 = st.columns([0.30, 0.33, 0.37], gap='small')
            with col1:
                is_State = st.button(":orange[State]", use_container_width=True, type="primary")
            with col2:
                is_District = st.button(":orange[District]", use_container_width=True, type="primary")
            with col3:
                is_Pincode = st.button(":orange[Pincode]", use_container_width=True, type="primary")

            with st.container(height=400):
                if is_District:
                    user_items = pd.read_sql(sql=f'''SELECT DistrictName Field1,
                                                            RegisteredUsers Field2 
                                                     FROM Top_User_District
                                                     WHERE Year="{selected_year}" and Quarter<={selected_quarter}
                                                     ORDER BY RegisteredUsers desc
                                                     LIMIT 10''', con=conn)

                elif is_Pincode:
                    user_items = pd.read_sql(sql=f'''SELECT Pincodes Field1,
                                                            RegisteredUsers Field2 
                                                      FROM Top_User_Pincode
                                                      WHERE Year="{selected_year}" and Quarter<={selected_quarter}
                                                      ORDER BY RegisteredUsers desc
                                                      LIMIT 10''', con=conn)

                else:
                    user_items = pd.read_sql(sql=f'''SELECT State Field1,
                                                            RegisteredUsers Field2 
                                                      FROM User_state
                                                      WHERE Year="{selected_year}" and Quarter<={selected_quarter}
                                                      ORDER BY RegisteredUsers desc
                                                      LIMIT 10''', con=conn)

                for index, row in user_items.iterrows():
                    col1, col2 = st.columns([0.5, 0.5], gap='small')
                    with col1:
                        st.text(row["Field1"].capitalize())
                    with col2:
                        st.text(row["Field2"])
    elif selected_category == 'Insurance':
        with col1:
            st.header(body=":violet[Insurance]", divider='rainbow')
            Insurance_detail = pd.read_sql(sql=f'''SELECT SUM(Count)Policies,
                                                          SUM(amount)Premium,
                                                          round(SUM(amount)/SUM(Count),0) Avg 
                                                    FROM Insurance_State
                                                    WHERE Year<"{selected_year}" or (Year="{selected_year}" 
                                                    AND Quarter<={selected_quarter})''', con=conn)
            st.subheader(f''':violet[All India Insurance Policies Purchased (Nos.)]''')
            st.subheader(Insurance_detail['Policies'].iloc[0])
            st.subheader(f''':violet[Total premium value]''')
            st.subheader(format_cash(Insurance_detail['Premium'].iloc[0]))
            st.subheader(f''':violet[Average premium value]''')
            st.subheader(format_cash(Insurance_detail['Avg'].iloc[0]))
        with col2:
            with st.container():
                col1, col2, col3 = st.columns([0.30, 0.33, 0.37], gap='small')
                with col1:
                    is_State = st.button(":orange[State]", use_container_width=True, type="primary")
                with col2:
                    is_District = st.button(":orange[District]", use_container_width=True, type="primary")
                with col3:
                    is_Pincode = st.button(":orange[Pincode]", use_container_width=True, type="primary")

            with st.container(height=400):
                if is_District:
                    insurance_items = pd.read_sql(sql=f'''SELECT DistrictName Field1
                                                                 ,Amount Field2 
                                                          FROM Top_Insurance_District
                                                          WHERE Year="{selected_year}" and Quarter={selected_quarter}
                                                          ORDER BY Amount desc
                                                          LIMIT 10''', con=conn)

                elif is_Pincode:
                    insurance_items = pd.read_sql(sql=f'''SELECT Pincodes Field1,
                                                                 Amount Field2 
                                                          FROM Top_Insurance_Pincode
                                                          WHERE Year="{selected_year}" 
                                                          AND Quarter={selected_quarter}
                                                          ORDER BY Amount desc
                                                          LIMIT 10''', con=conn)

                else:
                    insurance_items = pd.read_sql(sql=f'''SELECT State Field1,
                                                                 Amount Field2 
                                                          FROM INSURANCE_STATE
                                                          WHERE Year="{selected_year}" 
                                                          AND Quarter={selected_quarter}
                                                          ORDER BY Amount desc
                                                          LIMIT 10''', con=conn)

                for index, row in insurance_items.iterrows():
                    col1, col2 = st.columns([0.5, 0.5], gap='small')
                    with col1:
                        st.text(row["Field1"].capitalize())
                    with col2:
                        st.text(format_cash(row["Field2"]))

    else:
        with col1:
            st.header(body=":violet[Transactions]", divider='rainbow')
            transaction_detail = pd.read_sql(sql=f'''SELECT round(sum(Transactionamount),0) Total_payment_Value,
                                                            round(sum(Transactionamount)/sum(Transactioncount),0)Avg_transaction_Value
                                                     FROM Transaction_state
                                                     WHERE Year="{selected_year}" 
                                                     AND Quarter={selected_quarter}
                                                     GROUP BY Year, Quarter''', con=conn)
            st.subheader(":violet[Total payment Value]")
            st.subheader(format_cash(transaction_detail['Total_payment_Value'].iloc[0]))
            st.subheader(":violet[Avg.transaction Value]")
            st.subheader(format_cash(transaction_detail['Avg_transaction_Value'].iloc[0]))
        with col2:
            with st.container():
                col1, col2, col3 = st.columns([0.30, 0.33, 0.37], gap='small')
                with col1:
                    is_State = st.button(":orange[State]", use_container_width=True, type="primary")
                with col2:
                    is_District = st.button(":orange[District]", use_container_width=True, type="primary")
                with col3:
                    is_Pincode = st.button(":orange[Pincode]", use_container_width=True, type="primary")

            with st.container(height=400):
                if is_District:
                    transaction_items = pd.read_sql(sql=f'''SELECT DistrictName Field1,
                                                                   Amount Field2 
                                                            FROM Top_Transaction_District
                                                            WHERE Year="{selected_year}" 
                                                            AND Quarter={selected_quarter}
                                                            ORDER BY amount desc
                                                            LIMIT 10''', con=conn)

                elif is_Pincode:
                    transaction_items = pd.read_sql(sql=f'''SELECT Pincodes Field1,
                                                                   Amount Field2
                                                            FROM Top_Transaction_Pincode
                                                            WHERE Year="{selected_year}" 
                                                            AND Quarter={selected_quarter}
                                                            ORDER BY Amount desc
                                                            LIMIT 10''', con=conn)

                else:
                    transaction_items = pd.read_sql(sql=f'''SELECT State Field1,
                                                                   Transactionamount Field2 
                                                            FROM Transaction_state
                                                            WHERE Year="{selected_year}" 
                                                            AND Quarter={selected_quarter}
                                                            ORDER BY  Transactionamount desc
                                                            LIMIT 10''', con=conn)

                for index, row in transaction_items.iterrows():
                    col1, col2 = st.columns([0.5, 0.5], gap='large')
                    with col1:
                        st.text(row["Field1"].capitalize())
                    with col2:
                        st.text(format_cash(row["Field2"]))

if selected_category == 'Transaction':
    with st.container(height=400):
        transaction_items = pd.read_sql(sql=f'''SELECT Transactiontype,
                                                        round(sum(Transactionamount),0) Transactionamount 
                                                FROM Transaction_state
                                                WHERE Year="{selected_year}" 
                                                AND Quarter={selected_quarter}
                                                GROUP BY Year, Quarter, Transactiontype
                                                ''', con=conn)
        st.header(":violet[Categories]", divider='rainbow')
        for index, row in transaction_items.iterrows():
            subcol1, subcol2 = st.columns([0.7, 0.3], gap='small')
            with subcol1:
                st.subheader(row["Transactiontype"])
            with subcol2:
                st.subheader(format_cash(row["Transactionamount"]))

#insights information
with st.container():
    st.header(body=f''':violet[Insights {selected_category}]''', divider='rainbow')

    if selected_category == 'Transaction':
        load_barchart('1.Which Category in Transaction Business Performed Best in Terms of Amount?',
                      '''SELECT Transactiontype,sum(Transactionamount)[Transaction Amount]
                                 FROM Transaction_state
                                 group by Transactiontype''')

        load_barchart('2..Which Category in Transaction Business Performed Best in Terms of nos?',
                      '''SELECT Transactiontype,sum(Transactioncount)[Transaction count]
                                 FROM Transaction_state
                                 group by Transactiontype''')

        load_barchart('3.Which Year OutPerformed in Transaction Business?',
                      '''SELECT Year,sum(Transactionamount)[Transaction Amount]
                                 FROM Transaction_state
                                 group by Year''')

        load_barchart('4.Which Quarter OutPerformed in Transaction Business?',
                      '''SELECT Year,sum(Transactionamount)[Transaction Amount]
                                 FROM Transaction_state
                                 group by Year''')

        load_barchart('5.Which District has Worst Performed in Transaction Business?',
                      '''SELECT DistrictName,Sum(Amount)Amount  
                                 FROM Transaction_District
                                 group by state,DistrictName
                                 order by 2 asc
                                 limit 10 ''')

    elif selected_category == 'User':

        load_barchart('1.Which Year OutPerformed in Registered Users?',
                      '''SELECT Year,sum(RegisteredUsers) [Registered Users]
                                 FROM User_State
                                 group by Year''')

        load_barchart('2.Which Quarter OutPerformed in Registered Users?',
                      '''SELECT 'Q'|| Quarter Quarter,sum(RegisteredUsers) [Registered Users]
                                 FROM User_State
                                 group by Quarter''')

        load_barchart('3.Which State Worst Performed in Registered Users?',
                      '''SELECT  State,sum(RegisteredUsers) [Registered Users] 
                                  FROM User_State
                                  group by State
                                 order by 2 
                                 limit 10''')

        load_barchart('4.Which Year OutPerformed in Application Opens?',
                      '''SELECT Year,sum(AppOpens) [App Opens]
                                 FROM User_State
                                 group by Year''')

        load_barchart('5.Which Quarter OutPerformed in Application Opens?',
                      '''SELECT 'Q'|| Quarter Quarter,sum(AppOpens) [App Opens]
                                 FROM User_State
                                 group by Quarter''')

        load_barchart('6.Which State Worst Performed in Application Opens?',
                      '''SELECT  State,sum(AppOpens) [App Opens] 
                                  FROM User_State
                                  group by State
                                 order by 2 
                                 limit 10''')

    else:

        load_barchart('1.Which Year OutPerformed in Insurance Business?',
                      '''SELECT Year,sum(Amount) Amount 
                                  FROM Insurance_State
                                  group by Year''')

        load_barchart('2.Which Quarter OutPerformed in Insurance Business?',
                      '''SELECT  'Q'|| Quarter Quarter,sum(Amount) Amount 
                                FROM Insurance_State
                                group by Quarter''')

        load_barchart('3.Which State Worst Performed in Insurance Business?',
                      '''SELECT  State,sum(Amount) Amount 
                                  FROM Insurance_State
                                  group by State
                                  order by 2 
                                  limit 10''')

        load_barchart('4.Which Year OutPerformed in Insurance Policies?',
                      '''SELECT Year,sum(Count) [No of Policies] 
                                  FROM Insurance_State
                                  group by Year''')

        load_barchart('5.Which Quarter OutPerformed in Insurance Policies?',
                      '''SELECT  'Q'|| Quarter Quarter,sum(Count) [No of Policies] 
                                FROM Insurance_State
                                group by Quarter''')

        load_barchart('6.Which State Worst Performed in Insurance Policies?',
                      '''SELECT  State,sum(Count) [No of Policies] 
                                  FROM Insurance_State
                                  group by State
                                  order by 2 
                                  limit 10''')

