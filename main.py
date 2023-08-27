from flask import Blueprint, render_template
from flask_login import login_required
from flask_login import login_required, current_user

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('main-page.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('profile-page.html', name=current_user.name)

@main.route('/discover')
def discover():
    return render_template('discover-page.html')
