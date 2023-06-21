import os
from dateutil.parser import parse
import pandas as pd
from openpyxl.styles import Alignment
from io import StringIO
from openpyxl.drawing.image import Image
import matplotlib.pyplot as plt
from config import Config, Appication
import json


def create_df_from_file():
    with open(Config.Const.dump_file, "r") as file:
        dump_content = file.read()
    cleaned_content = "\n".join(
        line for line in dump_content.splitlines() if line and line[0].isdigit()
    )

    df = pd.read_csv(
        StringIO(cleaned_content),
        sep="\t",
        usecols=[1, 2, 4, 5],
        names=[
            Config.Const.user_id,
            Config.Const.login,
            Config.Const.auth_type,
            Config.Const.viewing_time,
        ],
    )

    return df


def create_df_from_db():
    df = pd.read_sql(
        Config.Const.query,
        Appication.SQLALCHEMY_DATABASE_URI,
        dtype=str,
    )
    df.rename(
        columns={
            "userid": Config.Const.user_id,
            "emiaslogin": Config.Const.login,
            "info": Config.Const.auth_type,
            "created_at": Config.Const.viewing_time,
        },
        inplace=True,
    )
    return df


def create_excel(dataframe):
    with pd.ExcelWriter(Config.Const.output_excel_file) as writer:
        dataframe.to_excel(writer, index=False, sheet_name="Sheet1")
        worksheet = writer.sheets["Sheet1"]
        for column_cells in worksheet.columns:
            for cell in column_cells:
                cell.alignment = Alignment(horizontal="center", vertical="center")
            length = (
                max(len(str(cell.value)) for cell in column_cells) + Config.Const.offset
            )
            worksheet.column_dimensions[column_cells[0].column_letter].width = length

        image = Image(Config.Const.output_png_file)
        worksheet.add_image(image, "F1")


def get_statistics_and_change_df(dataframe):
    to_human_info = {"localhostservice": "АРМ", "emiasdb": "ФОРМА ЛОГИН/СНИЛС"}

    dataframe[Config.Const.auth_type] = dataframe[Config.Const.auth_type].map(
        lambda x: to_human_info[json.loads(x.replace("'", '"'))["authsource"]]
    )
    dataframe[Config.Const.viewing_time] = dataframe[Config.Const.viewing_time].map(
        lambda x: parse(x).strftime(Config.Const.time_type)
    )

    statistics = {key: 0 for key in to_human_info.values()}
    for row in dataframe.to_dict(orient="records"):
        statistics[row[Config.Const.auth_type]] += 1
    return statistics


def create_graph(service_data):
    total = sum(service_data.values())

    percentages = [value / total * 100 for value in service_data.values()]
    plt.bar(service_data.keys(), percentages)
    plt.bar_label(
        plt.bar(service_data.keys(), service_data.values()),
        labels=[f"{p:.1f}% ({v})" for p, v in zip(percentages, service_data.values())],
    )

    plt.title("Процентное соотношение")

    plt.savefig("./plot.png")
    plt.show()


def main():
    if os.environ.get("FLASK_ENV") == "development":
        df = create_df_from_file()
    elif os.environ.get("FLASK_ENV") == "production":
        df = create_df_from_db()
    else:
        raise Exception("Didn't load the enviroment")
    data = get_statistics_and_change_df(df)
    create_graph(data)
    create_excel(df)


if __name__ == "__main__":
    main()
