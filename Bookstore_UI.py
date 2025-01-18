# -*- coding: utf-8 -*-
"""
Created on Thu Jan  9 17:36:27 2025

@author: kaymo
"""


import streamlit as st
import requests

# Bugs in this version: updates to books not happening, need to check api. error after login and user creation.
    
# Passed- all filters, adding a book, deleting a book. login, create user.
    
API_USER_URL = st.secrets["api"]["user_url"]    
API_BOOKS_URL = "https://bodhi-23sn.onrender.com/api/books"

# API helper functions

# function to fetch all books from the books endpoint
# PASSED TESTING
# function to fetch all books from the books endpoint
def fetch_books(genre=None, title=None, author=None):
    params = {}
    if genre:
        params['genre'] = genre
    if title:
        params['title'] = title
    if author:
        params['author'] = author
   

    response = requests.get(API_BOOKS_URL, params=params)
    
    if response.status_code == 200:
        return response.json()  
    else:
        st.error("Failed to fetch books. Please try again.")
        return []


# tested and works
def add_book(title, author, genre, quantity, price, language, isbn):
    new_book = {
        "title": title,
        "author": author,
        "genre": genre,
        "quantity": quantity,
        "price": price,
        "language": language,
        "isbn": isbn

    }

    # Send the data to the API
    response = requests.post(API_BOOKS_URL, json=new_book)
    # Debugging: Inspect the request payload and response
    # st.write("Add Book Payload:", new_book)
    # st.write("API Response Status Code:", response.status_code)
    # st.write("API Response Body:", response.json())
    
    # Handle the response
    if response.status_code == 201:
        st.success("Book added successfully!")
    else:
        st.error(f"Failed to add book: {response.text}")
        
# Function to update an existing book 
# FIXME test update
def update_book(book_id, title, author, genre, quantity, price):
    updated_book = {
        "title": title,
        "author": author,
        "genre": genre,
        "quantity": quantity,
        "price": price,
    }
    
    # Debug log
    st.write("Payload sent to API:", updated_book)
    
    response = requests.put(f"{API_BOOKS_URL}/{book_id}", json=updated_book)
    if response.status_code == 200:
        st.success(f"Book '{title}' updated successfully.")
    else:
        st.error(f"Failed to update the book. Error: {response.text}")
        st.write("Debug Response:", response.json())

# Function to delete a book
# FIXME test update
def delete_book(book_id):
    response = requests.delete(f"{API_BOOKS_URL}/{book_id}")
    if response.status_code == 200:
        st.success("Book deleted successfully.")
    else:
        st.error(f"Failed to delete the book: {response.text}")

# API functions for manufacturer orders
# 
API_MFRORDER_URL = "https://bodhi-23sn.onrender.com/api/manufacturerOrders"

# Function to fetch orders
def fetch_orders(supplier_name=None, status=None):
    params = {}
    if supplier_name:
         params['supplierName'] = supplier_name
    if status:
         params['status'] = status
        
    response = requests.get(API_MFRORDER_URL, params=params)
    if response.status_code == 200:
        return response.json()  # Returns list of orders as JSON
    else:
        st.error("Failed to fetch orders. Please try again.")
        return []

# Function for creating orders (future POST endpoint)
# FIXME uncomment once POST is available
# def create_order(order_number, supplier_name, book_orders, status, total_cost, order_date, expected_delivery_date):
#     new_order = {
#         "orderNumber": order_number,
#         "supplierName": supplier_name,
#         "bookOrders": book_orders,
#         "status": status,
#         "totalCost": total_cost,
#         "orderDate": order_date,
#         "expectedDeliveryDate": expected_delivery_date,
#     }
    
    #FIXME uncomment when POST is available
    # response = requests.post(API_MFRORDER_URL, json=new_order)
    # if response.status_code == 201:
    #     st.success(f"Order '{order_number}' created successfully.")
    # else:
    #     st.error("Failed to create the order. Please try again.")
 
    
# API Fuctions for user authentication

# API_USER_URL = "https://bodhi-23sn.onrender.com/api/users"

# Function for adding a new user
def add_user_api(username, password, first_name, last_name, role):
    new_user = {
        "username": username,
        "password": password,
        "firstName": first_name,
        "lastName": last_name,
        "role": role
    }
    response = requests.post(f"{API_USER_URL}", json=new_user)
    # FIXME enable for testing
    #st.write(response.json()) # print response to see exact error
    if response.status_code == 201:
        return "User created successfully."
    elif response.status_code == 400:
        return "Invalid input or username already exists."
    else:
        return "Failed to create account. Please try again."

# Function to validate login
def validate_login_api(username, password):
    credentials = {
        "username": username,
        "password": password
    }
    response = requests.post(f"{API_USER_URL}/login", json=credentials)
    if response.status_code == 200:
        data = response.json()
        if data.get("message") == "Login successful":
            user_info = data.get("user", {})
            st.session_state.role = user_info.get("role")
            st.session_state.username = user_info.get("username")
            return True #login successful
        elif response.status_code == 401:
            st.error("Invalid username or password.")
        elif response.status_code == 400:
            st.error("Missing username or password.")
        else:
            st.error("failed to log in. Please try again.")
        return False # Login failed
            
    

# Streamlit UI components
# Set page configuration (must be the first Streamlit command)
st.set_page_config(page_title="Bodhi Books Management System", layout="wide")


# Sidebar Navigation
st.sidebar.header("Navigation")
page = st.sidebar.radio(
    "Go to",
    options=["Home", "Inventory Management", "Sales Records", "Orders"],
    format_func=lambda x: f"🏠 {x}" if x == "Home" else (
        "📦 Inventory" if x == "Inventory Management" else
        "📊 Sales" if x == "Sales Records" else
        "🛒 Orders"
    )
)

#Login State Management
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'name' not in st.session_state:
    st.session_state.name = ""

if 'role' not in st.session_state:
    st.session_state.role = ""

# Logout Functionality
if st.session_state.logged_in:
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.name = ""
        st.session_state.role = ""
        st.session_state['refresh'] = not st.session_state.get('refresh', False)



# Home Page (Always Accessible)
if page == "Home":
    st.title("📚 Bodhi Books Management System")
    st.subheader("Preserving Literary Treasures, One Page at a Time")
    st.write("""
    Welcome to the **Bodhi Books Management System** — your gateway to efficiently managing our exclusive collection of rare and antique books.

    This app is designed to empower our employees with the tools they need to:
    - **Manage inventory** of rare books
    - **Create purchase orders** for restocking
    - **View sales records** and generate reports

    Use the sidebar to navigate through the different sections of the app.
    """)
    
# Login Section
if not st.session_state.logged_in:
    st.divider()
    st.subheader("🔐 Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login"):
        # call the validate login function
        role = validate_login_api(username, password)
        if role:
            # update the session state for successful login
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = role
            # display a welcome message
            st.success(f"Welcome, {username}!")
            # Reset the login fields
            st.session_state.login_username = ""
            st.session_state.login_password = ""
        else:
            st.error("Invalid username or password. Please try again.")

         
            
# Create account toogles
# Initialize session state for the expander
if "show_create_account" not in st.session_state:
    st.session_state.show_create_account = False  # Expander starts collapsed

# Toggle function for the expander
def toggle_expander():
    st.session_state.show_create_account = not st.session_state.show_create_account

# Main "Create a New Account" toggle button
if not st.session_state.show_create_account:
    st.button("Create a New Account", on_click=toggle_expander)
    
# Initialize session state for role
if 'role' not in st.session_state or st.session_state.role not in ["staff", "manager"]:
    st.session_state.role = "staff"  # Default to 'staff'


# Only show the expander if "show_create_account" is True
if st.session_state.show_create_account:
    with st.expander("Create a New Account", expanded=True):
        # Input fields for creating a new account
        new_username = st.text_input("New Username", key="new_username")
        new_password = st.text_input("New Password", type="password", key="new_password")
        first_name = st.text_input("First Name", key="first_name")
        last_name = st.text_input("Last Name", key="last_name")
        role = st.selectbox("Role", ["staff", "manager"], key="role")

        if st.button("Create Account"):
            if new_username and new_password and first_name and last_name:
                response = add_user_api(new_username, new_password, first_name, last_name, role)
                st.info(response)

                # Reset form fields and collapse after success
                st.session_state.new_username = ""
                st.session_state.new_password = ""
                st.session_state.first_name = ""
                st.session_state.last_name = ""
                st.session_state.role = "staff"  # Reset to default
                st.session_state.show_create_account = False
            else:
                st.warning("All fields are required to create an account.")



        
# Protected Pages
# if st.session_state.logged_in:
    
    # Inventory Management Page
    if page == "Inventory Management":
        st.title("📦 Inventory Management")
        st.subheader("Manage Your Rare Book Collection")
        st.write("""
        Welcome to the **Inventory Management** section. Here you can:
        - View and search our current inventory of rare books.
        - Add new books to the collection.
        - Update book information, including stock levels and prices.
        - Remove books that are no longer available.
        """)
        
        # Add New Book Button and Form 
        # Tested and works
        with st.expander("➕ Add New Book"):
            with st.form("add_book_form", clear_on_submit=True):
                new_title = st.text_input("Book Title")
                new_author = st.text_input("Author")
                new_genre = st.selectbox("Genre", ["Fiction", "Non-Fiction", "Science", "Biography"])
                new_quantity = st.number_input("Quantity", min_value=1, value=1)
                new_price = st.number_input("Price", min_value=0.0, value=1.0)
                new_language = st.text_input("Language")
                new_isbn = st.text_input("ISBN")
                add_submitted = st.form_submit_button("Add Book")
                if add_submitted:
                    add_book(new_title, new_author, new_genre, new_quantity, new_price, new_language, new_isbn)
              
        # Filters for the search
        # PASSED testing
        st.subheader("Filter Inventory")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filter_by_genre = st.checkbox("Filter by Genre")
            selected_genre = st.text_input("Genre") if filter_by_genre else None
            

        with col2:
           filter_by_author = st.checkbox("Filter by Author")
           selected_author = st.text_input("Author") if filter_by_author else None

        with col3:
            filter_by_title = st.checkbox("Filter by Title")
            selected_title = st.text_input("Title") if filter_by_title else None


        # UpdateD fetch_books function based on selected filters
        filters = {
            "genre": selected_genre if filter_by_genre else None,
            "author": selected_author if filter_by_author else None,
            "title": selected_title if filter_by_title else None,
            
          
        }
                
        # Fetch and display the books using the API
        books = fetch_books(**{k: v for k, v in filters.items() if v is not None})

        # FIXME: Test Update to add headers using markdown
        st.subheader("Inventory List")
        
        if books:
           # Display table headers with HTML styling
           st.markdown("""
           <style>
           table {
               border-collapse: collapse;
               width: 100%;
           }
                          
           th, td {
               border: 1px solid #ddd;
               padding: 8px;
           }
           th {
               background-color: #f2f2f2;
               text-align: left;
           }
           </style>
           """, unsafe_allow_html=True)
    
           # Display header row using Streamlit columns for interaction
           col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 2, 1, 1, 2])
           col1.write("Title")
           col2.write("Author")
           col3.write("Genre")
           col4.write("Stock")
           col5.write("Price")
           col6.write("Actions")
    
           # Loop through books and create rows dynamically
           for book in books:
               col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 2, 1, 1, 2])
               col1.write(book.get('title', 'N/A'))
               col2.write(book.get('author', 'N/A'))
               col3.write(book.get('genre', 'N/A'))
               
               quantity = book.get('quantity', 0)
               # Highlight stock if it's low
               if quantity < 20:
                   col4.markdown(f"<span style='color: red;'>{quantity}</span>", unsafe_allow_html=True)
               else:
                   col4.write(quantity)
        
               col5.write(f"${book.get('price', 0.0):.2f}")
        
               # Add buttons for update and delete
               update_button = col6.button("Update", key=f"update_{book['_id']}")
               delete_button = col6.button("Delete", key=f"delete_{book['_id']}")

               # Update book logic
               if update_button:
                   with st.form(f"update_form_{book['_id']}", clear_on_submit=True):
                       new_title = st.text_input("Book Title", value=book['title'])
                       new_author = st.text_input("Author", value=book['author'])
                       new_genre = st.text_input("Genre", value=book['genre'])
                       new_quantity = st.number_input("Quantity", min_value=0, value=book['quantity'])
                       new_price = st.number_input("Price", min_value=0.0, value=book['price'])
                       update_submitted = st.form_submit_button("Submit Update")
                       if update_submitted:
                           
                           try:
                               update_book(
                                   book['_id'],
                                   new_title,
                                   new_author,
                                   new_genre,
                                   int(new_quantity),
                                   float(new_price)
                               )
                               st.experimental_rerun()
                           except Exception as e:
                               st.error(f"An error occurred: {e}")
        
               # Delete book logic
               if delete_button:
                   delete_book(book['_id'])
                   st.session_state['refresh'] = not st.session_state.get('refresh', False)  # Trigger a page refresh
              
                 
        
    # Sales Records Page
    elif page == "Sales Records":
        st.title("📊 Sales Records")
        st.subheader("View and Analyze Sales Data")
        st.write("""
        Welcome to the **Sales Records** section. Here you can:
        - View detailed sales records of rare books.
        - Generate sales reports.
        - Analyze trends and performance over time.
        """)
   
    # Orders Page
    elif page == "Orders":
        st.title("🛒 Orders")
        st.subheader("Manage Purchase Orders")
        st.write("""
        Welcome to the **Orders** section. Here you can:
        - View and manage existing purchase orders.
        - Create new orders for books running low on stock.
        - Ensure a steady supply of rare books for our customers.
        """)

        # Section: Create Purchase Order Form
        # order submission goes nowhere until we have an API endpoint for saving orders
        st.subheader("Create Purchase Order")
        with st.form("purchase_order_form"):
            book_title = st.selectbox("Select Book", [book['title'] for book in fetch_books()])
            quantity_to_order = st.number_input("Quantity to Order", min_value=1, value=1)
            submitted = st.form_submit_button("Save Purchase Order")
            if submitted:
                st.info(f"Order functionality is not yet connected to the backend. Order for {quantity_to_order} units of '{book_title}' was simulated.")
                # FIXME uncomment when endpoint is ready
                #selected_book = next(book for book in fetch_books() if book['title'] == book_title)
                #submit_order(selected_book['_id'], quantity_to_order)

        # Section: View Existing Purchase Orders
        st.subheader("Existing Purchase Orders")
        st.write("Table of existing purchase orders will be displayed here.")
