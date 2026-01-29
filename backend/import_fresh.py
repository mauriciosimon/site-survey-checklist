#!/usr/bin/env python3
"""Import Monday.com data to Kill Monday production"""

import json
import requests
import sys
from pathlib import Path

# Configuration  
MONDAY_EXTRACTION_PATH = Path('/tmp/monday-extraction/monday-extraction')
API_BASE_URL = 'https://api-production-2414.up.railway.app'
ADMIN_EMAIL = 'import@killmonday.app'
ADMIN_PASSWORD = 'import123'


def get_auth_token():
    """Login and get auth token"""
    response = requests.post(
        f'{API_BASE_URL}/auth/login',
        json={'email': ADMIN_EMAIL, 'password': ADMIN_PASSWORD}
    )
    if response.status_code != 200:
        print(f'Login failed: {response.text}')
        sys.exit(1)
    return response.json()['access_token']


def load_items(filename):
    """Load items from Monday.com export file"""
    filepath = MONDAY_EXTRACTION_PATH / filename
    with open(filepath) as f:
        data = json.load(f)
    
    # Handle structure: data.boards[0].items_page.items
    if 'data' in data:
        boards = data['data'].get('boards', [])
        if boards:
            return boards[0].get('items_page', {}).get('items', [])
    
    # Or direct items array
    if 'items' in data:
        return data['items']
    
    return []


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
    return date_str[:10] if len(date_str) >= 10 else None


def import_leads(token):
    """Import leads"""
    items = load_items('satoris-leads.json')
    print(f'Found {len(items)} leads')

    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    imported, skipped = 0, 0

    for item in items:
        lead = {
            'name': item.get('name', 'Unknown Lead'),
            'status': get_column_value(item, 'lead_status') or 'New Lead',
            'priority': get_column_value(item, 'priority') or None,
            'source': get_column_value(item, 'status') or None,
            'owner_name': get_column_value(item, 'lead_owner') or None,
            'contact_name': get_column_value(item, 'lead_company') or None,
            'job_title': get_column_value(item, 'text') or None,
            'email': get_column_value(item, 'lead_email') or None,
            'phone': get_column_value(item, 'lead_phone') or None,
            'next_interaction_date': parse_date(get_column_value(item, 'date')),
            'monday_item_id': item.get('id'),
        }
        lead = {k: v for k, v in lead.items() if v is not None}

        response = requests.post(f'{API_BASE_URL}/leads', headers=headers, json=lead)
        if response.status_code in (200, 201):
            imported += 1
        elif 'already exists' in response.text.lower() or 'duplicate' in response.text.lower():
            skipped += 1
        else:
            if imported + skipped < 3:
                print(f'  Failed: {lead.get("name")}: {response.text[:100]}')

    print(f'Leads: {imported} imported, {skipped} skipped')
    return imported


def import_deals(token):
    """Import deals"""
    items = load_items('satoris-deals.json')
    print(f'Found {len(items)} deals')

    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    imported, skipped = 0, 0

    for item in items:
        group_title = item.get('group', {}).get('title', 'Prospects')
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
            'contact_name': get_column_value(item, 'text0') or None,
            'deal_type': get_column_value(item, 'dropdown_mkxsyxw3') or None,
            'value': value,
            'close_date': parse_date(get_column_value(item, 'deal_close_date')),
            'monday_item_id': item.get('id'),
        }
        deal = {k: v for k, v in deal.items() if v is not None}

        response = requests.post(f'{API_BASE_URL}/deals', headers=headers, json=deal)
        if response.status_code in (200, 201):
            imported += 1
        elif 'already exists' in response.text.lower() or 'duplicate' in response.text.lower():
            skipped += 1

    print(f'Deals: {imported} imported, {skipped} skipped')
    return imported


def import_accounts(token):
    """Import accounts"""
    items = load_items('satoris-accounts.json')
    print(f'Found {len(items)} accounts')

    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    imported, skipped = 0, 0

    for item in items:
        group_title = item.get('group', {}).get('title', 'Prospect')
        account = {
            'name': item.get('name', 'Unknown Account'),
            'status': group_title if group_title in ['Qualified', 'Active', 'Inactive', 'Prospect'] else 'Prospect',
            'label': get_column_value(item, 'color_mkvcf1b0') or None,
            'industry': get_column_value(item, 'industry') or None,
            'employee_count': get_column_value(item, 'employee_count') or None,
            'website': get_column_value(item, 'company_domain') or None,
            'company_profile_url': get_column_value(item, 'company_profile') or None,
            'address': get_column_value(item, 'location') or None,
            'notes': get_column_value(item, 'text_mkzj6z1z') or None,
            'monday_item_id': item.get('id'),
        }
        account = {k: v for k, v in account.items() if v is not None}

        response = requests.post(f'{API_BASE_URL}/accounts', headers=headers, json=account)
        if response.status_code in (200, 201):
            imported += 1
            if imported % 100 == 0:
                print(f'  {imported} accounts...', flush=True)
        elif 'already exists' in response.text.lower() or 'duplicate' in response.text.lower():
            skipped += 1

    print(f'Accounts: {imported} imported, {skipped} skipped')
    return imported


def import_contacts(token):
    """Import contacts"""
    items = load_items('satoris-contacts.json')
    print(f'Found {len(items)} contacts')

    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    imported, skipped = 0, 0

    for item in items:
        contact = {
            'name': item.get('name', 'Unknown Contact'),
            'company': get_column_value(item, 'text') or None,
            'contact_type': get_column_value(item, 'status') or None,
            'job_title': get_column_value(item, 'text_mkzj9zfp') or None,
            'tier': get_column_value(item, 'text_mkzj1q6x') or None,
            'email': get_column_value(item, 'contact_email') or None,
            'phone': get_column_value(item, 'contact_phone') or None,
            'linkedin_url': get_column_value(item, 'linkedin__1') or None,
            'location': get_column_value(item, 'location__1') or None,
            'source': get_column_value(item, 'color_mkveb8kg') or None,
            'owner_name': get_column_value(item, 'people') or None,
            'icp_fit': get_column_value(item, 'color_mkzj6yzf') or None,
            'about': get_column_value(item, 'about__1') or None,
            'monday_item_id': item.get('id'),
        }
        contact = {k: v for k, v in contact.items() if v is not None}

        response = requests.post(f'{API_BASE_URL}/contacts', headers=headers, json=contact)
        if response.status_code in (200, 201):
            imported += 1
            if imported % 100 == 0:
                print(f'  {imported} contacts...', flush=True)
        elif 'already exists' in response.text.lower() or 'duplicate' in response.text.lower():
            skipped += 1

    print(f'Contacts: {imported} imported, {skipped} skipped')
    return imported


def main():
    print('='*50)
    print('Kill Monday - Data Import')
    print('='*50, flush=True)

    print('\nLogging in...', flush=True)
    token = get_auth_token()
    print('✓ Logged in', flush=True)

    print('\n--- Importing Leads ---', flush=True)
    import_leads(token)

    print('\n--- Importing Deals ---', flush=True)
    import_deals(token)

    print('\n--- Importing Accounts ---', flush=True)
    import_accounts(token)

    print('\n--- Importing Contacts ---', flush=True)
    import_contacts(token)

    print('\n' + '='*50)
    print('Import complete!')
    print('='*50, flush=True)


if __name__ == '__main__':
    main()
