import os
import psycopg2
from flask import Flask, render_template, redirect, url_for, request, jsonify, g
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from collective.models import Person, Collective, Project, Skill, BelongsTo, Possesses, Participates, Organizes, Requires, CollectiveMessage, ProjectMessage, Database, Location
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime;
import re


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['DATABASE_URL'] = 'postgresql://pacollective:mynameispa@localhost/collective'

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Person.get_by_id(user_id)

@app.template_filter('short_timestamp')
def short_timestamp_filter(timestamp):
    return timestamp.strftime('%Y-%m-%d %H:%M')

# Ensure the filter is registered with the app
app.jinja_env.filters['short_timestamp'] = short_timestamp_filter

@app.teardown_appcontext
def close_db(exception):
    Database.close_db()

@app.route('/')
def startup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template('startup.html')

@app.route('/home')
@login_required
def home():
    user_id = current_user.id
    user = Person.get_by_id(user_id)
    collectives = BelongsTo.get_collectives_for_user(user_id)
    projects = Participates.get_projects_for_user(user_id)
    skills = Possesses.get_skills_for_user(user_id)
    return render_template('home.html', user=user, collectives=collectives, projects=projects, skills = skills)

@app.route('/<string:username>')
@login_required
def profilePage(username):
    user = Person.get_by_username(username)
    if not user:
        print(f"User with username={username} not found")
        return "User not found", 404
    current_username = current_user.username
    if(username == current_username):
        return redirect(url_for('home'))
    collectives = BelongsTo.get_collectives_for_user(user.id)
    projects = Participates.get_projects_for_user(user.id)
    skills = Possesses.get_skills_for_user(user.id)
    return render_template('user.html', user=user, collectives=collectives, projects=projects, skills = skills)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = current_user
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        username = request.form['username']
        bio = request.form['bio']
        location = request.form['location']
        existing_skills = request.form.getlist('existing_skills')
        new_skill_name = request.form.get('new_skill_name')
        new_skill_description = request.form.get('new_skill_description')

        Database.execute(
            "UPDATE persons SET name = %s, email = %s, username = %s, bio = %s, location = %s WHERE id = %s",
            (name, email, username, bio, location, user.id)
        )

        # Remove all existing skills
        Database.execute(
            "DELETE FROM possesses WHERE person_id = %s",
            (user.id,)
        )

        # Add existing skills to the user
        for skill_id in existing_skills:
            Database.execute(
                "INSERT INTO possesses (person_id, skill_id) VALUES (%s, %s)",
                (user.id, skill_id)
            )

        # Add new skill to the user if provided
        if new_skill_name:
            skill = Skill.get_by_name(new_skill_name)
            if not skill:
                skill_id = Skill.create(new_skill_name, new_skill_description)
            else:
                skill_id = skill.id
            Database.execute(
                "INSERT INTO possesses (person_id, skill_id) VALUES (%s, %s)",
                (user.id, skill_id)
            )

        return redirect(url_for('home'))

    skills = Skill.get_all()
    user_skill_ids = [skill.id for skill in Possesses.get_skills_for_user(user.id)]
    return render_template('profile.html', user=user, skills=skills, user_skill_ids=user_skill_ids)

def is_valid_password(password):
    if re.search(r'[A-Za-z]', password) and re.search(r'\d', password):
        return True
    return False

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        isPasswordApproved = True
        isPasswordApproved = is_valid_password(request.form['password'])
        if (isPasswordApproved):
            password = request.form['password']
        else:
            return render_template('register.html', isPasswordApproved=isPasswordApproved)
            # return redirect(url_for('register'))
        name = request.form['name']
        email = request.form['email']
        username = request.form['username']
        bio = request.form['bio']
        location = request.form['location']
        existing_skills = request.form.getlist('existing_skills')
        new_skill_name = request.form.get('new_skill_name')
        new_skill_description = request.form.get('new_skill_description')

        user_id = Person.create(name, email, username, password, bio, location)
        
        # Add existing skills to the user
        for skill_id in existing_skills:
            Database.execute(
                "INSERT INTO possesses (person_id, skill_id) VALUES (%s, %s)",
                (user_id, skill_id)
            )

        # Add new skill to the user if provided
        if new_skill_name:
            skill = Skill.get_by_name(new_skill_name)
            if not skill:
                skill_id = Skill.create(new_skill_name, new_skill_description)
            else:
                skill_id = skill.id
            Database.execute(
                "INSERT INTO possesses (person_id, skill_id) VALUES (%s, %s)",
                (user_id, skill_id)
            )

        return redirect(url_for('login'))

    skills = Skill.get_all()
    return render_template('register.html', skills=skills)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Person.get_by_username(username)
        if user is None:
            error = 'User does not exist.'
        elif not check_password_hash(user.password, password):
            error = 'Incorrect password.'
        else:
            login_user(user)
            return redirect(url_for('home'))
    return render_template('login.html', error=error)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('startup'))

@app.route('/browse_collectives')
def browse_collectives():
    print("Accessing browse_collectives route")
    collectives = Collective.get_all()
    logged_in = current_user.is_authenticated
    for collective in collectives:
        print(f"Collective: id={collective.id}, name={collective.name}, description={collective.description}")
    if logged_in:
        print("User is logged in")
    else:
        print("User is not logged in")
    return render_template('browse_collectives.html', collectives=collectives, logged_in=logged_in, locations = Location.get_unique_locations(), collectives_empty = len(collectives) == 0)

@app.route('/filter_collectives_by_location/<location>')
def filter_collectives_by_location(location):
    collectives = Collective.get_collectives_by_location(location)
    logged_in = current_user.is_authenticated
    return render_template('browse_collectives.html', collectives=collectives, logged_in=logged_in, locations=Location.get_unique_locations(), collectives_empty = len(collectives) == 0)

@app.route('/browse_projects')
def browse_projects():
    projects = Project.get_all()
    project_ids = [project.id for project in projects]
    collectives_for_projects = {
        project_id: Organizes.get_collectives_for_project(project_id)
        for project_id in project_ids}
    logged_in = current_user.is_authenticated
    for project in projects:
        print(f"Project: id={project.id}, name={project.name}, description={project.description}")
    if logged_in:
        print("User is logged in")
    else:
        print("User is not logged in")
    return render_template('browse_projects.html', projects=projects, logged_in=logged_in, skills = Skill.get_all(), collectives_for_projects=collectives_for_projects, projects_empty = len(projects) == 0)

@app.route('/filter_projects_by_skill/<skill_id>')
def filter_projects_by_skill(skill_id):
    projects = Requires.get_projects_for_skill(skill_id)
    project_ids = [project.id for project in projects]
    collectives_for_projects = {
        project_id: Organizes.get_collectives_for_project(project_id)
        for project_id in project_ids}
    logged_in = current_user.is_authenticated
    return render_template('browse_projects.html', projects=projects, logged_in=logged_in, skills = Skill.get_all(), collectives_for_projects=collectives_for_projects, projects_empty = len(projects) == 0)

@app.route('/create_collective', methods=['GET', 'POST'])
@login_required
def create_collective():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        location = request.form['location']
        collective_id = Collective.create(name, description, location)
        BelongsTo.create(current_user.id, collective_id)
        return redirect(url_for('collective_home',collective_id=collective_id))
    return render_template('create_collective.html')

@app.route('/collective/<int:collective_id>/create_project', methods=['GET', 'POST'])
@login_required
def create_project(collective_id):
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        existing_skills = request.form.getlist('existing_skills')
        new_skill_name = request.form.get('new_skill_name')
        new_skill_description = request.form.get('new_skill_description')
        project_id = Project.create(name, description)
        Participates.create(current_user.id, project_id)
        
        # Link the project to the main collective
        Database.execute(
            "INSERT INTO organizes (collective_id, project_id) VALUES (%s, %s)",
            (collective_id, project_id)
        )
        
        # Link the project to the selected co-hosting collectives
        co_hosting_collectives = request.form.getlist('collectives')
        for co_collective_id in co_hosting_collectives:
            Database.execute(
                "INSERT INTO organizes (collective_id, project_id) VALUES (%s, %s)",
                (co_collective_id, project_id)
            )
        
        # Add existing skills to the project
        for skill_id in existing_skills:
            Database.execute(
                "INSERT INTO requires (project_id, skill_id) VALUES (%s, %s)",
                (project_id, skill_id)
            )

        # Add new skill to the project if provided
        if new_skill_name:
            skill = Skill.get_by_name(new_skill_name)
            if not skill:
                skill_id = Skill.create(new_skill_name, new_skill_description)
            else:
                skill_id = skill.id
            Database.execute(
                "INSERT INTO requires (project_id, skill_id) VALUES (%s, %s)",
                (project_id, skill_id)
            )
            
        return redirect(url_for('collective_home', collective_id=collective_id))
    
    skills = Skill.get_all()
    all_collectives = Collective.get_all()
    return render_template('create_project.html', collective_id=collective_id, all_collectives=all_collectives, skills=skills)

@app.route('/collective/<int:collective_id>/post_message', methods=['POST'])
@login_required
def post_collective_message(collective_id):
    user_name = current_user.username
    message_content = request.form['message']
    CollectiveMessage.create(collective_id, user_name, message_content)
    return redirect(url_for('collective_home', collective_id=collective_id))

@app.route('/project/<int:project_id>/post_message', methods=['POST'])
@login_required
def post_project_message(project_id):
    user_name = current_user.username
    message_content = request.form['message']
    ProjectMessage.create(project_id, user_name, message_content)
    return redirect(url_for('project_home', project_id=project_id))

@app.route('/collective/<int:collective_id>')
@login_required
def collective_home(collective_id):
    print(f"Accessing collective_home route with id={collective_id}")
    collective = Collective.get_by_id(collective_id)
    if not collective:
        print(f"Collective with id={collective_id} not found")
        return "Collective not found", 404
    is_member = BelongsTo.is_member(current_user.id, collective_id)
    members = BelongsTo.get_members(collective.id)
    print(f"User is {'a member' if is_member else 'not a member'} of collective {collective_id}")
    projects = Organizes.get_projects_for_collective(collective_id) if is_member else []
    project_ids = [project.id for project in projects]
    collectives_for_projects = {
        project_id: Organizes.get_collectives_for_project(project_id)
        for project_id in project_ids}
    messages = CollectiveMessage.get_messages(collective_id) if is_member else []
    return render_template('collective_home.html', collective=collective, is_member=is_member, projects=projects, messages=messages,members=members, collectives_for_projects = collectives_for_projects)

@app.route('/project/<int:project_id>')
@login_required
def project_home(project_id):
    print(f"Accessing project_home route with id={project_id}")
    project = Project.get_by_id(project_id)
    if not project:
        print(f"Project with id={project_id} not found")
        return "Project not found", 404
    is_member = Participates.is_member(current_user.id, project_id)
    members = BelongsTo.get_members(project_id)
    collectives = Organizes.get_collectives_for_project(project_id)
    skills = Requires.get_skills_for_project(project_id)
    print(f"User is {'a participant' if is_member else 'not a participant'} of project {project_id}")
    messages = ProjectMessage.get_messages(project_id) if is_member else []
    return render_template('project_home.html', project=project, is_member=is_member, messages=messages, collectives= collectives, skills=skills, members=members)

# Route to join a collective
@app.route('/collective/<int:collective_id>/join', methods=['POST'])
@login_required
def join_collective(collective_id):
    user_id = current_user.id
    if not BelongsTo.is_member(user_id, collective_id):
        Database.execute(
            "INSERT INTO belongs_to (person_id, collective_id) VALUES (%s, %s)",
            (user_id, collective_id)
        )
    return redirect(url_for('collective_home', collective_id=collective_id))

# Route to join a project
@app.route('/project/<int:project_id>/join', methods=['POST'])
@login_required
def join_project(project_id):
    user_id = current_user.id
    if not Participates.is_member(user_id, project_id):
        Database.execute(
            "INSERT INTO participates (person_id, project_id) VALUES (%s, %s)",
            (user_id, project_id)
        )
    return redirect(url_for('project_home', project_id=project_id))

@app.route('/delete_profile', methods=['POST'])
@login_required
def delete_profile():
    user_id = current_user.id
    Database.execute("DELETE FROM persons WHERE id = %s", (user_id,))
    logout_user()
    return redirect(url_for('startup'))

@app.route('/collective/<int:collective_id>/delete', methods=['POST'])
@login_required
def delete_collective(collective_id):
    user_id = current_user.id
    if BelongsTo.is_member(user_id, collective_id):
        Database.execute("DELETE FROM collectives WHERE id = %s", (collective_id,))
        Database.execute("DELETE FROM belongs_to WHERE collective_id = %s", (collective_id,))
        Database.execute("DELETE FROM organizes WHERE collective_id = %s", (collective_id,))
        Database.execute("DELETE FROM collective_messages WHERE collective_id = %s", (collective_id,))
    return redirect(url_for('home'))

@app.route('/project/<int:project_id>/delete', methods=['POST'])
@login_required
def delete_project(project_id):
    user_id = current_user.id
    if Participates.is_member(user_id, project_id):
        Database.execute("DELETE FROM projects WHERE id = %s", (project_id,))
        Database.execute("DELETE FROM participates WHERE project_id = %s", (project_id,))
        Database.execute("DELETE FROM organizes WHERE project_id = %s", (project_id,))
        Database.execute("DELETE FROM project_messages WHERE project_id = %s", (project_id,))
    return redirect(url_for('home'))

@app.route('/collective/<int:collective_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_collective(collective_id):
    user_id = current_user.id
    if not BelongsTo.is_member(user_id, collective_id):
        return redirect(url_for('home'))
    collective = Collective.get_by_id(collective_id)
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        location = request.form['location']
        Database.execute(
            "UPDATE collectives SET name = %s, description = %s, location = %s WHERE id = %s",
            (name, description, location, collective_id)
        )
        return redirect(url_for('collective_home', collective_id=collective_id))
    
    return render_template('edit_collective.html', collective=collective)

@app.route('/project/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    user_id = current_user.id
    project = Project.get_by_id(project_id)
    
    if not project or not Participates.is_member(user_id, project_id):
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        existing_skills = request.form.getlist('existing_skills')
        new_skill_name = request.form.get('new_skill_name')
        new_skill_description = request.form.get('new_skill_description')
        Database.execute(
            "UPDATE projects SET name = %s, description = %s WHERE id = %s",
            (name, description, project_id)
        )
        
        # Update co-hosting collectives
        Database.execute("DELETE FROM organizes WHERE project_id = %s", (project_id,))
        co_hosting_collectives = request.form.getlist('collectives')
        for co_collective_id in co_hosting_collectives:
            Database.execute(
                "INSERT INTO organizes (collective_id, project_id) VALUES (%s, %s)",
                (co_collective_id, project_id)
            )
        # Remove all existing skills
        Database.execute(
            "DELETE FROM requires WHERE project_id = %s",
            (project_id,)
        )

        # Add existing skills to the project
        for skill_id in existing_skills:
            Database.execute(
                "INSERT INTO requires (project_id, skill_id) VALUES (%s, %s)",
                (project_id, skill_id)
            )

        # Add new skill to the project if provided
        if new_skill_name:
            skill = Skill.get_by_name(new_skill_name)
            if not skill:
                skill_id = Skill.create(new_skill_name, new_skill_description)
            else:
                skill_id = skill.id
            Database.execute(
                "INSERT INTO requires (project_id, skill_id) VALUES (%s, %s)",
                (project_id, skill_id)
            )
        
        return redirect(url_for('project_home', project_id=project_id))
    
    skills = Skill.get_all()
    project_skill_ids = [skill.id for skill in Requires.get_skills_for_project(project_id= project.id)]
    all_collectives = Collective.get_all()
    project.collective_ids = [c.id for c in Organizes.get_collectives_for_project(project.id)]
    return render_template('edit_project.html', project=project, all_collectives=all_collectives,skills=skills, project_skill_ids=project_skill_ids)

@app.route('/profile/add_skill', methods=['GET', 'POST'])
@login_required
def add_skill():
    if request.method == 'POST':
        existing_skill_id = request.form.get('existing_skill')
        skill_name = request.form.get('skill_name')
        skill_description = request.form.get('skill_description')

        if existing_skill_id:
            skill_id = existing_skill_id
        else:
            # Check if the skill already exists
            skill = Skill.get_by_name(skill_name)
            if not skill:
                # Create the new skill if it doesn't exist
                skill_id = Skill.create(skill_name, skill_description)
            else:
                skill_id = skill.id

        # Add the skill to the user's profile
        Database.execute(
            "INSERT INTO possesses (person_id, skill_id) VALUES (%s, %s)",
            (current_user.id, skill_id)
        )
        
        return redirect(url_for('profile'))

    skills = Skill.get_all()
    return render_template('add_skill.html', skills=skills)

@app.route('/project/<int:project_id>/add_skill', methods=['GET', 'POST'])
@login_required
def add_project_skill(project_id):
    if request.method == 'POST':
        existing_skill_id = request.form.get('existing_skill')
        skill_name = request.form.get('skill_name')
        skill_description = request.form.get('skill_description')

        if existing_skill_id:
            skill_id = existing_skill_id
        else:
            # Check if the skill already exists
            skill = Skill.get_by_name(skill_name)
            if not skill:
                # Create the new skill if it doesn't exist
                skill_id = Skill.create(skill_name, skill_description)
            else:
                skill_id = skill.id

        # Add the skill to the project's requirements
        Database.execute(
            "INSERT INTO requires (project_id, skill_id) VALUES (%s, %s)",
            (project_id, skill_id)
        )
        
        return redirect(url_for('project_home', project_id=project_id))

    skills = Skill.get_all()
    return render_template('add_project_skill.html', skills=skills, project_id=project_id)


if __name__ == "__main__":
    print("Starting Flask application...")
    app.run(debug=True)