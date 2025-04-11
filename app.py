import streamlit as st
import pandas as pd

st.title("Nancy's Quote Dashboard")

st.markdown("""
This dashboard helps you quickly update quotes’ statuses based on:
- **CLOSED (ORDERED)** – if the order was placed.
- **LOST** – if the quote did not result in an order.
- **FOLLOW UP** – if you need to check back with the customer.
""")

# --- Step 1: Upload Excel File ---
uploaded_file = st.file_uploader("Upload NANCY_OPEN_QUOTES Excel file", type=["xlsx"])

if uploaded_file is not None:
    try:
        # Read the uploaded Excel file
        df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Error reading file: {e}")
    else:
        # Ensure the STATUS column is a string and stripped of whitespace
        df['STATUS'] = df['STATUS'].astype(str).str.strip()

        st.subheader("Current Open Quotes")
        st.dataframe(df)

        # --- Step 2: Quote Update Section ---
        st.subheader("Update Quote Status")

        # Prepare a dictionary for session state updates
        if 'updates' not in st.session_state:
            st.session_state.updates = {}

        # Let the user choose a quote to update
        quote_ids = df['QUOTE#'].unique().tolist()

        # Build a display map: if a quote has been updated, add a checkmark
        display_map = {}
        for quote in quote_ids:
            if quote in st.session_state.updates:
                label = f"✔ {quote}"
            else:
                label = str(quote)
            display_map[label] = quote

        # Dropdown uses the display labels, but then we extract the actual quote id
        selected_label = st.selectbox("Select a Quote to Update", options=list(display_map.keys()))
        selected_quote = display_map[selected_label]

        # Retrieve the selected quote’s record
        selected_row = df[df['QUOTE#'] == selected_quote].iloc[0]
        st.write("### Details for Quote#", selected_quote)
        st.write(selected_row)

        # Provide a selectbox for the new status
        status_options = ["CLOSED (ORDERED)", "LOST", "FOLLOW UP"]
        # Try to pre-select the current status if it matches one of the options
        try:
            default_index = status_options.index(selected_row['STATUS'])
        except ValueError:
            default_index = 0

        new_status = st.selectbox("Update Status", status_options, index=default_index)

        # Generate the suggested note based on new status
        if new_status == "CLOSED (ORDERED)":
            suggested_note = "Order placed: Z-stamped and closed."
        elif new_status == "LOST":
            suggested_note = "Quote marked as lost."
        else:
            suggested_note = "Pending customer reply. Follow-up needed."

        st.write("**Suggested Note:**", suggested_note)

        # Button to record the update in session state
        if st.button("Update Quote"):
            st.session_state.updates[selected_quote] = {
                "STATUS": new_status,
                "Suggested Note": suggested_note
            }
            st.success(f"Quote {selected_quote} updated!")

        # Display current updates from the session state
        if st.session_state.updates:
            st.subheader("Current Updates")
            updates_df = pd.DataFrame.from_dict(st.session_state.updates, orient='index').reset_index()
            updates_df.rename(columns={"index": "QUOTE#"}, inplace=True)
            st.dataframe(updates_df)

        # --- Step 3: Merge Updates and Download Updated Data ---
        if st.button("Download Updated File"):
            updated_df = df.copy()

            # For each updated quote, update the STATUS and add Suggested Note
            for quote, update in st.session_state.updates.items():
                updated_df.loc[updated_df['QUOTE#'] == quote, 'STATUS'] = update["STATUS"]
                # Create or update the Suggested Note column
                if 'Suggested Note' not in updated_df.columns:
                    updated_df['Suggested Note'] = ""
                updated_df.loc[updated_df['QUOTE#'] == quote, 'Suggested Note'] = update["Suggested Note"]

            # Convert updated dataframe to CSV for download
            csv_data = updated_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Updated CSV",
                data=csv_data,
                file_name='NANCY_OPEN_QUOTES_UPDATED.csv',
                mime='text/csv'
            )
else:
    st.info("Please upload the NANCY_OPEN_QUOTES Excel file to begin.")
