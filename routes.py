from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required , current_user
from .models import User ,  groups_table , Achievements , Post , IdentifiedPlant , CarePlan
from . import db

routes = Blueprint('routes', __name__)

@routes.route('/scoreboard')
def scoreboard():
    # Fetch all users from the database and order them by identification count in descending order
    users = User.query.order_by(User.identification_count.desc()).all()
    
    # Render the scoreboard template with the users data
    return render_template('scoreboard.html', users=users)
@routes.route('/achievements')
@login_required
def achievements():
    all_achievements = Achievements.query.all()
    user_achievements = current_user.achievements

    # Check achievements based on identification count
    identification_count = current_user.identification_count

    beginner_achievement = check_achievement(current_user, "Beginner", 5)
    intermediate_achievement = check_achievement(current_user, "Intermediate", 10)
    advanced_achievement = check_achievement(current_user, "Advanced", 15)
    expert_achievement = check_achievement(current_user, "Expert", 20)
    master_achievement = check_achievement(current_user, "Master", 25)

    return render_template('achievements.html', all_achievements=all_achievements, user_achievements=user_achievements)

@routes.route("/profile")
def profile():
    return render_template("profile-page.html")

@routes.route("/discover")
def discover():
    return render_template("discover-page.html")

@routes.route("/search")
def search():
    return render_template("Search-Groups.html")

@routes.route('/groups', methods=['GET', 'POST'])
@login_required
def view_groups():
    if request.method == 'POST':
        group_id = request.form.get('group_id')
        group = groups_table.query.get(group_id)

        if group:
            if current_user in group.users:
                flash('You are already a member of this group.')
            else:
                group.users.append(current_user)
                db.session.commit()
                flash('You have joined the group successfully.')
        else:
            flash('Group does not exist.')

    groups = groups_table.query.all()
    return render_template('Groups-view.html', groups=groups)

@routes.route('/groups/create', methods=['GET', 'POST'])
@login_required
def create_group():
    if request.method == 'POST':
        
        group_name = request.form['group-name']
        description = request.form['group-description']
        country = request.form['select-country']
        
        
        new_group = groups_table(group_name=group_name, description=description , country = country)
        new_group.users.append(current_user)
        
        
        db.session.add(new_group)
        db.session.commit()
        
        
        newly_created_group_id = new_group.id
        
        #return redirect(url_for('group_details', group_id=newly_created_group_id))
        return redirect(url_for('main.profile'))
    
    
    return render_template('Groups-create.html')

@routes.route('/groups/<int:group_id>')
@login_required
def group_profile(group_id):
    group = groups_table.query.get(group_id)

    #if not group:
        #abort(404)

    if current_user not in group.users:
        flash("You are not a member of this group.")
        return redirect(url_for('routes.view_groups'))

    posts = Post.query.filter_by(group_id=group_id).all()

    return render_template('group_profile.html', group=group, posts=posts)

@routes.route('/create_post/<int:group_id>', methods=['POST'])
@login_required
def create_post(group_id):
    content = request.form.get('content')
    group = groups_table.query.get(group_id)
    
    if content:
        post = Post(content=content, group_id=group_id, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        flash('Post created successfully.', 'success')
    else:
        flash('Post content cannot be empty.', 'danger')
    
    return redirect(url_for('routes.group_profile', group_id=group_id))


@routes.route('/profile/myplants')
@login_required
def my_plants():
    user_plants = IdentifiedPlant.query.filter_by(user_id=current_user.id).all()
    return render_template('my_plants.html', user_plants=user_plants)

@routes.route('/profile/myplants/<int:plant_id>')
@login_required
def my_plant_details(plant_id):
    plant = IdentifiedPlant.query.get(plant_id)
    
    if not plant or plant.user_id != current_user.id:
        #flash('Plant not found.', 'error')
        return redirect(url_for('routes.my_plants'))
    
    return render_template('my_plant_details.html', plant=plant)


@routes.route('/profile/myplants/<int:plant_id>/add-care-plan', methods=['GET', 'POST'])
@login_required
def add_care_plan(plant_id):
    plant = IdentifiedPlant.query.get(plant_id)

    if not plant or plant.user_id != current_user.id:
        flash('Plant not found.')
        return redirect(url_for('routes.my_plants'))

    if request.method == 'POST':
        plan_name = request.form.get('plan_name')
        light = request.form.get('light')
        last_watered = request.form.get('last_watered')
        pot_height = float(request.form.get('pot_height'))
        pot_diameter = float(request.form.get('pot_diameter'))

        water_amount = 0
        fertilize_interval = ""

        # Calculate water amount based on light type
        if light == 'option1':
            water_amount = 30
        elif light == 'option2':
            water_amount = 20
        elif light == 'option3':
            water_amount = 10
        elif light == 'option4':
            water_amount = 5

        # Calculate fertilize interval based on pot size
        pot_size = pot_height * pot_diameter
        if pot_size > 100:
            fertilize_interval = "every month"
        elif 50 <= pot_size <= 100:
            fertilize_interval = "every week"
        elif pot_size < 50:
            fertilize_interval = "every 2 days"

        # Create and store the care plan in the database
        care_plan = CarePlan(plant_id=plant.id, water_amount=water_amount, fertilize_interval=fertilize_interval, plan_name=plan_name)
        db.session.add(care_plan)
        db.session.commit()

        flash('Care plan added successfully.', 'success')
        return redirect(url_for('routes.my_plant_details', plant_id=plant_id))

    return render_template('Smart_Care.html', plant=plant)



@routes.route("/identification")
def identification():
    return render_template("identification-page.html")

@routes.route("/register")
def register():
    return render_template("register-page.html")

@routes.route('/login')
def login():
    return render_template('login-page.html')

@routes.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('routes.login'))

    login_user(user, remember=remember)
    return redirect(url_for('main.profile'))

@routes.route('/signup')
def signup():
    return render_template('register-page.html')

@routes.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    confirm_password = request.form.get("confirm-password")

    user = User.query.filter_by(email=email).first()

    if user:
        flash('Email address already exists.')
        return redirect(url_for('routes.register'))
    
    if password != confirm_password:
       flash("Confirmation password does not mactch with password.")
       return redirect(url_for('routes.register'))
    
    new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))

    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('routes.login'))

@routes.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

def check_achievement(user, achievement_name, identification_count_threshold):
    if user.identification_count >= identification_count_threshold:
        achievement = Achievements.query.filter_by(name=achievement_name).first()
        if achievement not in user.achievements:
            user.achievements.append(achievement)
            db.session.commit()
            return True
    return False

