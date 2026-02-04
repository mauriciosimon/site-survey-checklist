import os
import requests
import logging

logger = logging.getLogger(__name__)

MONDAY_API_URL = "https://api.monday.com/v2"
MONDAY_API_TOKEN = os.getenv("MONDAY_API_TOKEN")

# Site Surveys board configuration (MVP Template workspace)
SITE_SURVEYS_BOARD_ID = "5090310184"
SITE_SURVEYS_COLUMNS = {
    "status": "status",
    "date": "date4",
    "link": "link_mkzqat3",
    "person": "person",
    "created_by": "text_mm08xxxv"  # Text field for surveyor name
}


def create_site_survey_item(
    name: str,
    survey_url: str,
    survey_date: str = None,
    status: str = "Working on it",
    created_by: str = None
) -> dict:
    """
    Create a new item in the Monday.com Site Surveys board.

    Args:
        name: The survey name (will be the item name in Monday.com)
        survey_url: The URL to the survey in our app
        survey_date: Optional date in YYYY-MM-DD format
        status: Status label (Working on it, Done, Stuck)
        created_by: Name of the user who created the survey

    Returns:
        dict with 'success' boolean and 'item_id' or 'error'
    """
    if not MONDAY_API_TOKEN:
        logger.warning("MONDAY_API_TOKEN not configured, skipping Monday.com sync")
        return {"success": False, "error": "Monday.com API token not configured"}

    # Build column values
    column_values = {}

    # Status column
    status_index = {"Working on it": 0, "Done": 1, "Stuck": 2}.get(status, 0)
    column_values[SITE_SURVEYS_COLUMNS["status"]] = {"index": status_index}

    # Date column
    if survey_date:
        column_values[SITE_SURVEYS_COLUMNS["date"]] = {"date": survey_date}

    # Link column
    column_values[SITE_SURVEYS_COLUMNS["link"]] = {
        "url": survey_url,
        "text": "View Survey"
    }

    # Created By column (surveyor name)
    if created_by:
        column_values[SITE_SURVEYS_COLUMNS["created_by"]] = created_by

    # Build GraphQL mutation
    import json
    column_values_json = json.dumps(json.dumps(column_values))

    # Escape quotes in name for GraphQL
    escaped_name = name.replace('"', '\\"')

    query = f'''
    mutation {{
        create_item (
            board_id: {SITE_SURVEYS_BOARD_ID},
            item_name: "{escaped_name}",
            column_values: {column_values_json}
        ) {{
            id
        }}
    }}
    '''

    headers = {
        "Authorization": MONDAY_API_TOKEN,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            MONDAY_API_URL,
            json={"query": query},
            headers=headers,
            timeout=10
        )
        response.raise_for_status()

        data = response.json()

        if "errors" in data:
            logger.error(f"Monday.com API error: {data['errors']}")
            return {"success": False, "error": str(data["errors"])}

        item_id = data.get("data", {}).get("create_item", {}).get("id")
        if item_id:
            logger.info(f"Created Monday.com item {item_id} for survey: {name}")
            return {"success": True, "item_id": item_id}
        else:
            return {"success": False, "error": "No item ID returned"}

    except requests.RequestException as e:
        logger.error(f"Monday.com API request failed: {e}")
        return {"success": False, "error": str(e)}


def update_site_survey_item(
    item_id: str,
    name: str = None,
    survey_url: str = None,
    survey_date: str = None,
    status: str = None
) -> dict:
    """
    Update an existing item in the Monday.com Site Surveys board.

    Args:
        item_id: The Monday.com item ID
        name: Optional new name
        survey_url: Optional new URL
        survey_date: Optional date in YYYY-MM-DD format
        status: Optional status label

    Returns:
        dict with 'success' boolean and 'error' if failed
    """
    if not MONDAY_API_TOKEN:
        logger.warning("MONDAY_API_TOKEN not configured, skipping Monday.com sync")
        return {"success": False, "error": "Monday.com API token not configured"}

    # Build column values for fields that are provided
    column_values = {}

    if status:
        status_index = {"Working on it": 0, "Done": 1, "Stuck": 2}.get(status, 0)
        column_values[SITE_SURVEYS_COLUMNS["status"]] = {"index": status_index}

    if survey_date:
        column_values[SITE_SURVEYS_COLUMNS["date"]] = {"date": survey_date}

    if survey_url:
        column_values[SITE_SURVEYS_COLUMNS["link"]] = {
            "url": survey_url,
            "text": "View Survey"
        }

    import json
    column_values_json = json.dumps(json.dumps(column_values))

    # Build mutation - update name and/or columns
    mutations = []

    if name:
        escaped_name = name.replace('"', '\\"')
        mutations.append(f'''
        change_simple_column_value(
            board_id: {SITE_SURVEYS_BOARD_ID},
            item_id: {item_id},
            column_id: "name",
            value: "{escaped_name}"
        ) {{
            id
        }}
        ''')

    if column_values:
        mutations.append(f'''
        change_multiple_column_values(
            board_id: {SITE_SURVEYS_BOARD_ID},
            item_id: {item_id},
            column_values: {column_values_json}
        ) {{
            id
        }}
        ''')

    if not mutations:
        return {"success": True}  # Nothing to update

    query = f"mutation {{ {' '.join(mutations)} }}"

    headers = {
        "Authorization": MONDAY_API_TOKEN,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            MONDAY_API_URL,
            json={"query": query},
            headers=headers,
            timeout=10
        )
        response.raise_for_status()

        data = response.json()

        if "errors" in data:
            logger.error(f"Monday.com API error: {data['errors']}")
            return {"success": False, "error": str(data["errors"])}

        logger.info(f"Updated Monday.com item {item_id}")
        return {"success": True}

    except requests.RequestException as e:
        logger.error(f"Monday.com API request failed: {e}")
        return {"success": False, "error": str(e)}
