pip install --upgrade pip
import streamlit as st
import pandas as pd
from st_aggrid import AgGrid
from PIL import Image, ImageDraw
import os
import io
import base64
import matplotlib.pyplot as plt
import seaborn as sns
from streamlit_option_menu import option_menu
from streamlit_cropper import st_cropper

# Define CSS style for the boxed section
box_style = """
    <style>
    .box {
        background-color: #f0f0f0;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
    }
    .logo {
        margin-right: 20px;
    }
    </style>
"""

# Display boxed section with title, logo, and tagline
st.markdown('<style>' + box_style + '</style>', unsafe_allow_html=True)
st.markdown('<div class="box">', unsafe_allow_html=True)

#st.image("logo1.png", width=100)  # Replace with your logo path and adjust width as needed
st.markdown('<div style="flex-grow: 1;">', unsafe_allow_html=True)
#st.markdown('<h1 style="color: blue;">Custom Header with Blue Color</h1>', unsafe_allow_html=True)
st.markdown('<h2 style="background-color: #f0f0f0; padding: 10px;text-align: center, font-size: 46px">FARSuN</h2>', unsafe_allow_html=True)
#st.markdown('<h3 style="font-family: Arial, sans-serif;">Header with Custom Font Family</h3>', unsafe_allow_html=True)
st.write("**Findability and Accessibility of historical (1610-1980) Raw Sunspot Numbers**")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# List of years available
years = [1951, 1952, 1953, 1954, 1955, 1956, 1957, 1958, 1959,1960,1961,1962,1963,1964,1965,1966,1967,1968,1969,1970,1971,1972,1973,1974,1975,1976,1977,1978,1979]  # Add other years as needed

# Custom CSS to stretch the menu bar
menu_style = """
    <style>
    .horizontal-menu {
        display: flex;
        justify-content: space-between;
        width: 100%;
        padding: 10px 0;
        border-bottom: 1px solid #ccc;
    }
    .horizontal-menu .menu-item {
        flex-grow: 1;
        text-align: center;
    }
    .horizontal-menu .menu-item .menu-content {
        justify-content: center;
    }
    </style>
"""

# Display CSS
st.markdown(menu_style, unsafe_allow_html=True)

# Sidebar menu for selecting the year
selected_year = option_menu(
    "Select Year",
    options=[str(year) for year in years],
    icons=["calendar"] * len(years),
    menu_icon="calendar",
    default_index=0,
    orientation="horizontal"
)
# Function to load images and their captions from a directory
def load_images_and_captions(directory):
    images = []
    captions = []
    # List all files in the directory
    files = os.listdir(directory)
    # Filter out only image files (assuming they have .jpg extension)
    image_files = [f for f in files if f.endswith('.jpg') or f.endswith('.jpeg') or f.endswith('.png')]
    # Sort image files by filename if necessary
    image_files.sort()

    for img_file in image_files:
        images.append(os.path.join(directory, img_file))
        captions.append(f' {img_file}')

    return images, captions

# Function to create a sample DataFrame (you can replace this with your actual data loading logic)
def create_sample_dataframe(img_index):
    page_number = f"p{img_index + 1:03}.jpg"  # Format page number as p001, p002, etc.
    data = [
        {"Page": page_number, "Date": i, "g.f-1": "", "k-1": "", "g.f-2": "", "k-2": "",
         "g.f-3": "", "k-3": "", "g.f-4": "", "k-4": "", "g.f-5": "", "k-5": "", "g.f-6": "", "k-6": "",
         "g.f-7": "", "k-7": "", "g.f-8": "", "k-8": "", "g.f-9": "", "k-9": "", "g.f-10": "", "k-10": "",
         "g.f-11": "", "k-11": "", "g.f-12": "", "k-12": ""}
        for i in range(1, 32)  # Example: 31 dates
    ]
    return pd.DataFrame(data)

# Function to plot stacked bar chart
def plot_filled_empty_columns(df):
    filled_counts = df.apply(lambda x: x != "").sum()
    empty_counts = df.apply(lambda x: x == "").sum()

    data = pd.DataFrame({'Filled': filled_counts, 'Empty': empty_counts}).reset_index()
    data = pd.melt(data, id_vars=['index'], value_vars=['Filled', 'Empty'], var_name='Status', value_name='Count')

    plt.figure(figsize=(8, 2))
    # Define custom colors for filled and empty categories
    custom_palette = {"Filled": "skyblue", "Empty": "salmon"}
    sns.barplot(x='index', y='Count', hue='Status', data=data, dodge=True, palette=custom_palette)
    
    plt.xticks(rotation=90)
    plt.xlabel('Columns')
    plt.ylabel('Count')
    plt.title('Filled vs Empty Cells per Column')
    plt.legend(title='Status', fontsize=5)
    st.pyplot(plt)

# Initialize session state if not already done
if 'img_index' not in st.session_state:
    st.session_state.img_index = 0

# Initialize download count dictionary if not already done
if 'download_count' not in st.session_state:
    st.session_state.download_count = {}

# Directory for the selected year
image_directory = f'{selected_year}_jpg'

# Load images and captions for the selected year
images, captions = load_images_and_captions(image_directory)

# Navigation buttons
col1, col2, col3 = st.columns([1, 2, 1])

# Previous button with custom styling
if col1.button('Previous', key='prev_button', disabled=st.session_state.img_index == 0):
    if st.session_state.img_index > 0:
        st.session_state.img_index -= 1

# Next button with custom styling and disabled state
if col3.button('Next', key='next_button', disabled=st.session_state.img_index >= len(images) - 1):
    if st.session_state.img_index < len(images) - 1:
        st.session_state.img_index += 1

# Display current image and caption if images exist
if images:
    current_img_path = images[st.session_state.img_index]
    current_caption = captions[st.session_state.img_index]

    # Layout for side-by-side display
    col_image, col_zoomed, col_form = st.columns([3, 2, 4])


    with col_image:
        st.subheader("Original Image: Table for Year: "+ str(selected_year) +" Page: "+ str(st.session_state.img_index + 1))
        image = Image.open(current_img_path)
        img_data = image.convert("RGB")
        cropped_image = st_cropper(image, realtime_update=True, box_color='#0000FF', aspect_ratio=None)
        
        #cropped_e = cropped_image.resize((col_image.width, int(cropped_image.height * col_image.width / cropped_image.width)))

        #st.image(image, caption=current_caption, use_column_width=True)

    with col_zoomed:
        st.subheader("Zoomed Image")
        if cropped_image:
            st.image(cropped_image, use_column_width=True)
    # Sample DataFrame creation based on the current image index
    df_key = f"df_{st.session_state.img_index}"
    if df_key not in st.session_state:
        st.session_state[df_key] = create_sample_dataframe(st.session_state.img_index)

    # Display DataFrame form in the second column
    with col_form:
        st.subheader("Transcribed Table")
        with st.form("Transcribed Table"):
            # Display AgGrid with the DataFrame
            response = AgGrid(st.session_state[df_key],
                              editable=True,
                              allow_unsafe_jscode=True,
                              theme='alpine',
                              height=800,
                              width=800,
                              fit_columns_on_grid_load=True,
                              enterNavigatesVertically = True,
                              enterNavigatesVerticallyAfterEdit= True,
                              editType='fullrow',
                              undoRedoCellEditing= True,
                              autoSizeStrategy ='fitProvidedWidth'
                            )

            # Submit button with custom styling
            submit_button = st.form_submit_button("Confirm")
# Determine download count for current page
        page_key = os.path.basename(current_img_path)
        if page_key not in st.session_state.download_count:
            st.session_state.download_count[page_key] = 0

        download_count = st.session_state.download_count[page_key]

        # Display download history
        st.markdown("<p style='font-size: 18px;'><strong>Download History:</strong></p>", unsafe_allow_html=True)
        if download_count > 0:
            st.markdown(f"<p style='font-size: 18px; color: green;'>&#10004; Downloaded {download_count} times</p>", unsafe_allow_html=True)

        # Download button with custom styling
        csv_bytes = st.session_state[df_key].to_csv(index=False).encode('utf-8')
        st.download_button(
            label=f"Download {os.path.basename(current_img_path)} Table 🗳️",
            data=csv_bytes,
            file_name=f"{os.path.splitext(os.path.basename(current_img_path))[0]}_table.csv",
            mime="text/csv"
        )

        # Increment download count upon download
        if submit_button:
            st.session_state.download_count[page_key] += 1

    # Display the final DataFrame output in the middle after confirming
    if submit_button:
        
        # Update the session state with the latest DataFrame
        st.session_state[df_key] = response['data']

        # Display final DataFrame
        st.write(st.session_state[df_key])

        #st.session_state.df = response['data']

        # Display final DataFrame
        #st.write(st.session_state.df)

        # Plot the stacked bar chart
        st.subheader("Filled vs Empty Cells per Column")
        plot_filled_empty_columns(pd.DataFrame(st.session_state[df_key]))

        
