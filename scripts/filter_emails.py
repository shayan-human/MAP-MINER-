import csv
import re

input_file = '/home/shayan/Documents/coding/google-maps-scraper-local-repo/CAR DETAILER florida - google_enriched.csv'
output_file = '/home/shayan/Documents/coding/google-maps-scraper-local-repo/CAR DETAILER florida - emails_only.csv'

def is_valid_email_list(email_string):
    if not email_string or not email_string.strip():
        return False
    
    invalid_markers = [
        "None found",
        "Status 400",
        "Status 403",
        "Failed: ConnectionError",
        "SSL Error: SSLError",
        "user@domain.com",
        "example@mysite.com",
        "info@mysite.com"
    ]
    
    for marker in invalid_markers:
        if marker.lower() in email_string.lower():
            return False
            
    # Remove image assets and other non-email junk
    image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.pdf']
    
    emails = [e.strip() for e in email_string.split(',')]
    valid_non_junk = []
    
    for email in emails:
        # Basic email check: must have @ and .
        if '@' not in email or '.' not in email:
            continue
            
        # Check for image extensions
        if any(email.lower().endswith(ext) for ext in image_extensions):
            continue
            
        # Check for Sentry placeholders
        if 'sentry' in email.lower():
            continue
            
        valid_non_junk.append(email)
            
    if not valid_non_junk:
        return False
        
    return True

def filter_csv():
    try:
        with open(input_file, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            
            filtered_rows = []
            for row in reader:
                if is_valid_email_list(row.get('E MAILS', '')):
                    filtered_rows.append(row)
                    
        with open(output_file, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(filtered_rows)
            
        print(f"Filtering complete. {len(filtered_rows)} rows kept.")
        print(f"Results saved to: {output_file}")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    filter_csv()
