# rightmove-radius-price-watch
Watching house price changes in an area

# quick setup
```shell
python3 -mvenv venv
. venv/bin/activate
python -mpip install --upgrade pip
pip install -r requirements.txt
sqlite3 -init database.sql rightmove.db
python main.py
sqlite_web -p 8080 -H 0.0.0.0 -r -x rightmove.db
```
