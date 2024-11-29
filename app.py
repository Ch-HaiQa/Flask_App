import os
from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from io import BytesIO
from xhtml2pdf import pisa

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Portfolio model to store user data
class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    profile_picture = db.Column(db.String(200), nullable=False)
    bio = db.Column(db.Text, nullable=False)

# Home route - Create Portfolio
@app.route('/')
def home():
    return render_template('home.html')

# Create Portfolio form route
@app.route('/create-portfolio', methods=['GET', 'POST'])
def create_portfolio():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone = request.form['phone']
        profile_picture = request.form['profile_picture']  # Save the selected image
        bio = request.form['bio']

        new_portfolio = Portfolio(first_name=first_name, last_name=last_name, email=email, phone=phone, profile_picture=profile_picture, bio=bio)
        db.session.add(new_portfolio)
        db.session.commit()

        return redirect(url_for('view_portfolio'))

    # Get available images from the static/images folder
    image_folder = os.path.join(app.static_folder, 'images')
    images = os.listdir(image_folder)  # List all images in the folder
    images = [f'images/{img}' for img in images]  # Create relative paths

    return render_template('create_portfolio.html', images=images)

# View Portfolio page
@app.route('/view-portfolio')
def view_portfolio():
    portfolio = Portfolio.query.order_by(Portfolio.id.desc()).first()
    return render_template('portfolio.html', portfolio=portfolio)

# Download Portfolio as PDF
@app.route('/portfolio/pdf')
def portfolio_pdf():
    portfolio = Portfolio.query.order_by(Portfolio.id.desc()).first()
    # Render HTML with correct image URL
    html = render_template('portfolio.html', portfolio=portfolio)
    
    # Convert the HTML to PDF
    pdf = BytesIO()
    pisa_status = pisa.CreatePDF(BytesIO(html.encode("UTF-8")), dest=pdf)

    if not pisa_status.err:
        pdf.seek(0)
        return send_file(pdf, mimetype='application/pdf', as_attachment=True, download_name='portfolio.pdf')
    else:
        return "Error generating PDF"

# Custom Use Case Page (Contact Form as example)
@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
