# -*- coding: utf-8 -*-
"""
Created on Thu Jan  9 17:36:27 2025

@author: kaymo
"""

import requests
import streamlit as st


# For streamlit cloud deployment uncomment this sesction, comment out local section
API_BASE_URL = st.secrets["api"]["base_url"]
if not API_BASE_URL:
    raise ValueError("API_BASE_URL is not set in Streamlit secrets.")

API_BOOKS_URL = API_BOOKS_URL = f"{API_BASE_URL}/books"
API_USER_URL = f"{API_BASE_URL}/users"
API_MFRORDER_URL = f"{API_BASE_URL}/manufacturerOrders"


# Define all functions

# datetime formatters
def formatDate(datetime):
    date = datetime.split("T")
    formatDate = date[0].split("-")
    
    day = formatDate[2]
    month = formatDate[1]
    year = formatDate[0]
    
    if month[0] == "0":
        month = month[1]
    if day[0] == "0":
        day = day[1]
        
    return (f"{month}/{day}/{year}")

def formatTime(datetime):
    time = datetime.split("T")
    formatTime = time[1].split(":")
    
    hour = formatTime[2]
    minute = formatTime[1]
    
    if hour[0] == "0":
        hour = hour[1]
        
    return (f"{hour}:{minute}")

def formatDatetime(datetime):
    date = formatDate(datetime)
    time = formatTime(datetime)
        
    return (f"{date} {time}")

# function to fetch all books- Passed testing

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


# Function to add a book- Passed testing
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
    
    # Handle the response
    if response.status_code == 201:
        st.success("Book added successfully!")
    else:
        st.error(f"Failed to add book: {response.text}")
        
# Function to update an existing book 
def update_book(book_id, title, author, genre, quantity, price, language=None, isbn=None):
    updated_book = {
        "title": title,
        "author": author,
        "genre": genre,
        "quantity": quantity,
        "price": price,
    }
    # Optionally include additional fields if provided
    if language:
        updated_book["language"] = language
    if isbn:
        updated_book["isbn"] = isbn
        
    response = requests.put(f"{API_BOOKS_URL}/{book_id}", json=updated_book)
    if response.status_code == 200:
        st.success(f"Book '{title}' updated successfully!")
        return True
    else:
        st.error(f"Failed to update book: {response.text}")
        return False
 
    
# Function to delete a book
def delete_book(book_id):
    response = requests.delete(f"{API_BOOKS_URL}/{book_id}")
    if response.status_code == 200:
        st.success("Book deleted successfully.")
    else:
        st.error(f"Failed to delete the book: {response.text}")


#Function for creating orders 
#FIXME requires testing
def create_order(order_number, supplier_name, books_ordered, status, total_cost, order_date, expected_delivery_date):
    new_order = {
        "orderNumber": order_number,
        "supplierName": supplier_name,
        "booksOrdered": books_ordered,
        "status": status,
        "totalCost": total_cost,
        "orderDate": order_date,
        "expectedDeliveryDate": expected_delivery_date,
    }
    
    
    response = requests.post(API_MFRORDER_URL, json=new_order)
    
    # Handle the response
    if response.status_code == 201:
        st.success(f"Order '{order_number}' created successfully.")
        return response.json() # Return the created order for further use
    elif response.status_code == 400:
        st.error(" Invalid input or order already exists")
        return None
    else:
        st.error("Failed to create the order. Please try again.")
        return None
  
 
# Function to fetch manufacturer orders
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

# Updated Function to Cancel an Order
def cancel_order(order_id):
    try:
        # Use the correct endpoint as per Swagger
        response = requests.put(f"{API_BASE_URL}/manufacturerOrders/cancel/{order_id}")
        
        if response.status_code == 200:
            st.success("Order canceled successfully!")
            return True
        else:
            st.error(f"Failed to cancel order: {response.json()}")
            return False
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")
        return False
    
# API Fuctions for user authentication

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

# Function to handle login
def handle_login():
    role = validate_login_api(st.session_state.temp_username, st.session_state.temp_password)
    if role:
        # update the session state for successful login
        st.session_state.logged_in = True
        st.session_state.username = st.session_state.temp_username
        st.session_state.role = role
        # Set a flag to clear fields on rerun
        st.session_state.clear_fields = True
        st.rerun()
    else:
        st.error("Invalid username or password. Please try again.")
        

# Initialize session state variables
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "temp_username" not in st.session_state:
    st.session_state.temp_username = ""
if "temp_password" not in st.session_state:
    st.session_state.temp_password = ""
if "clear_fields" not in st.session_state:
    st.session_state.clear_fields = False
 
# Login Section
if not st.session_state.logged_in:
    st.divider()
    st.subheader("🔐 Login")
    # Clear fields if the flag is set
    if st.session_state.clear_fields:
        st.session_state.temp_username = ""
        st.session_state.temp_password = ""
        st.session_state.clear_fields = False  # Reset the flag
    # Temporary variables for login inputs
    username = st.text_input("Username", key="temp_username")
    password = st.text_input("Password", type="password", key="temp_password")
    if st.button("Login"):
        handle_login()
else:
    st.success(f"Welcome, {st.session_state.username}!")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
         
            
# Create account section

# Initialize session state for the expander
if not st.session_state.logged_in and page == "Home":
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
        
    # Add a flag to reset fields after success
    if "reset_create_account_fields" not in st.session_state:
        st.session_state.reset_create_account_fields = False
    
    
    # Only show the expander if "show_create_account" is True
    if st.session_state.show_create_account:
        with st.expander("Create a New Account", expanded=True):
            # Reset fields if the flag is set
            if st.session_state.reset_create_account_fields:
                st.session_state.new_username = ""
                st.session_state.new_password = ""
                st.session_state.first_name = ""
                st.session_state.last_name = ""
                st.session_state.role = "staff"
                st.session_state.reset_create_account_fields = False
                
            # Input fields for creating new account
            new_username = st.text_input("New Username", key="new_username")
            new_password = st.text_input("New Password", type="password", key="new_password")
            first_name = st.text_input("First Name", key="first_name")
            last_name = st.text_input("Last Name", key="last_name")
            role = st.selectbox("Role", ["staff", "manager"], key="role")
    
            if st.button("Create Account"):
                if new_username and new_password and first_name and last_name:
                    response = add_user_api(new_username, new_password, first_name, last_name, role)
                    st.info(response)
                    
                    # set the reset flag to clear fields
                    st.session_state.reset_create_account_fields = True
                    st.session_state.show_create_account = False
                    st.rerun()
          
                else:
                    st.warning("All fields are required to create an account.")
    

        
# Protected Pages
if st.session_state.logged_in and page == "Inventory Management":
   # Inventory Management Page
   st.title("📦 Inventory Management")
   st.subheader("Manage Your Rare Book Collection")
   st.write("""
   Welcome to the **Inventory Management** section. Here you can:
   - View and search our current inventory of rare books.
   - Add new books to the collection.
   - Update book information, including stock levels and prices.
   - Remove books that are no longer available.
   """)
   
   # Reset flags for refreshing inventory and clearing selected book
   if "refresh_inventory" not in st.session_state:
       st.session_state.refresh_inventory = False
   if "selected_book" not in st.session_state:
       st.session_state.selected_book = None
    
            
    # Add New Book Button and Form
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
   st.subheader("Filter Inventory")
   col1, col2, col3 = st.columns(3)
    
   with col1:
       filter_by_genre = st.checkbox("Filter by Genre", key="filter_by_genre")
       selected_genre = st.text_input("Genre", key="selected_genre") if filter_by_genre else None
    
   with col2:
       filter_by_author = st.checkbox("Filter by Author", key="filter_by_author")
       selected_author = st.text_input("Author", key="selected_author") if filter_by_author else None
    
   with col3:
       filter_by_title = st.checkbox("Filter by Title", key="filter_by_title")
       selected_title = st.text_input("Title", key="selected_title") if filter_by_title else None
    
   # Update fetch_books function based on selected filters
   filters = {
       "genre": selected_genre if filter_by_genre else None,
       "author": selected_author if filter_by_author else None,
       "title": selected_title if filter_by_title else None,
   }

   # Fetch and display the books using the API
   books = fetch_books(**{k: v for k, v in filters.items() if v})
   
   # Ensure only one block renders the inventory list
   if "refresh_inventory" not in st.session_state:
       st.session_state.refresh_inventory = False
       
   # Refresh inventory list after deletion
   if st.session_state.refresh_inventory:
       books = fetch_books()
       st.session_state.refresh_inventory = False
        
   # Display books in a table format
   st.subheader("Inventory List")
   if books:
       # Display table headers with Streamlit columns
       header_cols = st.columns([2, 2, 2, 1, 1, 2])
       header_cols[0].write("Title")
       header_cols[1].write("Author")
       header_cols[2].write("Genre")
       header_cols[3].write("Stock")
       header_cols[4].write("Price")
       header_cols[5].write("Actions")
       
       # Display inventory rows
       for book in books:
           cols = st.columns([2, 2, 2, 1, 1, 2])
           cols[0].write(book["title"])
           cols[1].write(book["author"])
           cols[2].write(book["genre"])
           
    
           quantity = book.get("quantity", 0)
           # Highlight stock if it's low
           if quantity < 20:
               cols[3].markdown(f"<span style='color: red;'>{quantity}</span>", unsafe_allow_html=True)
           else:
               cols[3].write(quantity)
    
           cols[4].write(f"${book['price']:.2f}")
    
           # Add "Edit" and "Delete" buttons
           if cols[5].button("Edit", key=f"edit_{book['_id']}"):
               st.session_state.selected_book = book
    
           if cols[5].button("Delete", key=f"delete_{book['_id']}"):
               delete_book(book["_id"])
               st.success(f"Book '{book['title']}' deleted successfully.")
               st.session_state.refresh_inventory = True
               st.rerun()
        

        
   # Display the edit form in the sidebar if a book is selected
   if st.session_state.selected_book:
       book = st.session_state.selected_book
       with st.sidebar:
           st.subheader("Edit Book")
           with st.form("update_book_form", clear_on_submit=True):
               new_title = st.text_input("Book Title", value=book["title"])
               new_author = st.text_input("Author", value=book["author"])
               new_genre = st.text_input("Genre", value=book["genre"])
               new_quantity = st.number_input("Quantity", min_value=0, value=book["quantity"])
               new_price = st.number_input("Price", min_value=0.0, value=book["price"])
               new_language = st.text_input("Language", value=book.get("language", ""))
               new_isbn = st.text_input("ISBN", value=book.get("isbn", ""))
        
               update_submitted = st.form_submit_button("Update Book")
               if update_submitted:
                   success = update_book(
                       book["_id"],
                       new_title,
                       new_author,
                       new_genre,
                       int(new_quantity),
                       float(new_price),
                       new_language,
                       new_isbn,
                   )
                   if success:
                       st.success(f"Book '{new_title}' updated successfully!")
                       # Clear the selected book and refresh the books
                       st.session_state.selected_book = None
                       st.session_state.refresh_inventory = True
                       st.rerun()
        
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

    # Generate Sales Report
    st.subheader("Generate Sales Report")
    with st.form("sales_report_form"):
         start_date = st.date_input("Start Date")
         end_date = st.date_input("End Date")
         report_type = st.selectbox("Report Type", ["Summary", "Detailed"])
         submitted = st.form_submit_button("Generate Report")

         if submitted:
             try:
                 report_params = {
                     "start_date": str(start_date),
                     "end_date": str(end_date),
                     "type": report_type,
                 }
                 report_response = requests.get(f"{API_BASE_URL}/sales/report", params=report_params)
                 if report_response.status_code == 200:
                     report_data = report_response.json()
                     st.write("### Sales Report")
                     st.dataframe(report_data)
                 else:
                     st.error(f"Failed to generate report: {report_response.text}")
             except requests.exceptions.RequestException as e:
                 st.error(f"Error generating sales report: {e}")

    # Fetch and Display Sales Records
    st.subheader("Sales Records")
    try:
        response = requests.get(f"{API_BASE_URL}/sales")  # Replace with the correct endpoint
        if response.status_code == 200:
            sales_data = response.json()
            st.dataframe(sales_data)  # Display sales records in a tabular format
        else:
            st.write("No sales records found or failed to fetch data.")
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching sales data: {e}")

    
    # Sales Trends Analysis
    st.subheader("Sales Trends and Analysis")
    trend_options = ["Sales Over Time", "Top Selling Books", "Revenue by Genre"]
    selected_trend = st.selectbox("Select Trend to Analyze", trend_options)

    try:
        if selected_trend == "Sales Over Time":
            trend_data = requests.get(f"{API_BASE_URL}/sales/trends/time").json()
            if trend_data:
                st.line_chart(trend_data)
            else:
                st.write("No data available for this trend.")

        elif selected_trend == "Top Selling Books":
            top_books_data = requests.get(f"{API_BASE_URL}/sales/trends/top-books").json()
            if top_books_data:
                st.bar_chart(top_books_data)
            else:
                st.write("No data available for this trend.")

        elif selected_trend == "Revenue by Genre":
            revenue_data = requests.get(f"{API_BASE_URL}/sales/trends/revenue-by-genre").json()
            if revenue_data:
                st.bar_chart(revenue_data)
            else:
                st.write("No data available for this trend.")
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching trend data: {e}")




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
    # Needs testing
    st.subheader("Create Purchase Order")
    with st.form("purchase_order_form", clear_on_submit=True):
        # Select book titles from the inventory
        books = fetch_books()
        book_titles = [book['title'] for book in books]
        book_title = st.selectbox("Select Book", book_titles if books else [])

        # Input other fields
        quantity_to_order = st.number_input("Quantity to Order", min_value=1, value=1)
        order_number = st.text_input("Order Number", placeholder="e.g., ORD123")
        supplier_name = st.text_input("Supplier Name", placeholder="e.g., Book Supplier Inc.")
        status = st.selectbox("Status", ["Pending", "Confirmed", "Shipped"])
        total_cost = st.number_input("Total Cost", min_value=0.0, step=0.01)
        order_date = st.date_input("Order Date")
        expected_delivery_date = st.date_input("Expected Delivery Date")

        submitted = st.form_submit_button("Save Purchase Order")
        if submitted:
            if book_title and order_number and supplier_name:
                # Match the selected book with its details
                selected_book = next((book for book in books if book['title'] == book_title), None)
                if selected_book:
                    # Create the new order
                    books_ordered = [{"title": book_title, "quantity": quantity_to_order}]
                    new_order = create_order(
                        order_number=order_number,
                        supplier_name=supplier_name,
                        books_ordered=books_ordered,
                        status=status,
                        total_cost=total_cost,
                        order_date=str(order_date),  # Convert date to string for API
                        expected_delivery_date=str(expected_delivery_date),  # Convert date to string for API
                    )
                    if new_order:
                        st.info(f"Order for {quantity_to_order} units of '{book_title}' created successfully!")
                    else:
                        st.error("Failed to match the selected book.")
                else:
                    st.error("Please fill out all required fields.")

           

        cancel_button = False
        cancel_order_id = ""

        # Section: View Existing Purchase Orders
        st.subheader("Existing Purchase Orders")
        orders = fetch_orders()
        if orders:

            for order in orders:
                order_id = order['_id']
                date = ''
                with st.expander(f"Order: {order['orderNumber']} ({order['status']})"):
                    st.write(f"**Supplier Name**: {order['supplierName']}")
                    st.write(f"**Books Ordered**: {order['booksOrdered']}")
                    st.write(f"**Total Cost**: ${order['totalCost']:.2f}")
                    date = formatDate(order['orderDate'])
                    st.write(f"**Order Date**: {date}")
                    date = formatDate(order['expectedDeliveryDate'])
                    st.write(f"**Expected Delivery Date**: {date}")
                    if st.button(f"Cancel Order", order['_id']):
                        cancel_order(order_id)
        else:
            st.write("No existing purchase orders found.")

                

