import json
import os 
import datetime

def prep_prompt (product_title, product_description):
    prompt = f"""Task: Optimize the following product title and description for SEO and return the optimized content as a JSON object with the following attributes:
              - name: The optimized product title.
              - description: The optimized product description.
              Product Title: {product_title} 
              Product Description: {product_description}

              Requirements:

                  1. Identify the main SEO keyword and any relevant secondary keywords.
                  2. Rewrite the title to incorporate the main keyword naturally and prominently.
                  3. Rewrite the description to:
                      - Include the main keyword and secondary keywords strategically throughout the text, ensuring a natural flow and readability.
                      - Maintain the original structure and bullet points.
                      - Remove any mentions of country names or sourcing countries.
                      - Be engaging and informative, highlighting the product's benefits and unique selling points.
                      - Include a clear call to action, encouraging users to "order now" or take a similar desired action. 
                      - Use an active voice and transition words for improved readability.
                  4. At the end of the description, add a paragraph stating: "This product can also be found using the following keywords:" followed by the top 5 most relevant Google search SEO keywords (comma-separated).
                  5. Ensure the overall tone is persuasive and aligns with the product's target audience.
                  6. Use an active voice.
                  7. Consecutive sentences should not start with the same word.
                  8. The description should have two headlines (containing main seo keyword) and two paragraphs. 
                  9. The description should be at least 200 words long 

              Return only a valid JSON object with the optimized title (JSON attribute "name") and description (JSON attribute "description").
            """
    return prompt


def has_attributes(json_obj, attributes):
  """Checks if a JSON object has all the specified attributes."""
  for attr in attributes:
    if attr not in json_obj:
      return False
  return True

def read_page_ids(pages_file_name):
    """Reads a list of product IDs from a JSON file."""
    try:
        with open(pages_file_name, 'r') as f:
            data = json.load(f)
            return data['page_ids']  
    except FileNotFoundError:
        return []


def update_processed_page_ids(new_id, pages_file_name="pages.json"):
    """
    Updates the list of page IDs in a JSON file, 
    adding the new ID if it doesn't already exist.
    """
    existing_ids = read_page_ids(pages_file_name)

    if new_id not in existing_ids:
        existing_ids.append(new_id)

    with open(pages_file_name, 'w') as f:
        json.dump({'page_ids': existing_ids}, f, indent=4)
        
def read_product_ids(products_file_name):
    """Reads a list of product IDs from a JSON file."""
    try:
        with open(products_file_name, 'r') as f:
            data = json.load(f)
            return data['product_ids']  
    except FileNotFoundError:
        return []

def update_processed_product_ids(new_id, products_file_name = "products.json"):
    """
    Updates the list of product IDs in a JSON file, 
    adding the new ID if it doesn't already exist.
    """
    existing_ids = read_product_ids(products_file_name)
    
    if new_id not in existing_ids:
        existing_ids.append(new_id) 
    
    with open(products_file_name, 'w') as f:
        json.dump({'product_ids': existing_ids}, f, indent=4)

def log_error(error_message, log_file="logs.json"):
  """
  Logs an error message to a JSON file.

  Creates the log file if it doesn't exist.

  Args:
      error_message: The error message to log (string).
      log_file: The name of the log file (default: "logs.json").
  """

  try:
    # Check if the log file exists
    if not os.path.exists(log_file):
      # If it doesn't exist, create an empty JSON array in the file
      with open(log_file, "w") as f:
        json.dump([], f)

    # Load existing logs from the file
    with open(log_file, "r") as f:
      logs = json.load(f)

    # Add the new error message to the logs
    logs.append({"timestamp": datetime.datetime.now().isoformat(), "message": error_message})

    # Write the updated logs back to the file
    with open(log_file, "w") as f:
      json.dump(logs, f, indent=4)

  except Exception as e:
    print(f"Error writing to log file: {e}")


