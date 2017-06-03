import os, shutil
from Doc2VecModelMaker import Doc2VecModel
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from JIRAparser import JiraParser

app = Flask("Bug reports analyzer")

@app.route("/", methods=['GET', 'POST'])
def main_menu():
    if request.method == 'POST':
        parser = JiraParser("database/")
        flash("Start parsing JIRA")
        start_date = datetime.strptime(request.form['start-date'], "%Y-%m-%d")
        end_date = datetime.strptime(request.form['end-date'], "%Y-%m-%d")

        parser.parse_date_period(start_date.strftime("%Y/%m/%d"),
                                 end_date.strftime("%Y/%m/%d"))

        flash("Start word2vec training")
        print(start_date)
        print(end_date)
        model = Doc2VecModel("")
        model.train_model_on_database()
        model.visualize_dataset()

        shutil.rmtree("database")
        os.mkdir("database")

        return render_template('result.html')
    else:
        shutil.rmtree("database")
        os.mkdir("database")
        return render_template('main_page.html')

@app.route("/templates/saveVectors.csv")
def return_file():
    return render_template("saveVectors.csv")

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host="0.0.0.0", port=5000)