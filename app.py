import datetime
from fileinput import filename
import pandas
from flask import Flask, render_template, request, send_file
from geopy.geocoders import ArcGIS
from werkzeug import secure_filename

app=Flask(__name__)

def find_lat_lon(df):
    nom = ArcGIS()
    df['Coordinates'] = df['Address'].apply(nom.geocode)
    df['Lat'] = df['Coordinates'].apply(lambda x: x.latitude if x != None else None)
    df['Lon'] = df['Coordinates'].apply(lambda x: x.longitude if x != None else None)
    return df.drop(columns=['Coordinates'])

def check_labels(df):
    return any(x in ['address','Address'] for x in df.keys())

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/success-table', methods=['POST'])
def success_table():
    #global file
    global filename
    if request.method=='POST':
            file=request.files["file"]
            if file.filename != "":
                file_name = "import_files/" + secure_filename("uploaded_"+file.filename)
                file.save(file_name)
                try:
                    df = pandas.read_csv(file_name)
                    if check_labels(df):
                        try:
                            df = find_lat_lon(df)
                            filename = datetime.datetime.now().strftime("export_files/%Y%m%d_%H%M%S_%f"+".csv")
                            df.to_csv(filename,index=None)
                            return render_template("index.html", tbl=df.to_html(index=None), filename=filename , btn="download.html")
                        except:
                            warn = "Let op: Sorry, er is iets fout gegaan bij het ophalen van de coordinaten. Probeer het nog een keer"    
                            return render_template("index.html", warn=warn )
                    else:
                        warn = """Let op: Het bestand heeft niet de juiste format.<br>
                                  <dl>
                                    <dt>Voorwaarde:</dt>
                                        <dd>- De kolomscheiding moet een <strong>','</strong> zijn;</dd>
                                        <dd>- De kolom met het adres moet de label <strong>'address'</strong> of <strong>'Address'</strong> hebben.</dd>
                                  </dl>"""    
                        return render_template("index.html", warn=warn, tbl=df.to_html(index=None) )
                except:
                    warn = "Let op: Het bestand heeft niet de juiste CSV format."    
                    return render_template("index.html", warn=warn )
            else:
                warn = "Let op: Er is geen bestand geupload."    
                return render_template("index.html", warn=warn )

@app.route("/download-file/")
def download():
    return send_file(filename, attachment_filename="yourfile.csv", as_attachment=True)

if __name__=="__main__":
    app.run(debug=True)
