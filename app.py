from flask import Flask, redirect, url_for, render_template, request, session, flash, Blueprint, g
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from flask_admin import Admin, BaseView, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink
from flask_login import UserMixin, login_user, current_user, LoginManager, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

# twilio not recognized as python module, fix path 
#from twilio.rest import Client

# Your Twilio API credentials
TWILIO_ACCOUNT_SID = " "
TWILIO_AUTH_TOKEN = " "
TWILIO_PHONE_NUMBER = "+18885232483"

app = Flask(__name__)
# this will change before production
app.secret_key = 'mysecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///userv3.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False






#login manager / access control
login_manager = LoginManager()

#redirect to login page if not logged in
login_manager.login_view='auth.login'
login_manager.init_app(app)

from datetime import datetime, timedelta
from flask_login import current_user, logout_user


# This class creates navbar link back to homepage of application from admin page
class MainIndexLink(MenuLink):
    def get_url(self):
        return url_for("home")


#initialize database
with app.app_context():
    db = SQLAlchemy(app)

    class User(db.Model, UserMixin):
        # Basic user info here
        id = db.Column(db.Integer, primary_key=True)
        firstName = db.Column(db.String(120), nullable=False)
        lastName = db.Column(db.String(120), nullable=False)
        username = db.Column(db.String(80), unique=True, nullable=False)
        email = db.Column(db.String(120), unique=True, nullable=False)
        password = db.Column(db.String(120), nullable=False)

        # admin / worker attributes
        is_admin = db.Column(db.Boolean, default=False)
        is_worker = db.Column(db.Boolean, default=False)

        # enter required training below
        laser_training = db.Column(db.Boolean, default=False)



         # return string when access db
        def __repr__(self):
            return '<Name %r>' % self.id


    class MakerspaceStatus(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        is_open = db.Column(db.Boolean, default=False)


    # create a new MakerspaceStatus object
    makerspace_status = MakerspaceStatus(is_open=False)

    # add the object to the database session
    #db.session.add(makerspace_status)

    # commit the changes to the database
    db.session.commit()



    db.create_all()






# allows admin to edit users in DB
# Define a custom base view with admin permission
# only allow signed on admin to view admin DB page
class MyModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('home'))

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

# add main page link to db page, init admin page
admin = Admin(app, index_view=MyAdminIndexView())
admin.add_view(MyModelView(User, db.session))
admin.add_link(MainIndexLink(name="Main Page"))





# access user info to store id of logged-in user
@ login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login')
def login():
    # login html file is called for login

    return render_template("login.html")

@app.route('/people')
def people():
    # login html file is called for login

    return render_template("people.html")

@app.route('/test')
def test():
    makerspace_status = MakerspaceStatus.query.first()
    return render_template('test.html', is_open=makerspace_status.is_open)

@app.route('/test/update_status', methods=['POST'])
@login_required
def update_status():
    makerspace_status = MakerspaceStatus.query.first()
    makerspace_status.is_open = (request.form['is_open'] == 'True')
    db.session.commit()

    return redirect(url_for('test'))


@app.route('/calendly')
def calendar():
    # calendly html file is called for homepage
    return render_template("calendly.html")

@app.route('/contact')
def contact():
    # test html file is called for contact
    return render_template("contact.html")

@app.route('/equipment')
def equipment():
    # login html file is called for login
    return render_template("equipment.html")

@app.route('/information')
def information():
    # login html file is called for login
    return render_template("information.html")

@app.route('/faq')
def faq():
    # test html file is called for about
    return render_template("faq.html")

@app.route('/signup')
def signup():
    # test html file is called for about
    return render_template("signup.html")


@app.route('/signup', methods=['POST', 'GET'])
def signup_post():
    if request.method == 'POST':
        # get the form data
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # check if a user with this email or username already exists
        existing_email = User.query.filter_by(email=email).first()
        existing_username = User.query.filter_by(username=username).first()
        if existing_email or existing_username:
            # flash correct error message and render signup page again
            # this will consider duplicate email, username, or both
            if existing_username and existing_email:
                flash('Both Email and Username are already in use', category='error')
                return render_template('signup.html')
            elif existing_email:
                flash('Email address already in use', category='error')
                return render_template('signup.html')
            else:
                flash('Username already exists', category='error')
                return render_template('signup.html')

            # add password length field

        # create a new user
        user = User(firstName=firstName, lastName=lastName, username=username, email=email, password=generate_password_hash(password, method='sha256'))
        db.session.add(user)
        db.session.commit()
        flash('User created successfully')
        return redirect(url_for('login'))

    else:
        return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login_post():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user:
            # check hashed password
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                # Make session permanent
                flash("Login Successful!")
                return redirect(url_for("home"))

        else:
            flash("Invalid email or password")
            return redirect(url_for("login"))



@app.route('/forgotPassword')
def forgotPassword():
    # index html file is called for homepage
    return render_template("forgotpassword.html")

@app.route('/emergency')
def emergency():
    return render_template("emergency.html")

# pop user from session
# flash a messaged saying you have successfully logged out
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have successfully logged out!")
    return redirect(url_for("home"))


@app.route("/send_message", methods=["POST"])
def send_message():
    current_user = request.form["current_user"]
    recipients = ["+1234567890", "+0987654321"]  # Replace these with the actual phone numbers
    message = f"{current_user} has pressed the button."

    send_sms(recipients, message)
    return redirect(url_for("index"))

def send_sms(recipients, message):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    for recipient in recipients:
        client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=recipient
        )

if __name__ == '__main__':
    # change host to ip4 address for mobile view
    app.run(debug=True, host = '0.0.0.0', port=8000)
