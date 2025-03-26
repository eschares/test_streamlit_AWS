# IOI Publishing Profiler - Plot only HTML graphs
# Eric Schares, 5/4/24 - 3/25/25

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
#pd.options.mode.chained_assignment = None  # default='warn'
pd.set_option('mode.chained_assignment', None)
import plotly.express as px
import plotly.graph_objects as go  # to enable total count labels on top of stacked bar chart
import requests
from tqdm import tqdm
from stqdm import stqdm
from time import sleep
import glob
import re

stqdm.pandas()

st.header('IOI Publishing Profiler - Rewrite')
st.markdown('#### Eric Schares')

with st.expander('More information:'):
    st.write('''
             This interactive dashboard helps to visualize characteristics about research publications from several universities. Using Dimensions data enriched with OpenAlex, we plot:
            
             - Count and percentages of Corresponding Authored publications
             - Count and percentages of US federally funded publications
             - Count and percentages of Corresponding Authored **AND** US federally funded publications
             - Breakdown of these by publisher, year, journal title, US funder and Open Access status
             - Deeper dive into a custom US funder of interest
             ''')

debug_flag = 0
debug_flag_savecommands = 0

institution_lookup_table = pd.read_csv('data/data_comparison_nolinks.csv', encoding='latin1')
#institution_lookup_table

# make sure these names are what appears in the Dimensions export file for Corresponding Author
institution_name_list = institution_lookup_table['Institution_name']
institution_name = st.selectbox('**Choose an Institution to Analyze**', institution_name_list)

#nospaces gets used when saving and loading filenames
names_nospaces_lookup_dict = dict(zip(institution_lookup_table['Institution_name'], institution_lookup_table['Name_no_spaces']))
#names_nospaces_lookup_dict
    #{'Iowa State University': 'ISU',
    #'William & Mary': 'WilliamandMary',
    #'West Virginia': 'WestVirginia'}

institution_name_nospaces = names_nospaces_lookup_dict[institution_name]

# OpenAlex IDs, looked up with https://api.openalex.org/institutions/ror:https://ror.org/04rswrd78?select=id,ror,display_name,country_code
institution_ids_lookup_dict  = dict(zip(institution_lookup_table['Institution_name'], institution_lookup_table['OpenAlex_ID']))
    #{'Iowa State University': 'I173911158',
    #'William & Mary': 'I16285277'}

institution_id = institution_ids_lookup_dict[institution_name]    # used in OpenAlex data enrichment for Corresponding Authors

#file_load_location_dict = dict(zip(institution_lookup_table['Institution_name'], institution_lookup_table['Drive_link']))
#file_load_location = file_load_location_dict[institution_name]

st.write(f'OpenAlex Institution ID: **{institution_id}**, using shortcut name **{institution_name_nospaces}**')# from {file_load_location}')
#st.write(f'Loading from {file_load_location}')


### Load data - do it this way so it's not re-loaded over and over again each time we save this file
@st.cache_data(ttl=1*3600)  # time to live, in seconds. Removed after 1 hour
def load_data_parquet(link, header):
   #st.write(f'Loading file **{link}**')
   df = pd.read_parquet(link, engine='pyarrow')
   return df


###### Summary ######
st.markdown('---')
st.subheader(f'Executive Summary')

file_path = f'summaries/{institution_name_nospaces}_summary.txt'
with open (file_path, 'r') as file:
    content = file.read()
    st.write(content)


###### Plots ######

plots_filepath = f'HTML_graphs/{institution_name_nospaces}'

st.markdown('---')
st.subheader(f'Corresponding Authored Records by {institution_name}, by Year')

col1, col2 = st.columns(2)

with col1:
    st.markdown('#### Raw Counts')
    #st.plotly_chart(fig)
    components.iframe(f"https://eschares.github.io/test_streamlit_AWS/HTML_graphs/{institution_name_nospaces}_fig1.html", height=500, width=400)

with col2:
    st.markdown('#### Percentages')
    #st.plotly_chart(fig2)
    components.iframe(f"https://eschares.github.io/test_streamlit_AWS/HTML_graphs/{institution_name_nospaces}_fig2.html", height=500, width=400)

# st.write('iframe')
# components.iframe("https://eschares.github.io/test_streamlit_AWS/Cary_fig.html", height=500)   # works! Github pages  Settings - Pages - Deploy
# st.write('iframe 2')
# components.iframe("https://eschares.github.io/test_streamlit_AWS/CaryInstitute_fig1_includeplotlyjs_cdn.html", height=500)   # works! Github pages  Settings - Pages - Deploy
# #https://stackoverflow.com/questions/8446218/how-to-see-an-html-page-on-github-as-a-normal-rendered-html-page-to-see-preview
# st.write('Google drive link')
# components.html("https://drive.google.com/file/d/1La34zDaXrqXH3tJIr5I37O3YFSIRAXqS/view?usp=sharing")
# st.write('components html')
# components.html("https://eschares.github.io/test_streamlit_AWS/Cary_fig.html", height=500)


st.markdown('---')
st.subheader(f'US Federally Funded Research with any {institution_name} author, by Year')
col3, col4 = st.columns(2)

with col3:
    st.subheader('Raw Counts')
    components.iframe(f"https://eschares.github.io/test_streamlit_AWS/HTML_graphs/{institution_name_nospaces}_fig3.html", height=500, width=400)

with col4:
    st.subheader('Percentages')
    components.iframe(f"https://eschares.github.io/test_streamlit_AWS/HTML_graphs/{institution_name_nospaces}_fig4.html", height=500, width=400)



st.markdown('---')
st.subheader(f'{institution_name} Corresponding Authored US Federally Funded Research, by Year')
bullet_text = ''' Legend shows many combinations of Corresponding Author and US federal funding
* **'unknown_no'** means we don't know if the CorrAuth is from the institution of interest, but it's not federally funded (available only if data ran through OpenAlex)
* **'unknown_yes'** means it **is** federally funded, but we still don't have the CorrAuth information
* **'no_no'** are publications that are neither CorrAuth by our institution or federally funded
* **'no_yes'** are publications that are not CorrAuth by the institution of interest, but *do* have federal funding
* **'yes_no'** are publications that *are* CorrAuth from the institution of interest, but not federally funded
* **['yes_yes]** *finally* the records we are interested in. CorrAuth is from the insitution and also have federal funding acknowledged
'''

st.markdown(bullet_text)

col5, col6 = st.columns(2)


with col5:
    st.subheader('Raw Counts')
    components.iframe(f"https://eschares.github.io/test_streamlit_AWS/HTML_graphs/{institution_name_nospaces}_fig5.html", height=500, width=400)

with col6:
    st.subheader('Percentages')
    components.iframe(f"https://eschares.github.io/test_streamlit_AWS/HTML_graphs/{institution_name_nospaces}_fig6.html", height=500, width=500)


#### 50% points by publisher
# base code from StackOverflow user Maarten Fabré, modified by Eric Schares
# this is VERY hardcoded to what I'm trying to do so edit carefully
# for example, I hardcode the yesyes_bypublisher['PubYear'] filter
# had to do it this way to automate the calcuation by year of number of publishers that make up 50%
def get_50_percent_passyear(year, pct=50):
    '''
    Input: year as int
    Returns: int, length of Series required to meet pct level, defaults to 50%  (example: 4)
    '''    
    group = yesyes_bypublisher[yesyes_bypublisher['PubYear']==year]
    
    # moves is one Series, in this case DOI. Descending series of counts
    moves = group['DOI'].sort_values(ascending=False)
    #print(moves)
    
    # cumsum is series of fractions, cumulatively summing each row (0.21, 0.34. 0.45, 0.56)
    cumsum = moves.cumsum() / moves.sum()
    #print(cumsum)
    
    # idx is the length of cumulative sum where it is still less than .50, then go one more
    idx = len(cumsum[cumsum < pct/100]) + 1
    #print(f'idx: {idx}\n')
    
    # `idx` is the first index which has a cumulative sum of `pct` or higher
    # so grab indexes 0 to whatever index we need
    idx = moves.index[:idx]  
    #print(f'second idx: {idx}')
    
    # here, `idx` is the Index of all the moves with a cumulative contribution of `pct` or higher
    #print(f'here is {group.loc[idx]}')
    return len(group.loc[idx].set_index(['Publisher'], drop=True)['DOI'])


st.markdown('---')
st.header(f"Further Details on the 'yes_yes' Section")
st.subheader(f'Look at {institution_name} Corresponding Authored & Federally Funded Documents')
st.subheader('Breakdown by **:red[Publisher]**')


st.subheader('By Count')

components.iframe(f"https://eschares.github.io/test_streamlit_AWS/HTML_graphs/{institution_name_nospaces}_fig8.html", height=600, width=1100)



st.subheader('By Percent')

components.iframe(f"https://eschares.github.io/test_streamlit_AWS/HTML_graphs/{institution_name_nospaces}_fig9.html", height=600, width=1000, scrolling=True)


# st.write(f"How many publishers are represented each year? How many does it take to make up 50% of {institution_name}'s CorrAuth USFF publications?")
# publisher_50percent_point = yesyes_bypublisher.groupby(['PubYear'])['Publisher'].count().reset_index()
# publisher_50percent_point.loc[:, '50percent_point'] = publisher_50percent_point.loc[ :, 'PubYear'].apply(get_50_percent_passyear)
# publisher_50percent_point.rename(columns={'Publisher': 'NumPublishers'}, inplace=True)
# publisher_50percent_point



st.markdown('---')
#st.header('Further Details on the `yes_yes` Documents (Corresponding & Federally Funded)')
st.subheader('Breakdown by **:red[Journal Title]**')

components.iframe(f"https://eschares.github.io/test_streamlit_AWS/HTML_graphs/{institution_name_nospaces}_fig10.html", height=600, width=1000)#, scrolling=True)
components.iframe(f"https://eschares.github.io/test_streamlit_AWS/HTML_graphs/{institution_name_nospaces}_fig13.html", height=800, width=1000)#, scrolling=True)





st.markdown('---')
#st.header('Further Details on the `yes_yes` Documents (Corresponding & Federally Funded)')
st.subheader('Breakdown by **:red[Funder]**')

components.iframe(f"https://eschares.github.io/test_streamlit_AWS/HTML_graphs/{institution_name_nospaces}_fig11.html", height=800, width=1000)#, scrolling=True)








# Let the user choose a funder to look at more closely. First list all the possible funders found in this set
list_of_funders = funder_totals['ParentAgency']
chosen_funder = st.selectbox('Choose a funder to investigate their credited publications in more detail', list_of_funders)

# funders_exploded is still DOI-level
chosen_funder_DOIlevel = funders_exploded[funders_exploded['ParentAgency']==chosen_funder]
chosen_funder_DOIlevel[['DOI', 'Source title', 'Publisher', 'PubYear', 'Title', 'ISSN', 'Open Access', 'Authors', 'Authors (Raw Affiliation)', 'Corresponding Authors', 'Authors Affiliations', 'Research Organizations - standardized', 'Funder', 'ParentAgency']]

chosenfunder_byjournaltitle = chosen_funder_DOIlevel.groupby(['Source title', 'PubYear', 'Publisher']).count().reset_index()[['Source title', 'PubYear', 'Publisher', 'DOI']]
#chosenfunder_byjournaltitle.astype({'PubYear':'int32'}).dtypes
chosenfunder_byjournaltitle.sort_values(by='PubYear', ascending=True, inplace=True)
if(debug_flag_savecommands):
    chosenfunder_byjournaltitle.to_csv(f'data/{institution_name_nospaces}/{institution_name_nospaces}_yesyes_chosenfunder_groupbyjournaltitle.csv', index=False)

fig12 = px.bar(chosenfunder_byjournaltitle, x='Source title', y='DOI', color='PubYear', text_auto='True',
                     title=f'{institution_name} Corresponding Authored with Funding from <br>the {chosen_funder}, by Journal Title and Year',
                     category_orders={'PubYear': [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]})
fig12.update_xaxes(categoryorder='total descending', maxallowed=maxallowed)
fig12.update_layout(height=1000, showlegend=True, legend_traceorder='reversed')
st.plotly_chart(fig12)



chosenfunder_byjournal_and_OA = chosen_funder_DOIlevel.groupby(['Source title', 'PubYear', 'Open Access']).count().reset_index()[['Source title', 'PubYear', 'Open Access', 'DOI']]
chosenfunder_byjournal_and_OA.sort_values(by='PubYear', ascending=True, inplace=True)
if(debug_flag_savecommands):
    chosenfunder_byjournal_and_OA.to_csv(f'data/{institution_name_nospaces}/{institution_name_nospaces}_yesyes_chosenfunder_groupbyjournal_and_OA.csv', index=False)

fig14 = px.bar(chosenfunder_byjournal_and_OA, x='Source title', y='DOI', color='Open Access',
            category_orders={'Open Access': ["Closed", "All OA; Gold", "All OA; Bronze", "All OA; Green", "All OA; Hybrid"]},
            color_discrete_map={
                "Closed": "#AB63FA",
                "All OA; Gold": "gold",
                "All OA; Bronze": "#636EFA",
                "All OA; Green": "#2CA02C",
                "All OA; Hybrid": "#EF553B"},
            #pattern_shape='Open Access'
           title = f'{institution_name} Corresponding Authored with Funding from<br>the {chosen_funder}, by Journal title and Open Access status' )

fig14.update_xaxes(categoryorder = 'total descending', maxallowed=maxallowed)
fig14.update_layout(height=1000, showlegend=True, legend_traceorder='reversed')
#fig13.update_traces(dict(marker_line_width=0))

st.plotly_chart(fig14)





html_string = "<p style=font-size:13px>v1.0, last modified 3/26/2025 <br />by Eric Schares, <a href='mailto:scharesdatascience@gmail.com'>scharesdatascience@gmail.com</a></p>"
st.markdown(html_string, unsafe_allow_html=True)


html_string_statcounter = '''
<!-- Default Statcounter code for Publishing Profiler
https://publishingprofiler.streamlit.app/ -->
<script type="text/javascript">
var sc_project=13089181; 
var sc_invisible=1; 
var sc_security="b4f33304"; 
</script>
<script type="text/javascript"
src="https://www.statcounter.com/counter/counter.js"
async></script>
<noscript><div class="statcounter"><a title="Web Analytics
Made Easy - Statcounter" href="https://statcounter.com/"
target="_blank"><img class="statcounter"
src="https://c.statcounter.com/13089181/0/b4f33304/1/"
alt="Web Analytics Made Easy - Statcounter"
referrerPolicy="no-referrer-when-downgrade"></a></div></noscript>
<!-- End of Statcounter Code -->
'''

st.components.v1.html(html_string_statcounter)  # JavaScript works
