# export FLASK_APP=boston-info.py
# debug mode: export FLASK_ENV=development
# flask run
from config import get_env
from app import create_app

app = create_app(get_env('APP_ENV'))

if __name__ == '__main__':
    app.run()
