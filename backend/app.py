from flask import Flask, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
import stripe

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
CORS(app)

stripe.api_key = 'your_stripe_secret_key'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    name = db.Column(db.String(150))

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    description = db.Column(db.String(500))
    price = db.Column(db.Integer)  # price in cents

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({'error': 'User exists'}), 400
    new_user = User(email=data['email'],
                    name=data['name'],
                    password=generate_password_hash(data['password'], method='sha256'))
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data.get('email')).first()
    if not user or not check_password_hash(user.password, data.get('password')):
        return jsonify({'error': 'Invalid credentials'}), 401
    login_user(user)
    return jsonify({'message': f'Welcome {user.name}'}), 200

@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out'}), 200

@app.route('/api/courses', methods=['GET'])
def get_courses():
    courses = Course.query.all()
    return jsonify([{'id': c.id, 'title': c.title, 'description': c.description, 'price': c.price} for c in courses])

@app.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    data = request.json
    course = Course.query.get(data.get('course_id'))
    if not course:
        return jsonify({'error': 'Course not found'}), 404
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {'currency': 'usd', 'product_data': {'name': course.title}, 'unit_amount': course.price},
            'quantity': 1,
        }],
        mode='payment',
        success_url='http://localhost:3000/success',
        cancel_url='http://localhost:3000/cancel',
        customer_email=current_user.email,
    )
    return jsonify({'id': session.id})

if __name__ == '__main__':
    db.create_all()
    if Course.query.count() == 0:
        db.session.add(Course(title="Python for Beginners", description="Learn Python step-by-step.", price=4900))
        db.session.add(Course(title="Data Science Basics", description="Intro to data science.", price=9900))
        db.session.commit()
    app.run(debug=True)
