from __future__ import annotations

import smtplib
from email.mime.text import MIMEText

import requests

from backend.infra.config import SETTINGS


def send_pipeline_alert(pipeline_name: str, status: str, errors: list[str]) -> None:
    """
    Fire-and-forget alerting for pipeline incidents.
    Slack and email are both best-effort and should never crash ETL execution.
    """
    message = _build_message(pipeline_name, status, errors)
    _send_slack_alert(message)
    _send_email_alert(f"[PreStocks Infra] {pipeline_name} {status}", message)


def _build_message(pipeline_name: str, status: str, errors: list[str]) -> str:
    body = [
        f"Pipeline: {pipeline_name}",
        f"Status: {status}",
        "Errors:",
    ]
    for err in (errors or ["No explicit error details available."]):
        body.append(f"- {err}")
    return "\n".join(body)


def _send_slack_alert(message: str) -> None:
    if not SETTINGS.slack_webhook_url:
        return
    try:
        requests.post(
            SETTINGS.slack_webhook_url,
            json={"text": message},
            timeout=10,
        ).raise_for_status()
    except Exception:
        return


def _send_email_alert(subject: str, message: str) -> None:
    if not SETTINGS.smtp_host or not SETTINGS.alert_to_email:
        return
    try:
        msg = MIMEText(message)
        msg["Subject"] = subject
        msg["From"] = SETTINGS.smtp_from_email
        msg["To"] = SETTINGS.alert_to_email

        with smtplib.SMTP(SETTINGS.smtp_host, SETTINGS.smtp_port, timeout=10) as smtp:
            smtp.starttls()
            if SETTINGS.smtp_username and SETTINGS.smtp_password:
                smtp.login(SETTINGS.smtp_username, SETTINGS.smtp_password)
            smtp.sendmail(SETTINGS.smtp_from_email, [SETTINGS.alert_to_email], msg.as_string())
    except Exception:
        return

