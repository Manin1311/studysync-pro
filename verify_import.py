
try:
    print("Attempting to import app...")
    import app
    print(f"Module app imported: {app}")
    if hasattr(app, 'app'):
        print(f"Found app.app: {app.app}")
        print("Success! Gunicorn should be able to see this.")
    else:
        print("ERROR: app module has no attribute 'app'")
        print(f"Dir(app): {dir(app)}")
except Exception as e:
    print(f"Import failed with error: {e}")
    import traceback
    traceback.print_exc()
