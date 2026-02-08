
from flask import Flask, render_template, request, redirect
import sqlite3, os
from psd_manager import ler_campos_psd, gerar_png

app = Flask(__name__)

BASE = "static"
PSD = f"{BASE}/psd_base"
FOTOS = f"{BASE}/fotos"
GERADOS = f"{BASE}/gerados"

for p in [PSD, FOTOS, GERADOS]:
    os.makedirs(p, exist_ok=True)

def db():
    return sqlite3.connect("database.db")

def init():
    c=db(); cur=c.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS config(id INTEGER PRIMARY KEY, psd TEXT, area TEXT)")
    c.commit(); c.close()

init()

@app.route("/")
def admin():
    return render_template("admin.html")

@app.route("/upload_psd", methods=["POST"])
def upload_psd():
    ar=request.files["psd"]
    path=os.path.join(PSD, ar.filename)
    ar.save(path)
    c=db(); cur=c.cursor()
    cur.execute("DELETE FROM config")
    cur.execute("INSERT INTO config(id,psd) VALUES(1,?)",(ar.filename,))
    c.commit(); c.close()
    return redirect("/configurar")

@app.route("/configurar")
def configurar():
    c=db(); cur=c.cursor()
    cur.execute("SELECT psd FROM config WHERE id=1")
    r=cur.fetchone(); c.close()
    if not r: return redirect("/")
    campos=ler_campos_psd(os.path.join(PSD,r[0]))
    return render_template("configurar.html", psd=r[0], campos=campos)

@app.route("/salvar_area", methods=["POST"])
def salvar_area():
    area=request.form["area"]
    c=db(); cur=c.cursor()
    cur.execute("UPDATE config SET area=? WHERE id=1",(area,))
    c.commit(); c.close()
    return redirect("/gerar")

@app.route("/gerar")
def gerar():
    return render_template("gerar.html")

@app.route("/processar", methods=["POST"])
def processar():
    foto=request.files["foto"]
    fp=os.path.join(FOTOS,foto.filename)
    foto.save(fp)

    dados={k:v for k,v in request.form.items() if k!="foto"}

    c=db(); cur=c.cursor()
    cur.execute("SELECT psd, area FROM config WHERE id=1")
    psd,area=cur.fetchone(); c.close()

    area=eval(area)

    saida=os.path.join(GERADOS,"resultado.png")
    gerar_png(os.path.join(PSD,psd), dados, fp, area, saida)

    return render_template("resultado.html", img=saida)

if __name__=="__main__":
    app.run()
