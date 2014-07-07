from archiver import foreman

foreman.config_logging()

app = foreman.build_app()


if __name__ == '__main__':
    foreman.start(app)
