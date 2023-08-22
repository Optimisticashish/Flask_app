from flask import Flask, render_template, request, session, redirect, send_file
import mysql.connector
import os
import random
import numpy as np
import pickle
import json
import urllib.parse
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


application = Flask(__name__)  # changed
application.secret_key = os.urandom(24)

# try:
#    # Establish the connection
#     conn = mysql.connector.connect(
#         host="localhost",
#         user="root",
#         password="Trader@123",
#         database="creditscoreproject"

#     )

#     cursor = conn.cursor()

#     if conn.is_connected():
#         print("Connected to the MySQL database on localhost")

# except mysql.connector.Error as err:
#     print("Error:", err)


def get_mysql_connection():
    print("Getting mysql Connection ...")

    conn = None
    cursor = None  # Initialize the cursor variable

    try:
        # Establish the connection
        # conn = mysql.connector.connect(
        #     host="localhost",
        #     user="root",
        #     password="Trader@123",
        #     database="creditscoreproject"

        # )
        conn = mysql.connector.connect(
            # host="http://mydb1.c5vd9w1jzl35.ap-south-1.rds.amazonaws.com/",
            host="mydb1.c5vd9w1jzl35.ap-south-1.rds.amazonaws.com",
            user="admin",
            password="yashu1234",
            database="creditscore"

        )
        cursor = conn.cursor()

        if conn.is_connected():
            print("Connected to the MySQL database ....")

    except mysql.connector.Error as err:
        print("mysql connection failed...")
        print("Error:", err)

    return conn, cursor


def store_user_credit_details(details, Users_name, score):
    conn, cursor = get_mysql_connection()

    values = [val for val in details.values()]

    values.insert(0, Users_name)
    values.append(score)

    if conn and cursor:
        try:
            insert_query = """
            INSERT INTO user_credit_score_detail
            (User_Name,Annual_Income, Num_Credit_Card, Num_of_Delayed_Payment, Changed_Credit_Limit,
             Num_Credit_Inquiries, Credit_Mix, Outstanding_Debt, Credit_Utilization_Ratio,
             Credit_History_Age,Credit_Score)
            VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s)
            """
            cursor.execute(insert_query, values)
            conn.commit()

            print("inserted successfully")
            return "Details stored successfully!"

        except mysql.connector.Error as err:
            conn.rollback()
            error_message = "Failed to store details"
            print("MySQL error:", err)
            return error_message
        finally:
            cursor.close()
            conn.close()

    else:
        error_message = "Database connection failed"
        return error_message

    pass


def create_pdf(filename, data, user_name):

    data['Credit_Score'] = session['score']
    cr_score = session['score']

    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []

    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    title_style.alignment = 0
    normal_style = styles["Normal"]
    # u_n_style = ParagraphStyle(
    #     name="Center", alignment=1, parent=normal_style)  # Center alignment
    u_n_style = ParagraphStyle(
        name="LeftAlign", alignment=0, parent=normal_style)

    para = ParagraphStyle(
        name="LeftAlign", alignment=0, parent=normal_style)

    title_style.textColor = colors.brown

    # Add title
    title_text = "Credit Score Report :"
    u_name = "User_Name" + " : " + user_name
    title_text2 = "Suggestions :"
    suggestions = Paragraph(title_text2, title_style)
    title = Paragraph(title_text, title_style)
    u_n = Paragraph(u_name, u_n_style)
    story.append(title)
    story.append(u_n)
    story.append(Spacer(2, 15))

    u_n_style.textColor = colors.blue
    para.textColor = colors.black

    # Create data table
    table_data = [["Parameter", "Value"]]
    for key, value in data.items():
        table_data.append([key, value])

     # Define table style
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        # ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])

    # Create the table
    table = Table(table_data)
    table.setStyle(table_style)
    story.append(table)
    story.append(Spacer(2, 15))
    story.append(suggestions)

    if cr_score == 'poor' or cr_score == 'standard':
        suggestions_text = (
            "<br/><br/>" +
            '<font size="12"><b>Credit history age :</b></font><br/><br/>'
            '"Credit history age" refers to the length of time that you have held active credit accounts. It\'s an '
            'important factor in determining your credit score and reflects how long you\'ve been using credit responsibly.<br/>'
            '<br/>'
            'To ensure that your accounts remain active and contribute to your credit history age, use them for small '
            'transactions from time to time. This shows that the accounts are still in use and helps maintain a positive history.<br/><br/>'
            '<font size="12"><b>Credit mix :</b></font><br/><br/>'
            '"Credit mix" refers to the variety of credit accounts you have in your credit history. It\'s one of the factors '
            'that credit scoring models consider when assessing your creditworthiness. Having a diverse credit mix can '
            'potentially have a positive impact on your credit score, as it demonstrates your ability to manage different '
            'types of credit responsibly.<br/><br/>'
            '<font size="12"><b>Outstanding Debt :</b></font><br/><br/>'
            'Outstanding debt refers to the amount of money that is owed by you to the bank which includes any loans, '
            'credit card balances or other financial obligations that have not been repaid fully. This is the main deciding factor in your credit score.<br/>'
            'Keeping your outstanding debt as low as possible can be achieved by repaying your debts on time and avoiding borrowing more while the previous debt remains unpaid.<br/><br/>'
            '<font size="12"><b>Number of Delayed Payments :</b></font><br/><br/>'
            'Your credit score worsens with each instance of missing a repayment on time. This typically occurs when you fail to make '
            'the credit card repayment within a period exceeding 30 days from the due date.<br/><br/>'
            '<font size="12"><b>Number of Credit Inquiries :</b></font><br/><br/>'
            'These are requests made by companies, or lenders to access your credit report from a credit bureau. These inquiries provide information '
            'about your credit history and financial behaviour, helping lenders assess your creditworthiness before making lending decisions.<br/>'
            'Lenders seeing many recent credit inquiries could signal you\'re actively seeking credit, possibly implying financial instability or risk of excess debt. '
            'This might increase your borrowing risk, thereby negatively impacting your credit score.<br/><br/>'
            '<font size="12"><b>Number of Credit Cards :</b></font><br/><br/>'
            'Opening new credit cards increases your available credit, which can lower your utilisation ratio if you\'re not accumulating more debt. '
            'A lower ratio is generally better for your score.<br/>'
            'Managing multiple credit cards responsibly can showcase your ability to handle different types of credit, which could have a positive impact on your credit mix and your overall score.<br/><br/>'
            '<font size="12"><b>Credit Utilisation Ratio :</b></font><br/><br/>'
            'It\'s the ratio of your outstanding credit card balances to your total credit card limits.<br/>'
            'A lower credit utilization ratio (less than 30%) is generally better for your credit score. Lenders see a low ratio as an indicator of responsible credit management, while a high ratio can suggest potential financial strain.<br/><br/>'
            '<font size="12"><b>Changed Credit Limit :</b></font><br/><br/>'
            'If your credit limit increases and your spending remains the same, your decrease. This can have a positive impact on your credit score, '
            'as it shows that you\'re using a smaller portion of your available credit.'
        )

    else:
        suggestions_text = (
            '<font size="12"><b>No suggestions required.</b></font><br/>'
            'As your score is good, no suggestions are required.'
        )

    suggestions_t = Paragraph(suggestions_text, para)
    story.append(suggestions_t)
    doc.build(story)


@application.route('/')
def login():
    return render_template('login.html')


@application.route('/register')
def about():
    return render_template('register.html')


@application.route('/home')
def home():
    if 'user_id' in session:
        score = None  # Default value if 'score' is not in session
        details = None  # Default value if 'details' is not in session
        name = None

        if 'score' in session:
            score = session['score']
            details = session['details']
            name = session['name']
        return render_template('home.html', score=score, details=details, name=name)
    else:
        return redirect('/')


@application.route('/Model_input_details', methods=['POST'])
def Model_input_details():
    print("inside model result..")

    details = {
        'Annual_Income': request.form.get('Annual_Income'),
        # 'Monthly_Inhand_Salary': request.form.get('Monthly_Inhand_Salary'),
        'Num_Credit_Card': request.form.get('Num_Credit_Card'),
        'Num_of_Delayed_Payment': request.form.get('Num_of_Delayed_Payment'),
        'Changed_Credit_Limit': request.form.get('Changed_Credit_Limit'),
        'Num_Credit_Inquiries': request.form.get('Num_Credit_Inquiries'),
        'Credit_Mix': request.form.get('Credit_Mix'),
        'Outstanding_Debt': request.form.get('Outstanding_Debt'),
        'Credit_Utilization_Ratio': request.form.get('Credit_Utilization_Ratio'),
        'Credit_History_Age': request.form.get('Credit_History_Age'),

    }
    Users_name = request.form.get('Users_name')
    inputs = []

    for i in details.values():
        inputs.append(i)

    input_details = np.array([inputs])

    print(input_details)
    # inporting model ..

    # pickled_model = pickle.load(open('model.pkl', 'rb'))
    # pickled_model = pickle.load(open('model2.pkl', 'rb'))
    pickled_model = pickle.load(open('Finalpkl.pkl', 'rb'))

    score = pickled_model.predict(input_details)

    # random_number = random.randint(0, 2)
    if score == 0:
        score = 'poor'
    elif score == 1:
        score = 'standard'
    else:
        score = 'good'
    print(f"Model Prediction : {score}")

    session['score'] = score
    session['details'] = details
    session['name'] = Users_name

    print(f"name ... {session['name']}")

    store_user_credit_details(details, Users_name, score)

    # return redirect('/home?score=' + score)
    return redirect('/home')


@application.route('/generate_and_download_pdf')
def generate_and_download_pdf():
    print('inside generate_and_download_pdf')
    current_directory = os.getcwd()
    output_folder = os.path.join(current_directory, "pdfs")
    user_name = session['name']
    pdf_name = user_name + "_" + "credit_score_report.pdf"
    output_path = os.path.join(output_folder, pdf_name)

    # Creating pdf ..

    data = session['details']

    print("Creating pdf...")
    create_pdf(output_path, data, user_name)
    print("Creating pdf done...")

    return send_file(output_path, as_attachment=True)
# @app.route('/Model_input_details', methods=['POST'])
# def Model_input_details():
#     print("inside model result..")

#     if request.method == 'POST':
#         details = {
#             'Annual_Income': request.form.get('Annual_Income'),
#             # 'Monthly_Inhand_Salary': request.form.get('Monthly_Inhand_Salary'),
#             'Num_Credit_Card': request.form.get('Num_Credit_Card'),
#             'Num_of_Delayed_Payment': request.form.get('Num_of_Delayed_Payment'),
#             'Changed_Credit_Limit': request.form.get('Changed_Credit_Limit'),
#             'Num_Credit_Inquiries': request.form.get('Num_Credit_Inquiries'),
#             'Credit_Mix': request.form.get('Credit_Mix'),
#             'Outstanding_Debt': request.form.get('Outstanding_Debt'),
#             'Credit_Utilization_Ratio': request.form.get('Credit_Utilization_Ratio'),
#             'Credit_History_Age': request.form.get('Credit_History_Age'),
#         }

#         inputs = []

#         for i in details.values():
#             inputs.append(i)

#         input_details = np.array([inputs])

#         print(input_details)
#         # inporting model ..

#         # pickled_model = pickle.load(open('model.pkl', 'rb'))
#         pickled_model = pickle.load(open('model2.pkl', 'rb'))

#         score = pickled_model.predict(input_details)

#         # random_number = random.randint(0, 2)
#         if score == 0:
#             score = 'poor'
#         elif score == 1:
#             score = 'standard'
#         else:
#             score = 'good'
#         print(f"Model Prediction : {score}")
#         # Convert NumPy array to Python list for JSON serialization
#         input_details_list = input_details.tolist()

#         input_details_json = json.dumps(input_details_list)
#         # return render_template('home.html', score=score, input_values=details)
#         # return redirect('/home?score=' + score)
#         # return render_template('home.html', score=score, input_values=details)
#         # return render_template('home.html', score=score, input_values=details, input_details=input_details_json)

#         return redirect('/home?score=' + score + '&' + urllib.parse.urlencode(details) + '&input_details=' + input_details_json)

#     else:
#         # Provide default values for input_values
#         default_values = {
#             'Annual_Income': '',
#             'Num_Credit_Card': '',
#             'Num_of_Delayed_Payment': '',
#             'Changed_Credit_Limit': '',
#             'Num_Credit_Inquiries': '',
#             'Credit_Mix': '',
#             'Outstanding_Debt': '',
#             'Credit_Utilization_Ratio': '',
#             'Credit_History_Age': '',
#         }

#         return render_template('home.html', score='', input_values=default_values)


@application.route('/login_validation', methods=['POST'])
def login_validation():
    email = request.form.get('email')
    password = request.form.get('password')

    conn, cursor = get_mysql_connection()
    # cursor.execute(
    #     f"select * from users where email LIKE '{email}' AND PASSWORD LIKE '{password}' ")

    # users = cursor.fetchall()

    # # Hardcoded user details...
    # # users = {'User_Name': "Ashish",
    # #          'email': "abc@gmail.com",
    # #          'password': "abc"}

    # print(users)

    # if len(users) > 0:
    #     # if email == "abc@gmail.com" and password == "abc":
    #     session['user_id'] = users[0][0]
    #     # session['user_id'] = users['User_Name']
    #     return redirect('/home')
    # else:
    #     error_message = "Invalid email or password"
    #     return redirect('/?error=' + error_message)
    try:
        if conn and cursor:  # Check if both conn and cursor are not None
            cursor.execute(
                f"select * from users where email LIKE '{email}' AND PASSWORD LIKE '{password}' ")
            users = cursor.fetchall()

            print(users)

            if len(users) > 0:
                session['user_id'] = users[0][0]
                return redirect('/home')
            else:
                error_message = "Invalid email or password"
                return redirect('/?error=' + error_message)

        else:
            error_message = "Database connection failed"
            return redirect('/?error=' + error_message)
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


@application.route('/logout')
def logout():
    if 'user_id' in session:
        session.pop('user_id')
    if 'score' in session:
        session.pop('score')
        session.pop('details')
    return redirect('/')


if __name__ == "__main__":
    application.run(debug=True)
