import os
import requests
import logging

logger = logging.getLogger(__name__)

MONDAY_API_URL = "https://api.monday.com/v2"

# Westley's Monday account (original)
MONDAY_API_TOKEN = os.getenv("MONDAY_API_TOKEN")
SITE_SURVEYS_BOARD_ID = "5090310184"
SITE_SURVEYS_COLUMNS = {
    "status": "status",
    "date": "date4",
    "link": "link_mkzqat3",
    "person": "person",
    "created_by": "text_mm08xxxv"  # Text field for surveyor name
}

# Westpark's Monday account (client)
WESTPARK_MONDAY_TOKEN = os.getenv("WESTPARK_MONDAY_TOKEN")
WESTPARK_BOARD_ID = "5091667006"
WESTPARK_COLUMNS = {
    "status": "color_mm0gb8b5",
    "date": "date_mm0gb28c",
    "link": "link_mm0gybba",
    "person": "multiple_person_mm0gzxfk",
    "created_by": "text_mm0gfqh"
}


def _create_item_on_board(
    token: str,
    board_id: str,
    columns: dict,
    name: str,
    survey_url: str,
    survey_date: str = None,
    status: str = "Working on it",
    created_by: str = None,
    board_label: str = "Monday.com"
) -> dict:
    """Helper to create an item on a specific board."""
    if not token:
        logger.warning(f"{board_label} token not configured, skipping")
        return {"success": False, "error": f"{board_label} token not configured"}

    # Build column values
    column_values = {}

    # Status column
    status_index = {"Working on it": 0, "Done": 1, "Stuck": 2}.get(status, 0)
    column_values[columns["status"]] = {"index": status_index}

    # Date column
    if survey_date:
        column_values[columns["date"]] = {"date": survey_date}

    # Link column
    column_values[columns["link"]] = {
        "url": survey_url,
        "text": "View Survey"
    }

    # Created By column (surveyor name)
    if created_by:
        column_values[columns["created_by"]] = created_by

    # Build GraphQL mutation
    import json
    column_values_json = json.dumps(json.dumps(column_values))

    # Escape quotes in name for GraphQL
    escaped_name = name.replace('"', '\\"')

    query = f'''
    mutation {{
        create_item (
            board_id: {board_id},
            item_name: "{escaped_name}",
            column_values: {column_values_json}
        ) {{
            id
        }}
    }}
    '''

    headers = {
        "Authorization": token,
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
            logger.error(f"{board_label} API error: {data['errors']}")
            return {"success": False, "error": str(data["errors"])}

        item_id = data.get("data", {}).get("create_item", {}).get("id")
        if item_id:
            logger.info(f"Created {board_label} item {item_id} for survey: {name}")
            return {"success": True, "item_id": item_id}
        else:
            return {"success": False, "error": "No item ID returned"}

    except requests.RequestException as e:
        logger.error(f"{board_label} API request failed: {e}")
        return {"success": False, "error": str(e)}


def create_site_survey_item(
    name: str,
    survey_url: str,
    survey_date: str = None,
    status: str = "Working on it",
    created_by: str = None
) -> dict:
    """
    Create a new item in BOTH Monday.com Site Surveys boards:
    1. Westley's board (original)
    2. Westpark's board (client)

    Args:
        name: The survey name (will be the item name in Monday.com)
        survey_url: The URL to the survey in our app
        survey_date: Optional date in YYYY-MM-DD format
        status: Status label (Working on it, Done, Stuck)
        created_by: Name of the user who created the survey

    Returns:
        dict with 'success' boolean, 'item_id' (Westley's), 'westpark_item_id', or 'error'
    """
    results = {"success": True, "errors": []}

    # Create in Westley's board
    westley_result = _create_item_on_board(
        token=MONDAY_API_TOKEN,
        board_id=SITE_SURVEYS_BOARD_ID,
        columns=SITE_SURVEYS_COLUMNS,
        name=name,
        survey_url=survey_url,
        survey_date=survey_date,
        status=status,
        created_by=created_by,
        board_label="Westley Monday"
    )
    if westley_result.get("success"):
        results["item_id"] = westley_result.get("item_id")
    else:
        results["errors"].append(f"Westley: {westley_result.get('error')}")

    # Create in Westpark's board
    westpark_result = _create_item_on_board(
        token=WESTPARK_MONDAY_TOKEN,
        board_id=WESTPARK_BOARD_ID,
        columns=WESTPARK_COLUMNS,
        name=name,
        survey_url=survey_url,
        survey_date=survey_date,
        status=status,
        created_by=created_by,
        board_label="Westpark Monday"
    )
    if westpark_result.get("success"):
        results["westpark_item_id"] = westpark_result.get("item_id")
    else:
        results["errors"].append(f"Westpark: {westpark_result.get('error')}")

    # Success if at least one board worked
    if not results.get("item_id") and not results.get("westpark_item_id"):
        results["success"] = False
        results["error"] = "; ".join(results["errors"])

    return results


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
