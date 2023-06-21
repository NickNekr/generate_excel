import os
from dotenv import load_dotenv

assert load_dotenv(
    "../.env", override=False
), """Can't load the environment:(
                                Set in .env file:
                                DB_USER=
                                DB_PASSWORD=
                                DB_NAME=
                                DB_HOST=
                                DB_PORT=
                                """


class Config:
    class Const:
        login = "ЛОГИН"
        user_id = "ID ПОЛЬЗОВАТЕЛЯ"
        auth_type = "ТИП АВТОРИЗАЦИИ"
        viewing_time = "ВРЕМЯ ПРОСМОТРА"

        output_excel_file = "output.xlsx"
        output_png_file = "plot.png"
        time_type = "%Y-%m-%d %H:%M"
        offset = 5

    ENV = os.environ["FLASK_ENV"]


class Production(Config):
    class Const(Config.Const):
        query = "SELECT userid, emiaslogin, info, created_at FROM security_survey;"

    class DataBase:
        PASSWORD = os.environ.get("DB_PASSWORD")
        HOST = os.environ.get("DB_HOST")
        DB = os.environ.get("DB_NAME")
        USERNAME = os.environ.get("DB_USER")
        PORT = os.environ.get("DB_PORT")

        SQLALCHEMY_DATABASE_URI = (
            f"postgresql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DB}"
        )


class Development(Config):
    class Const(Config.Const):
        dump_file = "../survey.psql"
