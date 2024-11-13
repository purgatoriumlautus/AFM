from app import create_app


# RUN THIS FILE TO START THE APPLICATION

flask_app = create_app()

if __name__ == '__main__':
    flask_app.run(debug=True)