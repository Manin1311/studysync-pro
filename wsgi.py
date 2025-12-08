from app import create_app

# Deployment Check: Final Verification

app = create_app()

if __name__ == "__main__":
    app.run()
