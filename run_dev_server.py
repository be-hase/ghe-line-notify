import os

if __name__ == "__main__":
    os.environ.setdefault('GHE_LN_DEBUG', '1')
    from app import app

    app.run()
