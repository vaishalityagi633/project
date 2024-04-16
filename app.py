from flask import Flask, flash, render_template, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
from flask import request


app = Flask(__name__)
app.secret_key = '22771d8a39fd4fca1531468593ff6006'


# PostgreSQL connection parameters
db_params = {
    'dbname': 'PROJECT',
    'user': 'postgres',
    'password': 'smart@vt2',
    'host': 'localhost', 
    'port': 5432, 
}
#@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html')
@app.route('/')
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
 
        conn =  psycopg2.connect(**db_params)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Staff WHERE Staffname = %s', (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user[2], password):
            session['username'] = user[1]
            
            
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password. Please try again.', 'error')
        
        return render_template('signin.html')
    return render_template('signin.html')




@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['uname']
        password = request.form['psw']
 
        # Hash the password before storage
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        #print(hashed_password)
 
        try:
            conn = psycopg2.connect(**db_params)
            cursor = conn.cursor()
            cursor.execute('INSERT INTO Staff(Staffname, Password) VALUES (%s,%s)', (username, hashed_password))
            conn.commit()
            conn.close()
 
            return redirect(url_for('signin'))
 
        except psycopg2.Error as e:
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
        con = psycopg2.connect(**db_params)
        cursor = con.cursor()
        cursor.execute('INSERT INTO Member(MemberName,ContactNumber,Email,Address) VALUES (%s, %s, %s,%s)', (mname,mcontact,memail,maddress))
        con.commit()
        
        return render_template('registermember.html')
    return render_template('registermember.html')
  
@app.route('/displaymember')
def displaymember():
      with psycopg2.connect(**db_params) as conn:
    
       cursor=conn.cursor()
      query=f'select * from Member'
      cursor.execute(query)
      data=cursor.fetchall()
      print(data)
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
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        
        # Check if the book exists
        cursor.execute('SELECT * FROM Book WHERE LOWER(Title) = %s', (btitle_lower,))
        book = cursor.fetchone()
        #conn.close()
        
        # If  book  exist
        if book :
            
               flash('Book already exist','error') 
        else:
           
           cursor.execute('INSERT INTO Book(Title,ISBN,Genre,PublishedDate,QuantityInStock) VALUES (%s, %s, %s,%s,%s)', (btitle,bISBN,genre,pdate,quantity))
     # Insert the book record into the database
           conn.commit()
           flash('Book registered successfully.', 'success')
        return render_template('registerbook.html')
    return render_template('registerbook.html')


@app.route('/display')
def display():
    with psycopg2.connect(**db_params) as conn:
        cursor=conn.cursor()
        query=f'select * from Book'
        cursor.execute(query)
        data=cursor.fetchall()
        print(data)
    return render_template('display.html',books=data,info="Registered")

@app.route('/searchbook',methods=['POST'])
def searchbook():
    if request.method=='POST':
        search_term=request.form['search']
        search_term=search_term.split()
        
        filt_books=[]
        with  psycopg2.connect(**db_params) as conn:
            cursor=conn.cursor()
            query=f'select * from Book '
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
        return render_template('searchbook.html',books=filt_books,info="Searched")

@app.route('/update/<id>',methods=['GET','POST'])
def update(id):
    if request.method=='POST':
        
        
        bQty=request.form['bookQuantity']
        books=(bQty,id)
        query=f'''UPDATE Book
                SET 
                    QuantityInStock=%s
                WHERE BookID=%s'''
        with  psycopg2.connect(**db_params) as conn:

            cursor=conn.cursor()
            cursor.execute(query,books)
            conn.commit()
        return redirect(url_for('display'))

    with  psycopg2.connect(**db_params)as conn:
        cursor=conn.cursor()
        query=f'select * from Book where BookID=%s'
        cursor.execute(query,(id,))
        data=cursor.fetchall()
        update_pr=data[0]
    print(update_pr)
    return render_template('update.html',books=update_pr)

@app.route('/delete/<id>')
def delete(id):
    with  psycopg2.connect(**db_params) as conn:
        cursor=conn.cursor()
        query=f'DELETE from Book where BookID=%s'
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
        conn =  psycopg2.connect(**db_params)
        cursor = conn.cursor()
        
        # Check if the book exists
        cursor.execute('SELECT * FROM Book WHERE Title=%s', (bname,))
        book = cursor.fetchone()
        print(book)
        # Check if the member exists
        cursor.execute('SELECT * FROM Member WHERE MemberName=%s', (mname,))
        member = cursor.fetchone()
        print(member)
        
        conn.close()
        
        # If both book and member exist
        if book and member:
            # Check if the book has sufficient quantity
            if book[5] > 0:  # Assuming quantity is at index 5
                # Decrement the quantity of the book by 1
                new_quantity = book[5] - 1
                
                # Update the quantity of the book in the database
                conn =  psycopg2.connect(**db_params)
                cursor = conn.cursor()
                cursor.execute('UPDATE Book SET QuantityInStock =%s WHERE Title =%s', (new_quantity, bname))
                conn.commit()
                #conn.close()
                
                # Insert the issue record into the database
                
                cursor.execute('INSERT INTO Issues(Title,MemberName,IssueDate,ReturnDate) VALUES (%s, %s, %s,%s)', (bname, mname, issuedate, returndate))
                conn.commit()
                return render_template('issues.html')
            else:
                flash('Book is out of stock.', 'error')
        else:
            flash('Book or member does not exist.', 'error')
        
        return redirect(url_for('issue'))
    return render_template('issues.html')



@app.route('/displayissue')
def displayissue():
    with psycopg2.connect(**db_params) as conn:
        cursor=conn.cursor()
        query=f'select * from Issues'
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
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Book WHERE Title= %s', (book_name))
        book = cursor.fetchone()
        if book:
            # Increment the quantity by 1
            new_quantity = book[5] + 1  # Assuming quantity is at index 5
            # Update the quantity in the database
            conn = psycopg2.connect(**db_params)
            cursor = conn.cursor()
            cursor.execute('UPDATE Book SET QuantityInStock = %s WHERE Title = %s', (new_quantity, book_name))
            

            # Delete book details from Records.Issues with particular title and member name

            cursor.execute('DELETE FROM Issues WHERE Title = %s AND MemberName= %s', (book_name,member_name))
            
            conn.commit()
            
            conn.close()
            
            flash('Book returned successfully.', 'success')
            return redirect(url_for('display'))
        else:
            flash('Book not issued.', 'error')
            #return redirect(url_for('display'))
    return render_template('return.html')

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')







        


      
   
 




           


    

                    
