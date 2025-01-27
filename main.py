import logging
from flask import Flask, request
import aliceskill as game

app = Flask(game.__name__)

@app.route('/', methods=['POST'])
def flask_handler():
    return game.handler(request.json)

def main():
    logging.basicConfig(level=logging.DEBUG)
    app.run("127.0.0.1", port = 5000, debug = True)

if __name__ == "__main__":
    main()