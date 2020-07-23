from django.shortcuts import render
import pandas as pd
import pymysql
from sklearn.externals import joblib
from django.views.generic.base import View
from surprise import Reader, Dataset, model_selection, KNNBaseline
from surprise.model_selection import GridSearchCV, cross_validate, train_test_split
import numpy as np

# Create your views here.


def getBooksSet():
    conn = pymysql.connect(host='127.0.0.1', user='root', password='123456', db='RS_BX', charset='utf8')

    sql = 'select * from bxdb_bx_info'
    books = pd.read_sql(sql, con=conn)
    conn.close()
    books.to_csv('static/dataset/books.csv',index=False)
    return books


def getUsersSet():
    conn = pymysql.connect(host='127.0.0.1', user='root', password='123456', db='RS_BX', charset='utf8')

    sql = 'select * from bxdb_user_info'
    users = pd.read_sql(sql, con=conn)
    conn.close()
    return users


def getRatingsSet():
    ratings = pd.read_csv('static/dataset/ratings.csv')
    return ratings


def updateRatingsSet():
    conn = pymysql.connect(host='127.0.0.1', user='root', password='123456', db='RS_BX', charset='utf8')

    sql = 'select * from bxdb_book_ratings'
    ratings = pd.read_sql(sql, con=conn)
    conn.close()
    ratings.to_csv('static/dataset/ratings.csv',index=False)
    return None


def SVD(userId):
    algo = joblib.load('static/trainingModels/svd_Data>105.pkl')
    ratings = getRatingsSet()
    n1 = ratings["user_id"].value_counts()
    ratings = ratings[ratings['user_id'].isin(n1[n1 >= 105].index)]
    already_read = ratings[ratings["user_id"] == userId]["book_id"].unique()
    rsbooks = ratings[~ratings["book_id"].isin(already_read)]
    rsbooks["Estimate_Score"] = rsbooks["book_id"].apply(lambda x: algo.predict(userId, x).est)
    rsbooks.drop_duplicates('book_id', keep='first', inplace=True)
    print(rsbooks)
    rsbooks = rsbooks[['book_id','Estimate_Score']]
    savepath = 'static/usersRSList/'+str(userId)+'_svd.csv'
    rsbooks.to_csv(savepath,index=False)

def SVD_All():
    algo = joblib.load('static/trainingModels/svd_Data>105.pkl')
    ratings = getRatingsSet()
    n1 = ratings["user_id"].value_counts()
    ratings = ratings[ratings['user_id'].isin(n1[n1 >= 105].index)]
    all_user = getUsersSet()
    for userId in all_user['user_id'].tolist():
        already_read = ratings[ratings["user_id"] == userId]["book_id"].unique()
        user_rsbooks = ratings[~ratings["book_id"].isin(already_read)]
        user_rsbooks["Estimate_Score"] = user_rsbooks["book_id"].apply(lambda x: algo.predict(userId, x).est)
        user_rsbooks.drop_duplicates('book_id', keep='first', inplace=True)
        #print(user_rsbooks)
        user_rsbooks = user_rsbooks[['book_id','Estimate_Score']]
        savepath = 'static/usersRSList/'+str(userId)+'_svd.csv'
        user_rsbooks.to_csv(savepath,index=False)
        print(userId)
        print("训练完成")


class backTraining(View):
    def get(self,request):
        return render(request, 'backGround.html')

    def post(self,request):
        type = request.POST.get('choice',None)
        print(type)
        if type == 'id':
            userId = request.POST.get('id_num',None)
            print(userId)
            #SVD(userId)
            print('训练完毕')
        elif type == 'num':
            num = int(request.POST.get('id_num', None))
            for id in range(1,num+1):
                print(id)
                SVD(id)
                print('训练完毕')
        else:

            print('all')
            #SVD_All()

        return render(request, 'backGround.html')


#生成聚类结果列表
def kmeans():

    '''
    all_book_ratings_for_clustering:用户物品矩阵截断SVD（100）矩阵（待预测数据）
    clusterer_KMeans：模型
    '''

    all_book_ratings_for_clustering = pd.read_csv('static/dataset/all_book_ratings_for_clustering.csv',index_col='user_id')
    clusterer_KMeans = joblib.load('static/trainingModels/clusterer_KMeans_6_svd_100_user_37076.pkl')
    ratings = getRatingsSet()
    preds_KMeans = clusterer_KMeans.predict(all_book_ratings_for_clustering)
    indices = all_book_ratings_for_clustering.index
    preds = pd.DataFrame(data=preds_KMeans, columns=['cluster']).set_index(indices)
    preds.to_csv('static/trainingModels/user_cluster.csv')

    for i in range(0,6):
        # 创建集群成员列表
        cluster_membership = preds.index[preds['cluster'] == i].tolist()
        # 构建该群集的图书评级的数据框
        cluster_ratings = ratings[ratings.user_id.isin(cluster_membership)]
        # 删除集群成员少于100个评级的书籍
        n1 = cluster_ratings["book_id"].value_counts()
        cluster_ratings = cluster_ratings[ratings['book_id'].isin(n1[n1 >= 100].index)]
        # 找到集群的整体平均评分和每本书
        means = cluster_ratings[['book_id','rating']].groupby('book_id').mean()
        # 按平均等级排序书籍
        favorites = means.sort_values(ascending=False,by='rating')
        savepath = 'static/usersRSList/cluster_'+str(i)+'_kmeans.csv'
        favorites.to_csv(savepath)


def ratings_list_baseKmeans():
    clusterlist = pd.read_csv('static/trainingModels/user_cluster.csv',index_col='user_id')
    ratings = getRatingsSet()
    for i in range(0,6):
        cluster_membership = clusterlist.index[clusterlist['cluster'] == i].tolist()
        cluster_ratings = ratings.loc[ratings['user_id'].isin(cluster_membership)]
        savepath = 'static/dataset/cluster_'+str(i)+'_ratings.csv'
        cluster_ratings.to_csv(savepath)


#分别训练6个聚类的用户相似模型
def training_similar_Users_Model_baseKNN():
    for i in range(0,6):
        cluster_ratings_name = 'static/dataset/cluster_'+str(i)+'_ratings.csv'
        print(cluster_ratings_name)
        cluster_ratings = pd.read_csv(cluster_ratings_name)

        data = Dataset.load_from_df(cluster_ratings[["user_id", "book_id", "rating"]], Reader())
        trainset = data.build_full_trainset()
        #用户相似模型
        sim_options = {'name': 'pearson_baseline', 'user_based': True}
        algo = KNNBaseline(sim_options=sim_options)
        algo.fit(trainset)
        savepath = 'static/trainingModels/knn_user_cluster_'+str(i)+'_pearson.pkl'
        joblib.dump(algo, savepath)


def training_similar_users_list(top_k, userId):
    clusterlist = pd.read_csv('static/trainingModels/user_cluster.csv',index_col='user_id')
    user_cluster = clusterlist.loc[int(userId), 'cluster']
    print('user_cluster:',user_cluster)
    modelName = 'static/trainingModels/knn_user_cluster_'+str(user_cluster)+'_pearson.pkl'
    algo = joblib.load(modelName)

    user_inner_id = algo.trainset.to_inner_uid(userId)
    user_neighbors = algo.get_neighbors(user_inner_id, k=top_k)
    user_neighbor_list = (algo.trainset.to_raw_uid(inner_id) for inner_id in user_neighbors)
    user_neighbor_list = list(user_neighbor_list)
    print(user_neighbor_list,type(user_neighbor_list))
    filename = 'static/usersRSList/'+str(userId)+'_simUser.txt'
    file= open(filename, 'w')
    file.write('user_id')
    file.write('\n')
    for fp in user_neighbor_list:

        file.write(str(fp))
        file.write('\n')
    file.close()


def training_similar_items_list(itemId,top_k):

    item_algo = joblib.load('static/trainingModels/knn_item_sim.pkl')

    for i in range(1,10001):
        itemId = i
        try:
            item_inner_id = item_algo.trainset.to_inner_iid(itemId)

        except:
            print('无',i)

        else:
            item_neighbors = item_algo.get_neighbors(item_inner_id, k=top_k)
            item_neighbor_list = (item_algo.trainset.to_raw_iid(inner_id) for inner_id in item_neighbors)
            item_neighbor_list = list(item_neighbor_list)

            filename = 'static/similarBooksList/'+str(itemId)+'_simBook.txt'
            file= open(filename, 'w')
            file.write('book_id')
            file.write('\n')
            for fp in item_neighbor_list:
                file.write(str(fp))
                file.write('\n')
            file.close()