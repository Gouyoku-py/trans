import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import json

st.title('Ιστορικό Κινήσεων Υλικών ΚΑ')

@st.cache_data
def load_trans_type_data():
    data = pd.read_excel('trans_types.xlsx', names = ['trans_type', 'trans_descr'], index_col = 'trans_type')
    return data
    
@st.cache_data
def load_trans_col_names():
    with open('trans_col_names.txt', 'r', encoding = 'utf-8') as f:
        data = json.loads(f.read())
    return data

@st.cache_data
def load_trans_data():
    data = pd.read_excel('trans.xlsx', names = trans_col_names.values(), index_col = 'code', 
                         converters = {'Κέντρο Κόστους': str}, parse_dates = ['date'])
    return data

trans_types = load_trans_type_data()

trans_col_names = load_trans_col_names()

trans = load_trans_data()
trans.drop(columns = ['date0', 'user', 'descr', 'res_id'], inplace = True)
trans.query('date < "2023-02-20"', inplace = True)
trans.insert(1, 'trans_descr', trans['trans_type'].apply(lambda x: trans_types.loc[x]))
trans.sort_values(['code', 'date', 'trans_type'], inplace = True)

new_date_range = pd.date_range(start = "1998-12-31", end = "2022-12-31", freq = 'Y')

#def make_pretty(styler):
#    styler.format_index(lambda x: x.strftime("%Y-%m-%d"))
#    return styler

def f(x):
    x = int(x)
    y = trans.query('code == @x').set_index('date')
    y_unit = y['unit'].unique()[0]
    y_q = y['quantity'].copy(deep = True)

    y_df = pd.concat([y_q.where(y_q > 0), y_q.where(y_q < 0)], axis = 1)
    y_df.columns = ['Εισαγωγή σε ΚΑ', 'Εξαγωγή από ΚΑ']

    freq = 'Y'
    y_df = y_df.resample(freq, closed = 'right', label = 'right').sum()

    new_date_range = pd.date_range(start = "1998-12-31", end = "2022-12-31", freq = freq)
    y_df = y_df.reindex(new_date_range, fill_value = 0)
    y_df.index = y_df.index.year

    fig_i, ax_i = plt.subplots()
    y_df.plot(kind = 'bar', ax = ax_i, title = 'Κινήσεις υλικού {}'.format(x), grid = True, 
              xlabel = 'Έτος', ylabel = 'Ποσότητα / {}'.format(y_unit), rot = 45, color = ['C2', 'C3'])
    ax_i.axhline(y = 0, c = 'k', ls = '--', lw = 1.0)
    
    y.fillna('-', inplace = True)
    y.index = y.index.strftime('%d/%m/%Y')
    y['cost_center'] = y['cost_center'].apply(lambda x: int(x) if isinstance(x, float) else x)
    y['value'] = y['value'].apply(lambda x: '{:,.1f} €'.format(x))
    
    y.columns = ['ΚΙΝ.', 'ΠΕΡΙΓΡΑΦΗ', 'Κ.Κ.', 'ΕΝΤ.', 'WBS', 'ΠΟΣ.', 'ΜΟΝ.', 'ΑΞΙΑ', 'ΠΑΡΑΛΗΠΤΗΣ']
    
    st.pyplot(fig_i)
    #st.dataframe(y.style.pipe(make_pretty))
    st.dataframe(y, use_container_width = True)
     
    return None

code = st.selectbox('Κωδικός', trans.index.unique(), key = 'code', help = '')

f(code)