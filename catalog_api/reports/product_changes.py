from catalog_api.utils.daily_changes_report import return_text_for_mail
from catalog_api.utils.send_mails import send_email


async def send_daily_report():
    body_content = await return_text_for_mail()
    if body_content:
        await send_email(body_content)
        return {"detail": "Report sucessfully sent!"}
    else:
        return {"detail": "No changes were found, report skipped."}
