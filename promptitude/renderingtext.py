from promptitude import application, dropzone
from flask import render_template, request, redirect, url_for, session
from .forms import QRCodeData
import secrets
import os

import cv2
import pytesseract
from PIL import Image
import numpy as np
from gtts import gTTS


from . import mutilingual
@application.route("/")
def index():
    return render_template("index.html")


@application.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == 'POST':

        
        sentence = ""
        
        f = request.files.get('file')
        filename,extension = f.filename.split(".")
        generated_filename = secrets.token_hex(20) + f".{extension}"
       

        file_location = os.path.join(application.config['UPLOADED_PATH'], generated_filename)

        f.save (file_location)

        

        
        pytesseract.tesseract_cmd =  '/opt/homebrew/Cellar/tesseract'

        img = cv2.imread(file_location)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


        boxes = pytesseract.image_to_data(img)
        
    
        for i, box in enumerate(boxes.splitlines()):
            if i == 0:
                continue

            box = box.split()
            
            if len(box) == 12:
                sentence += box[11] + " "
       
        # print(sentence)
        session["sentence"] = sentence

        # delete file after you are done working with it
        os.remove(file_location)

        return redirect("/decoded/")

    else:
       return render_template("upload.html", title="Home")


@application.route("/decoded", methods=["GET", "POST"])
def decoded():

    sentence = session.get("sentence")
    # print(sentence)

    # print(lang)
    lang, _ = mutilingual.detect_language(sentence)
    # print(lang, conf)
    

    form =QRCodeData() 

    if request.method == "POST":
        generated_audio_filename = secrets.token_hex(10) + ".mp4"
        text_data = form.data_field.data
        translate_to = form.language.data
        # print("Data here", translate_to)

  
        translated_text = mutilingual.translate_text(text_data, translate_to)
        print(translated_text)
        tts = gTTS(translated_text, lang=translate_to)



        file_location = os.path.join(
                            application.config['AUDIO_FILE_UPLOAD'], 
                            generated_audio_filename
                        )

        # save file as audio
        tts.save(file_location)

        # return redirect("/audio_download/" + generated_audio_filename)

        form.data_field.data = translated_text

        return render_template("translated.html", 
                        title="Decoded", 
                        form=form, 
                        lang=mutilingual.languages.get(lang),
                        audio = True,
                        file = generated_audio_filename
                    )


    # form.data_field.data = sentence
    form.data_field.data = sentence

    # set the sentence back to defautl blank
    # sentence = ""
    session["sentence"] = ""

    return render_template("translated.html", 
                            title="Decoded", 
                            form=form, 
                            lang=mutilingual.languages.get(lang),
                            audio = False
                        )



