from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String, JSON, DateTime
from datetime import datetime
import pandas as pd
from io import StringIO
from config import Config, Appication


engine = create_engine(Appication.SQLALCHEMY_DATABASE_URI, echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


class SecuritySurvey(Base):
    __tablename__ = "security_survey"

    id = Column(Integer, primary_key=True)
    userid = Column(Integer, default=0, nullable=False)
    emiaslogin = Column(String(255), default="", nullable=False)
    fingerprint = Column(String(255), default="", nullable=False)
    info = Column(JSON, default={}, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now, nullable=False)

    def __init__(self, data):
        self.userid = data[Config.Const.user_id]
        self.emiaslogin = data[Config.Const.login]
        self.fingerprint = data["finger"]
        self.info = data[Config.Const.auth_type]
        self.created_at = data[Config.Const.viewing_time]


Base.metadata.create_all(engine)


def create_df_from_file():
    dump_file = "./survey.psql"
    to_human_info = {"localhostservice": "АРМ", "emiasdb": "ФОРМА ЛОГИН/СНИЛС"}

    with open(dump_file, "r") as file:
        dump_content = file.read()
    cleaned_content = "\n".join(
        line for line in dump_content.splitlines() if line and line[0].isdigit()
    )

    df = pd.read_csv(
        StringIO(cleaned_content),
        sep="\t",
        usecols=[1, 2, 3, 4, 5],
        names=[
            Config.Const.user_id,
            Config.Const.login,
            "finger",
            Config.Const.auth_type,
            Config.Const.viewing_time,
        ],
    )

    return df


def add_data(df):
    surveys = []
    for el in df.to_dict(orient="records"):
        surveys.append(SecuritySurvey(el))

    session.add_all(surveys)
    session.commit()


df = create_df_from_file()
add_data(df)
