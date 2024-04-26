import streamlit as st
import datetime

def update_customer():
    st.title("Update New Customer")
    
    col1, col2 = st.columns(2)
    
    with col1:
        customer_name = st.text_input("Customer Name", max_chars=250)
        approval_no = st.text_input("Approval No", max_chars=50)
        rtkm = st.number_input("Round Trip KM", step=1.0)
        inox_ap_concern_region = st.selectbox("Inox AP Concern Region", ["Region A", "Region B", "Region C"])
        known_to_inoxap = st.selectbox("Known to InoxAP", ["Yes", "No"])
    
    with col2:
        potential_supplier = st.text_area("Potential Supplier", max_chars=250)
        industry_segment = st.selectbox("Industry Segment", ["Segment A", "Segment B", "Segment C"])
        type_of_customer = st.selectbox("Type of Customer", ["Type A", "Type B", "Type C"])
        project_type = st.selectbox("Project Type", ["Type X", "Type Y", "Type Z"])
        estimated_volume = st.number_input("Estimated Volume (In Sm3/Month)", step=1.0)
        site_condition = st.selectbox("Site Condition", ["Condition A", "Condition B", "Condition C"])
        site_photo = st.file_uploader("Site Photographs (Upload image [size < 1 MB])", type=["jpg", "jpeg", "png"])
    
    reason_for_loss = st.text_area("Reason for Business Loss to InoxAP")
    
    # Remarks with date
    remarks = st.text_area("Remarks")
    if st.button("Add Remark"):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        remarks += f"\n{current_time}: {remarks}"
    
    #st.write("Remarks:", remarks)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Update", key="update_btn"):
            # Logic to update the customer data
            st.success("Customer Updated Successfully!")
    
    with col2:
        if st.button("Cancel", key="cancel_btn"):
            st.warning("Operation Cancelled")

update_customer()
