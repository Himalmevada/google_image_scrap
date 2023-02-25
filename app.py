from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen
import logging
import pymongo
import os

logging.basicConfig(filename="scrapper.log", level=logging.INFO)

app = Flask(__name__)


@app.route("/", methods=['GET'])
def homepage():
    return render_template("index.html")


@app.route("/images", methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        try:

            # query to search for images
            query = request.form['content'].replace(" ", "")

            # directory to store downloaded images
            image_dir = "images/"

            # create the directory if it doesn't exist
            if not os.path.exists(image_dir):
                os.makedirs(image_dir)

            # fake user agent to avoid getting blocked by Google
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}

            # fetch the search results page
            response = requests.get(
                f"https://www.google.com/search?q={query}&sxsrf=AJOqlzUuff1RXi2mm8I_OqOwT9VjfIDL7w:1676996143273&source=lnms&tbm=isch&sa=X&ved=2ahUKEwiq-qK7gaf9AhXUgVYBHYReAfYQ_AUoA3oECAEQBQ&biw=1920&bih=937&dpr=1#imgrc=1th7VhSesfMJ4M")

            # parse the HTML using Beautifulimage_html_data
            image_html_data = bs(response.content, "html.parser")

            # find all img tags
            image_tag_list = image_html_data.find_all("img")

            # download each image and save it to the specified directory
            del image_tag_list[0]
            image_data_mongo = []

            for index, image_tag in enumerate(image_tag_list):
                # get the image source URL
                image_url = image_tag['src']
                # print(image_url)

                # send a request to the image URL and save the image
                image_data = requests.get(image_url).content

                img_dict = {"Index":index,"Name":query,"Image":image_data}

                image_data_mongo.append(img_dict)

                with open(os.path.join(image_dir, f"{query}_{image_tag_list.index(image_tag)}.jpg"), "wb") as ip:
                    ip.write(image_data)

            client = pymongo.MongoClient(
                "mongodb+srv://admin:admin@cluster0.ge05dtm.mongodb.net/?retryWrites=true&w=majority")

            db = client['scraper_db']
            img_coll = db['img_coll']

            img_coll.insert_many(image_data_mongo)

            return "image loaded"

        except Exception as e:

            logging.info(e)
            return 'something is wrong'

    # return render_template('results.html')

    else:
        return render_template('index.html')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
