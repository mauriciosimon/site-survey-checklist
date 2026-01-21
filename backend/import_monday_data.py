#!/usr/bin/env python3
"""
Import Monday.com data to Staging API
Reads JSON exports from Monday.com and imports to the site-checklist staging API
"""

import json
import requests
import sys
from pathlib import Path

# Configuration
MONDAY_EXTRACTION_PATH = Path('/Users/mauricio/Desktop/monday-extraction')
API_BASE_URL = 'https://api-staging-staging-f5ab.up.railway.app'
ADMIN_EMAIL = 'admin@test.com'
ADMIN_PASSWORD = 'admin123'


def get_auth_token():
    """Login and get auth token"""
    # Login expects JSON body with email/password
    response = requests.post(
        f'{API_BASE_URL}/auth/login',
        json={'email': ADMIN_EMAIL, 'password': ADMIN_PASSWORD}
    )
    if response.status_code != 200:
        print(f'Login failed: {response.text}')
        sys.exit(1)
    return response.json()['access_token']


def get_column_value(item, column_id):
    """Get text value from column_values by column id"""
    for cv in item.get('column_values', []):
        if cv.get('id') == column_id:
            return cv.get('text') or ''
    return ''


def parse_date(date_str):
    """Parse date string to API format (YYYY-MM-DD)"""
    if not date_str:
        return None
    # Handle formats like "2025-06-30" or with times
    return date_str[:10] if len(date_str) >= 10 else None


def import_leads(token):
    """Import leads from satoris-leads.json"""
    filepath = MONDAY_EXTRACTION_PATH / 'satoris-leads.json'
    if not filepath.exists():
        print('No leads file found')
        return 0

    with open(filepath) as f:
        data = json.load(f)

    items = data.get('data', {}).get('boards', [{}])[0].get('items_page', {}).get('items', [])
    print(f'Found {len(items)} leads to import')

    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    imported = 0

    for item in items:
        lead = {
            'name': item.get('name', 'Unknown Lead'),
            'status': get_column_value(item, 'lead_status') or 'New Lead',
            'priority': get_column_value(item, 'priority') or None,
            'source': get_column_value(item, 'status') or None,  # status column is actually source
            'owner_name': get_column_value(item, 'lead_owner') or None,
            'contact_name': get_column_value(item, 'lead_company') or None,  # lead_company is contact name
            'job_title': get_column_value(item, 'text') or None,  # text is title/job
            'email': get_column_value(item, 'lead_email') or None,
            'phone': get_column_value(item, 'lead_phone') or None,
            'next_interaction_date': parse_date(get_column_value(item, 'date')),
            'qualified_date': parse_date(get_column_value(item, 'date4')),  # date4 is close date
            'monday_item_id': item.get('id'),
        }
        # Remove None values
        lead = {k: v for k, v in lead.items() if v is not None}

        response = requests.post(f'{API_BASE_URL}/leads', headers=headers, json=lead)
        if response.status_code in (200, 201):
            imported += 1
        else:
            print(f'  Failed to import lead "{lead.get("name")}": {response.text}')

    print(f'Imported {imported}/{len(items)} leads')
    return imported


def import_deals(token):
    """Import deals from satoris-deals.json"""
    filepath = MONDAY_EXTRACTION_PATH / 'satoris-deals.json'
    if not filepath.exists():
        print('No deals file found')
        return 0

    with open(filepath) as f:
        data = json.load(f)

    items = data.get('data', {}).get('boards', [{}])[0].get('items_page', {}).get('items', [])
    print(f'Found {len(items)} deals to import')

    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    imported = 0

    for item in items:
        # Get group (stage) from item
        group_title = item.get('group', {}).get('title', 'Prospects')

        # Parse deal value
        value_str = get_column_value(item, 'deal_value')
        value = None
        if value_str:
            try:
                value = float(value_str.replace(',', '').replace('£', '').replace('$', '').strip())
            except:
                pass

        deal = {
            'name': item.get('name', 'Unknown Deal'),
            'stage': group_title,
            'status': get_column_value(item, 'deal_stage') or 'New deal',
            'owner_name': get_column_value(item, 'deal_owner') or None,
            'contact_name': get_column_value(item, 'text0') or None,  # text0 is contact name
            'deal_type': get_column_value(item, 'dropdown_mkxsyxw3') or None,
            'value': value,
            'next_interaction': parse_date(get_column_value(item, 'date')),
            'close_date': parse_date(get_column_value(item, 'deal_close_date')),
            'monday_item_id': item.get('id'),
        }
        # Remove None values
        deal = {k: v for k, v in deal.items() if v is not None}

        response = requests.post(f'{API_BASE_URL}/deals', headers=headers, json=deal)
        if response.status_code in (200, 201):
            imported += 1
        else:
            print(f'  Failed to import deal "{deal.get("name")}": {response.text}')

    print(f'Imported {imported}/{len(items)} deals')
    return imported


def import_accounts(token):
    """Import accounts from satoris-accounts.json"""
    filepath = MONDAY_EXTRACTION_PATH / 'satoris-accounts.json'
    if not filepath.exists():
        print('No accounts file found')
        return 0

    with open(filepath) as f:
        data = json.load(f)

    # Handle both formats: direct items list or nested in boards
    if 'items' in data:
        items = data.get('items', [])
    else:
        items = data.get('data', {}).get('boards', [{}])[0].get('items_page', {}).get('items', [])
    print(f'Found {len(items)} accounts to import')

    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    imported = 0

    for item in items:
        group_title = item.get('group', {}).get('title', 'Prospect')

        account = {
            'name': item.get('name', 'Unknown Account'),
            'status': group_title if group_title in ['Qualified', 'Active', 'Inactive', 'Prospect'] else 'Prospect',
            'label': get_column_value(item, 'color_mkvcf1b0') or None,  # Property Developer, etc.
            'industry': get_column_value(item, 'industry') or None,
            'employee_count': get_column_value(item, 'employee_count') or None,
            'website': get_column_value(item, 'company_domain') or None,
            'company_profile_url': get_column_value(item, 'company_profile') or None,
            'address': get_column_value(item, 'location') or None,
            'notes': get_column_value(item, 'text_mkzj6z1z') or None,
            'monday_item_id': item.get('id'),
        }
        # Remove None values
        account = {k: v for k, v in account.items() if v is not None}

        response = requests.post(f'{API_BASE_URL}/accounts', headers=headers, json=account)
        if response.status_code in (200, 201):
            imported += 1
            if imported % 100 == 0:
                print(f'  Progress: {imported} accounts imported...', flush=True)
        else:
            if 'already exists' not in response.text:
                if imported < 5:  # Only print first few errors
                    print(f'  Failed to import account "{account.get("name")}": {response.text}', flush=True)

    print(f'Imported {imported}/{len(items)} accounts', flush=True)
    return imported


def import_contacts(token):
    """Import contacts from satoris-contacts.json"""
    filepath = MONDAY_EXTRACTION_PATH / 'satoris-contacts.json'
    if not filepath.exists():
        print('No contacts file found')
        return 0

    with open(filepath) as f:
        data = json.load(f)

    # Handle both formats: direct items list or nested in boards
    if 'items' in data:
        items = data.get('items', [])
    else:
        items = data.get('data', {}).get('boards', [{}])[0].get('items_page', {}).get('items', [])
    print(f'Found {len(items)} contacts to import')

    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    imported = 0

    for item in items:
        contact = {
            'name': item.get('name', 'Unknown Contact'),
            'company': get_column_value(item, 'text') or None,  # Company name
            'contact_type': get_column_value(item, 'status') or None,  # Type: Architecture, Fit-Out, etc.
            'job_title': get_column_value(item, 'text_mkzj9zfp') or None,
            'tier': get_column_value(item, 'text_mkzj1q6x') or None,  # Tier 1, Tier 2, Tier 3
            'email': get_column_value(item, 'contact_email') or None,
            'phone': get_column_value(item, 'contact_phone') or None,
            'linkedin_url': get_column_value(item, 'linkedin__1') or None,
            'location': get_column_value(item, 'location__1') or None,
            'source': get_column_value(item, 'color_mkveb8kg') or None,
            'owner_name': get_column_value(item, 'people') or None,
            'icp_fit': get_column_value(item, 'color_mkzj6yzf') or None,  # Yes, Maybe, No
            'about': get_column_value(item, 'about__1') or None,
            'monday_item_id': item.get('id'),
        }
        # Remove None values
        contact = {k: v for k, v in contact.items() if v is not None}

        response = requests.post(f'{API_BASE_URL}/contacts', headers=headers, json=contact)
        if response.status_code in (200, 201):
            imported += 1
            if imported % 100 == 0:
                print(f'  Progress: {imported} contacts imported...', flush=True)
        else:
            if 'already exists' not in response.text:
                if imported < 5:  # Only print first few errors
                    print(f'  Failed to import contact "{contact.get("name")}": {response.text}', flush=True)

    print(f'Imported {imported}/{len(items)} contacts', flush=True)
    return imported


def clear_existing_data(token):
    """Clear existing test data before import"""
    headers = {'Authorization': f'Bearer {token}'}

    print('\nClearing existing data...')
    for entity in ['leads', 'deals', 'accounts', 'contacts', 'tasks']:
        try:
            response = requests.get(f'{API_BASE_URL}/{entity}?limit=1000', headers=headers)
            if response.status_code == 200:
                items = response.json().get('data', [])
                for item in items:
                    requests.delete(f'{API_BASE_URL}/{entity}/{item["id"]}', headers=headers)
                print(f'  Cleared {len(items)} {entity}')
        except Exception as e:
            print(f'  Error clearing {entity}: {e}')


def main():
    print('='*60)
    print('Monday.com Data Import to Staging')
    print('='*60)

    # Get auth token
    print('\nLogging in...')
    token = get_auth_token()
    print('Login successful!')

    # Skip clearing - data already exists
    # clear_existing_data(token)

    # Import all entities
    print('\n' + '='*60, flush=True)
    print('Importing data from Monday.com extracts...', flush=True)
    print('='*60, flush=True)

    # Skip leads/deals as they already exist (34 leads, 26 deals)
    print('\n--- Skipping Leads (already imported) ---', flush=True)
    # import_leads(token)

    print('\n--- Skipping Deals (already imported) ---', flush=True)
    # import_deals(token)

    print('\n--- Importing Accounts ---', flush=True)
    import_accounts(token)

    print('\n--- Importing Contacts ---', flush=True)
    import_contacts(token)

    print('\n' + '='*60)
    print('Import complete!')
    print('='*60)

    # Verify counts
    print('\nVerifying final counts...')
    headers = {'Authorization': f'Bearer {token}'}
    for entity in ['leads', 'deals', 'accounts', 'contacts', 'tasks']:
        try:
            response = requests.get(f'{API_BASE_URL}/{entity}?limit=1', headers=headers)
            total = response.json().get('total', 0)
            print(f'  {entity}: {total}')
        except Exception as e:
            print(f'  {entity}: Error - {e}')


if __name__ == '__main__':
    main()
