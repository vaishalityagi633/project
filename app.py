import os
from flask import Flask, render_template, request, url_for, redirect,session
from flask import flash
from werkzeug.security import generate_password_hash, check_password_hash
import pyodbc
database='PROJECT'

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY','fcd6741a4ad8ad430ff636bfd04ae5bed4286b6eeaefdf3edf06d02695782441')



#conn= pyodbc.connect('DRIVER={SQL Server};SERVER=BLT210003;DATABASE=PROJECT')
#cursor=conn.cursor()
#cursor.execute("Select * from Records.Book")
#for row in cursor.fetchall():
    #print(row)
def insert_data(database,data):
             with pyodbc.connect('DRIVER={SQL Server};SERVER=BLT210003;DATABASE=PROJECT;Trusted_Connection=yes') as conn:
                cursor=conn.cursor()
                query=f'''INSERT INTO Record.Book (Title,ISBN,Genre,PublishedDate,QuantityInStock) VALUES (?,?,?,?,?)'''
                cursor.execute(query,data)
                conn.commit()
def insert_datamember(database,data):
             with pyodbc.connect('DRIVER={SQL Server};SERVER=BLT210003;DATABASE=PROJECT;Trusted_Connection=yes') as conn:
                cursor=conn.cursor()
                query=f'''INSERT INTO Record.Member (MemberName,ContactNumber,Email,Address) VALUES (?,?,?,?)'''
                cursor.execute(query,data)
                conn.commit()    

def insert_dataissue(database,data):
             with pyodbc.connect('DRIVER={SQL Server};SERVER=BLT210003,1433;DATABASE=PROJECT;Trusted_Connection=yes') as conn:
             
                cursor=conn.cursor()
                query=f'''INSERT INTO Record.Issues(Title,MemberName,IssueDate,ReturnDate) VALUES (?,?,?,?)'''
                cursor.execute(query,data)
                conn.commit()                                                



@app.route('/')
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
 
        conn =  pyodbc.connect('DRIVER={SQL Server};SERVER=host.docker.internal;DATABASE=PROJECT;Trusted_Connection=yes')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Record.Staff WHERE Staffname = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user[2], password):
            session['username'] = user[1]
            
            
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password. Please try again.', 'error')
        
        return render_template('signin.html')
    return render_template('signin.html')
#@app.route('/')
@app.route('/home')
def home():
   return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['uname']
        password = request.form['psw']
 
        # Hash the password before storage
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        #print(hashed_password)
 
        try:
            conn = pyodbc.connect('DRIVER={SQL Server};SERVER=host.docker.internal;DATABASE=PROJECT;Trusted_Connection=yes')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO Record.Staff (Staffname, Password) VALUES (?,?)', (username, hashed_password))
            conn.commit()
            conn.close()
 
            return redirect(url_for('signin'))
 
        except pyodbc.Error as e:
            return f"An error occurred during signup. Error details: {e}"
 
    return render_template('signup.html')

@app.route('/registermember',methods=['GET','POST'])
def registermember():
    
    if request.method=='POST':
        
        #mid=request.form['memberid']
        mname=request.form['name']
        mcontact=request.form['contact']
        memail=request.form['emailid']
        maddress=request.form['address']
       # mname_lower=mname.lower()
        data=(mname,mcontact,memail,maddress)
        

        insert_datamember(database,data)
        return render_template('registermember.html')
    return render_template('registermember.html')
  
@app.route('/displaymember')
def displaymember():
    with pyodbc.connect('DRIVER={SQL Server};SERVER=host.docker.internal;DATABASE=PROJECT;Trusted_Connection=yes') as conn:
        cursor=conn.cursor()
        query=f'select * from Record.Member'
        cursor.execute(query)
        data=cursor.fetchall()
    return render_template('displaymember.html',members=data,info="Registered")


@app.route('/register',methods=['GET','POST'])
def register():
    

    if request.method=='POST':
        
       # bid=request.form['bookid']
        btitle=request.form['title']
        bISBN=request.form['ISBN']
        #aid=request.form['authorid']
        genre=request.form['genre']
        pdate=request.form['publisheddate']
        quantity=request.form['quantity']
         # Convert book title to lowercase for case-insensitive check
        btitle_lower = btitle.lower()
        data=(btitle_lower,bISBN,genre,pdate,quantity)
        # Check if both the book and member exist
        conn = pyodbc.connect('DRIVER={SQL Server};SERVER=host.docker.internal;DATABASE=PROJECT;Trusted_Connection=yes')
        cursor = conn.cursor()
        
        # Check if the book exists
        cursor.execute('SELECT * FROM Record.Book WHERE LOWER(Title) = ?', (btitle_lower,))
        book = cursor.fetchone()
       
        
        conn.close()
        
        # If  book  exist
        if book :
            
               flash('Book already exist','error') 
        else:
                # Insert the book record into the database
          insert_data(database,data)
          flash('Book registered successfully.', 'success')
        return render_template('registerbook.html')
    return render_template('registerbook.html')


@app.route('/display')
def display():
    with pyodbc.connect('DRIVER={SQL Server};SERVER=BLT210003;DATABASE=PROJECT;Trusted_Connection=yes') as conn:
        cursor=conn.cursor()
        query=f'select * from Record.Book'
        cursor.execute(query)
        data=cursor.fetchall()
    return render_template('display.html',books=data,info="Registered")

@app.route('/searchbook',methods=['POST'])
def searchbook():
    if request.method=='POST':
        search_term=request.form['search']
        search_term=search_term.split()
        
        filt_books=[]
        with pyodbc.connect('DRIVER={SQL Server};SERVER=BLT210003;DATABASE=PROJECT;Trusted_Connection=yes') as conn:
            cursor=conn.cursor()
            query=f'select * from Record.book '
            cursor.execute(query)
            rows=cursor.fetchall()
        for term in search_term:
            for row in rows:
                # Debugging: Print the row to inspect its contents
                #print(row)
                for row_items in row:
                 if isinstance(row_items,str):
                        if term.lower() in row_items.lower():
                            filt_books.append(row)
                            break
                        #print(filt_books)
         #filt_books=list(set(filt_books))
                
                
        
        return render_template('searchbook.html',books=filt_books,info="Searched")

@app.route('/update/<id>',methods=['GET','POST'])
def update(id):
    if request.method=='POST':
        
        
        bQty=request.form['bookQuantity']
        books=(bQty,id)
        query=f'''UPDATE Record.Book
                SET 
                    QuantityInStock=?
                WHERE BookID=?'''
        with pyodbc.connect('DRIVER={SQL Server};SERVER=BLT210003;DATABASE=PROJECT;Trusted_Connection=yes') as conn:

            cursor=conn.cursor()
            cursor.execute(query,books)
            conn.commit()
        return redirect(url_for('display'))

    with pyodbc.connect('DRIVER={SQL Server};SERVER=BLT210003;DATABASE=PROJECT;Trusted_Connection=yes') as conn:
        cursor=conn.cursor()
        query=f'select * from Record.Book where BookID=?'
        cursor.execute(query,(id,))
        data=cursor.fetchall()
        update_pr=data[0]
    print(update_pr)
    return render_template('update.html',books=update_pr)
@app.route('/delete/<id>')
def delete(id):
    with pyodbc.connect('DRIVER={SQL Server};SERVER=BLT210003;DATABASE=PROJECT;Trusted_Connection=yes') as conn:
        cursor=conn.cursor()
        query=f'DELETE from Record.Book where BookID=?'
        cursor.execute(query,(id,))
        conn.commit()
    return redirect(url_for('display'))
@app.route('/issue', methods=['GET','POST'])
def issue():
    if request.method == 'POST':
        # Get data 
        
        bname = request.form['bname']
        mname = request.form['mname']
        issuedate = request.form['issuedate']
        returndate = request.form['returndate']
        
        # Check if both the book and member exist
        conn = pyodbc.connect('DRIVER={SQL Server};SERVER=BLT210003;DATABASE=PROJECT;Trusted_Connection=yes')
        cursor = conn.cursor()
        
        # Check if the book exists
        cursor.execute('SELECT * FROM Record.Book WHERE Title = ?', (bname,))
        book = cursor.fetchone()
        
        # Check if the member exists
        cursor.execute('SELECT * FROM Record.Member WHERE MemberName = ?', (mname,))
        member = cursor.fetchone()
        
        conn.close()
        
        # If both book and member exist
        if book and member:
            # Check if the book has sufficient quantity
            if book[5] > 0:  # Assuming quantity is at index 5
                # Decrement the quantity of the book by 1
                new_quantity = book[5] - 1
                
                # Update the quantity of the book in the database
                conn = pyodbc.connect('DRIVER={SQL Server};SERVER=BLT210003;DATABASE=PROJECT;Trusted_Connection=yes')
                cursor = conn.cursor()
                cursor.execute('UPDATE Record.Book SET QuantityInStock = ? WHERE Title = ?', (new_quantity, bname))
                conn.commit()
                conn.close()
                
                # Insert the issue record into the database
                data = (bname, mname, issuedate, returndate)
                insert_dataissue(database, data)
                
                return render_template('issues.html')
            else:
                flash('Book is out of stock.', 'error')
        else:
            flash('Book or member does not exist.', 'error')
        
        return redirect(url_for('issue'))
    return render_template('issues.html')



@app.route('/displayissue')
def displayissue():
    with pyodbc.connect('DRIVER={SQL Server};SERVER=BLT210003;DATABASE=PROJECT;Trusted_Connection=yes') as conn:
        cursor=conn.cursor()
        query=f'select * from Record.Issues'
        cursor.execute(query)
        data=cursor.fetchall()
    return render_template('displayissue.html',issues=data,info="Registered")

@app.route('/returnbook', methods=['POST','GET'])
def returnbook():
    if request.method == 'POST':
        book_name = request.form['bookname']  # Assuming you pass the book ID from the frontend
        #Also take member_name from the frontend
        member_name=request.form['membername']
        # Retrieve book details from the database
        conn = pyodbc.connect('DRIVER={SQL Server};SERVER=BLT210003;DATABASE=PROJECT;Trusted_Connection=yes')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Record.Book WHERE Title= ? ', (book_name))
        book = cursor.fetchone()
       
        
        if book:
            # Increment the quantity by 1
            new_quantity = book[5] + 1  # Assuming quantity is at index 5
            # Update the quantity in the database
            conn = pyodbc.connect('DRIVER={SQL Server};SERVER=BLT210003;DATABASE=PROJECT;Trusted_Connection=yes')
            cursor = conn.cursor()
            cursor.execute('UPDATE Record.Book SET QuantityInStock = ? WHERE Title = ?', (new_quantity, book_name))

            # Delete book details from Records.Issues with particular title and member name

            cursor.execute('DELETE FROM Record.Issues WHERE Title = ? AND MemberName=?', (book_name,member_name))
            #cursor.execute('DELETE FROM Record.Issues WHERE Title = ? AND MemberName', (book_name,m_name))
            conn.commit()
            
            conn.close()
            
            flash('Book returned successfully.', 'success')
            return redirect(url_for('display'))
        else:
            flash('Book not issued.', 'error')
            #return redirect(url_for('display'))
    return render_template('return.html')


    
if __name__=='__main__':  
    app.run(debug=False,host='0.0.0.0')



    

                    
