-- schema.sql

-- Drop existing tables
DROP TABLE IF EXISTS belongs_to CASCADE;
DROP TABLE IF EXISTS possesses CASCADE;
DROP TABLE IF EXISTS participates CASCADE;
DROP TABLE IF EXISTS organizes CASCADE;
DROP TABLE IF EXISTS requires CASCADE;
DROP TABLE IF EXISTS persons CASCADE;
DROP TABLE IF EXISTS collectives CASCADE;
DROP TABLE IF EXISTS projects CASCADE;
DROP TABLE IF EXISTS skills CASCADE;
DROP TABLE IF EXISTS collective_messages CASCADE;
DROP TABLE IF EXISTS project_messages CASCADE;
DROP TABLE IF EXISTS invitations CASCADE;


CREATE TABLE persons (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    bio VARCHAR(500),
    location VARCHAR(100)
);

CREATE TABLE collectives (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(500),
    location VARCHAR(100)
);

CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(500)
);

CREATE TABLE skills (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(500)
);

CREATE TABLE belongs_to (
    person_id INT REFERENCES persons(id) ON DELETE CASCADE,
    collective_id INT REFERENCES collectives(id) ON DELETE CASCADE,
    PRIMARY KEY (person_id, collective_id)
);

CREATE TABLE possesses (
    person_id INT REFERENCES persons(id) ON DELETE CASCADE,
    skill_id INT REFERENCES skills(id) ON DELETE CASCADE,
    PRIMARY KEY (person_id, skill_id)
);

CREATE TABLE participates (
    person_id INT REFERENCES persons(id) ON DELETE CASCADE,
    project_id INT REFERENCES projects(id) ON DELETE CASCADE,
    PRIMARY KEY (person_id, project_id)
);

CREATE TABLE organizes (
    collective_id INT REFERENCES collectives(id) ON DELETE CASCADE,
    project_id INT REFERENCES projects(id) ON DELETE CASCADE,
    PRIMARY KEY (collective_id, project_id)
);

CREATE TABLE requires (
    project_id INT REFERENCES projects(id) ON DELETE CASCADE,
    skill_id INT REFERENCES skills(id) ON DELETE CASCADE,
    PRIMARY KEY (project_id, skill_id)
);

CREATE TABLE collective_messages (
    collective_id INT REFERENCES collectives(id) ON DELETE CASCADE,
	sender_name VARCHAR(100) NOT NULL REFERENCES persons(username) ON DELETE CASCADE,
    message TEXT NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (collective_id, timestamp)
);

CREATE TABLE project_messages (
    project_id INT REFERENCES projects(id) ON DELETE CASCADE,
	sender_name VARCHAR(100) NOT NULL REFERENCES persons(username) ON DELETE CASCADE,
    message TEXT NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (project_id, timestamp)
);
