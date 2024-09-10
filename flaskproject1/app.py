from flask import Flask, session, render_template, url_for, request, redirect,flash, send_from_directory
from peewee import *
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import secrets
import os 
from werkzeug.utils import secure_filename
import time
from dotenv import load_dotenv
import os
import smtplib
from flask_socketio import SocketIO, emit
from datetime import datetime
import pytz,requests

load_dotenv('adm.env')

SECRET_KEY = os.getenv('SECRET_KEY')
SITE_KEY = os.getenv('SITE_KEY')

USERNAME = os.getenv('USERNAME')
PASS = os.getenv('PASS')

app = Flask(__name__)

socketio = SocketIO(app)

app.config['SECRET_KEY'] = SECRET_KEY
app.config['SESSION_TYPE'] = 'peewee'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['REMEMBER_COOKIE_HTTPONLY'] = True

from dotenv import load_dotenv
import os

db = SqliteDatabase('mydatabase.db')


ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
ADMIN_PASSWORD_HASH = os.getenv('ADMIN_PASSWORD_HASH')

UPLOAD_FOLDER = os.getenv('UPL_FOLDER')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_IMAGES = 5

class BaseModel(Model):
   class Meta:
      database=db

class User(BaseModel):
   name=TextField(unique=True)
   password=TextField()
   email=TextField(unique=True)
   bio=TextField()
   class Meta:
      database=db
      db_table='User'


class TemporaryMSGs(BaseModel):
   user=ForeignKeyField(User, backref='usermsg')
   remetente=TextField()
   msg=TextField()
   class Meta:
      database=db
      db_table='TemporaryMSGs'

class Products(BaseModel):
   name=TextField()
   description=TextField()
   path=TextField()
   categoria=TextField()
   datee=TextField()
   author=TextField()
   emailauthor=TextField()
   class Meta:
      database=db
      db_table='Products'


db.connect()
db.create_tables([User, TemporaryMSGs, Products])

connected_clients = set()

def make_session_permanent():
    session.permanent = True

@app.route('/login')
def login():
   return render_template('login.html')

@app.route('/updateprofile', methods=['POST'])
def updateprofile():
   if session.get('user'):
      nametoUpdate = request.form['name']
      biografia = request.form['bio']
      if nametoUpdate.__len__() > 6 and nametoUpdate.__len__() <= 20:
               
               qry = User.update({User.name:nametoUpdate, User.bio:biografia}).where(User.name == session.get('user'))
               session['user'] = nametoUpdate
               print(session.get('user'))
               qry.execute()
               userProfile = User.select().where(User.name == session.__getitem__('user'))
              
               info = []
               for v in userProfile:
                  info.append(v.email)
                  info.append(v.bio)
               Myposts = Products.update({Products.author:session.get('user')}).where(Products.emailauthor == info[0])
               Myposts.execute()
               return render_template('profile.html', userinfo=info, user=session.get('user'))
      else:
         return 'Não foi possível'


@app.route('/editprofile')
def editprofile():
   if session.get('user'):
      return render_template('editProfile.html')
   else:
      return render_template('forbidden.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/saveprod', methods=['POST',])
def saveprod():
   timezone_sao_paulo = pytz.timezone('America/Sao_Paulo')
   datetime_ = datetime.now(timezone_sao_paulo)
   description = request.form['description']
   name = request.form['name']
   image = request.files['file']
   categoria = request.form['categoria']
   userProfile = User.select().where(User.name == session.__getitem__('user'))
   info = [];
   for v in userProfile: 
      info.append(v.email)

   if image and allowed_file(image.filename):
      date=datetime_.time()
      file_name = f'{image.filename}{date}'
      filename = secure_filename(image.filename)
      file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
      Products.create(name=name, description=description, path=file_name, categoria=categoria, datee=datetime_.date(), author=session.get('user'), emailauthor=info[0])
      image.save(file_path)
      flash('Post adicionado com sucesso!')
      return redirect(url_for('adp'))
   return redirect(url_for('adp'))

@app.route('/ad/adp')
def adp():
   products = Products.select()
   userProfile = User.select().where(User.name == session.__getitem__('user'))
   info = []
   for inf in userProfile:
      info.append(inf.name)
      info.append(inf.email)
   if session.get('logged_in'):
      return render_template('addProduct.html', prod=products, infouser=info)
   else:
      return render_template('login.html')

@app.route('/products', methods=['POST', ])
def products():
   lista=[]
   products = [];
   product_name = request.form['product_name']
   if product_name in lista:
      products.append(product_name)
   else:
      pass
   return render_template('showProducts.html', prod=products)

@app.route('/removeprod', methods=['POST'])
def removeprod():
   name_prod = request.form['nameprod'];
   ProdRemove = Products.select().where(Products.name == name_prod)

   if session.get('admin_logged_in') or session.get('logged_in'):
      for i in ProdRemove:
         file_path = os.path.join(app.config['UPLOAD_FOLDER'], i.path)
         os.remove(file_path)
      pr = Products.select().where(Products.name == name_prod);
      for m in pr:
         m.delete_instance()
      flash('Removido!')
      return redirect(url_for('profile'))
   else:
      return render_template('forbidden.html')
   



@app.route('/updateprod', methods=['POST'])
def updateprod():
   description = request.form['description']
   name_prod = request.form['name']
   image = request.files['file']
   categoria = request.form['categoria']
   if session.get('admin_logged_in'):
      if image and allowed_file(image.filename):
         
         filename = secure_filename(image.filename)
         file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
         
         qry = Products.update({Products.name:name_prod, Products.description:description, Products.path:filename, Products.categoria:categoria}).where(Products.name == prodtoupdate)
         qry.execute()
         image.save(file_path)
         db.close()
         flash('Produto atualizado com sucesso!')
         return redirect(url_for('adp'))
      else:
         return redirect('home')



@app.route('/produto/<int:product_id>')
def produto_detail(product_id):
   if session.get('user'):
      get_prod = Products.select().where(Products.id == product_id)
      return render_template('PostPage.html', prod=get_prod)
   else:
      return render_template('createProfile.html')

@app.route('/home', methods=['GET'])
@app.route('/', methods=['GET'])
def home():
   products = Products.select()
   path_list = []
   for v in products:
      print(v.path)
      path_list.append(v.path)
   
   InfoUser = User.select().where(User.name == session.get('user'))
   infouser = []
   for t in InfoUser:
      infouser.append(t.name)
      infouser.append(t.email)
   name_list = []
   for n in products:
      name_list.append(n.name)
   if session.get('logged_in'):
      return render_template('home.html', prod=products,infouser=InfoUser)
   if session.get('admin_logged_in'):
      return render_template('adminHome.html',prod=products, infouser=InfoUser)
   else:
      return render_template('home.html', prod=products, infouser=InfoUser)

@app.route('/cad')
def cad():
    if request.method == 'GET':
        
        return render_template('cad.html')


@app.route('/config')
def config():
   return render_template('config.html')

@app.route('/sobre')
def sobre():
   return render_template('sobre.html')

@app.route('/profile')
def profile():
   
   if session.get('logged_in'):
     
      msg_ = []
      session_user = session.__getitem__('user')

      if session_user in session['user']:
         for user in TemporaryMSGs.select():

            if session_user == user.user_id:
               msg_.append(f'{user.remetente}:' + ' ' +f'{user.msg}')
            else:
               pass

      if session.get('logged_in'):
         print(session.__getitem__('user'))
         userProfile = User.select().where(User.name == session.__getitem__('user'))
         info = []
         for v in userProfile:
            info.append(v.email)
            info.append(v.bio)
         print(info)
         myposts = Products.select().where(Products.emailauthor == info[0])
         return render_template('profile.html', user=session.__getitem__('user'), msg=msg_, posts=myposts, userinfo=info)
      else:
         return render_template('forbidden.html')
   else:
      return render_template('createProfile.html')

@app.route('/login/login')
def adminhome():
      return render_template('admin.html')

@app.route('/ad/config')
def adminconfig():
   if 'admin_logged_in' in session and session['admin_logged_in'] == True:
      return render_template('configadmin.html')
   else:
      return redirect(url_for('home'))

@app.route('/login/home')
def adminhomepage():
   return render_template('adminHome.html')
      
@app.route('/login/val', methods=['POST'])
def adminlogin():
   if request.method == 'POST':
      admin = request.form['username']
      passwd = request.form['passwd']

      if admin == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, passwd):
            session['admin_logged_in'] = True
            session['user'] = ADMIN_USERNAME;
            return redirect(url_for('adminhomepage'))
      else:
         flash('Login inválido.')
   return render_template('admin.html')

@app.route('/validation', methods=['POST',])
def validation():
   user = request.form['user']
   pass_ = request.form['pass']

   users = User.select()

   for usuario in users:
        if usuario.name == user and check_password_hash(usuario.password, pass_):
            session['logged_in'] = True
            session['user'] = user
            print('LOGADO!!')
            print(session)
            msg = f'{user} você está logado!'
            flash(msg)
            return redirect(url_for('home'))

    # Se nenhum usuário corresponder
   flash('Nome de usuário ou senha incorretos.')
   return render_template('login.html') 
    

@app.route('/msg', methods=['POST',])
def msg():
   if 'user' in session and session.__getitem__('user') != ADMIN_USERNAME:
         name = request.form['name_user']
         text = request.form['msg']
         TemporaryMSGs.create(user=name, remetente=session.__getitem__('user'),msg=text)
         return redirect(url_for('home'))
   
   if session['admin_logged_in'] == True:
      if 'del' in request.form:
         option_del = request.form['del']
         if option_del == 'yes':
            name = request.form['name_user']
            obj=User.get(User.name==name)
            obj.delete_instance()
            text = request.form['msg']
            msg = TemporaryMSGs.select().where(TemporaryMSGs.user == name)
            for m in msg:
               m.delete_instance()
            
            name = request.form['name_user']
            text = request.form['msg']
            print('MSSSG', msg.__len__(), text)
            if text.__len__() == 0:
               pass
            else:
               TemporaryMSGs.create(user=name, remetente=session.__getitem__('user'),msg=text)
            
            return redirect(url_for('adview'))
      else:
            name = request.form['name_user']
            text = request.form['msg']
            TemporaryMSGs.create(user=name, remetente=session.__getitem__('user'),msg=text)
            
            return redirect(url_for('adminhomepage'))

   else:
      return render_template('forbidden.html')

@app.route('/ad/view')
def adview():

   if session['admin_logged_in'] == True:
      users_list = []
      rows=User.select()

      print('YES')
      for row in rows:
         print("user: {} pass: {}".format(row.name, row.password))
         users_list.append(row.name)
      db.close()

      return render_template('adminViewUsers.html', users=users_list)
   else:
      print('Not')
      return render_template('forbidden.html')
      

@app.route('/show')
def show():
   users_list = []
   rows=User.select()
   if 'logged_in' in session:
      print('YES')
      for row in rows:
         print("user: {} pass: {}".format(row.name, row.password))
         users_list.append(row.name)
      db.close()

      return render_template('users.html', users=users_list)
   else:
      print('Not')
      return render_template('forbidden.html')


@app.route('/logout')
def logout():

   session.clear()
   print('LOGOUT')
   flash('Logout!')
   return redirect(url_for('home'))

@app.route('/add_cad', methods=['POST',])
def add_cad():
  
   user = request.form['user']
   pass_ = request.form['pass']
   email = request.form['email']

   names = []
   nms = User.select()
   for n in nms:
      names.append(n.name)

   emails_list = []
   emails = User.select()
   for n in emails:
      emails_list.append(n.email)
   if user not in names and email not in emails_list:
         if user not in names and user.__len__() > 6 and user.__len__() <= 20 and pass_.__len__() > 6 and email not in emails_list and email.__len__() > 6 and email.__len__() <= 20:
            session['logged_in'] = True
            session['user'] = user
            stringvazia=' '
            hashed_password = generate_password_hash(pass_, method='pbkdf2:sha256', salt_length=16)
            cf = User.insert(name=user, password=hashed_password, email=email, bio=stringvazia)
            cf.execute()
            
            db.close()
         elif user in names:
            print('ERROR')
            flash('Nome existente!')
            return redirect(url_for('cad'))
         else:
            flash('Erro! os campos devem ter no mínimo 6 caracteres e máximo de 20')
            return redirect(url_for('cad')) 

         return redirect(url_for('home'))
   else:
       flash('Email ou nome já existente!')
       return redirect(url_for('cad'))


if __name__ == '__main__':
   socketio.run(app, debug=True)
   