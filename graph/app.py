from flask import Flask, request, redirect, url_for, render_template, send_file
import pandas as pd
import io
import matplotlib.pyplot as plt

app = Flask(__name__)

# 허용할 파일 확장자 설정
ALLOWED_EXTENSIONS = {'csv'}
df = None  # 글로벌 변수로 데이터프레임 선언

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    global df
    # 파일이 요청에 포함되어 있는지 확인
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    
    # 파일이 비어 있는지 확인
    if file.filename == '':
        return redirect(request.url)
    
    # 파일이 허용된 형식인지 확인
    if file and allowed_file(file.filename):
        df = pd.read_csv(io.StringIO(file.stream.read().decode("UTF8")), encoding='utf-8')
        
        # 데이터프레임의 컬럼 이름을 HTML 테이블로 변환하고 체크박스 추가
        columns = pd.DataFrame(df.columns, columns=['Column Names'])
        table_html = '<table border="1"><tr><th>Column Names</th><th>Select</th></tr>'
        for column in columns['Column Names']:
            table_html += f'<tr><td>{column}</td><td><input type="checkbox" name="columns" value="{column}"></td></tr>'
        table_html += '</table>'

        return render_template('result.html', table=table_html)
    
    return 'File type not allowed'

@app.route('/process', methods=['POST'])
def process_file():
    global df
    selected_columns = request.form.getlist('columns')
    if not selected_columns:
        return 'No columns selected', 400

    plt.figure(figsize=(10, 6))
    for column in selected_columns:
        if column in df.columns:
            plt.plot(df[column], label=column)
    
    plt.yscale('log')
    plt.xlabel('Index')
    plt.ylabel('Value')
    plt.title('Selected Columns (Log Scale)')
    plt.legend()
    
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    
    return send_file(img, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
