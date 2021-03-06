import os
from flask import Flask, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import arrow
from test_scoring_script import calculate_full_score
import operator

UPLOAD_FOLDER = ''astrohack/submissions'

LEADERBOARD = dict()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['LEADERBOARD'] = LEADERBOARD

ALLOWED_EXTENSIONS = set(['csv', 'txt'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_leaderboard(new_kv):
    k,v = new_kv

    #read leaderboard
    leaderboard = dict()

    leaderboard_path = 'astrohack/leaderboard/0_latest_board.txt'

    with open(leaderboard_path) as f:
        lines = f.readlines()
        for line in lines:
            a,b = line.split(',')
            leaderboard[a]=b

    if (k in leaderboard and leaderboard[k] > v) or k not in leaderboard:
        leaderboard[k] = v

        #rewrite
        with open(leaderboard_path) as f:
            for k,v in leaderboard:
                f.writeline(k + ',' + v)

    return leaderboard


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        if 'teamname' not in request.form:
            flash('No teamname was chosen1!')
            return redirect(request.url)

        file = request.files['file']
        teamname = request.form['teamname']

        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):

            # give unique filename
            timestamp = arrow.utcnow().timestamp
            filename = secure_filename(file.filename)[:-4] + '_' + teamname + '_' + str(timestamp) + '.csv'
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            chi2_score = calculate_full_score(filepath)
            upload_leaderboard((teamname, chi2_score))

            return redirect(url_for('upload_file',
                                    filename=filename))
    else:

        sorted_leaderboard = sorted(app.config['LEADERBOARD'].items(), key=operator.itemgetter(1), reverse=False)
        leaderboard_string = """<table>
                              <tr>
                                <th>Team</th>
                                <th>Score</th>
                              </tr>
                              <tr>"""

        for (k, v) in sorted_leaderboard:
            # print k, v
            leaderboard_string += '<tr><td>' + str(k) + '</td><td>' + str(v) + '</td></tr>'

        #todo: https://stackoverflow.com/questions/7863251/clicking-the-text-to-select-corresponding-radio-button
        return '''
            <!doctype html>
            <title>Upload new File</title>
            <h1>Upload new File2</h1>
            <p> Please mind that this assumes your first row is a HEADER row, and that your columns are in order ['SDSS_ID', 'logMstar']. <\p>
            <form method=post enctype=multipart/form-data>
              <p><input type=file name=file>
                 <input type=submit value=Upload>
              <\p>
              <br>
            <input type="radio" name="teamname" value="AstroWhack">AstroWhack</input><br>
            <input type="radio" name="teamname" value="Milky Way Wizards">Milky Way Wizards</input><br>
            <input type="radio" name="teamname" value="Bayesian Buddies">Bayesian Buddies</input><br>
            <input type="radio" name="teamname" value="The Juniors">The Juniors</input><br>
            <input type="radio" name="teamname" value="Aldebaran">Aldebaran</input><br>
            <input type="radio" name="teamname" value="Guardians of the Galaxy aka team supertof">Guardians of the Galaxy aka team supertof</input><br>
            <input type="radio" name="teamname" value="Brussels Commuters">Brussels Commuters</input><br>
            <input type="radio" name="teamname" value="disASTR0">disASTR0</input><br>
            <input type="radio" name="teamname" value="Stardust">Stardust</input><br>
            <input type="radio" name="teamname" value="Andromeda42">Andromeda42</input><br>
            </form><br>
            ''' + leaderboard_string

    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File1</h1>
    <p> Please mind that this assumes your first row is a HEADER row, and that your columns are in order ['SDSS_ID', 'logMstar']. <\p>
    <form method=post enctype=multipart/form-data>
      <p><input type=file name=file>

         <input type=submit value=Upload>
    </form>
    '''

if __name__ == "__main__":

    app.run(host='0.0.0.0',port='80')
