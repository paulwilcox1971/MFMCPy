# -*- coding: utf-8 -*-
"""
Created on Fri Jul 14 12:59:50 2023

@author: mepdw
"""
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            # Save the uploaded file to a desired location
            file.save('uploads/' + file.filename)
            
            # Read the contents of the uploaded file
            with open('uploads/' + file.filename, 'r') as f:
                contents = f.read()
                
            # Process the contents and generate the desired text
            # In this example, we'll just return the contents as is
            processed_text = contents
            
            return render_template('result.html', text=processed_text)
    
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)