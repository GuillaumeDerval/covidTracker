# Install requirements

```
pip install -r requirements.txt
```

# Create database

```
python -c "from covidbelgium.database import init_db; init_db()"
```

# Start app

```
flask run
````

# Updating translations

First update the .mo's

```
pybabel extract -F babel.cfg -k _l -o messages.pot .
pybabel update -i messages.pot -d covidbelgium/translations
```

Then complete them. Once it's done, generate the .po's.

```
pybabel compile -d covidbelgium/translations
```
