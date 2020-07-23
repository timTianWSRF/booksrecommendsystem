from django.shortcuts import render
from RSofBX.apps.rs_offline import views as offviews
import pandas as pd
from RSofBX.apps.bxdb.models import book_ratings
from sklearn.externals import joblib
import random


# Create your models here.

def getTopN(num):
    books = pd.read_csv('static/dataset/books.csv')

    hot100 = books.sort_values('ratings_count', ascending=False)[:100]
    hot100 = hot100['book_id']
    hotIdlist  = hot100.sample(num).values.tolist()

    return hotIdlist


def recommendation(userId,algo,num):
    if algo == 'svd':
        rsbooks = recommendation_svd(userId,num)

        return rsbooks

    if algo == 'kmeans':
        rsbooks = recommendation_kmeans(userId,num)

        return rsbooks


def mixedRS(userId):
    svd = recommendation(userId,'svd',10)
    print('svd:', svd)
    kmeans = recommendation(userId,'kmeans',10)
    print('kmeans:', kmeans)
    svd.extend(kmeans)
    mixList = list(set(svd))
    print('mixlist:',mixList)
    return mixList


def recommendation_svd(userId,num):
    algo = 'svd'
    userRSList = 'static/usersRSList/'+str(userId)+'_'+algo+'.csv'
    rsbooks = pd.read_csv(userRSList)
    rsbooks = rsbooks.sort_values("Estimate_Score", ascending=False).head(num)
    rsbooks = rsbooks['book_id']
    return rsbooks.values.tolist()


def recommendation_kmeans(userId,num):
    clusterlist = pd.read_csv('static/trainingModels/user_cluster.csv',index_col='user_id')
    ratings = offviews.getRatingsSet()

    user_cluster = clusterlist.loc[int(userId), 'cluster']
    favorites = pd.read_csv('static/usersRSList/cluster_'+str(user_cluster)+'_kmeans.csv',index_col='book_id')
    booklist = []

    for i, book in zip(range(0, num), favorites.index):
        if ratings.loc[(ratings['user_id']==userId)&(ratings['book_id']==book)].empty:
            booklist.append(book)
    return booklist


def get_simUser(userId,topK):
    neighbourList = []

    try:
        filename = 'static/usersRSList/' + str(userId) + '_simUser.txt'
        neighbour = pd.read_csv(filename)

    except:
        print('暂无此用户推荐',userId)

    else:

        #print(neighbour)
        neighbourList = neighbour['user_id'].head(topK)
        neighbourList = neighbourList.values.tolist()
    return neighbourList

def RSbaseSimUser(userId,num):
    ratings = offviews.getRatingsSet()
    simUserlist = get_simUser(userId,num)
    RSbookBaseUser = []
    if simUserlist:
        for user in simUserlist:
            book = ratings.loc[ratings['user_id']==user].sort_values(by='rating',ascending=False)[:10]
            book = book['book_id']
            RSbookBaseUser.extend(book.sample(1).values.tolist())
        print('baseUser:',RSbookBaseUser)
    else:
        print('相似列表为空')
    return RSbookBaseUser


def get_simBook(bookId,num):
    neighbourList = []
    try:
        filename = 'static/similarBooksList/'+str(bookId)+'_simBook.txt'
        neighbour = pd.read_csv(filename)

    except:
        print('暂无此书推荐',bookId)

    else:

        neighbourList = neighbour['book_id'].head(num)
        neighbourList = neighbourList.values.tolist()
    return neighbourList


def simpleRS(userId):
    simpleList = []
    tmp = []
    result = book_ratings.objects.filter(user_id=userId).values_list('book_id')
    for i in result:
        tmp.extend(list(i))
    for book in tmp:
         simpleList.extend(get_simBook(book,5))
    print('simplelen',len(simpleList))
    if len(simpleList) >= 20:
        simpleList = random.sample(simpleList,15)
    return simpleList