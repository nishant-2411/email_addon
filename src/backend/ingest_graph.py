"""Microsoft Graph ingestion template.
NOTE: This is a template showing how to structure Graph API calls using MSAL.
To actually run this:
- Register an app in Azure AD and obtain client_id, client_secret, tenant_id.
- Grant Mail.Read or Mail.ReadWrite application or delegated permissions.
- For production, implement full OAuth2 flow (authorization code / device code).
"""

import os, requests, json
from msal import ConfidentialClientApplication, PublicClientApplication

# Placeholder functions / examples

def get_access_token_client_credentials(client_id, client_secret, tenant_id, scope=['https://graph.microsoft.com/.default']):
    app = ConfidentialClientApplication(
        client_id=client_id,
        client_credential=client_secret,
        authority=f'https://login.microsoftonline.com/{tenant_id}'
    )
    result = app.acquire_token_for_client(scopes=scope)
    if 'access_token' in result:
        return result['access_token']
    raise RuntimeError('Failed to get access token: ' + str(result))

def fetch_messages_graph(access_token, top=10):
    url = f'https://graph.microsoft.com/v1.0/me/messages?$top={top}'
    headers = {'Authorization': f'Bearer {access_token}'}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    messages = data.get('value', [])
    # minimal parsing
    parsed = []
    for m in messages:
        parsed.append({
            'id': m.get('id'),
            'subject': m.get('subject'),
            'from': m.get('from'),
            'receivedDateTime': m.get('receivedDateTime'),
            'bodyPreview': m.get('bodyPreview'),
            'webLink': m.get('webLink')
        })
    return parsed
