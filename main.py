import requests
import json
import os
import csv
from datetime import datetime
import unicodedata
import sys
import configparser
from pathlib import Path
from dotenv import load_dotenv

def get_salesforce_oauth_token(username, password, client_id, client_secret):
    """Get Salesforce access token using OAuth2 password flow"""
    
    # OAuth2 token endpoint
    token_url = 'https://login.salesforce.com/services/oauth2/token'
    
    # Request parameters
    params = {
        'grant_type': 'password',
        'client_id': client_id,
        'client_secret': client_secret,
        'username': username,
        'password': password
    }
    
    # POST request to get token
    response = requests.post(token_url, data=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Authentication error: {response.status_code}")
        print(response.text)
        return None

def to_half_width(text):
    """Convert full-width characters to half-width"""
    return unicodedata.normalize('NFKC', text)


            return []
    
    print(f"Could not read CSV file. Encoding might not be supported: {file_path}")
    return []

def search_company(auth_info, company_name, search_mode="partial"):
    """Search for company information (partial or exact match)"""
    if not auth_info:
        return False, []
    
    # Convert full-width to half-width characters
    company_name = to_half_width(company_name)
    
    # Get instance URL and access token
    instance_url = auth_info['instance_url']
    access_token = auth_info['access_token']
    
    # API endpoint
    api_url = f"{instance_url}/services/data/v60.0/query/"
    
    # SOQL query - get company info and needed fields
    # Change condition based on search mode
    if search_mode == "exact":
        where_clause = f"WHERE Name = '{company_name}'"
    else:
        where_clause = f"WHERE Name LIKE '%{company_name}%'"
    
    # Specify fields (using standard fields only)
    query = (
        "SELECT Id, Name, "
        "BillingStreet, BillingCity, BillingState, BillingPostalCode, BillingCountry, "
        "Phone, Website, Description, Industry, NumberOfEmployees "
        "FROM Account "
        f"{where_clause}"
    )
    
    # Request headers
    headers = {
        'Authorization': f"Bearer {access_token}",
        'Content-Type': 'application/json'
    }
    
    # GET request to fetch data
    try:
        response = requests.get(api_url, headers=headers, params={'q': query})
        
        if response.status_code == 200:
            results = response.json()['records']
            return len(results) > 0, results
        else:
            print(f"API call error: {response.status_code}")
            print(response.text)
            return False, []
    except Exception as e:
        print(f"Error: {e}")
        return False, []

def get_contacts(auth_info, account_id):
    """Get contacts related to an account"""
    if not auth_info:
        return []
    
    # Get instance URL and access token
    instance_url = auth_info['instance_url']
    access_token = auth_info['access_token']
    
    # API endpoint
    api_url = f"{instance_url}/services/data/v60.0/query/"
    
    # SOQL query for contacts
    query = (
        "SELECT Id, Name, Title, Email, Phone, Department "
        "FROM Contact "
        f"WHERE AccountId = '{account_id}'"
    )
    
    # Request headers
    headers = {
        'Authorization': f"Bearer {access_token}",
        'Content-Type': 'application/json'
    }
    
    # GET request to fetch data
    try:
        response = requests.get(api_url, headers=headers, params={'q': query})
        
        if response.status_code == 200:
            results = response.json()['records']
            return results
        else:
            print(f"Contact API call error: {response.status_code}")
            print(response.text)
            return []
    except Exception as e:
        print(f"Contact info retrieval error: {e}")
        return []

def format_address(account):
    """Format address information"""
    address_parts = []
    
    # Add address components if they exist
    if account.get('BillingPostalCode'):
        address_parts.append(account['BillingPostalCode'])
    
    if account.get('BillingCountry'):
        address_parts.append(account['BillingCountry'])
        
    if account.get('BillingState'):
        address_parts.append(account['BillingState'])
        
    if account.get('BillingCity'):
        address_parts.append(account['BillingCity'])
        
    if account.get('BillingStreet'):
        address_parts.append(account['BillingStreet'])
    
    # Join address components
    return " ".join(address_parts) if address_parts else "No address available"

def display_results(auth_info, results, company_name=""):
    """Display search results"""
    total_accounts = len(results)
    
    # List to store all company data
    all_company_data = []
    
    if company_name:
        print(f"\nSearch results for company name \"{company_name}\":")
    print(f"Number of accounts found: {total_accounts}")
    
    if total_accounts > 0:
        for i, account in enumerate(results, 1):
            print(f"\n===== Account {i} =====")
            print(f"Account ID: {account['Id']}")
            print(f"Company Name: {account['Name']}")
            print(f"Address: {format_address(account)}")
            
            if account.get('Phone'):
                print(f"Phone: {account['Phone']}")
            
            if account.get('Website'):
                print(f"Website: {account.get('Website')}")
                
            if account.get('Industry'):
                print(f"Industry: {account.get('Industry')}")
                
            if account.get('NumberOfEmployees'):
                print(f"Number of Employees: {account.get('NumberOfEmployees')}")
                
            if account.get('Description'):
                print(f"Description: {account.get('Description')}")
            
            # Get related contacts
            contacts = get_contacts(auth_info, account['Id'])
            
            # Store account data
            account_data = {
                'SearchKeyword': company_name,
                'SFStatus': 'Found in Salesforce',
                'AccountId': account['Id'],
                'AccountName': account['Name'],
                'AccountAddress': format_address(account),
                'AccountPhone': account.get('Phone', ''),
                'Website': account.get('Website', ''),
                'Industry': account.get('Industry', ''),
                'NumberOfEmployees': account.get('NumberOfEmployees', ''),
                'Description': account.get('Description', '')
            }
            
            # If no contacts, still add the account data
            if not contacts:
                print("\n  No related contacts found.")
                all_company_data.append(account_data)
            else:
                print(f"\n  === Related Contacts ({len(contacts)} found) ===")
                
                for j, contact in enumerate(contacts, 1):
                    print(f"\n  --- Contact {j} ---")
                    print(f"  Contact ID: {contact['Id']}")
                    print(f"  Name: {contact.get('Name', 'N/A')}")
                    print(f"  Title: {contact.get('Title', 'N/A')}")
                    print(f"  Email: {contact.get('Email', 'N/A')}")
                    print(f"  Phone: {contact.get('Phone', 'N/A')}")
                    print(f"  Department: {contact.get('Department', 'N/A')}")
                    
                    # Create a copy of account data with contact info
                    contact_data = account_data.copy()
                    contact_data.update({
                        'ContactId': contact['Id'],
                        'ContactName': contact.get('Name', ''),
                        'ContactTitle': contact.get('Title', ''),
                        'ContactEmail': contact.get('Email', ''),
                        'ContactPhone': contact.get('Phone', ''),
                        'ContactDepartment': contact.get('Department', '')
                    })
                    all_company_data.append(contact_data)
    else:
        print("No company information found.")
        # Add dummy data for not found companies
        if company_name:
            not_found_data = {
                'SearchKeyword': company_name,
                'SFStatus': 'Not found in Salesforce',
                'AccountId': 'Not in Salesforce',
                'AccountName': '',
                'AccountAddress': '',
                'AccountPhone': '',
                'Website': '',
                'Industry': '',
                'NumberOfEmployees': '',
                'Description': ''
            }
            all_company_data.append(not_found_data)
    
    return all_company_data

def export_to_csv(all_results, all_company_data):
    """Export search results to CSV file"""
    # Skip if no results
    if not any(results for _, results in all_results) and not all_company_data:
        print("No data to export.")
        return
    
    # Get current timestamp for filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. Export account information to CSV
    account_filename = f"salesforce_companies_{timestamp}.csv"
    
    try:
        with open(account_filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
            # Define CSV header
            fieldnames = [
                'Search Keyword', 'Salesforce ID', 'Company Name', 
                'Postal Code', 'Full Address', 'Phone', 'Website', 
                'Industry', 'Number of Employees', 'Description'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            # Write information for each search result
            for idx, (company_name, results) in enumerate(all_results):
                if not results:
                    # Add empty row for companies not found
                    writer.writerow({
                        'Search Keyword': company_name,
                        'Salesforce ID': 'Not in Salesforce',
                        'Company Name': '',
                        'Postal Code': '',
                        'Full Address': '',
                        'Phone': '',
                        'Website': '',
                        'Industry': '',
                        'Number of Employees': '',
                        'Description': ''
                    })
                else:
                    # Add data for each account found
                    for account in results:
                        # Get postal code
                        postal_code = account.get('BillingPostalCode', '')
                        
                        # Format address
                        address_parts = []
                        if account.get('BillingCountry'):
                            address_parts.append(account['BillingCountry'])
                        if account.get('BillingState'):
                            address_parts.append(account['BillingState'])
                        if account.get('BillingCity'):
                            address_parts.append(account['BillingCity'])
                        if account.get('BillingStreet'):
                            address_parts.append(account['BillingStreet'])
                        address = " ".join(address_parts) if address_parts else ""
                        
                        # Write to CSV
                        writer.writerow({
                            'Search Keyword': company_name,
                            'Salesforce ID': account['Id'],
                            'Company Name': account.get('Name', ''),
                            'Postal Code': postal_code,
                            'Full Address': address,
                            'Phone': account.get('Phone', ''),
                            'Website': account.get('Website', ''),
                            'Industry': account.get('Industry', ''),
                            'Number of Employees': account.get('NumberOfEmployees', ''),
                            'Description': account.get('Description', '')
                        })
            
        print(f"\nExported company information to CSV file: {account_filename}")
        
        # 2. Export contact information to CSV
        # Only output if we have contact data
        if any('ContactId' in data for data in all_company_data):
            contact_filename = f"salesforce_contacts_{timestamp}.csv"
            
            with open(contact_filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
                # Define CSV header with both account and contact fields
                fieldnames = [
                    'Search Keyword', 'Salesforce Status',
                    'Account ID', 'Company Name', 'Company Address', 'Company Phone', 
                    'Website', 'Industry', 'Number of Employees', 'Description',
                    'Contact ID', 'Contact Name', 'Title', 'Contact Email', 
                    'Contact Phone', 'Department'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                # Write each contact record
                for data in all_company_data:
                    row_data = {
                        'Search Keyword': data.get('SearchKeyword', ''),
                        'Salesforce Status': data.get('SFStatus', ''),
                        'Account ID': data.get('AccountId', ''),
                        'Company Name': data.get('AccountName', ''),
                        'Company Address': data.get('AccountAddress', ''),
                        'Company Phone': data.get('AccountPhone', ''),
                        'Website': data.get('Website', ''),
                        'Industry': data.get('Industry', ''),
                        'Number of Employees': data.get('NumberOfEmployees', ''),
                        'Description': data.get('Description', ''),
                        'Contact ID': data.get('ContactId', ''),
                        'Contact Name': data.get('ContactName', ''),
                        'Title': data.get('ContactTitle', ''),
                        'Contact Email': data.get('ContactEmail', ''),
                        'Contact Phone': data.get('ContactPhone', ''),
                        'Department': data.get('ContactDepartment', '')
                    }
                    writer.writerow(row_data)
                
            print(f"Exported contact information to CSV file: {contact_filename}")
    except Exception as e:
        print(f"Error exporting to CSV: {e}")

def load_config():
    """Load configuration from config file or environment variables"""
    # First try to load from .env file
    load_dotenv()
    
    # Check environment variables first
    username = os.environ.get('SALESFORCE_USERNAME')
    password = os.environ.get('SALESFORCE_PASSWORD')
    client_id = os.environ.get('SALESFORCE_CLIENT_ID')
    client_secret = os.environ.get('SALESFORCE_CLIENT_SECRET')
    
    # If any of the credentials are missing, try config file
    if not all([username, password, client_id, client_secret]):
        config = configparser.ConfigParser()
        config_path = Path('config.ini')
        
        if config_path.exists():
            config.read(config_path)
            if 'Salesforce' in config:
                sf_config = config['Salesforce']
                username = username or sf_config.get('username')
                password = password or sf_config.get('password')
                client_id = client_id or sf_config.get('client_id')
                client_secret = client_secret or sf_config.get('client_secret')
    
    # If still missing credentials, prompt user
    if not username:
        username = input("Enter Salesforce username: ").strip()
    
    if not password:
        import getpass
        password = getpass.getpass("Enter Salesforce password: ").strip()
    
    if not client_id:
        client_id = input("Enter Salesforce client ID: ").strip()
    
    if not client_secret:
        client_secret = input("Enter Salesforce client secret: ").strip()
    
    return {
        'username': username,
        'password': password,
        'client_id': client_id,
        'client_secret': client_secret
    }

def main():
    """Main function"""
    # Set default language to English
    language = os.environ.get('LANG', 'en').lower()
    japanese = language.startswith('ja') or 'japanese' in language
    
    # Messages in both languages
    messages = {
        'title': {
            'en': "Salesforce Company Search Tool",
            'ja': "Salesforce 企業検索ツール"
        },
        'connecting': {
            'en': "Connecting to Salesforce...",
            'ja': "Salesforceに接続しています..."
        },
        'auth_success': {
            'en': "Authentication successful!",
            'ja': "認証成功！"
        },
        'instance_url': {
            'en': "Instance URL",
            'ja': "インスタンスURL"
        },
        'select_search_mode': {
            'en': "Select search mode:",
            'ja': "検索モードを選択してください:"
        },
        'partial_match': {
            'en': "Partial match (company name contains search term)",
            'ja': "部分一致（会社名に検索語が含まれる）"
        },
        'exact_match': {
            'en': "Exact match (company name equals search term)",
            'ja': "完全一致（会社名が検索語と一致する）"
        },
        'select_prompt': {
            'en': "Select (1 or 2)",
            'ja': "選択してください (1 または 2)"
        },
        'invalid_selection': {
            'en': "Invalid selection. Please select 1 or 2.",
            'ja': "無効な選択です。1または2を選択してください。"
        },
        'select_input_method': {
            'en': "Select company name input method:",
            'ja': "会社名の入力方法を選択してください:"
        },
        'direct_input': {
            'en': "Direct input (comma-separated for multiple names)",
            'ja': "直接入力（複数の名前はカンマ区切り）"
        },
        'load_csv': {
            'en': "Load from CSV file",
            'ja': "CSVファイルから読み込む"
        },
        'enter_company_names': {
            'en': "Enter company name(s) to search (separate multiple names with commas):",
            'ja': "検索する会社名を入力してください（複数の場合はカンマで区切る）:"
        },
        'company_names_prompt': {
            'en': "Company name(s)",
            'ja': "会社名"
        },
        'enter_csv_path': {
            'en': "Enter the path to your CSV file (e.g., C:\\Users\\username\\companies.csv):",
            'ja': "CSVファイルのパスを入力してください（例：C:\\Users\\username\\companies.csv）:"
        },
        'file_path_prompt': {
            'en': "File path",
            'ja': "ファイルパス"
        },
        'file_not_found': {
            'en': "File not found",
            'ja': "ファイルが見つかりません"
        },
        'no_valid_names': {
            'en': "No valid company names entered.",
            'ja': "有効な会社名が入力されていません。"
        },
        'searching_for': {
            'en': "Searching for company",
            'ja': "会社を検索中"
        },
        'export_to_csv': {
            'en': "Export results to CSV file? (y/n)",
            'ja': "結果をCSVファイルにエクスポートしますか？ (y/n)"
        },
        'no_results': {
            'en': "No results found for any company name.",
            'ja': "どの会社名でも結果が見つかりませんでした。"
        },
        'auth_failed': {
            'en': "Authentication failed. Please check your credentials.",
            'ja': "認証に失敗しました。認証情報を確認してください。"
        }
    }
    
    # Helper function to get message in correct language
    def msg(key):
        lang = 'ja' if japanese else 'en'
        return messages[key][lang]
    
    print(msg('title'))
    print("-" * len(msg('title')))
    
    # Load configuration
    config = load_config()
    
    print(f"\n{msg('connecting')}")
    auth_info = get_salesforce_oauth_token(
        config['username'], 
        config['password'], 
        config['client_id'], 
        config['client_secret']
    )
    
    if auth_info:
        print(f"{msg('auth_success')}")
        print(f"{msg('instance_url')}: {auth_info['instance_url']}")
        
        # Choose search mode
        print(f"\n{msg('select_search_mode')}")
        print(f"1: {msg('partial_match')}")
        print(f"2: {msg('exact_match')}")
        search_mode = input(f"{msg('select_prompt')}: ").strip()
        
        if search_mode not in ["1", "2"]:
            print(f"{msg('invalid_selection')}")
            return
        
        search_mode_value = "partial" if search_mode == "1" else "exact"
        
        # Choose input method
        print(f"\n{msg('select_input_method')}")
        print(f"1: {msg('direct_input')}")
        print(f"2: {msg('load_csv')}")
        input_method = input(f"{msg('select_prompt')}: ").strip()
        
        company_names = []
        
        if input_method == "1":
            # Direct input
            print(f"\n{msg('enter_company_names')}")
            company_names_input = input(f"{msg('company_names_prompt')}: ").strip()
            
            # Split comma-separated company names and remove whitespace
            company_names = [name.strip() for name in company_names_input.split(',') if name.strip()]
        
        elif input_method == "2":
            # Load from CSV file
            print(f"\n{msg('enter_csv_path')}")
            csv_path = input(f"{msg('file_path_prompt')}: ").strip()
            
            # Remove quotes from path (in case user copy-pasted with quotes)
            csv_path = csv_path.strip('"\'')
            
            if not os.path.exists(csv_path):
                print(f"{msg('file_not_found')}: {csv_path}")
                return
            
            company_names = read_company_names_from_csv(csv_path)
        
        else:
            print(f"{msg('invalid_selection')}")
            return
        
        if not company_names:
            print(f"{msg('no_valid_names')}")
            return
        
        # Lists to store search results and company data
        all_results = []
        all_company_data = []
        
        # Search for each company name
        for company_name in company_names:
            print(f"\n{msg('searching_for')} \"{company_name}\"...")
            exists, results = search_company(auth_info, company_name, search_mode_value)
            
            # Display results and get company data
            company_data = display_results(auth_info, results, company_name)
            all_company_data.extend(company_data)
            
            # Store search results
            all_results.append((company_name, results))
        
        # Ask to export results to CSV
        if any(results for _, results in all_results) or len(all_results) > 0:
            export_choice = input(f"\n{msg('export_to_csv')}: ").strip().lower()
            if export_choice == 'y':
                export_to_csv(all_results, all_company_data)
        else:
            print(f"\n{msg('no_results')}")
    else:
        print(f"{msg('auth_failed')}")

if __name__ == "__main__":
    main()