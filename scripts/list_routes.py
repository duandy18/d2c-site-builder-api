from app.main import app

for route in sorted(app.routes, key=lambda item: getattr(item, "path", "")):
    print(sorted(getattr(route, "methods", []) or []), getattr(route, "path", ""))
