import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
from PIL import Image
import pandas as pd
import numpy as np
import re
import io
import mysql.connector 

#Connnection to the mysql bixcard database
mydb = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = "",
        database = "bizcard",
        port = "3306"
    )

cursor =mydb.cursor()

def image_to_text(path):

    input_img= Image.open(path)

    #converting image to array formet
    image_arr= np.array(input_img)

    reader= easyocr.Reader(['en'])
    text= reader.readtext(image_arr,detail= 0)
    return text,input_img

def extracted_text(texts):
    extrd_dict = {"NAME":[],"DESIGNATION":[],"COMPANY_NAME":[],"CONTACT":[],"EMAIL":[],
                  "WEBSITE":[],"ADDRESS":[],"PINCODE":[]}
    extrd_dict["NAME"].append(texts[0])
    extrd_dict["DESIGNATION"].append(texts[1])

    for i in range(2,len(texts)):
        if texts[i].startswith("+") or (texts[i].replace("-","").isdigit() and '-' in texts[i]):
            extrd_dict["CONTACT"].append(texts[i])

        elif "@" in texts[i] and ".com" in texts[i]:
            small =texts[i].lower()
            extrd_dict["EMAIL"].append(small)

        elif "WWW" in texts[i] or "www" in texts[i] or "Www" in texts[i] or "wWw" in texts[i] or "wwW" in texts[i]:
            small = texts[i].lower()
            extrd_dict["WEBSITE"].append(small)

        elif "Tamil Nadu" in texts[i]  or "TamilNadu" in texts[i] or texts[i].isdigit():
            extrd_dict["PINCODE"].append(texts[i])

        elif re.match(r'^[A-Za-z]',texts[i]):
            extrd_dict["COMPANY_NAME"].append(texts[i])

        else:
            remove_colon = re.sub(r'[,;]', '', texts[i])
            extrd_dict["ADDRESS"].append(remove_colon)

    for key,value in extrd_dict.items():
        if len(value)>0:
            concadenate = ' '.join(value)
            extrd_dict[key] = [concadenate]
        else:
            value = 'NA'
            extrd_dict[key] = [value]

    return extrd_dict

# Streamlit Part

st.set_page_config(layout= "wide")
st.title(":rainbow[_EXTRACTING BUSINESS CARD DATA WITH 'OCR' :red[: ▶]_]")
st.write("")

Menu=st.sidebar.selectbox(":red[_**Please Select The Menu:-**_]",("Home", "Upload&Modify", "Delete"))

if Menu == "Home":
    with st.sidebar:
            st.header(":red[_Skill:-_]")
            st.write(':blue[ :star: Python scripting]') 
            st.write(':blue[ :star: OCR]')
            st.write(':blue[ :star: Data Extraction]')
            st.write(':blue[ :star: SQL]')
            st.write(':blue[ :star: Streamlit]')
    st.header("_**Project**_")
    st.subheader(':gray[Install the required packages:-]') 
    st.write('You will need to install Python, Streamlit, easyOCR, and a database management system like SQLite or MySQL.')
    st.subheader(':gray[Design the user interface:-]') 
    st.write("Create a simple and intuitive user interface using Streamlit that guides users through the process of uploading the business card image and extracting its information. You can use widgets like file uploader, buttons, and text boxes to make the interface more interactive.")
    st.subheader(':gray[Implement the image processing and OCR:-]') 
    st.write("Use easyOCR to extract the relevant information from the uploaded business card image. You can use image processing techniques like resizing, cropping, and thresholding to enhance the image quality before passing it to the OCR engine.")
    st.subheader(':gray[Display the extracted information:-]') 
    st.write("Once the information has been extracted, display it in a clean and organized manner in the Streamlit GUI. You can use widgets like tables, text boxes, and labels to present the information.")
    st.subheader(':gray[Implement database integration:-]') 
    st.write("Use a database management system like SQLite or MySQL to store the extracted information along with the uploaded business card image. You can use SQL queries to create tables, insert data, and retrieve data from the database, Update the data and Allow the user to delete the data through the streamlit UI")
    st.subheader(':gray[Test the application:-]') 
    st.write("Test the application thoroughly to ensure that it works as expected. You can run the application on your local machine by running the command streamlit run app.py in the terminal, where app.py is the name of your Streamlit application file.")
    st.subheader(':gray[Improve the application:-]') 
    st.write("Continuously improve the application by adding new features, optimizing the code, and fixing bugs. You can also add user authentication and authorization to make the application more secure.")


elif Menu == "Upload&Modify":

  img= st.file_uploader("Upload the Image", type= ["png", "jpg", "jpeg"], label_visibility= "hidden")

  if img is not None:
    st.image(img,width= 300)

    text_image,input_img= image_to_text(img)
    text_dict= extracted_text(text_image)

    if text_dict:
      st.success("TEXT IS EXTRACTED SUCCESSFULLY")


    df= pd.DataFrame(text_dict)

    #Converting Image to Bytes
    Image_bytes= io.BytesIO()
    input_img.save(Image_bytes,format= "PNG")

    image_data= Image_bytes.getvalue()

    #Creating dictionary
    data= {"Image":[image_data]}
    df_1= pd.DataFrame(data)

    concat_df= pd.concat([df,df_1],axis=1)

    button3= st.button("Save",use_container_width= True)

    print(concat_df)

    if button3:

     # Define the table creation query
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS bizcard_details (
            NAME varchar(225),
            DESIGNATION varchar(225),
            COMPANY_NAME varchar(225),
            CONTACT varchar(225),
            EMAIL text,
            WEBSITE text,
            ADDRESS text,
            PINCODE varchar(225),
            Image text
        )'''

        cursor.execute(create_table_query)
        
        concat_df= pd.concat([df,df_1],axis=1)
        for index, row in concat_df.iterrows():
            insert_query = '''
                    INSERT INTO bizcard_details (NAME,DESIGNATION,COMPANY_NAME,CONTACT,EMAIL,WEBSITE,ADDRESS,PINCODE,Image)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            '''
            values= (row['NAME'], row['DESIGNATION'], row['COMPANY_NAME'], row['CONTACT'],
                    row['EMAIL'], row['WEBSITE'], row['ADDRESS'], row['PINCODE'],row["Image"])

            try:                     
                cursor.execute(insert_query,values)
                mydb.commit()    
            except: 
                pass


  method= st.radio("Select the Option",["None","Preview","Modify"])
  if method == "None":
        st.write("")

  if method == "Preview":

    df= pd.DataFrame(text_dict)

    #Converting Image to Bytes
    Image_bytes= io.BytesIO()
    input_img.save(Image_bytes,format= "PNG")
    image_data= Image_bytes.getvalue()

    #Creating dictionary
    data= {"Image":[image_data]}
    df_1= pd.DataFrame(data)

    concat_df= pd.concat([df,df_1],axis=1)
    st.image(input_img, width = 350)
    st.dataframe(concat_df)

  elif method == "Modify":

    
    df= pd.DataFrame(text_dict)

    #Converting Image to Bytes
    Image_bytes= io.BytesIO()
    input_img.save(Image_bytes,format= "PNG")
    image_data= Image_bytes.getvalue()

    #Creating dictionary
    data= {"Image":[image_data]}
    df_1= pd.DataFrame(data)
    concat_df= pd.concat([df,df_1],axis=1)
    
    query= "select * from bizcard_details"
    cursor.execute(query)
    
    table = cursor.fetchall()

    df3= pd.DataFrame(table, columns= ["NAME","DESIGNATION","COMPANY_NAME","CONTACT",
                                      "EMAIL","WEBSITE","ADDRESS","PINCODE","IMAGE"])

    st.dataframe(df3)

    col1,col2= st.columns(2)
    with col1:
      select_name = st.selectbox("Select the Name",df3["NAME"])
    
    df4 = df3[df3["NAME"]==select_name]
    st.write("")

    col1,col2= st.columns(2)
    with col1:
        def get_first_unique_value_or_default(column, default=""):
            if column in df4 and len(df4[column].unique()) > 0:
                return df4[column].unique()[0]
            return default

        modify_name = st.text_input("Name", get_first_unique_value_or_default("NAME", "Default Name"))
        modify_desig = st.text_input("Designation", get_first_unique_value_or_default("DESIGNATION", "Default Designation"))
        modify_company = st.text_input("Company_Name", get_first_unique_value_or_default("COMPANY_NAME", "Default Company"))
        modify_contact = st.text_input("Contact", get_first_unique_value_or_default("CONTACT", "Default Contact"))


        concat_df["NAME"] = modify_name
        concat_df["DESIGNATION"] = modify_desig
        concat_df["COMPANY_NAME"] = modify_company
        concat_df["CONTACT"] = modify_contact


    with col2:
        def get_first_unique_value_or_default(column, default=""):
            if column in df4 and len(df4[column].unique()) > 0:
                return df4[column].unique()[0]
            return default


        modify_email = st.text_input("Email", get_first_unique_value_or_default("EMAIL", "example@email.com"))
        modify_web = st.text_input("Website", get_first_unique_value_or_default("WEBSITE", "https://www.example.com"))
        modify_address = st.text_input("Address", get_first_unique_value_or_default("ADDRESS", "Default Address"))
        modify_pincode = st.text_input("Pincode", get_first_unique_value_or_default("PINCODE", "000000"))


        concat_df["EMAIL"] = modify_email
        concat_df["WEBSITE"] = modify_web
        concat_df["ADDRESS"] = modify_address
        concat_df["PINCODE"] = modify_pincode


    col1,col2= st.columns(2)
    with col1:
      button3= st.button("Modify",use_container_width= True)

    if button3:
        for index, row in concat_df.iterrows():
            update_query = '''
                    UPDATE bizcard_details
                    SET DESIGNATION = %s, COMPANY_NAME = %s, CONTACT = %s, EMAIL = %s, WEBSITE = %s, ADDRESS = %s, PINCODE = %s, Image = %s
                    WHERE NAME = %s
            '''
            values = ( row['DESIGNATION'], row['COMPANY_NAME'], row['CONTACT'],
                      row['EMAIL'], row['WEBSITE'], row['ADDRESS'], row['PINCODE'], row["Image"], row["NAME"])

            try:
                cursor.execute(update_query, values)
                mydb.commit()
            except Exception as e:
                st.error(f"Failed to update data: {e}")
                # Optionally, break or continue based on the nature of the error and your application's requirements

        st.success("MODIFIED SUCCESSFULLY")

        # If you want to display the updated records, you can fetch them again as shown previously
        query = "SELECT * FROM bizcard_details"
        cursor.execute(query)
        table = cursor.fetchall()
        df6 = pd.DataFrame(table, columns=["NAME", "DESIGNATION", "COMPANY_NAME", "CONTACT", "EMAIL", "WEBSITE", "ADDRESS", "PINCODE", "IMAGE"])
        st.dataframe(df6)



if Menu == "Delete":

  col1,col2= st.columns(2)
  with col1:
    cursor.execute("SELECT NAME FROM bizcard_details")
    table1= cursor.fetchall()

    names=[]

    for i in table1:
      names.append(i[0])

    name_select= st.selectbox("Select the Name",options= names)

  with col2:
    cursor.execute(f"SELECT DESIGNATION FROM bizcard_details WHERE NAME ='{name_select}'")
    table2= cursor.fetchall()

    designations= []

    for j in table2:
      designations.append(j[0])

    designation_select= st.selectbox("Select the Designation", options= designations)

  if name_select and designation_select:
    col1,col2,col3= st.columns(3)

    with col1:
      st.write(f"Selected Name : name_select")
      st.write("")
      st.write("")

      st.write(f"Selected Designation : designation_select")

    with col2:
      st.write("")
      st.write("")
      st.write("")
      st.write("")
      remove= st.button("Delete",use_container_width= True)

      if remove:
        cursor.execute(f"DELETE FROM bizcard_details WHERE NAME ='{name_select}' AND DESIGNATION = '{designation_select}'")
        mydb.commit()
        st.warning("DELETED")
        