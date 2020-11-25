import streamlit as st 
import requests
import boto3
import json
from scrape import scrape_transcripts
#from extract_entities import get_entities
#from maskanm import mask_deidentify_entities, store_deidentified_entities
#from reidentify import re_identify_entities
from load_css import local_css
from credentials import authorize_user
from signup import signup_user
import time
import ast
from PIL import Image


st.title('Named Entity Recognition for Earnings Transcript')
region = 'us-east-1'
client_sf = boto3.client('stepfunctions')
s3_client = boto3.client('s3', region_name = region)



local_css("style.css")

st.markdown("""
<style>
.sidebar .sidebar-content {
    color: white;
    background-color: #0A3648;
    background-image: linear-gradient(#20B2AA,#2F4F4F);
}
</style>
    """, unsafe_allow_html=True)

back = "<div style='height:500px;width:700px;overflow:auto;background-color:GHOSTWHITE;color:DARKSLATEGRAY;scrollbar-base-color:gold;font-family:sans-serif;padding:10px;'>"

menu = ['Login Signup Page', 'Entity Recognition(NER) Pipeline', 'Pipeline Architecture']

st.sidebar.markdown('**Select Dashboard**')
choices = st.sidebar.selectbox("", menu)
st.sidebar.markdown("---")


if choices == 'Entity Recognition(NER) Pipeline':
    st.subheader('Entity Recognition(NER) Pipeline')
    #st.sidebar.success("Greed, for lack of a better word, is good")


    st.write('NER Pipeline allows you to scrape any Earnings call Report from seeking alpha\
             and get entities using AWS Comprehend. It allows you to also use Masking and Anonymization\
             to encrypt your output report')

    
    
    authorized = False
    st.markdown("---")
    user_input = ''
    st.markdown('Enter your **Username & Password for Authorized Access**')
    username = ''
    username = st.text_input("Enter Username")
    password = st.text_input("Enter ID Token for Authentication", type='password')
    #authorize = st.button('Authorize')

    st.markdown("---")
    st.markdown('***Select your Options for PIPELINE***')
    scrape = st.checkbox('Scrape Earnings Call Transcript', True)
    if scrape:
        st.markdown('Enter **Seeking Alpha URL**')
        url = st.text_input(" ", '')
    detect = st.checkbox('Extract Entities(NER) using AWS Comprehend', True)
    deidentify = st.checkbox('Masking & De-Identification of Entities', True)
    reidentify = st.checkbox('Re-Identify Entities', True)

    st.sidebar.markdown('***Entity Labels***')
    entity_list = ['PERSON', 'ORGANIZATION','EVENT', 'TITLE', 'LOCATION', 'COMMERCIAL_ITEM', 'DATE', 'QUANTITY', 'OTHER']
    defaultent = ['PERSON', 'ORGANIZATION','EVENT', 'TITLE', 'LOCATION', 'COMMERCIAL_ITEM', 'DATE', 'QUANTITY']
    selected_entity = st.sidebar.multiselect("", entity_list, default=defaultent)
    authorized = True

    run = st.button('Run')
    if run:
            
        #if authorized:
        #st.success("Signed In as {}".format(username))
        # check here if data exists in cognito and time is < curr time 


        st.markdown("---")
        st.success("Signed In as {}".format(username))
        st.write('Initiating Pipeline...')
        
        scrape_file_name = scrape_transcripts(url)

        scrape_file_path= 'scraper_output/{}'.format(scrape_file_name)
        scrape_response = s3_client.get_object(Bucket='ner-recognized-entites', Key=scrape_file_path)
        original_text = scrape_response['Body'].read().decode('utf-8')

        #original_text = open(file_name, encoding='utf8').read()

        st.markdown("---")
        st.subheader('***Scraped Earnings Call Transcript from Seeking Alpha***')
        st.markdown("---")
        #st.text(original_text)
        original_html = back + original_text + '</div>'

        st.markdown(original_html, unsafe_allow_html=True)
        timestr = time.strftime("%Y%m%d-%H%M%S")
        Reidentify_opt = 'Permanent'
        if reidentify:
            Reidentify_opt = 'Reidentify'

        sf_name = 'csyeSFExecution' + timestr

        sf_input = json.dumps({"body": {"file_name": scrape_file_name, 
                       "ReversibleorPermanent":Reidentify_opt,
                       "User": username}}, sort_keys=True)
        response = client_sf.start_execution(
        stateMachineArn='arn:aws:states:us-east-1:165885578631:stateMachine:EntityRecognitionMachine',
        name=sf_name,
        input= sf_input)

        #st.write(response)



        #extracted_entities_, entity_file = get_entities(file_name= file_name)
        #st.text(extracted_entities_['Entities'])
        file_names = 'file_names.txt'
        _file_path= 'filenames_output/{}'.format(file_names)
        file_res = s3_client.get_object(Bucket='ner-recognized-entites', Key=_file_path)
        file_res_ = file_res['Body'].read().decode('utf-8')
        file_res_text = ast.literal_eval(file_res_)
        
        entities_file_ = file_res_text['entity_file']
        annonymize_file_ = file_res_text['annonymize_file']
        reidentify_file = file_res_text['reidentify_file']

        # entities
        entity_file_path= 'entities_output/{}'.format(entities_file_)
        entity_res = s3_client.get_object(Bucket='ner-recognized-entites', Key=entity_file_path)
        entity_res_ = entity_res['Body'].read().decode('utf-8')
        
        entities_e = ast.literal_eval(entity_res_)['Entities']

        entities = []
        for entity in entities_e:
            if entity['Type'] in selected_entity:
                entities.append(entity)

        st.markdown("---")
        st.subheader('***Extracted Entities from AWS Comprehend***')
        st.markdown("---")

        #st.text(entities)
        entities_ = str(entities)
        entity_html = back + entities_ + '</div>'

        st.markdown(entity_html, unsafe_allow_html=True)


        st.markdown("---")
        st.subheader('***Entities Visualized within Earnings Transcript***')
        st.markdown("---")
        ## put your logic here for text format 

        color_lookup = {'PERSON':'tomato', 'ORGANIZATION':'aqua','EVENT':'dred', 'TITLE':'orchid', 'LOCATION':'blue', 'COMMERCIAL_ITEM':'red', 'DATE':'coral', 'QUANTITY':'pink', 'OTHER':'greenyellow'}
        start = 0
        orignial_html = '<div>'
        for entity in entities:
            orignial_html += original_text[start:entity['BeginOffset']] + "<span class='highlight " +  color_lookup[entity['Type']] + "'>" + entity['Text'] + "<span class='bold'>" + entity['Type'] + "</span></span>"

            start = entity['EndOffset']
        orignial_html += '</div>'
        st.markdown(orignial_html, unsafe_allow_html=True)


        ## masking 
        st.markdown("---")
        st.subheader('***Masked, Anonymized & De-Identified Transcript***')
        st.markdown("---")
        
        ddb_table='DeIdentifed_Entities'
        #deidentified_message, entity_map, deiden_entities = mask_deidentify_entities(original_text, entities)
        #hash_msg = store_deidentified_entities(deidentified_message, entity_map, ddb_table)
        
        mask_file_path= 'annonymize_output/{}'.format(annonymize_file_)
        mask_res_ = s3_client.get_object(Bucket='ner-recognized-entites', Key=mask_file_path)
        deidentified_message = mask_res_['Body'].read().decode('utf-8')
        

        #st.text(deidentified_message)
        deidentify_html = back + deidentified_message + '</div>'

        st.markdown(deidentify_html, unsafe_allow_html=True)

        if reidentify:
            st.markdown("---")
            st.subheader('***Re-Identification of De-Identified Entities - Organization, Event, Location***')
            st.markdown("---")

            reid_file_path= 'reidentify_output/{}'.format(reidentify_file)
            reid_res = s3_client.get_object(Bucket='ner-recognized-entites', Key=reid_file_path)
            re_identified_message = reid_res['Body'].read().decode('utf-8')
            
            
            reidentify_html = back + re_identified_message + '</div>'

            st.markdown(reidentify_html, unsafe_allow_html=True)
            st.markdown("---")

elif choices == 'Pipeline Architecture':
    image = 'AWS_architecture.png'
    arch_image = Image.open(image)
    st.image(arch_image, use_column_width=True)



elif choices == 'Login Signup Page':
    st.sidebar.markdown('**Login/SignUp to use our Services**')

    radio = st.radio('', ('Login - Existing User', 'SignUp - New User'))
    st.markdown('---')
    if(radio == 'Login - Existing User'):
        st.markdown('**Login to get Your Authorized Access Token**')
        st.markdown('**Enter UserName**')
        username = st.text_input("")
        st.markdown('**Enter Password**')
        password = st.text_input(" ", type='password')
        login = st.button('Login')

        if login:
            authorized, username, IdToken = authorize_user(username, password)
            if authorized:
                st.success("Signed In as {}".format(username))
                st.markdown('**Your ID Token**')
                st.write(IdToken)
            else:
                st.success("User {} could not be Authorized".format(username))

    if(radio == 'SignUp - New User'):
        st.markdown('**SignUp to get Your Authorized Access Token**')
        st.markdown('**Enter UserName**')
        username = st.text_input("")
        st.markdown('**Enter Password**')
        password = st.text_input(" ", type='password')
        st.markdown('**Enter Full Name**')
        name = st.text_input("   ")
        st.markdown('**Enter Email Id**')
        email = st.text_input("    ")
        
        signup = st.button('SignUp')
        sign = ''
        message = ''

        if signup:
            message, sign = signup_user(username, email, name, password)
            if sign:
                st.success(message)
                
            else:
                st.success(message)



    else:
        pass


