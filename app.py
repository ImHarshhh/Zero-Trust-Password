from flask import Flask, render_template, redirect, url_for, request, jsonify
import mysql.connector
import smtplib
import os
import random
import math

global receiver_email

app = Flask(__name__)
app.secret_key = os.urandom(16)
# Configure MySQL connection
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '1234',
    'database': 'zerotrust'
}


def connect_to_db():
    return mysql.connector.connect(**db_config)


@app.route('/')
def welcome():
    return render_template('Welcome_page.html')


@app.route('/login1')
def login_page():
    return render_template('login1.html')


@app.route('/signup1')
def signup_page():
    return render_template('signup1.html')


@app.route('/password_checker_signup')
def password_checker():
    return render_template('password_check.html')


@app.route('/password_checker_login')
def password_checker_login():
    return render_template('password_check_login.html')


@app.route('/sendOtp')
def send_otp():
    return render_template('Login2.html')
@app.route('/signup_add')
def signup_add():
    return render_template("signup_add.html")


@app.route('/submit_form', methods=['POST'])
def submit_form():
    try:
        connection = connect_to_db()
        cursor = connection.cursor()
        # Get form data from the request
        name = request.form['name']
        father_name = request.form['father-name']
        mother_name = request.form['mother-name']
        city = request.form['city']
        dob = request.form['dob']
        mobile_number = request.form['mobile-number']
        doj = request.form['doj']
        email = request.form['email']
        ans = request.form['ans']
        if ans=="YES":
            query = "INSERT INTO data (Name, Father_Name, Mother_Name, City, dob, Mobile, doj,email_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            values = (name, father_name, mother_name, city, dob, mobile_number,doj,email)
            cursor.execute(query, values)
            connection.commit()
            cursor.close()
            connection.close()
            return redirect(url_for('signup_add'))
        else:
            query = "INSERT INTO data (Name, Father_Name, Mother_Name, City, dob, Mobile, doj,email_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            values = (name, father_name, mother_name, city, dob, mobile_number,doj,email)
            cursor.execute(query, values)
            connection.commit()
            cursor.close()
            connection.close()
            return redirect(url_for('password_checker'))
    except Exception as e:
        print(e)
        error_message = "User already exists."
        return render_template('signup1.html', error_message=error_message)
@app.route('/submit_signupform',methods=['POST'])
def submit_signupform():
    spouse_name = request.form['spouse-name']
    spouse_dob = request.form['spouse-dob']
    doa = request.form['doa']
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute("SELECT MAX(ID) FROM data")
    max_id = cursor.fetchone()[0]
    # Insert data using the retrieved maximum ID
    query = "UPDATE data SET spouse_name = %s, spouse_dob = %s, doa = %s WHERE ID = %s"
    values = (spouse_name, spouse_dob, doa, max_id)
    cursor.execute(query, values)
    connection.commit()
    cursor.close()
    connection.close()
    return render_template('password_check.html')
@app.route('/send_OTP', methods=['POST'])
def send_OTP():
    global temp
    mob = request.form['mobile']
    temp = mob
    if check_user(mob):
        search_user(mob)
        return render_template('Login2.html', msg=msg)
    else:
        error_message = "User does not exist."
        return render_template('login1.html', error_message=error_message)


@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    received_otp = request.form['OTP'].strip()
    global_otp_str = str(global_otp)
    # verifying the entered OTP
    if received_otp == global_otp_str:
        return redirect(url_for('password_checker_login'))
    else:
        error_message = "Invalid OTP."
        return render_template('Login2.html', error_message=error_message)


@app.route('/password', methods=['POST'])
def password():
    password = request.form['Password']
    result,time = password_verify((password))
    if time==None:
        response_data = {
            'result': result
        }
        return jsonify(response_data)
    else:
        time = "Estimated time to crack:"+time
        response_data = {
            'result':result,
            'time':time
        }
        return jsonify(response_data)

@app.route('/password_login', methods=['POST'])
def password_login():
    password = request.form['Password']
    result,time = password_verify_login((password))
    if time==None:
        response_data = {
            'result': result
        }
        return jsonify(response_data)
    else:
        time = "Estimated time to crack: "+time
        response_data = {
            'result':result,
            'time':time
        }
        return jsonify(response_data)

@app.route('/recommend', methods=['GET'])
def recommend():
    password = password_recommender()
    r_password = "Recommmended password:  " + str(password)
    response_data = {
        'r_password': r_password
    }
    return jsonify(response_data)


@app.route('/recommend_login', methods=['GET'])
def recommend_login():
    password = password_recommender_login()
    r_password = "Recommmended password:" + str(password)
    response_data = {
        'r_password': r_password
    }
    return jsonify(response_data)


def password_recommender_login():
    try:
        connection = connect_to_db()
        cursor = connection.cursor()
        select_query = "SELECT *  FROM data WHERE Mobile = %s;"
        cursor.execute(select_query, (temp,))
        result = cursor.fetchone()
        if result:
            return generate_password(*result[1:-6])
        else:
            print("No data found.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")


def password_recommender():
    try:
        connection = connect_to_db()
        cursor = connection.cursor()
        select_query = "SELECT *  FROM data ORDER BY ID DESC LIMIT 1;"
        cursor.execute(select_query)
        result = cursor.fetchone()
        if result:
            return generate_password(*result[1:-6])
        else:
            print("No data found.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")


def search_user(mobile_no):
    try:
        connection = connect_to_db()
        cursor = connection.cursor()
        query = "SELECT email_id FROM data WHERE Mobile = %s;"
        cursor.execute(query, (mobile_no,))
        result = cursor.fetchone()
        if result and len(result) > 0:
            email_id = result[0]
            otp_generate(email_id)
            return 1
        else:
            return 0

    except Exception as e:
        print(f"An error occurred: {str(e)}")


def check_user(mobile_no):
    try:
        connection = connect_to_db()
        cursor = connection.cursor()
        query = "SELECT id FROM data WHERE Mobile = %s;"
        cursor.execute(query, (mobile_no,))
        result = cursor.fetchone()
        if result and len(result) > 0:
            return 1
        else:
            return 0
    except Exception as e:

        print(f"An error occurred: {str(e)}")


def hide_email(email):
    hidden = email[:2]
    index = email.index("@")
    for i in range(2, index - 2):
        hidden += "*"
    for j in range(index - 2, len(email)):
        hidden += email[j]
    return hidden


def otp_generate(email):
    global msg
    global global_otp
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    password = "cnnn ktbh hnwe zoys"
    server.login("bytebendersztp@gmail.com", password)
    OTP = random.randint(100000, 999999)
    body = "Dear User," + "\n" + "\n" + "Your One Time Password (OTP) is " + str(OTP) + "."  # generating a message
    subject = "One Time Password (OTP) for verification"
    message = f'Subject:{subject}\n\n{body}'
    receiver_email = email
    server.sendmail("bytebendersztp@gmail.com", receiver_email, message)
    msg = "OTP has been sent to " + (hide_email(receiver_email))
    server.quit()
    global_otp = OTP


def password_verify(password):
    try:
        connection = connect_to_db()
        cursor = connection.cursor()
        select_query = "SELECT * FROM data ORDER BY ID DESC LIMIT 1;"
        cursor.execute(select_query)
        result = cursor.fetchone()
        if result:
            return check_password(*result[1:-1], password)
        else:
            print("No data found.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")


def password_verify_login(password):
    try:
        connection = connect_to_db()
        cursor = connection.cursor()
        select_query = "SELECT * FROM DATA WHERE Mobile = %s;"
        cursor.execute(select_query, (temp,))
        result = cursor.fetchone()
        if result:
            return check_password(*result[1:-1], password)
        else:
            print("No data found.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")


def preprocess(date):
    date_str = date.replace("-", "")
    return date_str


def subdate(date):
    pattern = []
    str1 = preprocess(date)
    for i in range(0, len(str1) + 1):
        if len(str1[i:i + 2]) == 2 and str1[i:i + 2] not in pattern:
            pattern.append(str1[i:i + 2])
    return pattern


def substring(str1):
    str1 = str(str1)
    list1 = str1.split()
    pattern = []
    for word in list1:
        pattern.append(word[::-1].lower())
        if len(word) < 4:
            pattern.append(word.lower())

        else:
            for i in range(0, len(word) + 1):
                if len(word[i:i + 4]) == 4:
                    pattern.append(str(word[i:i + 4]).lower())
    return pattern


def mob_check(Mobile):
    Mobile = str(Mobile)
    list1 = Mobile.split()
    pattern = []
    for word in list1:
        for i in range(0, len(word) + 1):
            if len(word[i:i + 4]) == 4:
                pattern.append(str(word[i:i + 4]).lower())
    return pattern


def LPSarray(pattern, Lps, len2):
    length = 0  # length of longest prefix
    i = 1
    Lps[0] = 0  # pre defining LPS of first element as 0 (no repetition)
    while (i < len2):
        if (pattern[length] == pattern[i]):
            Lps[i] = length + 1
            length += 1
            i += 1
        else:
            if (length == 0):
                Lps[i] = 0
                i += 1
            else:
                length = Lps[length - 1]


# Implementing KMP Algorithm
def KMP(pattern, password):
    len1 = len(password)
    len2 = len(pattern)
    Lps = [0] * len2  # creating LPS Array of length same as pattern
    LPSarray(pattern, Lps, len2)
    i = 0
    j = 0
    occurence = []  # creating occurence array to store indices at which pattern is found
    while (i < len1):
        if (password[i] == pattern[j]):
            i += 1
            j += 1
        else:
            if (j == 0):
                i += 1
            else:
                j = Lps[j - 1]
        if (j == len2):  # j is incremented if last character is also matched making it equal to pattern length
            occurence.append(i - j)
            j = Lps[j - 1]  # for finding multiple occurences
    if (len(occurence) != 0):  # if given pattern occurs atleast once in the password
        return True
    else:
        return False


def KMPsearch(detail, password):
    for i in range(0, len(detail)):
        if KMP(detail[i], password.lower()) == True:
            return 0
    return 1


def basic_check(password):
    try:
        if len(password) < 8:
            return "f Length < 8"
        if not any(char.islower() for char in password):
            return "f Use atleast one lower case character"
        if not any(char.isupper() for char in password):
            return "f Use atleast one upper case character"
        if not any(char.isdigit() for char in password):
            return "f Use atleast one digit"
        if not any(char in r"""@_!#$%^&*()<>?/|}{~:`-+=[]\;",'.""" for char in password):
            return "f Use atleast one special case character"
        if any(ord(password[i + 2]) == ord(password[i + 1]) + 1 == ord(password[i]) + 2 for i in
               range(len(password) - 2) if password[i:i + 3].isalpha()):
            return "f Sequence of consecutive alphabets (abc,ijk)"
        if any(int(password[i + 2]) == int(password[i + 1]) + 1 == int(password[i]) + 2 for i in
               range(len(password) - 2) if password[i:i + 3].isdigit()):
            return "f Sequence of consecutive digits"
        return "t"
    except SyntaxError:
        pass


def check_password(Name, father_name, mother_name, Mobile, City, dob, doj, spouse_name, spouse_dob,
                   doa, password):
    basic_result = basic_check(password)
    check_name = substring(Name)
    check_dob = subdate(preprocess(dob))
    check_fname = substring(father_name)
    check_mname = substring(mother_name)
    check_mobile = mob_check(Mobile)
    check_city = substring(City)
    check_sname = substring(spouse_name)
    check_sdob = subdate(preprocess(spouse_dob))
    check_doa = subdate(preprocess(doa))
    check_doj = subdate(preprocess(doj))
    details = [check_name, check_dob, check_sname, check_sdob, check_doa, check_doj, check_fname, check_mname,
               check_mobile, check_city]

    if basic_result[0] == 'f':
        if len(password) < 10:
            time_crack,unit = time_to_crack_password(password)
            time_crack = "%.2f"%time_crack
            time_crack = str(time_crack)
            time = time_crack+" "+unit
            result = "Weak Password"
            result = result+" : "+basic_result[2:]
            return (result,time)
        else:
            result = "Weak Password"
            result = result+" : "+basic_result[2:]
            time = None
            return (result,time)

    for detail in details:
        check = KMPsearch(detail, password)
        if check == 0:
            result = "Weak Password"
            result = result+": Usage of Personal Details"
            time = None
            return (result,time)

    result = "Strong Password"
    time_crack,unit = time_to_crack_password(password)
    time_crack = "%.2f" % time_crack
    time_crack = str(time_crack)
    time = time_crack+" "+unit
    return (result,time)


# Password recommendation

global recommended_passwords
recommended_passwords = []




def password_gen1(Name,father_name, mother_name, Mobile, City):
    global recommended_passwords
    new_password = ""
    details = [Name, father_name, mother_name, City]
    # taking length of password to be 14
    numbers = "0123456789"
    symbols = "@_!#$%^&*?/~-+="
    list1 = [numbers, symbols]
    j = 0
    new_password += Mobile[0]
    for i in range(0, 13, 4):
        detail_list = details[j].split()
        detail = detail_list[0]
        new_password += detail[0].upper() + detail[-1].lower()
        if (i == 4 or i == 12):
            new_password += random.choice(symbols)
        else:
            new_password += random.choice(numbers)
        j += 1
    new_password += Mobile[-1]
    recommended_passwords.append(new_password)


def password_gen2(Name, father_name, mother_name, Mobile, City):
    global recommended_passwords
    new_password = ""
    details = [Name, father_name, mother_name, City]
    # taking length of password to be 14
    numbers = "0123456789"
    symbols = "@_!#$%^&*?/~-+="
    j = 0
    new_password += Mobile[0]
    for i in range(0, 10, 3):
        detail_list = details[j].split()
        detail = detail_list[0]
        new_password += detail[0].upper() + detail[-1].lower()
        j += 1
    for k in range(2):
        new_password += random.choice(numbers)
        new_password += random.choice(symbols)
    new_password += Mobile[-1]
    recommended_passwords.append(new_password)





# generating 5 different passwords for the user
def generate_password(Name, father_name, mother_name, Mobile, City):
    global recommended_passwords
    password_gen1(Name, father_name, mother_name, Mobile, City)
    password_gen1(Name, father_name, mother_name, Mobile, City)
    password_gen2(Name, father_name, mother_name, Mobile, City)
    password_gen2(Name, father_name, mother_name, Mobile, City)
    random_password = random.choice(recommended_passwords)
    return random_password

#Time to crack password using Brute Force, considering hacker tries every possible combination manually and doesn't use other attacks like
#rainbow attacks, dictionary attacks etc.
#Formula used here is -
#Time (in seconds) = Number of possible combinations / Guesses per second
#assuming guesses per second to be 1 billion (considering the trend of increasing computational power)
#this is the WORST CASE that we are considering

def time_to_crack_password(password):
    L=len(password)
    lower,upper,numbers,symbols=(0,0,0,0)
    for i in range(L):
        if password[i].isdigit():
            numbers+=1
        elif password[i].islower():
            lower+=1
        elif password[i].isupper():
            upper+=1
        else:
            symbols+=1
    if (numbers==len(password)):
        N=10 #here N is the size of character set
    elif (lower==len(password) or upper==len(password)):
        N=26
    elif (symbols==len(password)):
        N=33
    elif (upper==0 and symbols==0):
        N=36
    elif (lower==0 and symbols==0):
        N=36
    elif (numbers==0 and symbols==0):
        N=52
    elif (upper==0 and lower==0):
        N=43
    elif (upper==0 and numbers==0):
        N=59
    elif (lower==0 and numbers==0):
        N=59
    elif (symbols==0):
        N=62
    elif (lower==0):
        N=69
    elif (upper==0):
        N=69
    elif(numbers==0):
        N=85
    else:
        N=95
  #here N is the size of character set and L is the length of password
    G=10**9 #assuming 1 billion guesses per second made by the hacker
    time=(N**L)/G #seconds
    if (time<60):
        unit="seconds"
        return time,unit
    else:
        minutes=time/60
        if (minutes<60):
            unit="minutes"
            return minutes,unit
        else:
            hours=minutes/60
            if(hours<24):
                unit="hours"
                return hours,unit
            else:
                days=hours/24
                if (days<365):
                    unit="days"
                    return days,unit
                else:
                    years=days/365
                    if (years<10):
                        unit="years"
                        return years,unit
                    else:
                        centuries=years/10
                        unit="centuries"
                        return centuries,unit

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)