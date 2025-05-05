from flask import Flask, request, render_template
import sqlite3
import hashlib

app = Flask(__name__)



# Pripojenie k databáze
def pripoj_db():
    conn = sqlite3.connect("kurzy.db")
    return conn


@app.route('/')  # API endpoint
def index():
    # Úvodná stránka s dvoma tlačidami ako ODKAZMI na svoje stránky - volanie API nedpointu
    return '''
        <h1>Výber z databázy</h1>
        <a href="/kurzy"><button>Zobraz všetky kurzy</button></a>
        <a href="/treneri"><button>Zobraz všetkých trénerov</button></a>
        <a href="/ucastnici"><button>Zobraz všetkých účastníkov</button></a>
        <a href="/miesta"><button>Zobraz všetky miesta</button></a>
        <a href="/registracia"><button>Registruj trénera</button></a>
        <a href="/novykurz"><button>Vložiť kurz</button></a>
        <hr>
        
    '''

@app.route('/ucastnici')
def zobraz_ucastnikov():
    conn = pripoj_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Ucastnici")
    kurzy = cursor.fetchall()

    conn.close()


@app.route('/kurzy')  # API endpoint
def zobraz_kurzy():
    conn = pripoj_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Kurzy")
    kurzy = cursor.fetchall()
    conn.close()

    return render_template("kurzy.html", kurzy=kurzy)



@app.route('/treneri')  # API endpoint
def zobraz_trenerov():
    conn = pripoj_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT T.ID_trenera, T.Meno || ' ' || T.Priezvisko as Trener, Nazov_kurzu
        FROM Treneri T LEFT JOIN Kurzy K ON T.ID_trenera = K.ID_trenera
    """)
    treneri = cursor.fetchall()

    conn.close()

    # Jednoduchý textový výpis trénerov a ich kurzov
    vystup = "<h2>Zoznam trénerov a kurzov:</h2>"
    for trener in treneri:
        vystup += f"<p>{trener}</p>"

    # Odkaz na návrat
    vystup += '<a href="/"><button>Späť</button></a>'
    return vystup

@app.route('/miesta')
def zobraz_miesta():
    conn=pripoj_db()
    cursor=conn.cursor()

    cursor.execute("SELECT * from Miesta")
    miesta=cursor.fetchall()
    conn.close()

    vystup="<h2>Zoznam miest:</h2>"
    for miesto in miesta:
        vystup+= f"<p>{miesto}</p>"

    vystup+='<a href="/"><button>Späť</button></a>'
    return vystup

@app.route('/registracia', methods=['GET'])
def registracia_form():
    return '''
    <h2>Registracia trénera</h2>
    <form action="/registracia" method="post">
            <label>Meno:</label><br>
            <input type="text" name="meno" required><br><br>

            <label>Priezvisko:</label><br>
            <input type="text" name="priezvisko" required><br><br>

            <label>Špecializácia:</label><br>
            <input type="text" name="specializacia" required><br><br>

            <label>Telefón:</label><br>
            <input type="text" name="telefon" required><br><br>

            <label>Heslo:</label><br>
            <input type="password" name="heslo" required><br><br>

            <button type="submit">Registrovať</button>
        </form>
        <hr>
        <a href="/">Späť</a>
    '''

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
    conn = pripoj_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Treneri (Meno, Priezvisko, Specializacia, Telefon, Heslo) VALUES (?, ?, ?, ?, ?)", 
                   (meno, priezvisko, specializacia, telefon, heslo_hash))
    conn.commit()
    conn.close()

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
    conn = pripoj_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Kurzy (Nazov_kurzu, Typ_sportu, Max_pocet_ucastnikov,ID_trenera) VALUES (?, ?, ?, ?)", 
                   (sifracia_nazov, sifracia_typ, max, id))
    conn.commit()
    conn.close()

    # Hlásenie o úspešnej registrácii
    return '''
        <h2>Kurz bol úspešne zaregistrovaný!</h2>
        <hr>
        <a href="/">Späť</a>
    '''

if __name__ == '__main__':
    app.run(debug=True)