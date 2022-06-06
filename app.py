from SV import create_app


app         = create_app('flask.cfg')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)