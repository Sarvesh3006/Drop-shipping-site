import numpy as np
from django.shortcuts import render, redirect
from django.http import HttpResponse
import pandas as pd
import requests
import random
from bs4 import BeautifulSoup
import time
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder

from kmodes.kmodes import KModes
import plotly.io as pio
from plotly.subplots import make_subplots
import plotly.graph_objs as go



def scrap(input1):

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"
    }
    input1 = input1.replace(" ", '+')
    url1 = "https://www.snapdeal.com/search?keyword=" + input1
    time.sleep(random.randint(4,6))
    content = requests.get(url1, headers=headers)
    HTMLCON = content.content
    soup = BeautifulSoup(HTMLCON, 'html.parser')
    # soup
    # Hyperlinks
    list1 = soup.findAll('div', {'class': 'product-row js-product-list centerCardAfterLoadWidgets dp-click-widgets'})
    class1 = list1[0].findAll('section', {'class': 'js-section clearfix dp-widget'})
    data = []
    class2 = class1[0].findAll('img', {'class': 'product-image'})
    costclass = class1[0].findAll('span', {'class': 'lfloat product-price'})
    #categories = soup.find('div', {'class': 'cat-nav-wrapper dp-widget'}).findAll('div', {'class': 'sub-cat-name'})
    #print(categories)


    for i, e in enumerate(costclass):
        print(e.text.replace(" ", "").replace("Rs.", ""))
        data.append({"Name": class2[i]['title'],
                     "Cost": e.text.replace(" ", "").replace("Rs.", ""),
                     "Imgurl": class2[i]['src']
                     })
    return data[random.randint(0,len(data)-1)]