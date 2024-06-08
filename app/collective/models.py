from flask import current_app, g
from flask_login import UserMixin
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash

class Database:
    @staticmethod
    def get_db():
        if 'db' not in g:
            try:
                g.db = psycopg2.connect(current_app.config['DATABASE_URL'])
                print("Database connection established.")
            except Exception as e:
                print(f"Error establishing database connection: {e}")
        return g.db

    @staticmethod
    def close_db(e=None):
        db = g.pop('db', None)
        if db is not None:
            db.close()
            print("Database connection closed.")

    @staticmethod
    def query(query, params=None):
        conn = Database.get_db()
        cursor = None
        try:
            cursor = conn.cursor()
            print(f"Executing query: {query} with params: {params}")
            cursor.execute(query, params)
            conn.commit()
            return cursor
        except Exception as e:
            print(f"Database query error: {e}")
            raise
        # finally:
        #     if cursor:
        #         cursor.close()

    @staticmethod
    def execute(query, params=None):
        conn = Database.get_db()
        cursor = None
        try:
            cursor = conn.cursor()
            print(f"Executing query: {query} with params: {params}")
            cursor.execute(query, params)
            conn.commit()
        except Exception as e:
            print(f"Database execute error: {e}")
            raise
        # finally:
        #     if cursor:
        #         cursor.close()

    @staticmethod
    def fetchone(query, params=None):
        conn = Database.get_db()
        cursor = None
        try:
            cursor = conn.cursor()
            print(f"Executing query: {query} with params: {params}")
            cursor.execute(query, params)
            result = cursor.fetchone()
            print(f"Query result: {result}")
            return result
        except Exception as e:
            print(f"Database fetchone error: {e}")
            raise
        # finally:
        #     if cursor:
        #         cursor.close()

    @staticmethod
    def fetchall(query, params=None):
        conn = Database.get_db()
        cursor = None
        try:
            cursor = conn.cursor()
            print(f"Executing query: {query} with params: {params}")
            cursor.execute(query, params)
            results = cursor.fetchall()
            print(f"Query results: {results}")
            return results
        except Exception as e:
            print(f"Database fetchall error: {e}")
            raise
        # finally:
        #     if cursor:
        #         cursor.close()

class Person(UserMixin):
    def __init__(self, id, name, email, username, password, bio, location):
        self.id = id
        self.name = name
        self.email = email
        self.username = username
        self.password = password
        self.bio = bio
        self.location = location

    @staticmethod
    def get_by_id(user_id):
        result = Database.fetchone("SELECT * FROM persons WHERE id = %s", (user_id,))
        return Person(*result) if result else None

    @staticmethod
    def get_by_username(username):
        result = Database.fetchone("SELECT * FROM persons WHERE username = %s", (username,))
        return Person(*result) if result else None

    @staticmethod
    def create(name, email, username, password, bio, location):
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        Database.query(
            "INSERT INTO persons (name, email, username, password, bio, location) VALUES (%s, %s, %s, %s, %s, %s)",
            (name, email, username, hashed_password, bio, location)
        )
        result = Database.fetchone("SELECT * FROM persons WHERE username = %s", (username,))
        return Person(*result).id if result else None

    @staticmethod
    def update(user_id, name, email, bio, location):
        Database.query(
            "UPDATE persons SET name = %s, email = %s, bio = %s, location = %s WHERE id = %s",
            (name, email, bio, location, user_id)
        )

class Project:
    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description

    @staticmethod
    def create(name, description):
        cursor = Database.query(
            "INSERT INTO projects (name, description) VALUES (%s, %s) RETURNING id",
            (name, description)
        )
        project_id = cursor.fetchone()[0]
        return project_id

    @staticmethod
    def get_all():
        results = Database.fetchall("SELECT id, name, description FROM projects")
        return [Project(*row) for row in results]

class Collective:
    def __init__(self, id, name, description, location):
        self.id = id
        self.name = name
        self.description = description
        self.location = location

    @staticmethod
    def create(name, description, location):
        result = Database.query(
            "INSERT INTO collectives (name, description, location) VALUES (%s, %s, %s) RETURNING id",
            (name, description, location)
        )
        collective_id = result.fetchone()[0]
        return collective_id

    @staticmethod
    def get_all():
        results = Database.fetchall("SELECT id, name, description, location FROM collectives")
        return [Collective(*row) for row in results]

    @staticmethod
    def get_by_id(collective_id):
        print(f"Fetching collective with id={collective_id}")
        result = Database.fetchone("SELECT id, name, description, location FROM collectives WHERE id = %s", (collective_id,))
        if result:
            print(f"Collective found: {result}")
            return Collective(*result)
        print("Collective not found")
        return None
    
    @staticmethod
    def get_collectives_by_location(location):
        # Query collectives by location from the database
        results = Database.fetchall("SELECT * FROM collectives WHERE location LIKE %s", (f'%{location}%',))
        return [Collective(*row) for row in results]
    
class Project:
    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description

    @staticmethod
    def create(name, description):
        result = Database.query(
            "INSERT INTO projects (name, description) VALUES (%s, %s) RETURNING id",
            (name, description)
        )
        project_id = result.fetchone()[0]
        return project_id
    
    @staticmethod
    def get_by_id(project_id):
        print(f"Fetching project with id={project_id}")
        result = Database.fetchone("SELECT id, name, description FROM projects WHERE id = %s", (project_id,))
        if result:
            print(f"Project found: {result}")
            return Project(*result)
        print("Project not found")
        return None
    
    @staticmethod
    def get_all():
        results = Database.fetchall("SELECT id, name, description FROM projects")
        return [Project(*row) for row in results]

class Skill:
    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description

    @staticmethod
    def create(name, description):
        result = Database.fetchone(
            "INSERT INTO skills (name, description) VALUES (%s, %s) RETURNING id",
            (name, description)
        )
        return result[0]

    @staticmethod
    def get_by_name(name):
        result = Database.fetchone("SELECT id, name, description FROM skills WHERE name = %s", (name,))
        if result:
            return Skill(*result)
        return None

    @staticmethod
    def get_all():
        results = Database.fetchall("SELECT id, name, description FROM skills")
        return [Skill(*row) for row in results]


class BelongsTo:
    @staticmethod
    def create(person_id, collective_id):
        Database.query(
            "INSERT INTO belongs_to (person_id, collective_id) VALUES (%s, %s)",
            (person_id, collective_id)
        )

    @staticmethod
    def is_member(person_id, collective_id):
        result = Database.fetchone(
            "SELECT 1 FROM belongs_to WHERE person_id = %s AND collective_id = %s",
            (person_id, collective_id)
        )
        return result is not None

    @staticmethod
    def get_collectives_for_user(person_id):
        results = Database.fetchall(
            "SELECT c.id, c.name, c.description, c.location FROM collectives c JOIN belongs_to b ON c.id = b.collective_id WHERE b.person_id = %s",
            (person_id,)
        )
        return [Collective(*row) for row in results]
    
    @staticmethod
    def get_members(collective_id):
        results = Database.fetchall(
            "SELECT c.id, c.name, c.email, c.username, c.password, c.bio, c.location FROM persons c JOIN belongs_to b ON c.id = b.person_id WHERE b.collective_id = %s",
            (collective_id,))
        return [Person(*row) for row in results]

class Possesses:
    @staticmethod
    def create(person_id, skill_id):
        Database.query("INSERT INTO possesses (person_id, skill_id) VALUES (%s, %s)",
                       (person_id, skill_id))
        
    @staticmethod
    def get_skills_for_user(person_id):
        results =  Database.fetchall(
            "SELECT s.id, s.name, s.description FROM skills s JOIN possesses po ON s.id = po.skill_id WHERE po.person_id = %s",
            (person_id,)
        )
        return [Project(*row) for row in results]

class Participates:
    @staticmethod
    def create(person_id, project_id):
        Database.query(
            "INSERT INTO participates (person_id, project_id) VALUES (%s, %s)",
            (person_id, project_id)
        )

    @staticmethod
    def is_member(person_id, project_id):
        result = Database.fetchone(
            "SELECT 1 FROM participates WHERE person_id = %s AND project_id = %s",
            (person_id, project_id)
        )
        return result is not None

    @staticmethod
    def get_projects_for_user(person_id):
        results =  Database.fetchall(
            "SELECT p.id, p.name, p.description FROM projects p JOIN participates pa ON p.id = pa.project_id WHERE pa.person_id = %s",
            (person_id,)
        )
        return [Project(*row) for row in results]
    
class Organizes:
    @staticmethod
    def create(collective_id, project_id):
        Database.query("INSERT INTO organizes (collective_id, project_id) VALUES (%s, %s)",
                       (collective_id, project_id))
        
    @staticmethod
    def get_projects_for_collective(collective_id):
        results = Database.fetchall(
            "SELECT p.id, p.name, p.description FROM projects p JOIN organizes o ON p.id = o.project_id WHERE o.collective_id = %s",
            (collective_id,)
        )
        return [Project(*row) for row in results]
    
    @staticmethod
    def get_collectives_for_project(project_id):
        results = Database.fetchall(
            "SELECT c.id, c.name, c.description, c.location FROM collectives c JOIN organizes o ON c.id = o.collective_id WHERE o.project_id = %s",
            (project_id,)
        )
        print(results)
        return [Collective(*row) for row in results]

class Requires:
    @staticmethod
    def create(project_id, skill_id):
        Database.query("INSERT INTO requires (project_id, skill_id) VALUES (%s, %s)",
                       (project_id, skill_id))
        
    @staticmethod
    def get_skills_for_project(project_id):
        results = Database.fetchall(
            "SELECT s.id, s.name, s.description FROM skills s JOIN requires r ON s.id = r.skill_id WHERE r.project_id = %s",
            (project_id,)
        )
        return [Skill(*row) for row in results]
    
    @staticmethod
    def get_projects_for_skill(skill_id):
        results = Database.fetchall(
            "SELECT p.id, p.name, p.description FROM projects p JOIN requires r ON p.id = r.project_id WHERE r.skill_id = %s",
            (skill_id,)
        )
        return [Skill(*row) for row in results]


class CollectiveMessage:
    def __init__(self, collective_id, timestamp, sender_name, message):
        self.collective_id = collective_id
        self.timestamp = timestamp
        self.sender_name = sender_name
        self.message = message

    @staticmethod
    def create(collective_id, sender_name, message):
        Database.execute(
            "INSERT INTO collective_messages (collective_id, sender_name, message) VALUES (%s, %s, %s)",
            (collective_id, sender_name, message)
        )

    @staticmethod
    def get_messages(collective_id):
        results = Database.fetchall(
            "SELECT collective_id, timestamp, sender_name, message FROM collective_messages WHERE collective_id = %s ORDER BY timestamp",
            (collective_id,)
        )
        return [CollectiveMessage(*row) for row in results]

class ProjectMessage:
    def __init__(self, project_id, timestamp, sender_name, message):
        self.project_id = project_id
        self.timestamp = timestamp
        self.sender_name = sender_name
        self.message = message

    @staticmethod
    def create(project_id, sender_name, message):
        Database.execute(
            "INSERT INTO project_messages (project_id, sender_name, message) VALUES (%s, %s, %s)",
            (project_id, sender_name, message)
        )

    @staticmethod
    def get_messages(project_id):
        results = Database.fetchall(
            "SELECT project_id, timestamp, sender_name, message FROM project_messages WHERE project_id = %s ORDER BY timestamp",
            (project_id,)
        )
        return [ProjectMessage(*row) for row in results]
    
class Location:
    @staticmethod
    def get_unique_locations():
        # Query unique locations for collectives and users from the database
        user_locations = Database.fetchall("SELECT DISTINCT location FROM persons")
        collective_locations = Database.fetchall("SELECT DISTINCT location FROM collectives")
        # Combine locations
        all_locations = user_locations + collective_locations
        
        # Normalize and split locations
        unique_locations_set = set()
        for location_tuple in all_locations:
            if location_tuple[0]:  # Ensure the location is not None
                locations = [loc.strip() for loc in location_tuple[0].split(',')]
                unique_locations_set.update(locations)
        
        # Sort unique locations
        unique_locations = sorted(unique_locations_set)
        
        return unique_locations