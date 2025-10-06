"""Simple IMAP email ingestion prototype.
- Uses IMAPClient for a cleaner interface
- Fetches latest N emails, extracts headers and cleaned body
- Writes sample JSONL to /tmp/shipcube_emails.jsonl
"""

import os, json, re
from imapclient import IMAPClient
import email
from bs4 import BeautifulSoup
from datetime import datetime
from .schema import EmailRecord

def clean_html(raw_html: str) -> str:
    if not raw_html:
        return ''
    soup = BeautifulSoup(raw_html, 'lxml')
    # remove scripts/styles
    for script in soup(['script', 'style']):
        script.decompose()
    text = soup.get_text(separator=' ')
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_body(msg):
    # If message is multipart, prefer text/plain else fallback to html
    if msg.is_multipart():
        parts = msg.walk()
        for part in parts:
            ctype = part.get_content_type()
            if ctype == 'text/plain':
                return part.get_payload(decode=True).decode(part.get_content_charset('utf-8'), errors='replace')
        for part in msg.walk():
            ctype = part.get_content_type()
            if ctype == 'text/html':
                return clean_html(part.get_payload(decode=True).decode(part.get_content_charset('utf-8'), errors='replace'))
        return ''
    else:
        ctype = msg.get_content_type()
        payload = msg.get_payload(decode=True)
        if not payload:
            return ''
        text = payload.decode(msg.get_content_charset('utf-8'), errors='replace')
        if ctype == 'text/html':
            return clean_html(text)
        return text

def fetch_emails_imap(config: dict, mailbox='INBOX', limit=10):
    """Connect to IMAP server and fetch recent emails.
    config example:
    {
        'host': 'imap.gmail.com',
        'username': 'you@example.com',
        'password': 'app-password-or-oauth-token',
        'ssl': True
    }
    """
    host = config.get('host')
    username = config.get('username')
    password = config.get('password')
    ssl = config.get('ssl', True)
    out_file = config.get('out_file', '/tmp/shipcube_emails.jsonl')

    with IMAPClient(host, ssl=ssl) as client:
        client.login(username, password)
        client.select_folder(mailbox)
        # Search for recent messages (UNSEEN or ALL)
        messages = client.search(['ALL'])
        # take latest N
        messages = sorted(messages)[-limit:]
        results = []
        for msgid, data in client.fetch(messages, ['ENVELOPE', 'RFC822']).items():
            raw = data.get(b'RFC822')
            if not raw:
                continue
            msg = email.message_from_bytes(raw)
            subject = msg.get('Subject')
            from_ = msg.get('From')
            date_raw = msg.get('Date')
            try:
                date_parsed = email.utils.parsedate_to_datetime(date_raw)
            except Exception:
                date_parsed = None
            body = extract_body(msg)
            cleaned = clean_html(body)
            record = EmailRecord(
                raw_text=raw.decode('utf-8', errors='replace') if isinstance(raw, (bytes,bytearray)) else str(raw),
                cleaned_text=cleaned,
                sender=from_,
                timestamp=date_parsed,
                thread_id=subject or None,
                subject=subject
            )
            results.append(record.dict())
        # write to file
        os.makedirs(os.path.dirname(out_file), exist_ok=True)
        with open(out_file, 'w', encoding='utf-8') as f:
            for r in results:
                f.write(json.dumps(r, default=str) + '\n')
    return {"fetched": len(results), "out_file": out_file}
