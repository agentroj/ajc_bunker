# Flask Application 3.4 for Python Basic Course
Learn a difference between authentication and authorization, implement a function of login and logout.

# Usage
### 1. Create virtual environment to local environment
```
# Create
pyenv virtualenv 3.7.0 pytweet_auth

# Apply on local environment
pyenv local pytweet_auth

# rehash
pyenv rehash 
```

### 2. Install packages we need
```bash
pip install -r requirements.txt
```

### 3. The setting of environment variable
```bash
export FLASK_APP=run.py
```

### 4. Set up DB(Flask-Migrate)
```
#  We need to create DB anyway
mysql -u [User Name] -p

>>> CREATE DATABASE pytweet_auth_development;

We can quit inputting by pressing ctrl + d
```

```bash
# Initialization
flask db init

# Create a migration file
flask db migrate

# Run a migration
flask db upgrade

# (migrationのrollback) <= Downgrade migration o the one version before
flask db downgrade
```

### 5. Start up the server
```bash
flask run
```
