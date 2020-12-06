
# coding: utf-8

# In[216]:


import pyrebase
import requests
from bs4 import BeautifulSoup
import sys
import pickle
import threading
import os

# In[5]:


config = {
    'apiKey': "AIzaSyD2gQOTBgyQuGHAm1cvM4ErUlgfvQOXQSI",
    'authDomain': "shure-35e0d.firebaseapp.com",
    'projectId': "shure-35e0d",
    'storageBucket': "shure-35e0d.appspot.com",
    'messagingSenderId': "346311417995",
    'appId': "1:346311417995:web:879258027b30219c55b48e",
    'measurementId': "G-G09GXQBXRY",
    'databaseURL':'https://shure-35e0d-default-rtdb.firebaseio.com'
  }

firebase = pyrebase.initialize_app(config)


# In[219]:


database = firebase.database()
user = None
try:
    user = pickle.load(open('user','rb'))
except:
    pass
# In[48]:


auth = firebase.auth()

auth.current_user = user
# In[119]:


def sign_up(email, password, name):
    user = auth.create_user_with_email_and_password(email, password)
    email = email.replace('@','')
    email = email.replace('.','')
    database.child('users').child(email).set(name,user['idToken'])
    return user


# In[169]:


def sign_in(email, password):
    global user
    user = auth.sign_in_with_email_and_password(email, password)
    email = user['email']
    
    pickle.dump(user,open('user','wb'))
    threading.Thread(target = trim_own).start()
    

    return user


# In[46]:


def sign_out():
    try:
        if auth.current_user == None:
            print('Already Signed Out')
            return
        auth.current_user = None
        print('Signed Out')
    except NameError:
        print('Not Signed In')


# In[52]:


def signed_in():
    if auth.current_user!= None:
        return True
    else:
        return False


# In[39]:


def connect():
    database = firebase.database()


# In[201]:


def push_in_main_recent(url,title = None, msg = ''):
    global user
    if not signed_in():
        print('Sign In First')
        return
    if title==None:
        reqs = requests.get(url)
        soup = BeautifulSoup(reqs.text, 'html.parser')
        title = soup.title.get_text()
        
    email = user['email']
    email = email.replace('@','')
    email = email.replace('.','')
    user_name = dict(database.child('users').get(user['idToken']).val())[email]
        
    database.child('main').child('recent').push({'title':title, 'url':url, 'user':user_name, 'msg':msg}, user['idToken'])


# In[99]:


def trim_recent():
    global user
    articles = database.child('main').child('recent').get(user['idToken']).val()
    while True:
        if len(articles)<=5:
            break
        else:
            next_token = next(iter(articles))
            database.child('main').child('recent').child(next_token).remove(user['idToken'])
            del articles[next_token]


def trim_main():
    global user
    articles = database.child('main').get(user['idToken']).val()
    while True:
        if len(articles)<=20:
            break
        else:
            next_token = next(iter(articles))
            database.child('main').child(next_token).remove(user['idToken'])
            del articles[next_token]

def trim_own():
    global user
    email = user['email']
    email = email.replace('@','').replace('.','')
    user_name = dict(database.child('users').get(user['idToken']).val())[email]
    articles = database.child(user_name).get(user['idToken']).val()
    while True:
        if len(articles)<=10:
            break
        else:
            next_token = next(iter(articles))
            database.child(email).child(next_token).remove(user['idToken'])
            del articles[next_token]


# In[184]:


def push_in_main(url,title = None, msg = ''):
    global user
    if not signed_in():
        print('Sign In First')
        return
    if title==None:
        reqs = requests.get(url)
        soup = BeautifulSoup(reqs.text, 'html.parser')
        title = soup.title.get_text()
    
    email = user['email']
    email = email.replace('@','')
    email = email.replace('.','')
    user_name = dict(database.child('users').get(user['idToken']).val())[email]
    database.child('main').push({'title':title, 'url':url, 'user':user_name, 'msg':msg}, user['idToken'])


# In[ ]:


# In[207]:


def display(folder='main'):
    global user
    if(folder=='main'):
        data = database.child('main').get(user['idToken']).val()
        keys = list(data.keys())
        root_articles = [data[i] for i in keys if 'title' in list(data[i].keys())]
        print('Articles : ')
        for i in root_articles:
            print('-'*3, end = '')
            title = i['title']
            url = i['url']
            user_name = i['user']
            print(f'Name : {title} \n|   Url : {url} \n|   Saved By : {user_name}')
            
    elif folder =='recent':
        data = database.child('main').child('recent').get(user['idToken']).val()
        keys = list(data.keys())
        root_articles = [data[i] for i in keys if 'title' in list(data[i].keys())]
        print('Recent Articles : ')
        for i in root_articles:
            print('-'*3, end = '')
            title = i['title']
            url = i['url']
            user_name = i['user']
            print(f'Name : {title} \n|   Url : {url} \n|   Saved By : {user_name}')


# In[206]:


# In[213]:


def push_own(url, title=None, msg = ''):
    global user
    if not signed_in():
        print('Sign In First')
        return
    if title==None:
        reqs = requests.get(url)
        soup = BeautifulSoup(reqs.text, 'html.parser')
        title = soup.title.get_text()
    
    email = user['email']
    email = email.replace('@','')
    email = email.replace('.','')
    user_name = dict(database.child('users').get(user['idToken']).val())[email]
    database.child(user_name).push({'title':title, 'url':url, 'msg':msg}, user['idToken'])
    threading.Thread(target = trim_own).start()

# In[217]:

def save_sign_in(opt):
    if opt=='n':
        return
    elif opt == 'y':
        print('Enter your credentials:\n Email : ',end = '')
        email = input()
        print("Password : ", end = '')
        password = input()
        pfile = open('oauth','w+')
        pfile.write(email+" "+password)
        pfile.flush()
        pfile.close()
    else:
        print("Wrong option")
        


def main():
    
    need_argument = ['push', 'push-to-self', 'push-to-recent']
    neednt_argument = ['sign-in', 'sign-up']
    args = sys.argv[1:]
    cont = False
    if len(args)==0:
        pass
    else:
        for i in range(len(args)):
            if cont:
                cont = False
                continue
            if args[i] in need_argument:
                try:
                    if len(args)>2:
                
                        run(args[i],arg = args[i+1],args =  args[i+2:])
                    else:
                        run(args[i],args[i+1])
                except Exception as e:
                    if "expired" in str(e).lower():
                        if 'oauth' in os.listdir():
                            print('Sign in expired, please wait while we log you in')
                            dat = open('oauth','r+').read().split()
                            sign_in(dat[0],dat[1])
                            return
                        e = "Sign In Expired, Please Sign in again or do you want to save your password(insecure) (yes - y, no - n)"
                    print(e)
                    ans = input("Do you want to save your password\n")
                    save_sign_in(ans)
                cont = True
            elif args[i] in neednt_argument:
                run(args[i])
    

# In[ ]:


def run(com, arg=None, args = None):
    
    if com=='sign-in':
        email = input("Email : ")
        password = input("Password : ")
        user = sign_in(email,password)
        
    elif com=='sign-up':
        email = input("Email : ")
        password = input("Password : ")
        sign_up(email,password)
    elif com.startswith('push'):
        if com.endswith('main'):
            title = None
            if args!=None:
                if args[0]=='title':
                    title = args[1]
            push_in_main(arg, title=title)

        else:
            title = None
            if args!=None:
                if args[0]=='title':
                    title = args[1]
            push_own(arg, title=title)
        
        title = None
        if args!=None:
            if args[0]=='title':
                title = args[1]
        threading.Thread(target = push_in_main_recent, args = (arg,), kwargs = {'title':title}).start()
        
        threading.Thread(target = trim_recent).start()
        threading.Thread(target = trim_main).start()



if __name__ == '__main__':
    main()
