import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# API configuration
API_BASE_URL = "http://localhost:8000/api/v1"

def show():
    st.title("📊 Dashboard")
    
    # Display loading state
    with st.spinner("Loading dashboard data..."):
        try:
            # Fetch spending summary
            response = requests.get(f"{API_BASE_URL}/spending/stats/summary")
            response.raise_for_status()
            spending_stats = response.json()
            
            # Fetch recommendations stats
            response = requests.get(f"{API_BASE_URL}/recommendations/stats")
            response.raise_for_status()
            rec_stats = response.json()
            
            # Display KPIs
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Total Spending",
                    f"${spending_stats['total_amount']:,.2f}",
                    f"{len(spending_stats['category_distribution'])} categories"
                )
            
            with col2:
                st.metric(
                    "Avg. Transaction",
                    f"${spending_stats['average_amount']:,.2f}",
                    f"{spending_stats['total_transactions']} transactions"
                )
            
            with col3:
                pending = rec_stats.get('recommendations_by_status', {}).get('pending', 0)
                st.metric(
                    "Pending Recommendations",
                    pending,
                    f"${rec_stats.get('total_potential_savings', 0):,.2f} potential savings"
                )
            
            with col4:
                implemented = rec_stats.get('recommendations_by_status', {}).get('implemented', 0)
                st.metric(
                    "Implemented",
                    implemented,
                    f"{implemented / max(rec_stats.get('total_recommendations', 1), 1) * 100:.0f}% of total"
                )
            
            # Create two columns for charts
            col1, col2 = st.columns(2)
            
            # Spending by category chart
            with col1:
                st.subheader("Spending by Category")
                if spending_stats['category_distribution']:
                    df_cat = pd.DataFrame(spending_stats['category_distribution'])
                    fig = px.pie(
                        df_cat,
                        values='total',
                        names='category',
                        hole=0.4,
                        color_discrete_sequence=px.colors.sequential.RdBu
                    )
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(showlegend=False, height=400)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No spending data available.")
            
            # Recommendations by type chart
            with col2:
                st.subheader("Recommendations by Type")
                if rec_stats.get('recommendations_by_type'):
                    df_rec = pd.DataFrame(
                        [{"type": k, "count": v} for k, v in rec_stats['recommendations_by_type'].items()]
                    )
                    fig = px.bar(
                        df_rec,
                        x='type',
                        y='count',
                        color='type',
                        labels={'type': 'Recommendation Type', 'count': 'Count'},
                        color_discrete_sequence=px.colors.qualitative.Pastel
                    )
                    fig.update_layout(showlegend=False, height=400)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No recommendations generated yet.")
            
            # Recent spending activity
            st.subheader("Recent Spending")
            response = requests.get(f"{API_BASE_URL}/spending/", params={"limit": 5})
            if response.status_code == 200 and response.json():
                df_recent = pd.DataFrame(response.json())
                df_recent['date'] = pd.to_datetime(df_recent['date']).dt.strftime('%Y-%m-%d')
                st.dataframe(
                    df_recent[['date', 'vendor', 'category', 'amount']],
                    column_config={
                        "date": "Date",
                        "vendor": "Vendor",
                        "category": "Category",
                        "amount": st.column_config.NumberColumn(
                            "Amount",
                            format="$%.2f",
                        )
                    },
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.info("No recent transactions found.")
            
            # Quick actions
            st.subheader("Quick Actions")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🔄 Generate New Recommendations", use_container_width=True):
                    with st.spinner("Generating recommendations..."):
                        response = requests.post(f"{API_BASE_URL}/recommendations/generate")
                        if response.status_code == 200:
                            st.success(f"Generated {len(response.json())} new recommendations!")
                            st.experimental_rerun()
                        else:
                            st.error("Failed to generate recommendations.")
            
            with col2:
                if st.button("📊 View All Spending", use_container_width=True):
                    st.switch_page("pages/spending_analysis.py")
            
            with col3:
                if st.button("🔍 View Recommendations", use_container_width=True):
                    st.switch_page("pages/recommendations.py")
            
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching data: {str(e)}")
            st.info("Please make sure the backend server is running.")
        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")
