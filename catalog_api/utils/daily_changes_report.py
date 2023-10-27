import datetime
from datetime import date

from catalog_api.database import database


async def get_daily_changes(date: str):
    query = f"SELECT * FROM audit_log WHERE DATE(timestamp) = '{date}'"
    daily_changes = await database.fetch_all(query)

    if not daily_changes:
        return {}

    changes_formatted = {"added": [], "updated": [], "deleted": []}

    for entry in daily_changes:
        action = entry.action.lower()
        if action == "added":
            changes_formatted["added"].append(dict(entry))
        elif action == "updated":
            changes_formatted["updated"].append(dict(entry))
        elif action == "deleted":
            changes_formatted["deleted"].append(dict(entry))

    return changes_formatted


def construct_email_body(changes):
    body = (
        f"Hello Admin,\n\nHere's a summary of product changes for {date.today()}:\n\n"
    )

    total_changes = sum(len(v) for v in changes.values())
    body += f"**Total Changes:** {total_changes}\n\n---\n\n"

    if changes["added"]:
        body += "**New Products Added:**\n"
        for change in changes["added"]:
            body += f"- Product ID: {change['product_id']} - Added data: {change['new_data']} - Added by User: {change['changed_by']}\n"
        body += "---\n\n"

    if changes["updated"]:
        body += "**Products Updated:**\n"
        for change in changes["updated"]:
            body += f"- Product ID: {change['product_id']} - Previous data: {change['previous_data']} > New data: {change['new_data']} - Updated by User: {change['changed_by']}\n"
        body += "---\n\n"

    if changes["deleted"]:
        body += "**Products Deleted:**\n"
        for change in changes["deleted"]:
            body += f"- Product ID: {change['product_id']} - Deleted data: {change['previous_data']} - Deleted by User: {change['changed_by']}\n"
        body += "---\n\n"

    body += "Best regards,\nZ Brands"
    return body


async def return_text_for_mail():
    current_date = datetime.date.today()
    formatted_date = current_date.strftime("%Y-%m-%d")
    changes = await get_daily_changes(formatted_date)
    if changes:
        email_body = construct_email_body(changes)
        return email_body
