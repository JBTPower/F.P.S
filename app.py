import pathlib

app_path = pathlib.Path(__file__).parent / "F.P.S_app.py"
exec(app_path.read_text(encoding="utf-8"), globals())
