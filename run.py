from app import create_app
import flask

app = create_app()

@app.route('/')
def home():
    return flask.redirect('/login')
@app.route('/login')
def login():
    return flask.render_template('auth.html')


if __name__ == "__main__":
    app.run(debug=True)
