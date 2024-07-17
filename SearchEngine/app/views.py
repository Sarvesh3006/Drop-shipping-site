import time

import numpy as np
from django.shortcuts import render, redirect
from django.http import HttpResponse
import pandas as pd
import requests
import random
from . import scrap
from bs4 import BeautifulSoup
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder
from .forms import TextBoxForm,BuyButton,DashboardFilter
from django.contrib import messages
from kmodes.kmodes import KModes
import plotly.io as pio
from plotly.subplots import make_subplots
import plotly.graph_objs as go

def login(request):
    if request.method == 'POST':
        user = request.POST.get('UserName')
        password = request.POST.get('password')
        credentials = pd.read_csv(r'C:\Harshit\SearchEngineDjango\SearchEngine\app\Data\creds.csv')
        credentials1=pd.read_csv(r'C:\Harshit\SearchEngineDjango\SearchEngine\app\Data\admin_creds.csv')
        if len(credentials1[(credentials1['User'] == user) & (credentials1['Password'] == password)]) != 0:
            request.session['name'] = user
            return redirect('app:admin-page')
        elif len(credentials[(credentials['User'] == user) & (credentials['Password'] == password)]) == 0:
            return render(request, 'Login.html', {'output' : 'Please enter valid credentials!!'})
        else:
            request.session['name'] = user
            return redirect('app:funct')  # Replace 'func' with the name of your target view
    return render(request, 'Login.html')

def logout(request):
    request.session['name']=None
    return redirect('app:login')



def funct(request):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"
    }
    data = []
    recom=[]
    user=request.session.get("name")
    if not request.session.get("name"):
        return redirect('app:login')
    elif  request.session.get("name")=='admin':
        return redirect('app:admin-page')


    else:
        if request.method == 'POST':
            input2=''
            form = TextBoxForm(request.POST)
            if form.is_valid():
                input1 = form.cleaned_data['text_input']

                data = []
                # url1 = "https://www.flipkart.com/search?q="+input1
                #
                # content = requests.get(url1,headers=headers)
                # HTMLCON = content.content
                # soup = BeautifulSoup(HTMLCON, 'html.parser')
                # # Hyperlinks
                # list1 = soup.findAll('div', {'class': '_13oc-S'})
                # list2 = []
                # for i in range(0, len(list1)-5):
                #     list2.append(list1[i].find('a').get('href'))
                # hyperlinks = []
                # for i in list2:
                #     hyperlinks.append('https://www.flipkart.com'+i)
                # # Scraping all hyperlinks
                #
                # title = []
                # print(hyperlinks)
                # for e, i in enumerate(hyperlinks):
                #
                #     content = requests.get(i,headers=headers)
                #     HTMLCON = content.content
                #     soup = BeautifulSoup(HTMLCON, 'html.parser')
                #     title.append(soup)
                #     Imgurl = []
                #     for i in list1:
                #         Imgurl.append(i.find('img').get('src'))
                #
                #
                #
                #     data.append({"Name": soup.find('span', {'class': 'B_NuCI'}).text,
                #                  "Cost": soup.find('div', {'class': '_30jeq3 _16Jk6d'}).text,
                #                  "Link": 'https://www.flipkart.com'+list1[e].find('a').get('href'),  # ,
                #                  "Imgurl": Imgurl[e]
                #                  })

                # cat = soup.findAll('a', {'class': '_2whKao'})
                # cat = cat[1].get_text()
                # cat1 = soup.findAll('a', {'class': '_2whKao'})
                # cat1 = cat1[2].get_text()
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
                list1 = soup.findAll('div', {
                    'class': 'product-row js-product-list centerCardAfterLoadWidgets dp-click-widgets'})
                class1 = list1[0].findAll('section', {'class': 'js-section clearfix dp-widget'})
                data = []
                class2 = class1[0].findAll('img', {'class': 'product-image'})
                costclass = class1[0].findAll('span', {'class': 'lfloat product-price'})
                categories = soup.find('div', {'class': 'cat-nav-wrapper dp-widget'}).findAll('div',
                                                                                              {'class': 'sub-cat-name'})
                if  len(categories)==0:
                    cat='Other'
                    cat1='Other'
                elif len(categories)==1:
                    cat = categories[0].text
                    cat1='Other'
                else:
                    cat = categories[0].text
                    cat1 = categories[1].text

                for i, e in enumerate(costclass):
                    print(e.text.replace(" ", "").replace("Rs.", ""))
                    data.append({"Name": class2[i]['title'],
                                 "Cost": e.text.replace(" ", "").replace("Rs.", ""),
                                 "Imgurl": class2[i]['src']
                                 })

                #print(datetime.now().date())
                # Get the current date
                current_date = datetime.now().date()
                # Format it as "DD-MM-YYYY"
                formatted_date = current_date.strftime('%d-%m-%Y')
                record=pd.read_csv(r'C:\Harshit\SearchEngineDjango\SearchEngine\app\Data\record1.csv')
                new_row={'Search':input1,	'Time':	formatted_date,'Category1':cat,	'Category2':cat1,	'User':user}
                new_row = pd.DataFrame.from_dict(new_row, orient='index').T

        # Append the new row to the original DataFrame
                #df = record.append(new_row, ignore_index=True)
                dataframe=pd.concat([record,new_row])


                df=pd.get_dummies(dataframe,columns=['Category1','Category2','Search'])
                X=df.drop(columns=['Time','Group','User'])
                cost = []
                #print(X.isna().sum())
                for i in range(1, 11):
                    kmode = KModes(n_clusters=i, init='Cao', n_init=1, verbose=0)
                    kmode.fit_predict(X)
                    cost.append(kmode.cost_)

                # Find the "elbow" point programmatically
                elbow_point = None
                for i in range(1, len(cost) - 1):
                    if cost[i] - cost[i - 1] < cost[i + 1] - cost[i]:
                        elbow_point = i + 1
                        break

                kmode = KModes(n_clusters=elbow_point, init='Cao', n_init=1, verbose=0)
                clusters = kmode.fit_predict(X)
                dataframe['Group']=list(clusters)
                dataframe.to_csv(r'C:\Harshit\SearchEngineDjango\SearchEngine\app\Data\record1.csv',index=False)

                #class_col = list(clusters.labels_)


               #print(dataframe.tail(1))

                tfidf = TfidfVectorizer(stop_words='english')
                tfidf_matrix = tfidf.fit_transform(dataframe['Search'])
                #dataframe['Category1']=tfidf.transform(dataframe['Category1'])
                #dataframe['Category2']=tfidf.Stransform(dataframe['Category2'])
                cosine_similarities = linear_kernel(tfidf_matrix, tfidf_matrix)

                relevant_data = record.loc[
                 (
                                record['Category1'] == record['Category1'].tail(1).values[0]) & (
                                record['Category2'] == record['Category2'].tail(1).values[0])& (
                                record['Group'] == record['Group'].tail(1).values[0])]
                # Get the search query that was used in each of those rows
                relevant_queries = relevant_data['Search']

                # Compute the average cosine similarity between those queries and all the other queries in the dataset
                query_indices = [record[record['Search'] == record['Search'].tail(1).values[0]].index[0] for query in
                                 relevant_queries]
                similarities = cosine_similarities[query_indices].mean(axis=0)

                # Find the index of the most similar search query
                most_similar_index = similarities.argmax()
                prediction = record.iloc[most_similar_index]['Search']



        else:
            record=pd.read_csv(r'C:\Harshit\SearchEngineDjango\SearchEngine\app\Data\record1.csv')
            record=record[record['User']!='User1']
            form = TextBoxForm()
            tfidf = TfidfVectorizer(stop_words='english')
            tfidf_matrix = tfidf.fit_transform(record['Search'])
            # dataframe['Category1']=tfidf.transform(dataframe['Category1'])
            # dataframe['Category2']=tfidf.Stransform(dataframe['Category2'])
            cosine_similarities = linear_kernel(tfidf_matrix, tfidf_matrix)

            relevant_data = record.loc[
                (
                        record['Category1'] == record['Category1'].tail(1).values[0]) & (
                        record['Category2'] == record['Category2'].tail(1).values[0]) & (
                        record['Group'] == record['Group'].tail(1).values[0])]
            # Get the search query that was used in each of those rows
            relevant_queries = relevant_data['Search']

            # Compute the average cosine similarity between those queries and all the other queries in the dataset
            query_indices = [record[record['Search'] == record['Search'].tail(1).values[0]].index[0] for query in
                             relevant_queries]
            similarities = cosine_similarities[query_indices].mean(axis=0)
            print(similarities)
            # Find the index of the most similar search query
            most_similar_index=np.argpartition(-similarities,3)[:3]
            #most_similar_index = similarities.argmax()

            print(most_similar_index)
            input1 = record.iloc[most_similar_index[random.randint(0,2)]]['Search']
            print(input1)
            recom=scrap.scrap(input1)


            return render(request, 'home.html', {'form': form,'recom':recom})


    return render(request, 'home.html', {'form': form, 'tables': data})

def buy(request):
    user=request.session.get("name")
    if not request.session.get("name"):
        return redirect('app:login')

    else:
        if request.method == 'POST':
            form = BuyButton(request.POST)
            if form.is_valid():
                input1 = form.cleaned_data['quantity']
                if input1==0:
                    input1=1
                else:
                    pass


                product=request.POST.get('Product_name')
                Cost=request.POST.get('Product_cost')
                Cost = Cost[1:]
                print(product,Cost)
                input1=float(input1)
                Cost=float(Cost)
                current_date = datetime.now().date()
                # Format it as "DD-MM-YYYY"
                formatted_date = current_date.strftime('%d-%m-%Y')
                orders=pd.read_csv(r'C:\Harshit\SearchEngineDjango\SearchEngine\app\Data\buying.csv')
                new_row = {'Date': formatted_date,  'Product': product,'Quantity':input1,'Cost':Cost,'User':user}
                new_row = pd.DataFrame.from_dict(new_row, orient='index').T
                df=pd.concat([orders,new_row])
                df.to_csv(r'C:\Harshit\SearchEngineDjango\SearchEngine\app\Data\buying.csv',index=False)

        else:
            form = TextBoxForm()

        return redirect('app:funct')

def Subcat(df):
    # Generate some sample data for the chart
    # df = pd.read_csv(r'C:\Harshit\SearchEngineDjango\SearchEngine\app\Data\record1.csv', parse_dates=True)
    df['Time'] = pd.to_datetime(df['Time'])
    # Create a histogram trace using Plotly
    trace = go.Histogram(x=df['Category2'], name='Category frequency')

    # Create a Plotly figure and add the trace
    fig = go.Figure(data=[trace])
    fig.update_layout(title_text="Category Frequency")
    # Serialize the figure to HTML
    chart_html = pio.to_html(fig, full_html=False)

    return chart_html


def value_customer(df):
    # Generate some sample data for the chart
    # df = pd.read_csv(r'C:\Harshit\SearchEngineDjango\SearchEngine\app\Data\buying.csv', parse_dates=True)
    df['Date']=pd.to_datetime(df['Date'])
    # Create a histogram trace using Plotly
    trace = go.Bar(x=df['User'],y=df['Cost'], name='Value per customer')

    # Create a Plotly figure and add the trace
    fig = go.Figure(data=[trace])
    fig.update_layout(title_text="Customer Value")
    # Serialize the figure to HTML
    chart_html = pio.to_html(fig, full_html=False)

    return chart_html



def trend(df):
    # Generate some sample data for the chart
   # df = pd.read_csv(r'C:\Harshit\SearchEngineDjango\SearchEngine\app\Data\buying.csv', parse_dates=True)
    df['Date'] = pd.to_datetime(df['Date'])
    df['Sales']=(df['Cost'] * df['Quantity'])
    df.sort_values(by='Date',inplace=True)

    df=pd.DataFrame(df.groupby(['Date','Sales'])['Sales'].sum())
    df.rename(columns={'Sales':'Amount'},inplace=True)
    print(df)
    df.reset_index(inplace=True)





    # Create a histogram trace using Plotly
    trace = go.Scatter(x=df['Date'],y=df['Amount'], mode='lines',name='Value per customer')
   # print(df['Cost']*df['Quantity'])
    # Create a Plotly figure and add the trace
    fig = go.Figure(data=[trace])
    fig.update_layout(title_text="Sales Trend")
    # Serialize the figure to HTML
    chart_html = pio.to_html(fig, full_html=False)

    return chart_html




def search_trend(df):
    # Generate some sample data for the chart
    #df = pd.read_csv(r'C:\Harshit\SearchEngineDjango\SearchEngine\app\Data\record1.csv', parse_dates=True)
    df['Time'] = pd.to_datetime(df['Time'])
    df.sort_values(by='Time',inplace=True)
    df=pd.DataFrame(df.groupby(['Time','User'])['User'].count())
    df.rename(columns={'User':'Count'},inplace=True)
    print(df)
    df.reset_index(inplace=True)
    # Create a histogram trace using Plotly
    trace = go.Scatter(x=df['Time'],y=df['Count'], mode='lines',name='Search trend')

    # Create a Plotly figure and add the trace
    fig = go.Figure(data=[trace])
    fig.update_layout(title_text="No. Of Searches Trend")
    # Serialize the figure to HTML
    chart_html = pio.to_html(fig, full_html=False)

    return chart_html





def User_freq(df):
    # Generate some sample data for the chart
    #df = pd.read_csv(r'C:\Harshit\SearchEngineDjango\SearchEngine\app\Data\record1.csv', parse_dates=True)
    #df.sort_values(by='Time',inplace=True)
    #df=pd.DataFrame(df.groupby(['Time','User'])['User'].count())
   # df.rename(columns={'User':'Count'},inplace=True)
    #print(df)
    #Wdf.reset_index(inplace=True)
    # Create a histogram trace using Plotly
    df['Time'] = pd.to_datetime(df['Time'])
    trace = go.Histogram(x=df['User'], name='Search trend')

    # Create a Plotly figure and add the trace
    fig = go.Figure(data=[trace])
    fig.update_layout(title_text="Customer Frequency")
    # Serialize the figure to HTML
    chart_html = pio.to_html(fig, full_html=False)

    return chart_html



def admin(request):
    customercount=''
    Total=''
    category=''
    chart_html = ''
    chart_html1 = ''
    chart_html2 = ''
    chart_html3 = ''
    chart_html4 = ''
    if not request.session.get("name") or request.session.get("name")!='admin':

        return redirect('app:login')
    else:
        if request.method == 'POST':
            form = DashboardFilter(request.POST)
            if form.is_valid():
                fromdate=form.cleaned_data['from_date']
                todate=form.cleaned_data['to_date']
                fromdate = pd.to_datetime(fromdate)
                todate = pd.to_datetime(todate)
                print(fromdate,todate)
                data=pd.read_csv(r'C:\Harshit\SearchEngineDjango\SearchEngine\app\Data\record1.csv')

                orders=pd.read_csv(r'C:\Harshit\SearchEngineDjango\SearchEngine\app\Data\buying.csv')
                fromdate = pd.to_datetime(fromdate)
                todate = pd.to_datetime(todate)
                data['Time'] = pd.to_datetime(data['Time'], format='%d-%m-%Y')
                orders['Date'] = pd.to_datetime(orders['Date'], format='%d-%m-%Y')
                # Filter data based on date range
                data = data[(data['Time'] >= fromdate) & (data['Time'] <= todate)]
                orders = orders[(orders['Date'] >= fromdate) & (orders['Date'] <= todate)]

                #orders=orders[(orders['Date']>=fromdate)&(orders['Date']<=todate)]
                Total=sum(orders['Cost']*orders['Quantity'])
                customercount=len(data['User'].unique())
                category=data['Category2'].value_counts().idxmax()
                chart_html = Subcat(data)
                chart_html1=value_customer(orders)
                chart_html2=trend(orders)
                chart_html3=search_trend(data)
                chart_html4=User_freq(data)
                print('Here')

                # return render(request, 'admin.html',
                #           {'Total': Total, 'customer': customercount, 'category': category, 'chart': chart_html,
                #            'cust_val': chart_html1, 'Trend': chart_html2, 'search_trend': chart_html3,
                #            'sunburst': chart_html4})
        else:
            data = pd.read_csv(r'C:\Harshit\SearchEngineDjango\SearchEngine\app\Data\record1.csv')

            orders = pd.read_csv(r'C:\Harshit\SearchEngineDjango\SearchEngine\app\Data\buying.csv')
            Total = sum(orders['Cost'] * orders['Quantity'])
            customercount = len(data['User'].unique())
            category = data['Category2'].value_counts().idxmax()
            chart_html = Subcat(data)
            chart_html1 = value_customer(orders)
            chart_html2 = trend(orders)
            chart_html3 = search_trend(data)
            chart_html4 = User_freq(data)

        return render(request, 'admin.html',
                              {'Total': Total, 'customer': customercount, 'category': category, 'chart': chart_html,
                               'cust_val': chart_html1, 'Trend': chart_html2, 'search_trend': chart_html3,
                               'sunburst': chart_html4})

        # return render(request, 'admin.html',{'Total':Total,'customer':customercount,'category':category,'chart': chart_html,
        #                                  'cust_val':chart_html1,'Trend':chart_html2,'search_trend':chart_html3,'sunburst':chart_html4})













# def text_box_view(request):
#     result = None
#     if request.method == 'POST':
#         form = AddNumbersForm(request.POST)
#         if form.is_valid():
#             num1 = form.cleaned_data['num1']
#             num2 = form.cleaned_data['num2']
#             result = num1 + num2
#     else:
#         form = AddNumbersForm()
#
#     return render(request, 'demo.html', {'form': form, 'result': result})