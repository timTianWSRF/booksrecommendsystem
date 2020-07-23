from django.shortcuts import render,redirect
from RSofBX.apps.bxdb import models
from django.views.generic.base import View
from .forms import userForm,loginForm
from RSofBX.apps.rs_online import views as online
from django.db.models.aggregates import Count
from django.http import HttpResponse
from django.db import connection
from RSofBX.apps.rs_offline.views import updateRatingsSet

import json

# Create your views here.
userinfo = {}


def getCookies(func):
    def warpper(self,request,*args,**kwargs):
        user = request.COOKIES.get('username')
        userid = request.COOKIES.get('userid')
        userinfo.update({
            'user':user,
            'userid':userid,
        })
        return func(self,request,*args,**kwargs)
    return warpper


class login(View):
    nexturl = None

    def get(self,request):
        login.nexturl = request.GET.get('next',None)
        return render(request, 'login.html')

    def post(self, request):
        nexturl = login.nexturl
        print('next:', nexturl)
        # Get the posted form
        MyLoginForm = loginForm(request.POST)
        username = "not logged in"

        if MyLoginForm.is_valid():

            userinfo = MyLoginForm.clean_message()
            if userinfo == 2:
                print('密码错误')
                return render(request, 'login.html')
            elif userinfo == 1:
                print("管理员登录成功")
                return redirect('/background/', permanent=True)
            else:
                print("用户登录成功")

                if not nexturl:
                    response = redirect('/home/')
                    username = userinfo.user_name
                    userid = userinfo.user_id
                    response.set_cookie('username', username)
                    response.set_cookie('userid', userid)
                    return response

                else:
                    response = redirect('/bookdetail/'+str(nexturl))
                    username = userinfo.user_name
                    userid = userinfo.user_id
                    response.set_cookie('username', username)
                    response.set_cookie('userid', userid)
                    return response

        print('username:', username)
        return render(request, 'login.html')


class topN(View):

    def get(self,request):

        booklist = online.getTopN(10)
        return render(request,'topN.html',{"data":booklist})


class register(View):
    def get(self,request):
        registeFrorm = userForm()
        return render(request,'register.html',{'registeFrorm':registeFrorm})

    def post(self,request):
        registeFrorm = userForm(request.POST)

        if registeFrorm.is_valid():  # 判读是否全部通过验证
            print("通过验证")

            username = registeFrorm.cleaned_data.get("username")
            password = registeFrorm.cleaned_data.get("password")
            age = registeFrorm.cleaned_data.get("age")
            location = registeFrorm.cleaned_data.get("location")
            models.user_info.objects.create(user_name=username, password=password,age=age,location=location)

            response = redirect('/newUserRating/')
            userid = models.user_info.objects.get(user_name=username).user_id
            response.set_cookie('username', username)
            response.set_cookie('userid', userid)
            return response

            #return redirect("/login/")

        else:
            errors = registeFrorm.errors  # 字典类型,键是字段名,值是一个存着所有错误信息的列表 莫版中用{{ errors.字段名.0 }}
            # print(type(login_form.errors))# <class 'django.forms.utils.ErrorDict'>
            # login_form.errors={"user":["小于5位","不是数字"],"pwd":["",""]}

            error_all = errors.get("__all__")
            # 全局钩子的错误信息保存在了键是 __all__ 的值的列表中,在模版语言中用{{ error_all.0 }}

            return render(request, "register.html",
                          {"errors": errors, "error_all": error_all, "registeFrorm": registeFrorm})


class bookDetail(View):
    @getCookies
    def get(self,request,bid):
        book = models.bx_info.objects.get(book_id=bid)
        #print(book.book_title)
        ratelist = getRate(bid)
        simlist = online.get_simBook(bid, 10)
        simlist = idTobook(simlist)

        if userinfo.values is not None:
            myRate = getmyRate(userinfo['userid'], bid)
            #print(myRate)
        else:
            myRate = None
            print("没有登录")
        return render(request, "bookDetail.html",{'userinfo':userinfo,'book':book,'ratelist':ratelist,'simlist':simlist,'myRate':myRate})


class home(View):
    @getCookies
    def get(self,request):
        rslist =[]
        simUser_list = []
        ratingNum = 0
        #热门推荐
        hotlist = online.getTopN(num=10)
        hotlist = idTobook(hotlist)
        userId = userinfo['userid']
        print('userid:',userId)
        if  userId != None :
            ratingNum = numofRating(userId)
            #print(ratingNum)
            if ratingNum <=10:
                rslist = online.simpleRS(userId)
                rslist = idTobook(rslist)
            else:
                rslist = online.mixedRS(userId)
                rslist = idTobook(rslist)

                simUser_list = online.RSbaseSimUser(userId,15)
                simUser_list = idTobook(simUser_list)


        return render(request,'home.html',{'userinfo':userinfo,'hotlist':hotlist,'rslist':rslist,'simUser_booklist':simUser_list,'ratingNum':ratingNum})


class logout(View):
    def get(self,request):
        response = redirect('/home/')
        response.delete_cookie('username')
        response.delete_cookie('userid')
        return response


class search(View):
    @getCookies
    def get(self, request,tag):
        #print(tag)
        tagInfo = models.tags.objects.get(tag_name=tag)
        #print(tagInfo.tag_id)
        booklistgb = models.book_tags.objects.filter(tag_id=tagInfo.tag_id)
        booklistgb = booklistgb[:10].values('gb_id')
        #print(booklistgb)
        gblist = []
        booklist = []
        for book in booklistgb:
            gblist.append(book['gb_id'])
        for num in gblist:
            booklist.append(models.bx_info.objects.get(gb_id=num).book_id)
        #print(booklist)
        searchlist = idTobook(booklist)
        resultlen = len(searchlist)

        return render(request,'search.html',{'userinfo':userinfo,'searchlist':searchlist,'len':resultlen})

    @getCookies
    def post(self,request):
        bookName = request.POST.get('searchBook',None)
        authorName = request.POST.get('searchAuthor',None)
        resultlist = models.bx_info.objects.filter(book_title__icontains=bookName,book_author__icontains=authorName)
        #print(resultlist)
        searchlist = []
        for book in resultlist.values('book_id'):
            searchlist.append(book['book_id'])
        searchlist = idTobook(searchlist)
        resultlen = len(searchlist)
        return render(request,'search.html',{'userinfo':userinfo,'searchlist':searchlist,'len':resultlen})


class newUserRating(View):
    @getCookies
    def get(self,request):
        hotlist= []
        if userinfo.values is not None:
            hotlist = online.getTopN(num=50)
            hotlist = idTobook(hotlist)

        return render(request,'newUserRating.html',{'userinfo':userinfo,"hotlist":hotlist})


def idTobook(idList):
    bookLists = {}

    for item in idList:
        try:
            bookInfo = models.bx_info.objects.get(book_id=item)

        except bookInfo.DoesNotExist:
            print(item,"此书不在库中.")
        else:
            tmp = {
                'bookId': bookInfo.book_id,
                'bookTitle': bookInfo.book_title,
                'imgurl': bookInfo.image_url,
                'author': bookInfo.book_author
            }

        bookLists[item] = tmp

    return bookLists


def getRate(bookId):
    list = [0,0,0,0,0]

    rates = models.book_ratings.objects.filter(book_id=bookId).values('rating').annotate(num=Count('rating')).order_by('num')
    for book in  rates:
        list[book['rating']-1] = book['num']
    return list


def getmyRate(userId, bookId):
    myRate = 0
    try:
        myRate = models.book_ratings.objects.get(user_id=userId, book_id=bookId)
    except:
        print('没有评分')
    else:
        myRate = myRate.rating
    return myRate


def setmyRate(request):
    if request.is_ajax():
        ret = {'status': True, 'error': ""}
        userId = request.GET.get("userid")
        bookId = request.GET.get('bookid')
        rate = request.GET.get('rate')
        print('setrate',rate)
        try:
            myRate = getmyRate(userId, bookId)
            print("myrate",myRate)
            ratingCount = models.bx_info.objects.get(book_id=bookId)
            if myRate != 0:
                if not rate:
                    models.book_ratings.objects.filter(user_id=userId,book_id=bookId).delete()
                    models.bx_info.objects.filter(book_id=bookId).update(ratings_count=(ratingCount.ratings_count-1))
                else:
                    models.book_ratings.objects.filter(user_id=userId, book_id=bookId).update(rating=rate)
            else:
                if rate:
                    models.book_ratings.objects.create(user_id=userId, book_id=bookId, rating=rate)
                    models.bx_info.objects.filter(book_id=bookId).update(ratings_count=(ratingCount.ratings_count+1))

        except Exception as e:
            ret['status'] = False
            ret['error'] = str(e)
        j_ret = json.dumps(ret)

        return HttpResponse(j_ret)


def numofRating(userId):
    num = len(models.book_ratings.objects.filter(user_id=userId))
    return num


class test(View):
    def get(self,request):
        return render(request,'newUserRating.html')



