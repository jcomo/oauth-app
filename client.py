from client import app


if __name__ == '__main__':
    app.run(threaded=True, debug=True, port=5000)
