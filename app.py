from flask import Flask, request, render_template, g, session
import sqlite3
import hashlib
from flask_sqlalchemy import SQLAlchemy
from i18n import TRANSLATIONS, SUPPORTED
import os

app = Flask(__name__,instance_relative_config=True)
app.secret_key="tajny_kluc"

#konfigurácia sql_alchemy-databáza "kurzy.db" je v priečinku instance
db_path=os.path.join(app.instance_path,"kurzy.db")

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}".replace("\\","/")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
db= SQLAlchemy(app)
#-----------------------------


# Removed pripoj_db function as SQLAlchemy ORM will be used for database operations.

class Kurz(db.Model):
    __tablename__="Kurzy"
    ID_kurzu            =db.Column(db.Integer, primary_key=True)
    Nazov_kurzu         =db.Column(db.String)
    Typ_sportu          =db.Column(db.String)
    Max_pocet_ucastnikov=db.Column(db.Integer)
    Id_trenera          =db.Column(db.Integer)

    def __repr__(self):
        return f"<Kurz {self.Nazov_kurzu}>"
    
class Treneri(db.Model):
    __tablename__="Treneri"
    Id_trenera          =db.Column(db.Integer, primary_key=True)
    Meno                =db.Column(db.String)
    Priezvisko          =db.Column(db.String)
    Specializacia       =db.Column(db.String)
    Telefon             =db.Column(db.Text)
    Heslo               =db.Column(db.String)

class Miesta(db.Model):
    __tablename__="Miesta"
    Id_miesta           =db.Column(db.Integer, primary_key=True)
    Nazov_miesta        =db.Column(db.String)
    Adresa              =db.Column(db.String)
    Kapacita            =db.Column(db.Integer)

class Ucastnici(db.Model):
    __tablename__="Ucastnici"
    Id_ucastnika         =db.Column(db.Integer, primary_key=True)
    Meno                 =db.Column(db.String)
    Priezvisko           =db.Column(db.String)
    Datum_narodenia      =db.Column(db.Integer)
    Telefon              =db.Column(db.String)

@app.before_request
def set_lang():
    # 1. ?lang=en v URL má prednosť
    lang = request.args.get("lang")

    if lang is None:
        # 2. potom session
        lang = session.get("lang", "sk")  # 3. fallback na "sk"

    if lang not in SUPPORTED:
        lang = "slotovcina"

    session["lang"] = lang
    g.t = TRANSLATIONS[lang]

@app.context_processor
def inject_translations():
    return dict(t=g.t)

@app.route('/')  # API endpoint
def index():
    # Úvodná stránka s dvoma tlačidami ako ODKAZMI na svoje stránky - volanie API endpointu
    return render_template("mainweb.html")

@app.route('/ucastnici')
def zobraz_ucastnikov():
    '''
    conn = pripoj_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Ucastnici")
    ucastnici = cursor.fetchall()
    conn.close()
    '''

    ucastnici=Ucastnici.query.all()
    return render_template("ucastnici.html", ucastnici=ucastnici)


@app.route('/kurzy')  # API endpoint
def zobraz_kurzy():
    ''''
    Stary spôsob cez sqlite3:

    conn = pripoj_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Kurzy")
    kurzy = cursor.fetchall()
    conn.close()
    '''

    kurzy=Kurz.query.all()
    return render_template("kurzy.html", kurzy=kurzy)



@app.route('/treneri')  # API endpoint
def zobraz_trenerov():
    '''
    conn = pripoj_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT T.ID_trenera, T.Meno || ' ' || T.Priezvisko as Trener, Nazov_kurzu
        FROM Treneri T LEFT JOIN Kurzy K ON T.ID_trenera = K.ID_trenera
    """)
    treneri = cursor.fetchall()

    conn.close()
    '''
    
    treneri=Treneri.query.all()
    return render_template("treneri.html", treneri=treneri)

@app.route('/miesta')
def zobraz_miesta():
    '''
    conn=pripoj_db()
    cursor=conn.cursor()

    cursor.execute("SELECT * from Miesta")
    miesta=cursor.fetchall()
    conn.close()
    '''
    miesta=Miesta.query.all()
    return render_template("miesta.html", miesta=miesta)

@app.route('/registracia', methods=['GET'])
def registracia_form():
    return render_template("registracia.html")

@app.route('/registracia', methods=['POST'])
def registracia_trenera():
    meno = request.form['meno']
    priezvisko = request.form['priezvisko']
    specializacia = request.form['specializacia']
    telefon = request.form['telefon']
    heslo = request.form['heslo']

    # Hashovanie hesla
    heslo_hash = hashlib.sha256(heslo.encode()).hexdigest()

    # Zápis do databázy
    novy_trener = Treneri(Meno=meno, Priezvisko=priezvisko, Specializacia=specializacia, Telefon=telefon, Heslo=heslo_hash)
    db.session.add(novy_trener)
    db.session.commit()

    # Hlásenie o úspešnej registrácii
    return '''
        <h2>Tréner bol úspešne zaregistrovaný!</h2>
        <hr>
        <a href="/">Späť</a>
    '''

@app.route('/novykurz', methods=['GET'])
def pridaj_form():
    return '''
    <h2>pridanie kurzu</h2>
    <form action="/novykurz" method="post">
            <label>Názov kurzu:</label><br>
            <input type="text" name="nazov_kurzu" required><br><br>

            <label>Typ športu:</label><br>
            <input type="text" name="typ_sportu" required><br><br>

            <label>Max. počet účastníkov:</label><br>
            <input type="text" name="max_pocet_ucastnikov" required><br><br>

            <label>ID trénera:</label><br>
            <input type="text" name="id_trenera" required><br><br>

            <button type="submit">Pridať</button>
        </form>
        <hr>
        <a href="/">Späť</a>
    '''

def sifracia(text):
    pismeno=""
    a=5
    b=8
    for char in text:
        char=char.upper()
        CisloPismena=ord(char)-ord('A')
        sifrovanie=(a*CisloPismena+b)%26
        pismeno+=chr(sifrovanie+ord('A'))
    return pismeno

@app.route("/novykurz",methods=['POST'])
def pridaj_kurz():
    nazov=request.form['nazov_kurzu']
    typ=request.form['typ_sportu']
    max=request.form["max_pocet_ucastnikov"]
    id=request.form["id_trenera"]
    sifracia_nazov=sifracia(nazov)
    sifracia_typ=sifracia(typ)

    #zápis do databázy
    novy_kurz = Kurz(Nazov_kurzu=sifracia_nazov, Typ_sportu=sifracia_typ, Max_pocet_ucastnikov=max, Id_trenera=id)
    db.session.add(novy_kurz)
    db.session.commit()

    # Hlásenie o úspešnej registrácii
    return '''
        <h2>Kurz bol úspešne zaregistrovaný!</h2>
        <hr>
        <a href="/">Späť</a>
    '''

if __name__ == '__main__':
    app.run(debug=True)