# Developed by dnoobnerd [https://dnoobnerd.netlify.app]    Made with Streamlit


###### Packages Used ######
import streamlit as st # core package used in this project
import pandas as pd
import base64, random
import time,datetime
import pymysql
import os
import socket
import platform
import geocoder
import secrets
import io,random
import plotly.express as px # to create visualisations at the admin session
import plotly.graph_objects as go
import pdfplumber
import re
import spacy
nlp = spacy.load("en_core_web_sm")
from styles import page_bg
from ui import show_header, show_metrics, ats_chart
from geopy.geocoders import Nominatim
from parser import extract_resume_data

# libraries used to parse the pdf files
# from pyresparser import ResumeParser
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
from streamlit_tags import st_tags
from PIL import Image
# pre stored data for prediction purposes
from Courses import ds_course,web_course,android_course,ios_course,uiux_course,resume_videos,interview_videos
import nltk

try:
    nltk.data.find('corpora/stopwords')

except LookupError:
    nltk.download('stopwords')

from nltk.corpus import stopwords

stop_words = set(stopwords.words('english'))


###### Preprocessing functions ######
def extract_resume_data(pdf_path):

    text = ""

    # Extract text from PDF
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted

    # Extract email
    email = re.findall(r'[\w\.-]+@[\w\.-]+', text)
    email = email[0] if email else ""

    # Extract phone number
    phone = re.findall(r'\+?\d[\d -]{8,12}\d', text)
    phone = phone[0] if phone else ""

    # NLP processing
    doc = nlp(text)

    # Extract name
    name = ""

    for ent in doc.ents:
        if ent.label_ == "PERSON":
            name = re.sub(r'\\+?\\d.*', '', ent.text).strip()
            break

    # Skills database
    skills_db = [
        "python",
        "java",
        "sql",
        "mysql",
        "html",
        "css",
        "javascript",
        "react",
        "django",
        "streamlit",
        "machine learning",
        "tensorflow",
        "flask",
        "pandas",
        "numpy"
    ]

    found_skills = []

    lower_text = text.lower()

    for skill in skills_db:
        if skill.lower() in lower_text:
            found_skills.append(skill)

    return {
        "name": name,
        "email": email,
        "mobile_number": phone,
        "skills": found_skills,
        "no_of_pages": len(pdf.pages)
    }


# Generates a link allowing the data in a given panda dataframe to be downloaded in csv format 
def get_csv_download_link(df,filename,text):
    csv = df.to_csv(index=False)
    ## bytes conversions
    b64 = base64.b64encode(csv.encode()).decode()      
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href


# Reads Pdf file and check_extractable
def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)
            print(page)
        text = fake_file_handle.getvalue()

    ## close open handles
    converter.close()
    fake_file_handle.close()
    return text


# show uploaded file path to view pdf_display
def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


# course recommendations which has data already loaded from Courses.py
def course_recommender(course_list):
    st.subheader("**Courses & Certificates Recommendations 👨‍🎓**")
    c = 0
    rec_course = []
    ## slider to choose from range 1-10
    no_of_reco = st.slider('Choose Number of Course Recommendations:', 1, 10, 5)
    random.shuffle(course_list)
    for c_name, c_link in course_list:
        c += 1
        st.markdown(f"({c}) [{c_name}]({c_link})")
        rec_course.append(c_name)
        if c == no_of_reco:
            break
    return rec_course


###### Database Stuffs ######


# sql connector
# connection = pymysql.connect(host='localhost',user='root',password='',db='cv')
# cursor = connection.cursor()
try:

    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        db='cv'
    )

    cursor = connection.cursor()

except:

    connection = None
    cursor = None


# inserting miscellaneous data, fetched results, prediction and recommendation into user_data table
def insert_data(sec_token,ip_add,host_name,dev_user,os_name_ver,latlong,city,state,country,act_name,act_mail,act_mob,name,email,res_score,timestamp,no_of_pages,reco_field,cand_level,skills,recommended_skills,courses,pdf_name):
    DB_table_name = 'user_data'
    insert_sql = "insert into " + DB_table_name + """
    values (0,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    rec_values = (str(sec_token),str(ip_add),host_name,dev_user,os_name_ver,str(latlong),city,state,country,act_name,act_mail,act_mob,name,email,str(res_score),timestamp,str(no_of_pages),reco_field,cand_level,skills,recommended_skills,courses,pdf_name)
    cursor.execute(insert_sql, rec_values)
    connection.commit()


# inserting feedback data into user_feedback table
def insertf_data(feed_name,feed_email,feed_score,comments,Timestamp):
    DBf_table_name = 'user_feedback'
    insertfeed_sql = "insert into " + DBf_table_name + """
    values (0,%s,%s,%s,%s,%s)"""
    rec_values = (feed_name, feed_email, feed_score, comments, Timestamp)
    cursor.execute(insertfeed_sql, rec_values)
    connection.commit()


###### Setting Page Configuration (favicon, Logo, Title) ######


st.set_page_config(
   page_title="ResumeIQ",
   page_icon='./Logo/recommend.png',
)
st.markdown(page_bg, unsafe_allow_html=True) 

###### Main function run() ######


def run():
    st.markdown("""
    <h1 style='text-align:center; color:#4F46E5;'>
    ResumeIQ 🚀
    </h1>

    <h3 style='text-align:center;'>
    AI-Powered ATS Resume Analyzer
    </h3>
    """, unsafe_allow_html=True)
    
    # (Logo, Heading, Sidebar etc)
    # img = Image.open('./Logo/RESUM.png')
    # st.image(img)
    try:
        img = Image.open('Logo/RESUM.jpg')
        st.image(img, width=250)

    except:
        st.warning("Logo image not found.")

    col1, col2, col3 = st.columns([1,2,1])

   
    st.sidebar.title("ResumeIQ Dashboard")
    activities = ["User", "Feedback", "About", "Admin"]
    choice = st.sidebar.selectbox("Navigation", activities)
    # link = '<b>Built with 🤍 by Divya Maddula</b>' 
    # st.sidebar.markdown(link, unsafe_allow_html=True)
    # st.sidebar.markdown('''
    #     <!-- site visitors -->

    #     <div id="sfct2xghr8ak6lfqt3kgru233378jya38dy" hidden></div>

    #     <noscript>
    #         <a href="https://www.freecounterstat.com" title="hit counter">
    #             <img src="https://counter9.stat.ovh/private/freecounterstat.php?c=t2xghr8ak6lfqt3kgru233378jya38dy" border="0" title="hit counter" alt="hit counter"> -->
    #         </a>
    #     </noscript>
    
    #     <p>Visitors <img src="https://counter9.stat.ovh/private/freecounterstat.php?c=t2xghr8ak6lfqt3kgru233378jya38dy" title="Free Counter" Alt="web counter" width="60px"  border="0" /></p>
    
    # ''', unsafe_allow_html=True)

    ###### Creating Database and Table ######


    # Create the DB
    db_sql = """CREATE DATABASE IF NOT EXISTS CV;"""
    cursor.execute(db_sql)


    # Create table user_data and user_feedback
    DB_table_name = 'user_data'
    table_sql = "CREATE TABLE IF NOT EXISTS " + DB_table_name + """
                    (ID INT NOT NULL AUTO_INCREMENT,
                    sec_token varchar(20) NOT NULL,
                    ip_add varchar(50) NULL,
                    host_name varchar(50) NULL,
                    dev_user varchar(50) NULL,
                    os_name_ver varchar(50) NULL,
                    latlong varchar(50) NULL,
                    city varchar(50) NULL,
                    state varchar(50) NULL,
                    country varchar(50) NULL,
                    act_name varchar(50) NOT NULL,
                    act_mail varchar(50) NOT NULL,
                    act_mob varchar(20) NOT NULL,
                    Name varchar(500) NOT NULL,
                    Email_ID VARCHAR(500) NOT NULL,
                    resume_score VARCHAR(8) NOT NULL,
                    Timestamp VARCHAR(50) NOT NULL,
                    Page_no VARCHAR(5) NOT NULL,
                    Predicted_Field BLOB NOT NULL,
                    User_level BLOB NOT NULL,
                    Actual_skills BLOB NOT NULL,
                    Recommended_skills BLOB NOT NULL,
                    Recommended_courses BLOB NOT NULL,
                    pdf_name varchar(50) NOT NULL,
                    PRIMARY KEY (ID)
                    );
                """
    cursor.execute(table_sql)


    DBf_table_name = 'user_feedback'
    tablef_sql = "CREATE TABLE IF NOT EXISTS " + DBf_table_name + """
                    (ID INT NOT NULL AUTO_INCREMENT,
                        feed_name varchar(50) NOT NULL,
                        feed_email VARCHAR(50) NOT NULL,
                        feed_score VARCHAR(5) NOT NULL,
                        comments VARCHAR(100) NULL,
                        Timestamp VARCHAR(50) NOT NULL,
                        PRIMARY KEY (ID)
                    );
                """
    cursor.execute(tablef_sql)


    ###### CODE FOR CLIENT SIDE (USER) ######

    if choice == 'User':
        
        # Collecting Miscellaneous Information
        act_name = st.text_input('Name*')
        act_mail = st.text_input('Mail*')
        act_mob  = st.text_input('Mobile Number*')
        sec_token = secrets.token_urlsafe(12)
        host_name = socket.gethostname()
        ip_add = socket.gethostbyname(host_name)
        dev_user = os.getlogin()
        os_name_ver = platform.system() + " " + platform.release()
        g = geocoder.ip('me')
        latlong = g.latlng
        geolocator = Nominatim(user_agent="http")
        location = geolocator.reverse(latlong, language='en')
        address = location.raw['address']
        cityy = address.get('city', '')
        statee = address.get('state', '')
        countryy = address.get('country', '')  
        city = cityy
        state = statee
        country = countryy


        # Upload Resume
        st.markdown('''<h5 style='text-align: left; color: #021659;'> Upload Your Resume, And Get Smart Recommendations</h5>''',unsafe_allow_html=True)
        
        ## file upload in pdf format
        pdf_file = st.file_uploader("Choose your Resume", type=["pdf"])
        if pdf_file is not None:
            with st.spinner('Hang On While We Cook Magic For You...'):
                time.sleep(4)
        
            ### saving the uploaded resume to folder
            save_image_path = './Uploaded_Resumes/'+pdf_file.name
            pdf_name = pdf_file.name
            with open(save_image_path, "wb") as f:
                f.write(pdf_file.getbuffer())
            show_pdf(save_image_path)

            ### parsing and extracting whole resume 
            resume_data = extract_resume_data(save_image_path)
            if resume_data:
                
                ## Get the whole resume data into resume_text
                resume_text = pdf_reader(save_image_path)
                resume_text_lower = resume_text.lower()
                st.subheader("Select Target Role")

                role = st.selectbox(
                    "Choose Job Role",
                    [
                        "Software Engineer",
                        "Data Analyst",
                        "Data Scientist",
                        "Frontend Developer"
                    ]
                )
                default_jd = ""
                if role == "Software Engineer":

                    default_jd = """
                    Required Skills:
                    Python, Java, SQL, HTML, CSS, JavaScript,
                    React, Node.js, Git, GitHub,
                    REST APIs, Data Structures, Algorithms,
                    AWS, Docker
                    """

                elif role == "Data Analyst":

                    default_jd = """
                    Required Skills:
                    Python, SQL, Excel, Power BI,
                    Tableau, Pandas, NumPy,
                    Statistics, Data Visualization,
                    Data Cleaning
                    """

                elif role == "Data Scientist":

                    default_jd = """
                    Required Skills:
                    Python, Machine Learning,
                    TensorFlow, Scikit-learn,
                    Pandas, NumPy, Deep Learning,
                    NLP, Data Visualization
                    """

                elif role == "Frontend Developer":

                    default_jd = """
                    Required Skills:
                    HTML, CSS, JavaScript,
                    React, Bootstrap,
                    Responsive Design,
                    REST APIs, Git
                    """
                st.subheader("Job Description Matching")

                job_description = st.text_area(
                    "Job Description",
                    value=default_jd,
                    height=250
                )
                ats_score = 0
                missing_skills = []
                matched_skills = []
                reco_field = "ATS-Based Recommendation"
                recommended_skills = []
                rec_course = []
                if job_description:

                    jd_text = job_description.lower()
                    tech_skills = [
                        "python",
                        "java",
                        "sql",
                        "mysql",
                        "html",
                        "css",
                        "javascript",
                        "react",
                        "node.js",
                        "django",
                        "flask",
                        "streamlit",
                        "aws",
                        "docker",
                        "git",
                        "github",
                        "rest api",
                        "mongodb",
                        "data structures",
                        "algorithms",
                        "oop"
                    ]
                    jd_skills = []

                    for skill in tech_skills:
                        if skill in jd_text:
                            jd_skills.append(skill)
                    resume_skills = []

                    for skill in tech_skills:
                        if skill in resume_text_lower:
                            resume_skills.append(skill)

                    matched_skills = set(resume_skills).intersection(jd_skills)

                    ats_score = int(
                        (len(matched_skills) / len(jd_skills)) * 100
                    )
                    st.success(f"ATS Match Score: {ats_score}%")

                    st.progress(ats_score / 100)

                    st.subheader("Matched Skills")
                    st.write(list(matched_skills))

                    missing_skills = set(jd_skills) - set(resume_skills)

                    st.subheader("Missing Skills")
                    st.write(list(missing_skills))
                    st.subheader("Recommended Skills for You 🚀")
                    if missing_skills:

                        for skill in missing_skills:

                            st.markdown(
                                f"""
                                <div style="
                                    background-color:#4F46E5;
                                    color:white;
                                    padding:10px;
                                    border-radius:10px;
                                    margin-bottom:8px;
                                    width:fit-content;
                                ">
                                {skill.upper()}
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                    else:

                        st.success(
                            "Excellent! Your resume already matches most required skills."
                        )


                ## Showing Analyzed data from (resume_data)
                st.header("**Resume Analysis 🤘**")
                st.success("Hello "+ resume_data['name'])
                st.subheader("**Your Basic info 👀**")
                col1, col2 = st.columns(2)

                with col1:
                    st.info(f"📧 {resume_data['email']}")

                with col2:
                    st.info(f"📱 {resume_data['mobile_number']}")
                try:
                    st.text('Name: '+resume_data['name'])
                    st.text('Email: ' + resume_data['email'])
                    st.text('Contact: ' + resume_data['mobile_number'])
                    st.text('Degree: '+str(resume_data['degree']))                    
                    st.text('Resume pages: '+str(resume_data['no_of_pages']))

                except:
                    pass
                ## Predicting Candidate Experience Level 

                ### Trying with different possibilities
                cand_level = ''
                if resume_data['no_of_pages'] < 1:                
                    cand_level = "NA"
                    st.markdown( '''<h4 style='text-align: left; color: #d73b5c;'>You are at Fresher level!</h4>''',unsafe_allow_html=True)
                
                #### if internship then intermediate level
                elif 'INTERNSHIP' in resume_text:
                    cand_level = "Intermediate"
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
                elif 'INTERNSHIPS' in resume_text:
                    cand_level = "Intermediate"
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
                elif 'Internship' in resume_text:
                    cand_level = "Intermediate"
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
                elif 'Internships' in resume_text:
                    cand_level = "Intermediate"
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
                
                #### if Work Experience/Experience then Experience level
                elif 'EXPERIENCE' in resume_text:
                    cand_level = "Experienced"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',unsafe_allow_html=True)
                elif 'WORK EXPERIENCE' in resume_text:
                    cand_level = "Experienced"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',unsafe_allow_html=True)
                elif 'Experience' in resume_text:
                    cand_level = "Experienced"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',unsafe_allow_html=True)
                elif 'Work Experience' in resume_text:
                    cand_level = "Experienced"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',unsafe_allow_html=True)
                else:
                    cand_level = "Fresher"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at Fresher level!!''',unsafe_allow_html=True)


                ## Skills Analyzing and Recommendation
                st.subheader("**Skills Recommendation 💡**")
                
                ### Current Analyzed Skills
                # keywords = st_tags(label='### Your Current Skills',
                # st.subheader("Skills Detected")

                # skills_html = ""

                # for skill in resume_data['skills']:
                #     skills_html += f"<span class='skill-pill'>{skill}</span>"

                # st.markdown(skills_html, unsafe_allow_html=True)
                # text='See our skills recommendation below',value=resume_data['skills'],key = '1 '
                st.subheader("Skills Detected")

                skills_html = ""

                for skill in resume_data['skills']:
                    skills_html += f"""
                        <span style="
                        background:#4F46E5;
                        padding:8px 12px;
                        border-radius:20px;
                        margin:5px;
                        display:inline-block;
                        color:white;
                        font-size:14px;
                        ">
                        {skill.upper()}
                        </span>
                        """
                st.markdown(skills_html, unsafe_allow_html=True)
                ### Keywords for Recommendations
                ds_keyword = ['tensorflow','keras','pytorch','machine learning','deep Learning','flask','streamlit']
                web_keyword = ['react', 'django', 'node jS', 'react js', 'php', 'laravel', 'magento', 'wordpress','javascript', 'angular js', 'C#', 'Asp.net', 'flask']
                android_keyword = ['android','android development','flutter','kotlin','xml','kivy']
                ios_keyword = ['ios','ios development','swift','cocoa','cocoa touch','xcode']
                uiux_keyword = ['ux','adobe xd','figma','zeplin','balsamiq','ui','prototyping','wireframes','storyframes','adobe photoshop','photoshop','editing','adobe illustrator','illustrator','adobe after effects','after effects','adobe premier pro','premier pro','adobe indesign','indesign','wireframe','solid','grasp','user research','user experience']
                n_any = ['english','communication','writing', 'microsoft office', 'leadership','customer management', 'social media']
                ### Skill Recommendations Starts  


                # recommended_skills = []
                # reco_field = ''
                # rec_course = ''

                # ### condition starts to check skills from keywords and predict field
                # for i in resume_data['skills']:
                
                #     #### Data science recommendation
                #     if i.lower() in ds_keyword:
                #         print(i.lower())
                #         reco_field = 'Data Science'
                #         st.success("** Our analysis says you are looking for Data Science Jobs.**")
                #         recommended_skills = ['Data Visualization','Predictive Analysis','Statistical Modeling','Data Mining','Clustering & Classification','Data Analytics','Quantitative Analysis','Web Scraping','ML Algorithms','Keras','Pytorch','Probability','Scikit-learn','Tensorflow',"Flask",'Streamlit']
                #         recommended_keywords = st_tags(label='### Recommended skills for you.',
                #         text='Recommended skills generated from System',value=recommended_skills,key = '2')
                #         st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job</h5>''',unsafe_allow_html=True)
                #         # course recommendation
                #         rec_course = course_recommender(ds_course)
                #         break

                    #### Web development recommendation
                    # elif i.lower() in web_keyword:
                    #     print(i.lower())
                    #     reco_field = 'Web Development'
                    #     st.success("** Our analysis says you are looking for Web Development Jobs **")
                    #     recommended_skills = ['React','Django','Node JS','React JS','php','laravel','Magento','wordpress','Javascript','Angular JS','c#','Flask','SDK']
                    #     recommended_keywords = st_tags(label='### Recommended skills for you.',
                    #     text='Recommended skills generated from System',value=recommended_skills,key = '3')
                    #     st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h5>''',unsafe_allow_html=True)
                    #     # course recommendation
                    #     rec_course = course_recommender(web_course)
                    #     break

                    # #### Android App Development
                    # elif i.lower() in android_keyword:
                    #     print(i.lower())
                    #     reco_field = 'Android Development'
                    #     st.success("** Our analysis says you are looking for Android App Development Jobs **")
                    #     recommended_skills = ['Android','Android development','Flutter','Kotlin','XML','Java','Kivy','GIT','SDK','SQLite']
                    #     recommended_keywords = st_tags(label='### Recommended skills for you.',
                    #     text='Recommended skills generated from System',value=recommended_skills,key = '4')
                    #     st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h5>''',unsafe_allow_html=True)
                        # course recommendation
                    #     rec_course = course_recommender(android_course)
                    #     break

                    # #### IOS App Development
                    # elif i.lower() in ios_keyword:
                    #     print(i.lower())
                    #     reco_field = 'IOS Development'
                    #     st.success("** Our analysis says you are looking for IOS App Development Jobs **")
                    #     recommended_skills = ['IOS','IOS Development','Swift','Cocoa','Cocoa Touch','Xcode','Objective-C','SQLite','Plist','StoreKit',"UI-Kit",'AV Foundation','Auto-Layout']
                    #     recommended_keywords = st_tags(label='### Recommended skills for you.',
                    #     text='Recommended skills generated from System',value=recommended_skills,key = '5')
                    #     st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h5>''',unsafe_allow_html=True)
                    #     # course recommendation
                    #     rec_course = course_recommender(ios_course)
                    #     break

                    # #### Ui-UX Recommendation
                    # elif i.lower() in uiux_keyword:
                    #     print(i.lower())
                    #     reco_field = 'UI-UX Development'
                    #     st.success("** Our analysis says you are looking for UI-UX Development Jobs **")
                    #     recommended_skills = ['UI','User Experience','Adobe XD','Figma','Zeplin','Balsamiq','Prototyping','Wireframes','Storyframes','Adobe Photoshop','Editing','Illustrator','After Effects','Premier Pro','Indesign','Wireframe','Solid','Grasp','User Research']
                    #     recommended_keywords = st_tags(label='### Recommended skills for you.',
                    #     text='Recommended skills generated from System',value=recommended_skills,key = '6')
                    #     st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h5>''',unsafe_allow_html=True)
                    #     # course recommendation
                    #     rec_course = course_recommender(uiux_course)
                    #     break

                    # #### For Not Any Recommendations
                    # elif i.lower() in n_any:
                    #     print(i.lower())
                    #     reco_field = 'NA'
                    #     st.warning("** Currently our tool only predicts and recommends for Data Science, Web, Android, IOS and UI/UX Development**")
                    #     recommended_skills = ['No Recommendations']
                    #     recommended_keywords = st_tags(label='### Recommended skills for you.',
                    #     text='Currently No Recommendations',value=recommended_skills,key = '6')
                    #     st.markdown('''<h5 style='text-align: left; color: #092851;'>Maybe Available in Future Updates</h5>''',unsafe_allow_html=True)
                    #     # course recommendation
                    #     rec_course = "Sorry! Not Available for this Field"
                    #     break



                st.subheader("Resume Tips & Ideas 🥂")

                resume_score = 0

                resume_text_lower = resume_text.lower()

                resume_checks = [
                    {
                        "keywords": ["objective", "summary"],
                        "score": 6,
                        "success": "[+] Great! Resume has Objective/Summary section.",
                        "failure": "[-] Add an Objective or Summary section."
                    },

                    {
                        "keywords": ["education", "school", "college"],
                        "score": 12,
                        "success": "[+] Education details detected.",
                        "failure": "[-] Add Education details."
                    },

                    {
                        "keywords": ["work experience", "professional experience"],
                        "score": 16,
                        "success": "[+] Experience section detected.",
                        "failure": "[-] Add Work Experience section."
                    },

                    {
                        "keywords": ["internship", "internships"],
                        "score": 6,
                        "success": "[+] Internship section detected.",
                        "failure": "[-] Add Internship experience."
                    },

                    {
                        "keywords": ["skills", "skill"],
                        "score": 7,
                        "success": "[+] Skills section detected.",
                        "failure": "[-] Add Skills section."
                    },

                    {
                        "keywords": ["hobbies", "hobby"],
                        "score": 4,
                        "success": "[+] Hobbies section detected.",
                        "failure": "[-] Add Hobbies section."
                    },

                    {
                        "keywords": ["interests", "interest"],
                        "score": 5,
                        "success": "[+] Interests section detected.",
                        "failure": "[-] Add Interests section."
                    },

                    {
                        "keywords": ["achievements", "achievement"],
                        "score": 13,
                        "success": "[+] Achievements section detected.",
                        "failure": "[-] Add Achievements section."
                    },

                    {
                        "keywords": ["certifications", "certification"],
                        "score": 12,
                        "success": "[+] Certifications section detected.",
                        "failure": "[-] Add Certifications section."
                    },

                    {
                        "keywords": ["projects", "project"],
                        "score": 19,
                        "success": "[+] Projects section detected.",
                        "failure": "[-] Add Projects section."
                    }
                ]

                for section in resume_checks:

                    if any(
                        keyword in resume_text_lower
                        for keyword in section["keywords"]
                    ):

                        resume_score += section["score"]

                        st.markdown(
                            f"""
                            <h5 style='color:#1ed760;'>
                            {section["success"]}
                            </h5>
                            """,
                            unsafe_allow_html=True
                        )

                    else:

                        st.markdown(
                            f"""
                            <h5 style='color:#ff4b4b;'>
                            {section["failure"]}
                            </h5>
                            """,
                            unsafe_allow_html=True
                        )


                st.subheader("Resume Score 📝")

                st.markdown(
                    """
                    <style>
                        .stProgress > div > div > div > div {
                            background-color: #4F46E5;
                        }
                    </style>
                    """,
                    unsafe_allow_html=True
                )

                my_bar = st.progress(0)

                for percent in range(resume_score):
                    time.sleep(0.02)
                    my_bar.progress(percent + 1)

                st.success(f"Your Resume Score: {resume_score}/100")
                st.subheader("AI Resume Improvement Suggestions 🚀")
                suggestions = []

                # ATS-based suggestions
                if ats_score < 50:
                    suggestions.append(
                        "Improve ATS match by adding more job-specific technical skills."
                    )

                # Missing skills suggestions
                if "aws" in missing_skills:
                    suggestions.append(
                        "Consider learning and adding AWS/cloud experience."
                    )

                if "docker" in missing_skills:
                    suggestions.append(
                        "Docker and deployment skills are highly valuable for SDE roles."
                    )

                if "react" in missing_skills:
                    suggestions.append(
                        "Frontend frameworks like React can strengthen your profile."
                    )

                # Resume score suggestions
                if resume_score < 70:
                    suggestions.append(
                        "Add stronger projects and certifications to improve resume quality."
                    )

                # Candidate level suggestions
                if cand_level == "Fresher":
                    suggestions.append(
                        "Add internships, hackathons, or open-source contributions."
                    )

                # Achievement suggestions
                if "achievement" not in resume_text_lower:
                    suggestions.append(
                        "Add measurable achievements with numbers and impact metrics."
                    )

                # GitHub suggestion
                if "github" not in resume_text_lower:
                    suggestions.append(
                        "Include GitHub profile links to showcase your projects."
                    )
                if suggestions:

                    for tip in suggestions:

                        st.markdown(
                            f"""
                            <div style="
                                background-color:#111827;
                                padding:12px;
                                border-radius:10px;
                                margin-bottom:10px;
                                color:white;
                            ">
                            🚀 {tip}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                else:

                    st.success(
                        "Excellent Resume! Your profile looks strong."
                    )

                ### Getting Current Date and Time
                ts = time.time()
                cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                timestamp = str(cur_date+'_'+cur_time)


                ## Calling insert_data to add all the data into user_data                
                # insert_data(str(sec_token), str(ip_add), (host_name), (dev_user), (os_name_ver), (latlong), (city), (state), (country), (act_name), (act_mail), (act_mob), resume_data['name'], resume_data['email'], str(resume_score), timestamp, str(resume_data['no_of_pages']), reco_field, cand_level, str(resume_data['skills']), str(recommended_skills), str(rec_course), pdf_name)
                if connection:

                    insert_data(
                        str(sec_token),
                        str(ip_add),
                        host_name,
                        dev_user,
                        os_name_ver,
                        latlong,
                        city,
                        state,
                        country,
                        act_name,
                        act_mail,
                        act_mob,
                        resume_data['name'],
                        resume_data['email'],
                        str(resume_score),
                        timestamp,
                        str(resume_data['no_of_pages']),
                        reco_field,
                        cand_level,
                        str(resume_data['skills']),
                        str(recommended_skills),
                        str(rec_course),
                        pdf_name
                    )
                ## Recommending Resume Writing Video
                st.header("**Bonus Video for Resume Writing Tips💡**")
                resume_vid = random.choice(resume_videos)
                st.video(resume_vid)

                ## Recommending Interview Preparation Video
                st.header("**Bonus Video for Interview Tips💡**")
                interview_vid = random.choice(interview_videos)
                st.video(interview_vid)

                ## On Successful Result 
                st.balloons()

            else:
                st.error('Something went wrong..')  
            show_metrics(
                resume_data['skills'],
                resume_data['no_of_pages'],
                resume_score
            )

            ats_chart(resume_score)              


    ###### CODE FOR FEEDBACK SIDE ######
    elif choice == 'Feedback':   
        
        # timestamp 
        ts = time.time()
        cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
        cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
        timestamp = str(cur_date+'_'+cur_time)

        # Feedback Form
        with st.form("my_form"):
            st.write("Feedback form")            
            feed_name = st.text_input('Name')
            feed_email = st.text_input('Email')
            feed_score = st.slider('Rate Us From 1 - 5', 1, 5)
            comments = st.text_input('Comments')
            Timestamp = timestamp        
            submitted = st.form_submit_button("Submit")
            if submitted:
                ## Calling insertf_data to add dat into user feedback
                reco_field = "ATS-Based Recommendation"

                rec_course = []

                recommended_skills = list(missing_skills)
                insertf_data(feed_name,feed_email,feed_score,comments,Timestamp)    
                ## Success Message 
                st.success("Thanks! Your Feedback was recorded.") 
                ## On Successful Submit
                st.balloons()    


        # query to fetch data from user feedback table
        query = 'select * from user_feedback'        
        plotfeed_data = pd.read_sql(query, connection)                        


        # fetching feed_score from the query and getting the unique values and total value count 
        labels = plotfeed_data.feed_score.unique()
        values = plotfeed_data.feed_score.value_counts()


        # plotting pie chart for user ratings
        st.subheader("**Past User Rating's**")
        fig = px.pie(values=values, names=labels, title="Chart of User Rating Score From 1 - 5", color_discrete_sequence=px.colors.sequential.Aggrnyl)
        st.plotly_chart(fig)


        #  Fetching Comment History
        cursor.execute('select feed_name, comments from user_feedback')
        plfeed_cmt_data = cursor.fetchall()

        st.subheader("**User Comment's**")
        dff = pd.DataFrame(plfeed_cmt_data, columns=['User', 'Comment'])
        st.dataframe(dff, width=1000)

    
    ###### CODE FOR ABOUT PAGE ######
    elif choice == 'About':   

        st.subheader("**About The Tool - AI RESUME ANALYZER**")

        st.markdown('''

        <p align='justify'>
            A tool which parses information from a resume using natural language processing and finds the keywords, cluster them onto sectors based on their keywords. And lastly show recommendations, predictions, analytics to the applicant based on keyword matching.
        </p>

        <p align="justify">
            <b>How to use it: -</b> <br/><br/>
            <b>User -</b> <br/>
            In the Side Bar choose yourself as user and fill the required fields and upload your resume in pdf format.<br/>
            Just sit back and relax our tool will do the magic on it's own.<br/><br/>
            <b>Feedback -</b> <br/>
            A place where user can suggest some feedback about the tool.<br/><br/>
            <b>Admin -</b> <br/>
            For login use <b>admin</b> as username and <b>admin@resume-analyzer</b> as password.<br/>
            It will load all the required stuffs and perform analysis.
        </p><br/><br/>

       

        ''',unsafe_allow_html=True)  


    ###### CODE FOR ADMIN SIDE (ADMIN) ######
    else:
        st.success('Welcome to Admin Side')

        #  Admin Login
        ad_user = st.text_input("Username")
        ad_password = st.text_input("Password", type='password')

        if st.button('Login'):
            
            ## Credentials 
            if ad_user == 'admin' and ad_password == 'admin@resume-analyzer':
                
                ### Fetch miscellaneous data from user_data(table) and convert it into dataframe
                cursor.execute('''SELECT ID, ip_add, resume_score, convert(Predicted_Field using utf8), convert(User_level using utf8), city, state, country from user_data''')
                datanalys = cursor.fetchall()
                plot_data = pd.DataFrame(datanalys, columns=['Idt', 'IP_add', 'resume_score', 'Predicted_Field', 'User_Level', 'City', 'State', 'Country'])
                
                ### Total Users Count with a Welcome Message
                values = plot_data.Idt.count()
                st.success("Welcome Divya ! Total %d " % values + " User's Have Used Our Tool : )")                
                
                ### Fetch user data from user_data(table) and convert it into dataframe
                cursor.execute('''SELECT ID, sec_token, ip_add, act_name, act_mail, act_mob, convert(Predicted_Field using utf8), Timestamp, Name, Email_ID, resume_score, Page_no, pdf_name, convert(User_level using utf8), convert(Actual_skills using utf8), convert(Recommended_skills using utf8), convert(Recommended_courses using utf8), city, state, country, latlong, os_name_ver, host_name, dev_user from user_data''')
                data = cursor.fetchall()                

                st.header("**User's Data**")
                df = pd.DataFrame(data, columns=['ID', 'Token', 'IP Address', 'Name', 'Mail', 'Mobile Number', 'Predicted Field', 'Timestamp',
                                                 'Predicted Name', 'Predicted Mail', 'Resume Score', 'Total Page',  'File Name',   
                                                 'User Level', 'Actual Skills', 'Recommended Skills', 'Recommended Course',
                                                 'City', 'State', 'Country', 'Lat Long', 'Server OS', 'Server Name', 'Server User',])
                
                ### Viewing the dataframe
                st.dataframe(df)
                
                ### Downloading Report of user_data in csv file
                st.markdown(get_csv_download_link(df,'User_Data.csv','Download Report'), unsafe_allow_html=True)

                ### Fetch feedback data from user_feedback(table) and convert it into dataframe
                cursor.execute('''SELECT * from user_feedback''')
                data = cursor.fetchall()

                st.header("**User's Feedback Data**")
                df = pd.DataFrame(data, columns=['ID', 'Name', 'Email', 'Feedback Score', 'Comments', 'Timestamp'])
                st.dataframe(df)

                ### query to fetch data from user_feedback(table)
                query = 'select * from user_feedback'
                plotfeed_data = pd.read_sql(query, connection)                        

                ### Analyzing All the Data's in pie charts

                # fetching feed_score from the query and getting the unique values and total value count 
                labels = plotfeed_data.feed_score.unique()
                values = plotfeed_data.feed_score.value_counts()
                
                # Pie chart for user ratings
                st.subheader("**User Rating's**")
                fig = px.pie(values=values, names=labels, title="Chart of User Rating Score From 1 - 5 🤗", color_discrete_sequence=px.colors.sequential.Aggrnyl)
                st.plotly_chart(fig)

                # fetching Predicted_Field from the query and getting the unique values and total value count                 
                labels = plot_data.Predicted_Field.unique()
                values = plot_data.Predicted_Field.value_counts()

                # Pie chart for predicted field recommendations
                st.subheader("**Pie-Chart for Predicted Field Recommendation**")
                fig = px.pie(df, values=values, names=labels, title='Predicted Field according to the Skills 👽', color_discrete_sequence=px.colors.sequential.Aggrnyl_r)
                st.plotly_chart(fig)

                # fetching User_Level from the query and getting the unique values and total value count                 
                labels = plot_data.User_Level.unique()
                values = plot_data.User_Level.value_counts()

                # Pie chart for User's👨‍💻 Experienced Level
                st.subheader("**Pie-Chart for User's Experienced Level**")
                fig = px.pie(df, values=values, names=labels, title="Pie-Chart 📈 for User's 👨‍💻 Experienced Level", color_discrete_sequence=px.colors.sequential.RdBu)
                st.plotly_chart(fig)

                # fetching resume_score from the query and getting the unique values and total value count                 
                labels = plot_data.resume_score.unique()                
                values = plot_data.resume_score.value_counts()

                # Pie chart for Resume Score
                st.subheader("**Pie-Chart for Resume Score**")
                fig = px.pie(df, values=values, names=labels, title='From 1 to 100 💯', color_discrete_sequence=px.colors.sequential.Agsunset)
                st.plotly_chart(fig)

                # fetching IP_add from the query and getting the unique values and total value count 
                labels = plot_data.IP_add.unique()
                values = plot_data.IP_add.value_counts()

                # Pie chart for Users
                st.subheader("**Pie-Chart for Users App Used Count**")
                fig = px.pie(df, values=values, names=labels, title='Usage Based On IP Address 👥', color_discrete_sequence=px.colors.sequential.matter_r)
                st.plotly_chart(fig)

                # fetching City from the query and getting the unique values and total value count 
                labels = plot_data.City.unique()
                values = plot_data.City.value_counts()

                # Pie chart for City
                st.subheader("**Pie-Chart for City**")
                fig = px.pie(df, values=values, names=labels, title='Usage Based On City 🌆', color_discrete_sequence=px.colors.sequential.Jet)
                st.plotly_chart(fig)

                # fetching State from the query and getting the unique values and total value count 
                labels = plot_data.State.unique()
                values = plot_data.State.value_counts()

                # Pie chart for State
                st.subheader("**Pie-Chart for State**")
                fig = px.pie(df, values=values, names=labels, title='Usage Based on State 🚉', color_discrete_sequence=px.colors.sequential.PuBu_r)
                st.plotly_chart(fig)

                # fetching Country from the query and getting the unique values and total value count 
                labels = plot_data.Country.unique()
                values = plot_data.Country.value_counts()

                # Pie chart for Country
                st.subheader("**Pie-Chart for Country**")
                fig = px.pie(df, values=values, names=labels, title='Usage Based on Country 🌏', color_discrete_sequence=px.colors.sequential.Purpor_r)
                st.plotly_chart(fig)

            ## For Wrong Credentials
            else:
                st.error("Wrong ID & Password Provided")

# Calling the main (run()) function to make the whole process run
run()
