from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
import logging
from urllib.request import urlopen
import re
import json
from datetime import datetime, timedelta
import csv
logging.basicConfig(filename="scrapper.log" , level=logging.INFO)

app = Flask(__name__)

def convert_date(n_days_ago):
    #print(n_days_ago)
    today = datetime.now()    
    result = (today - timedelta(days=int(n_days_ago)))
    result = result.date()
    #print(today, result)
    return result

@app.route("/", methods = ['GET'])
def homepage():
    return render_template("index.html")

@app.route("/details" , methods = ['POST' , 'GET'])
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ","")
            youtube_url = "https://www.youtube.com/"+searchString+"/videos"
            urlclient = urlopen(youtube_url)
            youtube_page = urlclient.read().decode()
            re2 = re.compile("\"videoId\":\"(\S+)\",\"thumbnail\"")
            selected_channel_videos_list = []
            for c in re2.findall(youtube_page):
                search_text = "videoId\":\"{c}\"(.*?)watchEndpoint\":(.*?)\"videoId\":\"{c}\""
                #print(search_text.format(c=c))
                search_text = search_text.format(c=c)

                youtube_video_info = {
                    "video_url": None,
                    "thumbnail_url": None,
                    "youtube_title": None,
                    "views_count": None,
                    "posting_time":None
                }

                f = re.search(search_text, youtube_page)
                if f:
                    json_text2 = "{" + f.group(1)[1:-2] + "}}"
                    json_dict = json.loads(json_text2)
                    #print(json_dict)
                    thumbnail_url = json_dict.get("thumbnail").get("thumbnails")[0]["url"]
                    youtube_title = json_dict.get("title").get("runs")[0]["text"]
                    views_count = json_dict.get("viewCountText").get("simpleText")
                    views_count = re.sub("\D", "", views_count)
                    video_url = "https://youtu.be"+json_dict.get("navigationEndpoint").get("commandMetadata").get("webCommandMetadata").get('url')
                    posting_time = json_dict.get("publishedTimeText").get("simpleText")
                    posting_date_time = convert_date(posting_time.split(" ")[0])
                    #print(posting_date_time)
                    selected_channel_videos_list.append({
                        "video_url": video_url,
                        "thumbnail_url": thumbnail_url,
                        "youtube_title": youtube_title,
                        "views_count": views_count,
                        "posting_time": posting_date_time
                    })
            csv_columns = ['video_url','thumbnail_url','youtube_title','views_count','posting_time']

            csv_file = "Channel.csv"
            try:
                with open(csv_file, 'w') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
                    writer.writeheader()
                    for data in selected_channel_videos_list:
                        writer.writerow(data)
            except IOError:
                print("I/O error")
        
            
            logging.info("log my final result {}".format(selected_channel_videos_list))
            return render_template('result.html', datas=selected_channel_videos_list[0:(len(selected_channel_videos_list)-1)])
        except Exception as e:
            logging.info(e)
            return 'something is wrong'
    # return render_template('results.html')

    else:
        return render_template('index.html')


if __name__=="__main__":
    app.run(host="0.0.0.0")
