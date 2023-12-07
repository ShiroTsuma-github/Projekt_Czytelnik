from packages import app
import os

if __name__ == "__main__":
    app.run(debug=True)
    DATABASE_FOLDER = os.path.dirname(os.path.abspath(__file__))
