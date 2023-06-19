import pandas as pd
from openpyxl.styles import Alignment
from io import StringIO
from openpyxl.drawing.image import Image
import matplotlib.pyplot as plt
import json

TO_HUMAN_INFO = {"localhostservice": "АРМ", "emiasdb": "ФОРМА ЛОГИН/СНИЛС"}


def create_df():
    dump_file = './survey.psql'

    with open(dump_file, 'r') as file:
        dump_content = file.read()
    cleaned_content = '\n'.join(line for line in dump_content.splitlines() if line and line[0].isdigit())

    return pd.read_csv(StringIO(cleaned_content), sep="\t", usecols=[1, 2, 4, 5],
                       names=["userid", "emiaslogin", "info", "created_at"])


def create_excel(dataframe):
    filename = './output.xlsx'
    with pd.ExcelWriter(filename) as writer:
        dataframe.to_excel(writer, index=False, sheet_name='Sheet1')
        worksheet = writer.sheets['Sheet1']
        for column_cells in worksheet.columns:
            for cell in column_cells:
                cell.alignment = Alignment(horizontal='center', vertical='center')
            length = max(len(str(cell.value)) for cell in column_cells)
            worksheet.column_dimensions[column_cells[0].column_letter].width = length

        image = Image("./plot.png")
        worksheet.add_image(image, "F1")


def get_data(dataframe):
    auth_type = {"emiasdb": 0, "localhostservice": 0}

    for row in dataframe.itertuples():
        auth_type[json.loads(row.info)["authsource"]] += 1
    return auth_type


def create_graph(service_data):
    total = sum(service_data.values())

    percentages = [value / total * 100 for value in service_data.values()]
    keys = [TO_HUMAN_INFO[key] for key in service_data.keys()]
    plt.bar(keys, percentages)
    plt.bar_label(plt.bar(keys, service_data.values()),
                  labels=[f'{p:.1f}% ({v})' for p, v in zip(percentages, service_data.values())])

    plt.title('Процентное соотношение')

    plt.savefig("./plot.png")
    plt.show()


if __name__ == "__main__":
    df = create_df()
    data = get_data(df)
    create_graph(data)
    create_excel(df)
