import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# API configuration
API_BASE_URL = "http://localhost:8000/api/v1"

def get_confidence_color(score):
    """Return color based on confidence score"""
    if score >= 0.8:
        return "high"
    elif score >= 0.5:
        return "medium"
    return "low"

def show():
    st.title("💡 Recommendations")
    
    # Status filter
    status_filter = st.radio(
        "Filter by status",
        ["All", "Pending", "Implemented", "Rejected"],
        horizontal=True
    )
    
    # Confidence threshold
    min_confidence = st.slider(
        "Minimum Confidence",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.1
    )
    
    # Generate new recommendations button
    if st.button("🔄 Generate New Recommendations"):
        with st.spinner("Analyzing spending patterns and generating recommendations..."):
            try:
                response = requests.post(f"{API_BASE_URL}/recommendations/generate")
                response.raise_for_status()
                st.success(f"Generated {len(response.json())} new recommendations!")
                st.experimental_rerun()
            except requests.exceptions.RequestException as e:
                st.error(f"Failed to generate recommendations: {str(e)}")
    
    # Build query parameters
    params = {"min_confidence": min_confidence}
    if status_filter != "All":
        params["status"] = status_filter.lower()
    
    # Fetch recommendations
    with st.spinner("Loading recommendations..."):
        try:
            # Get recommendations
            response = requests.get(f"{API_BASE_URL}/recommendations/", params=params)
            response.raise_for_status()
            recommendations = response.json()
            
            if not recommendations:
                st.info("No recommendations found. Try adjusting the filters or generating new recommendations.")
                return
            
            # Display stats
            st.subheader("Recommendation Overview")
            
            # Get recommendation stats
            stats_response = requests.get(f"{API_BASE_URL}/recommendations/stats")
            stats = stats_response.json() if stats_response.status_code == 200 else {}
            
            # Calculate potential savings
            pending_savings = sum(
                rec["potential_savings"] 
                for rec in recommendations 
                if rec["status"] == "pending"
            )
            
            # Display metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Total Recommendations",
                    stats.get("total_recommendations", 0)
                )
            
            with col2:
                st.metric(
                    "Pending Recommendations",
                    stats.get("recommendations_by_status", {}).get("pending", 0),
                    f"${pending_savings:,.2f} potential savings"
                )
            
            with col3:
                st.metric(
                    "Total Potential Savings",
                    f"${stats.get('total_potential_savings', 0):,.2f}"
                )
            
            # Display recommendations
            st.subheader("Recommendations")
            
            # Group by type
            type_tabs = st.tabs(["All"] + list(set(rec["recommendation_type"].replace("_", " ").title() for rec in recommendations)))
            
            with type_tabs[0]:  # All tab
                for rec in recommendations:
                    display_recommendation(rec)
            
            # Create tabs for each recommendation type
            rec_by_type = {}
            for rec in recommendations:
                rec_type = rec["recommendation_type"].replace("_", " ").title()
                if rec_type not in rec_by_type:
                    rec_by_type[rec_type] = []
                rec_by_type[rec_type].append(rec)
            
            for i, (rec_type, recs) in enumerate(rec_by_type.items(), 1):
                with type_tabs[i]:
                    for rec in recs:
                        display_recommendation(rec)
            
            # Display charts
            st.subheader("Recommendation Insights")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Recommendations by type
                if stats.get("recommendations_by_type"):
                    df_type = pd.DataFrame(
                        [{"Type": k.replace("_", " ").title(), "Count": v} 
                         for k, v in stats["recommendations_by_type"].items()]
                    )
                    fig = px.pie(
                        df_type,
                        values='Count',
                        names='Type',
                        title='Recommendations by Type',
                        hole=0.4,
                        color_discrete_sequence=px.colors.qualitative.Pastel
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Recommendations by status
                if stats.get("recommendations_by_status"):
                    df_status = pd.DataFrame(
                        [{"Status": k.title(), "Count": v} 
                         for k, v in stats["recommendations_by_status"].items()]
                    )
                    fig = px.bar(
                        df_status,
                        x='Status',
                        y='Count',
                        title='Recommendations by Status',
                        color='Status',
                        color_discrete_sequence=px.colors.qualitative.Pastel
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching data: {str(e)}")
            st.info("Please make sure the backend server is running.")
        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")

def display_recommendation(rec):
    """Helper function to display a single recommendation card"""
    confidence_color = get_confidence_color(rec["confidence_score"])
    
    with st.container():
        st.markdown(
            f"""
            <div class="recommendation-card {confidence_color}">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <h3 style="margin: 0;">{rec['title']}</h3>
                    <div style="display: flex; align-items: center;">
                        <span style="margin-right: 1rem; font-weight: bold; color: {'#f44336' if confidence_color == 'high' else '#ff9800' if confidence_color == 'medium' else '#2196F3'};">
                            ${rec['potential_savings']:,.2f} potential savings
                        </span>
                        <span class="badge" style="background: {'#f44336' if confidence_color == 'high' else '#ff9800' if confidence_color == 'medium' else '#2196F3'}; color: white; padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.8rem;">
                            {rec['confidence_score']*100:.0f}% confidence
                        </span>
                    </div>
                </div>
                <p style="margin: 0.5rem 0;">{rec['description']}</p>
                <div style="font-size: 0.9rem; color: #666; margin-bottom: 0.5rem;">
                    <strong>Type:</strong> {rec['recommendation_type'].replace('_', ' ').title()} | 
                    <strong>Status:</strong> {rec['status'].title()}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Collapsible section for more details
        with st.expander("View Details & Actions"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown("#### Explanation")
                
                # Check if explanation contains calculation details (from HP AI Studio model)
                explanation_text = rec["explanation"]
                if "\n\nFactors considered:" in explanation_text:
                    # Split into calculation and factors
                    parts = explanation_text.split("\n\nFactors considered:")
                    
                    # Display calculation in a code block for better formatting
                    st.markdown("**Calculation Details:**")
                    st.code(parts[0], language="text")
                    
                    # Display factors in a bulleted list
                    st.markdown("**Factors Considered:**")
                    factors = parts[1].strip().split("\n")
                    for factor in factors:
                        st.markdown(factor)
                else:
                    # Display regular explanation
                    st.markdown(explanation_text)
                
                st.markdown("#### Suggested Action")
                st.markdown(rec["suggested_action"])
                
                # Add explainability metrics if available
                if rec.get("confidence_score"):
                    st.markdown("#### Confidence Metrics")
                    st.progress(rec["confidence_score"])
                    st.markdown(f"Confidence Score: **{rec['confidence_score']*100:.1f}%**")
                    
                    # Priority indicator
                    priority = rec.get("priority", "medium")
                    priority_color = {
                        "high": "🔴", 
                        "medium": "🟠",
                        "low": "🟢"
                    }.get(priority.lower(), "🟠")
                    st.markdown(f"Priority: **{priority_color} {priority.title()}**")
                
                if rec.get("spending_vendor"):
                    st.markdown("#### Related Transaction")
                    st.markdown(f"**Vendor:** {rec['spending_vendor']}")
                    st.markdown(f"**Amount:** ${rec['spending_amount']:,.2f}")
                    st.markdown(f"**Date:** {rec['spending_date']}")
            
            with col2:
                st.markdown("#### Update Status")
                
                status_options = ["pending", "implemented", "rejected"]
                new_status = st.radio(
                    "",
                    status_options,
                    index=status_options.index(rec["status"]),
                    format_func=lambda x: x.title(),
                    key=f"status_{rec['id']}"
                )
                
                if st.button("Update", key=f"update_{rec['id']}"):
                    try:
                        response = requests.put(
                            f"{API_BASE_URL}/recommendations/{rec['id']}",
                            json={"status": new_status}
                        )
                        response.raise_for_status()
                        st.success("Status updated successfully!")
                        st.experimental_rerun()
                    except requests.exceptions.RequestException as e:
                        st.error(f"Failed to update status: {str(e)}")
                
                st.markdown("---")
                if st.button("Dismiss", key=f"dismiss_{rec['id']}"):
                    try:
                        response = requests.delete(f"{API_BASE_URL}/recommendations/{rec['id']}")
                        response.raise_for_status()
                        st.success("Recommendation dismissed!")
                        st.experimental_rerun()
                    except requests.exceptions.RequestException as e:
                        st.error(f"Failed to dismiss recommendation: {str(e)}")
