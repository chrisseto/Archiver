from registerer import app
from registerer.views import rest

if __name__ == '__main__':
    app.run(port=7000, debug=True)