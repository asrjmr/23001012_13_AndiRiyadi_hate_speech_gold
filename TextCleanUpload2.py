import re
import pandas as pd
import csv
from flask import Flask, jsonify
from flask import request
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flasgger import swag_from

import matplotlib.pyplot as plt
import seaborn as sns
from pandas import DataFrame
import numpy as np


# DEFAULT FLASK AND SWAGGER DEFAULT SETTING
app = Flask(__name__)

#app.json_encoder = LazyJSONEncoder
#app.json_provider_class = LazyJSONEncoder
app.json_provider_class = LazyJSONEncoder
app.json = LazyJSONEncoder(app)

swagger_template = dict(
    info={
        'title': LazyString(lambda: 'API Documentation for Data Processing and Modeling'),
        'version': LazyString(lambda: '1.0.0'),
        'description': LazyString(lambda: 'Dokumentasi API untuk Data Processing dan Modeling'),
        },
    host=LazyString(lambda: request.host)
)
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'docs',
            "route": '/docs.json',
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/"
}
swagger = Swagger(app, template=swagger_template,             
                  config=swagger_config)

# IMPORT ABUSIVE.CSV AND NEW_KAMUSALAY.CSV TO PANDAS DATAFRAME (EACH)
df_abusive = pd.read_csv('abusive.csv')
df_kamusalay = pd.read_csv('new_kamusalay.csv', encoding='latin-1', header=None)
df_kamusalay.columns=["tidak baku","baku"]

# DEFINE ENDPOINTS: BASIC GET
@swag_from("docs/hello_world.yml", methods=['GET'])
@app.route('/', methods=['GET'])
def hello_world():
    json_response = {
        'status_code': 200,
        'description': "Menyapa Hello World",
        'data': "Hello World",
    }
    response_data = jsonify(json_response)
    return response_data

# DEFINE ENDPOINTS: POST FOR TEXT PROCESSING FROM TEXT INPUT
@swag_from("docs/text_processing.yml", methods=['POST'])
@app.route('/text-processing', methods=['POST'])
def text_processing():
    
    text = request.form.get('text')
    
    json_response = {
        'status_code': 200,
        'description': "Teks yang sudah diproses",
        'data': re.sub(r'[^a-zA-Z0-9]',' ', text)
    }
    
    response_data = jsonify(json_response)
    return response_data

# DEFINE ENDPOINTS: POST FOR TEXT PROCESSING FROM TEXT INPUT
@swag_from("docs/text_processing_file.yml", methods=['POST'])
@app.route('/text-processing-file', methods=['POST'])

def text_processing_file ():
    #file = request.files.getlist('file')[0]
    global file,df,final_df
    
    # get file dari API endpoint
    file = request.files.get('file')

    # IMPORT FILE OBJECT INTO PANDAS DATAFRAME
    df = pd.read_csv(file,delimiter=",",encoding="latin-1")

    # SET THE TWEET COLUMN ONLY FOR THE DATAFRAME
    df = df[['Tweet']]

    # DROP DUPLICATED TWEETS
    df = df.drop_duplicates(subset=["Tweet"],keep="first")

    # CREATE A FUNCTION TO CLEAN DATA FROM ANY NON ALPHA-NUMERIC (AND NON-SPACE) CHARACTERS, AND STRIP IT FROM LEADING/TRAILING SPACES
    def tweet_cleansing(x):
        tweet = x
        cleaned_tweet = re.sub(r'[^a-zA-Z0-9 ]','',tweet).strip()
        return cleaned_tweet
    
    # APPLY THE TWEET_CLEANSING FUNCTION ON TWEET COLUMN, AND CREATE A NEW CLEANED_TWEET COLUMN
    df['cleaned_tweet'] = df['Tweet'].apply(lambda x: tweet_cleansing(x))

    # create table
    import sqlite3
    conn=sqlite3.connect('binar_gold1.db')
    sqlcreatetabel = """
    CREATE TABLE if not exists tbl_textClean1 (textOri varchar(255), textClean varchar(255))
    """
    conn.execute(sqlcreatetabel)
    conn.commit()
    #print("Table created successfully")
    conn.close()

    json_response = {
        'status_code' : 200,
        'description' : "Teks sudah di proses 1",
        'data' : "Berhasil",
    }

    # get data hanya 100 dari teratas
    df = df.head(100)
   
    # insert ke database
    for i in range(len(df)):
        old = df['Tweet'].iloc[i]
        new = df['cleaned_tweet'].iloc[i]
        
        conn=sqlite3.connect('binar_gold1.db',timeout=500)

        # cek/validasi apakah data sudah ada di tabel tbl_textclean1
        dfCek = pd.read_sql_query("select textClean from tbl_textClean1 where textClean = '"+new+"'", conn)
        
        if dfCek['textClean'].count() == 0:
            conn.execute("insert into tbl_textClean1 (textOri,textClean) values (?,?)",(old, new))

        conn.commit()
        conn.close()

    # grafik
    conn=sqlite3.connect('binar_gold1.db',timeout=500)

    sqlUnion =""" 
    SELECT
	    CASE WHEN textOri = textClean then 'Kalimat ada character selain angka dan huruf' END as Label,
	    count(textOri) as varCount
    FROM
	    tbl_textClean1
    WHERE
	    textOri = textClean

    UNION

    SELECT
	    CASE WHEN textOri != textClean then 'Kalimat tidak ada character selain angka dan huruf' END as Label,
	    count(textClean) as varCount1
    FROM
	    tbl_textClean1
    WHERE
	    textOri != textClean
    """            
    cursor = conn.execute(sqlUnion)
    all_rows = cursor.fetchall()
    
    conn.commit()
    conn.close()

    list_row_col_a = []
    list_row_col_b = []

    for i in range(len(all_rows)):
        list_row_col_a.append(all_rows[i][0])
        list_row_col_b.append(all_rows[i][1])

    new_df_from_db = pd.DataFrame()
    new_df_from_db['label'] = list_row_col_a
    new_df_from_db['varCount'] = list_row_col_b

    fig = plt.figure(figsize=(15,5))
    ax=sns.barplot(data=new_df_from_db,x=new_df_from_db.varCount,y=new_df_from_db['label'])

    plt.title('Perbandingan Kalimat Memiliki Angka dan Huruf',fontsize=15)
    plt.xlabel('Jumlah',fontsize=13)
    plt.ylabel('Kategori kalimat',fontsize=13)
    ax.bar_label(ax.containers[0])

    plt.show()  

    response_data = jsonify(json_response)
    return response_data

if __name__ == '__main__':
    app.run()