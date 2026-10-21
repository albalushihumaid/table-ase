import io, json, os
from flask import Flask, request, jsonify, send_file, send_from_directory
from sqlalchemy import (create_engine, MetaData, Table, Column, String, Integer,
                        Text, LargeBinary, select, insert, update, delete, func)

url = os.getenv("DATABASE_URL", "sqlite:///data.db")
for p in ("postgres://", "postgresql://"):
    if url.startswith(p):
        url = "postgresql+psycopg2://" + url[len(p):]
eng = create_engine(url, pool_pre_ping=True)
md = MetaData()
EQ = Table("equipment", md, Column("id", String(40), primary_key=True),
           Column("pos", Integer, default=0), Column("data", Text))
MEDIA = Table("media", md, Column("id", String(40), primary_key=True),
              Column("name", String(255)), Column("mime", String(120)),
              Column("blob", LargeBinary))
md.create_all(eng)

with eng.begin() as c:  # first run: load sample data
    if not c.execute(select(EQ.c.id)).first():
        seed = os.path.join(os.path.dirname(__file__), "seed.json")
        for i, e in enumerate(json.load(open(seed, encoding="utf-8"))):
            c.execute(insert(EQ).values(id=e["id"], pos=i, data=json.dumps(e)))

app = Flask(__name__, static_folder="static", static_url_path="/static")
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024
PASSWORD = os.getenv("ADMIN_PASSWORD")


@app.before_request
def guard():  # optional: protect edits with ADMIN_PASSWORD
    if PASSWORD and request.method in ("POST", "PUT", "DELETE") \
            and request.headers.get("X-Key") != PASSWORD:
        return "Unauthorized", 401


@app.get("/")
def index():
    return send_from_directory("static", "index.html")


@app.get("/api/equipment")
def list_eq():
    with eng.connect() as c:
        rows = c.execute(select(EQ.c.data).order_by(EQ.c.pos)).all()
    return jsonify([json.loads(r[0]) for r in rows])


@app.put("/api/equipment/<eid>")
def put_eq(eid):
    d = request.get_json(force=True)
    d["id"] = eid
    with eng.begin() as c:
        if c.execute(select(EQ.c.id).where(EQ.c.id == eid)).first():
            c.execute(update(EQ).where(EQ.c.id == eid).values(data=json.dumps(d)))
        else:
            pos = (c.execute(select(func.max(EQ.c.pos))).scalar() or 0) + 1
            c.execute(insert(EQ).values(id=eid, pos=pos, data=json.dumps(d)))
    return jsonify(ok=True)


@app.delete("/api/equipment/<eid>")
def del_eq(eid):
    with eng.begin() as c:
        c.execute(delete(EQ).where(EQ.c.id == eid))
    return jsonify(ok=True)


@app.post("/api/media")
def up_media():
    f = request.files["file"]
    mid = os.urandom(8).hex()
    with eng.begin() as c:
        c.execute(insert(MEDIA).values(id=mid, name=f.filename[:250],
                                       mime=f.mimetype, blob=f.read()))
    return jsonify(id=mid, name=f.filename, mime=f.mimetype)


@app.get("/media/<mid>")
def get_media(mid):
    with eng.connect() as c:
        r = c.execute(select(MEDIA).where(MEDIA.c.id == mid)).first()
    if not r:
        return "Not found", 404
    return send_file(io.BytesIO(r.blob), mimetype=r.mime, download_name=r.name,
                     conditional=True, max_age=86400)


@app.get("/healthz")
def health():
    return "ok"


if __name__ == "__main__":
    app.run(debug=True, port=int(os.getenv("PORT", 5000)))
