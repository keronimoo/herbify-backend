from flask_login import UserMixin
from . import db
from datetime import datetime


# Intermediate table for the many-to-many relationship
memberships = db.Table('memberships',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('group_id', db.Integer, db.ForeignKey('groups_table.id'), primary_key=True)
)
# Intermediate table for the many-to-many relationship with achievements
user_achievements = db.Table('user_achievements',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('achievement_id', db.Integer, db.ForeignKey('achievements.id'), primary_key=True)
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    identification_count = db.Column(db.Integer, default=0)
    # Define the many-to-many relationship with achievements
    #achievements = db.relationship('Achievements', secondary='user_achievements', backref=db.backref('users', lazy='dynamic'))
    achievements = db.relationship('Achievements', secondary=user_achievements, backref=db.backref('users', lazy='dynamic'), lazy='dynamic')
    identified_plants = db.relationship('IdentifiedPlant', backref='user', lazy='dynamic')
    def get_id(self):
        return (self.id)

class groups_table(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    country = db.Column(db.String(100), nullable=False)  # the country 
    # Define the many-to-many relationship
    users = db.relationship('User', secondary=memberships, backref=db.backref('groups', lazy='dynamic'))
    posts = db.relationship('Post', backref='group', lazy='dynamic')
    
    def get_id(self):
        return (self.id)
    
class Achievements(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.Text)

    def get_id(self):
        return (self.id)
    
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups_table.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('posts', lazy='dynamic'))



class IdentifiedPlant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    plant_name = db.Column(db.String(100), nullable=False)
    date_identified = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    care_plans = db.relationship('CarePlan', backref='identified_plant', lazy='dynamic')
    def get_id(self):
        return self.id
    
class CarePlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plant_id = db.Column(db.Integer, db.ForeignKey('identified_plant.id'), nullable=False)
    water_amount = db.Column(db.Integer, nullable=False)
    fertilize_interval = db.Column(db.String(100), nullable=False)
    plan_name = db.Column(db.String(100), nullable=False)
    def get_id(self):
        return self.id