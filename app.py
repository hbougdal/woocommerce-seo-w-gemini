import requests
import base64
import json
import google.generativeai as genai
import requests

import streamlit as st
from typing import Dict, List

# import config & helper functions
from config import *
from helpers import *




def get_products(page_number):
    """Retrieves all products from a WooCommerce store.

    Args:
        page_number (int): Products page number.

    Returns:
        list: A list of product dictionaries.
    """

    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{CONSUMER_KEY}:{CONSUMER_SECRET}'.encode('utf-8')).decode('utf-8')}"
    }

    products = []

    params = {"per_page": 10, "page": page_number, "status": "publish"}  #10 is maximum allowed by the Woocommerce API.
    response = requests.get(STORE_URL + "/wp-json/wc/v3/products", headers=headers, params=params)

    if response.status_code == 200:
        products += response.json()
    else:
        return None

    return products

def get_product_pages_count():
    """Retrieves all products from a WooCommerce store.

    Returns:
        list: A list of product dictionaries.
    """
    params = {"per_page": 10, "status": "publish"}  #10 is maximum allowed by the Woocommerce API.
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{CONSUMER_KEY}:{CONSUMER_SECRET}'.encode('utf-8')).decode('utf-8')}"
    }

    response = requests.get(STORE_URL + "/wp-json/wc/v3/products", headers=headers, params=params)
    if response.status_code == 200:
        total_pages = int(response.headers.get('X-WP-TotalPages', 0))
        return total_pages
    else: 
        return None


def get_product_by_id(product_id):
    """Retrieves a product from a WooCommerce store by its ID.

    Args:
        store_url (str): The URL of the WooCommerce store.
        consumer_key (str): The consumer key for authentication.
        consumer_secret (str): The consumer secret for authentication.
        product_id (int): The ID of the product to retrieve.

    Returns:
        dict: The product data in JSON format if successful, None otherwise.
    """

    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{CONSUMER_KEY}:{CONSUMER_SECRET}'.encode('utf-8')).decode('utf-8')}"
    }

    url = f"{STORE_URL}/wp-json/wc/v3/products/{product_id}"  # Use GET request for retrieving

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None

def duplicate_product(product_id):
    """Duplicates a product in a WooCommerce store.

    Args:
        store_url (str): The URL of the WooCommerce store.
        consumer_key (str): The consumer key for authentication.
        consumer_secret (str): The consumer secret for authentication.
        product_id (int): The ID of the product to duplicate.

    Returns:
        dict: The response from the WooCommerce API.
    """

    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{CONSUMER_KEY}:{CONSUMER_SECRET}'.encode('utf-8')).decode('utf-8')}"
    }

    url = f"{STORE_URL}/wp-json/wc/v3/products/{product_id}/duplicate"

    response = requests.post(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None

def update_product(product_id, product_data):
    """Updates a product in a WooCommerce store.

    Args:
        product_id (int): The ID of the product to update.
        data (dict): A dictionary containing the updated product data.

    Returns:
        dict: The response from the WooCommerce API.
    """

    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{CONSUMER_KEY}:{CONSUMER_SECRET}'.encode('utf-8')).decode('utf-8')}"
    }

    url = f"{STORE_URL}/wp-json/wc/v3/products/{product_id}"

    response = requests.put(url, headers=headers, json=product_data)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None

def optimize_product_for_seo_gemini(model_type, prompt):

    try:
    
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(model_type)

        #Get response from Gemini
        response = model.generate_content(prompt)
        
        # Extract the text from the correct location in the response
        generated_text = response.candidates[0].content.parts[0].text

        # Remove the triple backticks and any newline characters before and after the JSON
        cleaned_json_str = generated_text.strip("```json\n")
        json_str = json.dumps(cleaned_json_str, ensure_ascii=False)  # ensure_ascii=False preserves Unicode characters

        # Now you can safely parse the JSON
        parsed_data = json.loads(json_str)
        data = json.loads(parsed_data)

        return data

    except Exception as e:
        print(f"Error while interacting with Gemini: {e}")
        return None  # Or handle the error differently as per your needs


 

def main():
    """Main function for the Streamlit app."""
    #st.title("WooCommerce Product Optimizer (powered by Gemini)")
    st.set_page_config(
        page_title="WooCommerce Product Listings Optimization with Gemini",
        page_icon=":rocket:",
    )

    st.subheader("WooCommerce Product Listings Optimization with Gemini", divider="blue")

    model_type = st.radio(
        "Choose your Gemini version",
        GEMINI_MODEL_TYPEs
    )

    product_pages_count = get_product_pages_count()
 
    if product_pages_count: 
    
        pages = list(range(1, product_pages_count + 1))
        
        page_number = st.selectbox("Choose a product page", pages, label_visibility="visible")

        generate_t2t = st.button("Optimize Product Listings", key="generate_t2t")

        existing_pages_ids = read_page_ids (PAGES_FILE_NAME)

        if (generate_t2t and page_number) and (page_number not in existing_pages_ids):
       
            
            #Read previously processed products IDs to avoid processing them again.
            existing_product_ids = read_product_ids(PRODUCTS_FILE_NAME)
            # Get products on the page numbe "page_number"
            all_products = get_products(page_number)
            if all_products :
                for product in all_products:
                    product_id = product['id']

                    if product_id not in existing_product_ids: #product has not yet be processed

                        with st.spinner(f"Optimizing your product title and description of product (ID = {product_id}) using Google Gemini ..."):
                    
                            try:
                                # We first duplicate the original product (as a Draft) so that we have a backup copy.
                                duplicate_product_response = duplicate_product(product_id)

                                if duplicate_product_response: 

                                    new_product_id = duplicate_product_response["id"]
                                    st.success(f"Product {product_id} duplicated successfully", icon="✅")
                                    
                                    #Get product details of the original product
                                    product_data = get_product_by_id(product_id)

                                    if product_data: 
                                        # Update Title of the title of duplicated product to include the ID of the original product >> ensure an easy mapping if manual updates are needed.
                                        new_title = f"{product_id} -- {product_data['name']}"
                                        updated_title = {
                                            "name": new_title
                                        }
                                        
                                        updated_product = update_product(new_product_id, updated_title)

                                        st.success(f"Product {product_id} duplicated successfully & Product title updated to include the original product ID.", icon="✅")
                                        
                                        #Extract product title & description
                                        product_title = product_data['name']
                                        product_description = product_data['description']

                                        #Prepare a prompt for Gemini
                                        prompt = prep_prompt (product_title, product_description)

                                        #Call Gemini to get an seo-optimized product title & description
                                        new_product_data = optimize_product_for_seo_gemini(model_type, prompt)

                                        #We will use this to check of Gemini response conatins expected attributes
                                        attributes_to_check = ["name", "description"]

                                        if has_attributes(new_product_data, attributes_to_check):

                                            # Update product title (name) and description 
                                            updated_product = update_product(product_id, new_product_data)
                                            
                                           
                                            if updated_product:

                                                new_product_link= f"{STORE_URL}wp-admin/post.php?post={product_id}&action=edit"
                                                st.link_button("View updated product On Woocommerce", new_product_link)
                                                st.success(f"SEO-optimization for product {product_id} is successful.", icon="✅")
                                                # Add product ID to the list of successfully processed products
                                                
                                                update_processed_product_ids(product_id)
                                            else:
                                                #print("Error updating product.")
                                                st.error(f"Error updating information of original product {product_id}", icon="🚨") 
                                                log_error(f"{product_id} >> An error occurred while trying to update information of the original product.", LOGS_FILE)
                                        else: 
                                            st.error(f"Error seo-optimizing product {product_id}:  the object is missing some required attributes (name or description).", icon="🚨")
                                            log_error(f"{product_id} >> An error occurred while trying to seo-optimize this product: missing some required attributes (name or description)", LOGS_FILE)
                                    else: 
                                        st.error(f"Error retrieving information of product {str(new_product_id)}", icon="🚨")
                                        log_error(f"{product_id} >> An error occurred while retrieving product information.", LOGS_FILE)
                                else: 
                                    log_error(f"{product_id} >> An error occurred while dupliating this product.", LOGS_FILE)
                            except Exception as e:
                                st.error(f"An error occurred: {e}")
                                log_error(f"{product_id} >> An error occurred: {e}", LOGS_FILE)
                    else: 
                        st.warning(f"Product with ID: {product_id} is already processed", icon="⚠️")
                
                #Save processed page number to files. 
                update_processed_page_ids (page_number)
            else: 
                st.error(f"Error while trying to retrieve products on page {page_number}", icon="🚨")
        elif page_number in existing_pages_ids : 
            st.warning("This product page is already processed before.", icon="⚠️")
    else: 
        st.warning("Could not retrieve the products list.", icon="⚠️")
        return


if __name__ == "__main__":
    main()
