# Application Setup and Usage
Follow these steps to get the application up and running.

## Prerequisites
Ensure you have Python installed and a virtual environment set up. It is highly recommended to use a virtual environment to manage dependencies.

## Step 1: Set Up Virtual Environment
If you haven't already, create and activate a virtual environment

## Step 2: Install Dependencies
Once your virtual environment is activated, install the necessary libraries by running:
```
pip install -r requirements.txt
```
## Step 3: Populate the Database
To populate the database with the initial data, run:
```
python populate.py
```

### Resetting the Database (Optional)
If you need to reset the database before running Step 3, run:
```
python manage.py flush
```
This will clear all data in the database.

## Step 4: Run the Application
Finally, start the application by running the following command:
```
python manage.py runserver
```

Your application should now be running locally. Open your browser and navigate to the URL provided in the terminal (usually http://127.0.0.1:8000)

