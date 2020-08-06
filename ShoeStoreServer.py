from flask import Flask, Markup, render_template,redirect, url_for, request,make_response
import pandas as pd
import json
from flask import jsonify
import datetime
import pymysql
from sqlalchemy import create_engine

app = Flask(__name__)

session = create_engine('mysql+pymysql://b1988b353f38a9:eb355ccd@us-cdbr-east-02.cleardb.com:3306/heroku_57e05bf7b956609')

@app.route('/fetchalliteams', methods = ['GET', 'POST'])
def fetchalliteams():
    result = pd.read_sql("select * from amazon_shoe_store",con=session)
    #print(result)
    return render_template('index.html',tables=[result.to_html(classes='result', header="true")])

@app.route('/selecteditem', methods = ['GET', 'POST'])
def selecteditem():
    selectedprodid=request.form['productid']
    result = pd.read_sql("select * from amazon_shoe_store where sell_price = {0}".format(float(selectedprodid)),con=session)
    return render_template('index.html',tables=[result.to_html(classes='result', header="true")])



@app.route('/range', methods = ['GET', 'POST'])
def range():
    selectedprodidmin=request.form['productidmin']
    selectedprodidmax = request.form['productidmax']
    result = pd.read_sql("select * from amazon_shoe_store where sell_price >= {0} and sell_price <= {1}".format(float(selectedprodidmin),float(selectedprodidmax)),con=session)
    return render_template('index.html',tables=[result.to_html(classes='result', header="true")])


def define_discount(x,maximum_discount):
    if x> 0 and x <= 20:
        return 'Up to 20% Discount'
    elif x> 20 and x<=50:
        return 'Minimum 20% to Up to 50% Discount'
    else:
        return 'More than 50% Discount Up to {0}%'.format(maximum_discount)


def reviewer_range(x):
    if x>= 1 and x <= 2:
        return 'Rating from 1.0 to 2.0'
    elif x>= 2 and x <= 3:
        return 'Rating from 2.0 to 3.0'
    elif x>= 3 and x <= 4:
        return 'Rating from 3.0 to 4.0'
    elif x>= 4 and x <= 5:
        return 'Rating from 4.0 to 5.0'

@app.route('/charts')
def charts():
    cleaned_dataset = pd.read_sql("select mrp_price,sell_price from amazon_shoe_store",con=session)
    discount = cleaned_dataset[(cleaned_dataset.mrp_price - cleaned_dataset.sell_price)>0][['mrp_price','sell_price']]
    discount['discount_precentage'] = round(((cleaned_dataset.mrp_price - cleaned_dataset.sell_price)/cleaned_dataset.mrp_price)*100,2)
    mimimum_discount = discount.discount_precentage.min()
    maximum_discount = discount.discount_precentage.max()
    discount['category'] = discount['discount_precentage'].apply(lambda x:define_discount(x,maximum_discount))
    d = discount.category.value_counts()
    discount_chart = pd.DataFrame({'discount_category':d.keys(),'number_of_products':d.values})

    xaxis=discount_chart['discount_category'].values.tolist()
    yaxis=discount_chart['number_of_products'].values.tolist()
    labels = xaxis
    values = yaxis

    colors = [
        "#32CD32", "#FDB45C", "#B22222"]
    bar_labels = labels
    bar_values = values
    max_v = discount_chart.number_of_products.max() + 100
    varaiable1 = str(discount_chart.number_of_products.sum())
    varaiable2 = str(mimimum_discount)+'%'
    varaiable3 = str(maximum_discount)+'%'

    return render_template('charts.html',var1=varaiable1,var2=varaiable2,var3=varaiable3, title='Number of products in each discount category', max=max_v, set=zip(values, labels, colors))



@app.route('/charts1')
def charts1():
    cleaned_dataset = pd.read_sql("select rating from amazon_shoe_store",con=session)
    ratings = cleaned_dataset[['rating']]
    rat = ratings.rating.value_counts()
    rating_chart = pd.DataFrame({'rating':rat.keys(),'number_of_products':rat.values})
    rating_chart = rating_chart[['rating','number_of_products']].sort_values('rating').reset_index(drop='index')

    xaxis=rating_chart['rating'].values.tolist()
    yaxis=rating_chart['number_of_products'].values.tolist()
    
    labels = xaxis
    values = yaxis
    bar_labels = labels
    bar_values = values
    max_v2 = rating_chart.number_of_products.max()+100

    return render_template('charts1.html', title='Rating wise Number of Products', max=max_v2, labels=bar_labels, values=bar_values)


@app.route('/charts2')
def charts2():
    cleaned_dataset = pd.read_sql("select product,sell_price,rating,reviews from amazon_shoe_store",con=session)
    reviewers = cleaned_dataset[['product','sell_price','rating','reviews']]
    reviewers['rating_range'] = reviewers['rating'].apply(lambda x:reviewer_range(x))
    reviewers = reviewers.groupby('rating_range').agg({'reviews':['min','max'],'sell_price':['min','max']}).reset_index()
    print(reviewers)
    reviewers.columns = ['rating','minimum_reviewers','maximum_reviewers','min_price_product','max_price_product']
    xaxis=reviewers['rating'].values.tolist()
    yaxis=reviewers['minimum_reviewers'].values.tolist()
    #print(yaxis)
    labels = xaxis
    values = yaxis
    
    bar_labels = labels
    bar_values = values
    max1 = reviewers['minimum_reviewers'].max() +1

    bar_labels1 = xaxis
    bar_values1 = reviewers['maximum_reviewers'].values.tolist()
    max2 = reviewers['maximum_reviewers'].max() +100

    bar_labels2 = xaxis
    bar_values2 = reviewers['min_price_product'].values.tolist()
    max3 = reviewers['min_price_product'].max() +10

    bar_labels3 = xaxis
    bar_values3 = reviewers['max_price_product'].values.tolist()
    max4 = reviewers['max_price_product'].max() + 50
    print(max1,max2,max3,max4)
    return render_template('charts2.html', title='', max1=max1,max2=max2,max3=max3,max4=max4, labels=bar_labels, values=bar_values,labels1=bar_labels1, values1=bar_values1,labels2=bar_labels2, values2=bar_values2,labels3=bar_labels3, values3=bar_values3)



@app.route("/")
def main():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='192.168.43.231',debug=True)