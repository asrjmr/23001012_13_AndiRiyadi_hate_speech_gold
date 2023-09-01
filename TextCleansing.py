import re
import pandas as pd
import csv
from flask import Flask, jsonify
from flask import request
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flasgger import swag_from


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
            "endpoint": 'textclean',
            "route": '/textclean.json',
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/textclean/"
}
swagger = Swagger(app, template=swagger_template,             
                  config=swagger_config)



@swag_from("docs/text_processing.yml", methods=['POST'])
@app.route('/textclean', methods=['POST'])
def text_processing ():
    text = request.form.get('text')
    
    json_response = {
        'status_code' : 200,
        'description' : "teks sudah di proses",
        'data' : re.sub(r'[^a-zA-z0-9]','',text),
    }

    response_data = jsonify(json_response)
    return response_data

if __name__ == '__main__':
    app.run()
