from dotenv import load_dotenv

load_dotenv()

from flask import Flask, render_template
import os
import logging

logger = logging.Logger("main", logging.INFO)

app = Flask("Blancmap")

@app.route("/")
def site_index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)