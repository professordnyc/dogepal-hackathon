import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# API configuration
API_BASE_URL = "http://localhost:8000/api/v1"

def show():
    st.title("💸 Spending Analysis")
    
    # Date range filter
    col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
    
    with col1:
        # Default to last 30 days
        default_end = datetime.now()
        default_start = default_end - timedelta(days=30)
        start_date = st.date_input("Start Date", default_start)
    
    with col2:
        end_date = st.date_input("End Date", default_end)
    
    with col3:
        st.write("")
        st.write("")
        if st.button("Apply Filters"):
            st.experimental_rerun()
    
    with col4:
        st.write("")
        st.write("")
        if st.button("Reset"):
            st.experimental_rerun()
    
    # Category and department filters
    col1, col2 = st.columns(2)
    
    with col1:
        # Fetch categories for filter
        response = requests.get(f"{API_BASE_URL}/spending/categories")
        categories = ["All"] + (response.json() if response.status_code == 200 else [])
        selected_category = st.selectbox("Category", categories, index=0)
    
    with col2:
        # Fetch departments for filter
        response = requests.get(f"{API_BASE_URL}/spending/departments")
        departments = ["All"] + (response.json() if response.status_code == 200 else [])
        selected_department = st.selectbox("Department", departments, index=0)
    
    # Build query parameters
    params = {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
    }
    
    if selected_category != "All":
        params["category"] = selected_category
    if selected_department != "All":
        params["department"] = selected_department
    
    # Fetch spending data
    with st.spinner("Loading spending data..."):
        try:
            # Get spending transactions
            response = requests.get(f"{API_BASE_URL}/spending/", params=params)
            response.raise_for_status()
            transactions = response.json()
            
            if not transactions:
                st.info("No transactions found for the selected filters.")
                return
            
            # Convert to DataFrame for easier manipulation
            df = pd.DataFrame(transactions)
            df['date'] = pd.to_datetime(df['date'])
            
            # Display summary stats
            st.subheader("Spending Summary")
            
            # Calculate metrics
            total_spent = df['amount'].sum()
            avg_transaction = df['amount'].mean()
            transactions_count = len(df)
            
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Spent", f"${total_spent:,.2f}")
            with col2:
                st.metric("Avg. Transaction", f"${avg_transaction:,.2f}")
            with col3:
                st.metric("Transactions", transactions_count)
            with col4:
                st.metric("Vendors", df['vendor'].nunique())
            
            # Time series chart
            st.subheader("Spending Over Time")
            
            # Group by date
            df_daily = df.set_index('date').resample('D')['amount'].sum().reset_index()
            
            fig = px.area(
                df_daily,
                x='date',
                y='amount',
                labels={'amount': 'Amount ($)', 'date': 'Date'},
                title="Daily Spending"
            )
            fig.update_traces(fill='tozeroy', line=dict(width=1))
            fig.update_layout(hovermode='x unified')
            st.plotly_chart(fig, use_container_width=True)
            
            # Category breakdown
            st.subheader("Spending by Category")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Bar chart
                df_category = df.groupby('category')['amount'].sum().reset_index()
                df_category = df_category.sort_values('amount', ascending=False)
                
                fig = px.bar(
                    df_category,
                    x='category',
                    y='amount',
                    labels={'amount': 'Amount ($)', 'category': 'Category'},
                    color='category',
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Donut chart
                fig = px.pie(
                    df_category,
                    values='amount',
                    names='category',
                    hole=0.4,
                    color_discrete_sequence=px.colors.sequential.RdBu
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(showlegend=False, height=300)
                st.plotly_chart(fig, use_container_width=True)
            
            # Top vendors
            st.subheader("Top Vendors")
            
            df_vendors = df.groupby('vendor')['amount'].agg(['sum', 'count']).reset_index()
            df_vendors = df_vendors.rename(columns={'sum': 'total_spent', 'count': 'transactions'})
            df_vendors = df_vendors.sort_values('total_spent', ascending=False).head(10)
            
            fig = px.bar(
                df_vendors,
                x='total_spent',
                y='vendor',
                orientation='h',
                labels={'total_spent': 'Total Spent ($)', 'vendor': 'Vendor'},
                color='transactions',
                color_continuous_scale='Blues',
                title="Top Vendors by Total Spent"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Transaction details
            st.subheader("Transaction Details")
            
            # Format the DataFrame for display
            display_df = df[['date', 'vendor', 'category', 'department', 'amount', 'description']].copy()
            display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
            
            st.dataframe(
                display_df.sort_values('date', ascending=False),
                column_config={
                    "date": "Date",
                    "vendor": "Vendor",
                    "category": "Category",
                    "department": "Department",
                    "amount": st.column_config.NumberColumn(
                        "Amount",
                        format="$%.2f",
                    ),
                    "description": "Description"
                },
                hide_index=True,
                use_container_width=True
            )
            
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching data: {str(e)}")
            st.info("Please make sure the backend server is running.")
        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")
    
    # Add new transaction form
    st.subheader("Add New Transaction")
    
    with st.form("new_transaction"):
        col1, col2 = st.columns(2)
        
        with col1:
            amount = st.number_input("Amount", min_value=0.01, step=0.01, format="%.2f")
            category = st.selectbox("Category", [c for c in categories if c != "All"])
            date = st.date_input("Date", datetime.now())
        
        with col2:
            vendor = st.text_input("Vendor")
            department = st.selectbox("Department", [d for d in departments if d != "All"])
            description = st.text_area("Description")
        
        if st.form_submit_button("Add Transaction"):
            if not all([amount, category, vendor, department]):
                st.error("Please fill in all required fields.")
            else:
                transaction_data = {
                    "amount": float(amount),
                    "category": category,
                    "vendor": vendor,
                    "department": department,
                    "date": date.isoformat(),
                    "description": description if description else None
                }
                
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/spending/",
                        json=transaction_data
                    )
                    response.raise_for_status()
                    st.success("Transaction added successfully!")
                    st.experimental_rerun()
                except requests.exceptions.RequestException as e:
                    st.error(f"Failed to add transaction: {str(e)}")
