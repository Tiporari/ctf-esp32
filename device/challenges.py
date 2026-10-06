import config
import morse

PAGE = """<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>body{{background:#0b0f14;color:#39ff14;font-family:monospace;max-width:42em;margin:3em auto;padding:0 1em}}
a{{color:#7fdbff}}code{{background:#16202b;padding:2px 6px}}
input,textarea,button{{background:#16202b;color:#39ff14;border:1px solid #39ff14;font-family:monospace;padding:6px;margin:4px 0}}
textarea{{width:100%;box-sizing:border-box}}.err{{color:#ff4136}}hr{{border-color:#1f3a1f;margin-top:2.5em}}</style></head>
<body>{body}
<hr><form method="POST" action="/submit"><label>Got a flag? </label>
<input name="flag" placeholder="FLAG{{...}}" size="30"><button>Submit</button></form></body></html>"""

LOGIN = """<h1>&gt; Lab Console</h1><p>Authorized users only.</p>
<!-- TODO: remove test account before launch -->
<form method="POST" action="/login">
<input name="user" placeholder="username" autocomplete="off"><br>
<input name="pass" type="password" placeholder="password"><br>
<button>Log in</button></form>%s"""


def _vault_b64():
    with open("vault.b64") as f:
        return f.read()


def register(srv):
    def page(body, title="Lab Console", status=200, headers=None):
        return PAGE.format(title=title, body=body), status, headers or {}

    @srv.route("/")
    def index(req):
        return page(LOGIN % "")

    @srv.route("/login", methods=("POST",))
    def login(req):
        f = req.form()
        if f.get("user") == config.LOGIN_USER and f.get("pass") == config.LOGIN_PASS:
            return "", 302, {"Location": "/vault", "Set-Cookie": "auth=1; Path=/"}
        return page(LOGIN % '<p class="err">Invalid credentials.</p>', status=401)

    @srv.route("/vault")
    def vault(req):
        if req.cookie("auth") != "1":
            return "", 302, {"Location": "/"}
        return page(
            "<h1>&gt; Vault</h1><p>Retrieved item:</p>"
            '<textarea rows="8" readonly>%s</textarea>' % _vault_b64(),
            title="Vault",
        )

    @srv.route("/submit", methods=("POST",))
    def submit(req):
        flag = req.form().get("flag", "").strip()
        for i, lvl in enumerate(config.LEVELS):
            if flag == lvl["flag"]:
                return page("<h1>&gt; Correct!</h1><p>%s</p>" % lvl["next"], title="Correct",
                            headers={"Set-Cookie": "lvl=%d; Path=/" % (i + 2)})
        return page('<h1 class="err">&gt; Nope.</h1><p>That is not a flag. <a href="javascript:history.back()">Try again</a></p>',
                    title="Nope", status=403)

    @srv.route("/radio", methods=("GET", "POST"))
    def radio(req):
        try:
            lvl = int(req.cookie("lvl") or 1)
        except ValueError:
            lvl = 1
        if lvl < 2:
            return "", 302, {"Location": "/"}
        msg = ""
        if req.method == "POST":
            ans = "".join(req.form().get("answer", "").upper().split())
            if ans == "".join(config.MORSE_KEY.upper().split()):
                return page('<h1>&gt; Transmission decoded</h1><p>The key fits. The door opens.</p>'
                            '<p>Flag: <code>%s</code></p>' % config.LEVELS[1]["flag"], title="Decoded")
            msg = '<p class="err">Static... that does not seem right. Listen again.</p>'
        with open("radio.html") as f:
            html = f.read()
        html = html.replace("%MSG%", msg).replace("%CHART%", morse.chart_html())
        html = html.replace("%MORSE%", morse.encode(config.MORSE_KEY))
        return html

    @srv.route("/ping")
    def ping(req):
        return "pong", 200, {"Content-Type": "text/plain"}
