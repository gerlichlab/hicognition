from app import create_app
#logging durchdenken

config = 'config'
app = create_app(config)


if __name__ == "__main__":
    app.run()
