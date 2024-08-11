from flask import Flask, render_template, request, send_file
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import io

app = Flask(__name__)

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("united-wavelet-432211-p8-d2bc6ea72002.json", scope)
client = gspread.authorize(creds)
sheet_id = '1XA76yuFM_4mtkQW__2fryUBMe5EZ6XMWtBHxylhV6k8'
sheet = client.open_by_key(sheet_id)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_timetable():
    # Get user input
    user_courses = request.form.get('courses', '')
    courses = [course.strip() for course in user_courses.split(',') if course.strip()]
    
    timetable = pd.DataFrame(columns=["Day", "Time", "Room", "Course"])

    def parse(sheetData, sheetName):
        df = pd.DataFrame(sheetData[1:], columns=sheetData[0])
        time_row_index = 3

        for i, row in df.iterrows():
            for col in df.columns:
                for course in courses:
                    if course in str(row[col]):
                        c_idx = df.columns.get_loc(col)
                        time = df.iloc[time_row_index, c_idx]
                        room = df.iloc[i, 0]
                        timetable.loc[len(timetable)] = [sheetName, time, room, course]

    for worksheet in sheet.worksheets():
        sheetName = worksheet.title
        sheetData = worksheet.get_all_values()
        parse(sheetData, sheetName)

    pivot_table = timetable.pivot_table(
        index="Day",
        columns="Time",
        values="Course",
        aggfunc=lambda x: ' '.join(str(i) for i in x),
        fill_value=""
    )

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        pivot_table.to_excel(writer, sheet_name="Timetable")

    output.seek(0)
    return send_file(output, as_attachment=True, attachment_filename="formatted_timetable.xlsx", mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

if __name__ == '__main__':
    app.run(debug=True)
