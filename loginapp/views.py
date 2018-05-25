from django.shortcuts import render, redirect
import os
import urllib.parse
import uuid

import adal
import requests

from . import settings

SESSION = requests.Session()

def index(request):
  return render(request, 'html/homepage.html', {'sample': 'django'})


def login(request):
  """Prompt user to authenticate."""
  auth_state = str(uuid.uuid4())
  SESSION.auth_state = auth_state

  # For this sample, the user selects an account to authenticate. Change
  # this value to 'none' for "silent SSO" behavior, and if the user is
  # already authenticated they won't need to re-authenticate.
  prompt_behavior = 'select_account'

  params = urllib.parse.urlencode({'response_type': 'code',
                                    'CLIENT_ID': settings.CLIENT_ID,
                                    'REDIRECT_URI': settings.REDIRECT_URI,
                                    'state': auth_state,
                                    'RESOURCE': settings.RESOURCE,
                                    'prompt': prompt_behavior})

  return redirect(settings.AUTHORITY_URL + '/oauth2/authorize?' + params)

def authorized(request):
    """Handler for the application's Redirect Uri."""
    code = request.GET.get('code')
    auth_state = request.GET.get('state')
    if auth_state != SESSION.auth_state:
      raise Exception('state returned to redirect URL does not match!')
    auth_context = adal.AuthenticationContext(settings.AUTHORITY_URL, api_version=None)
    token_response = auth_context.acquire_token_with_authorization_code(
        code, settings.REDIRECT_URI, settings.RESOURCE, settings.CLIENT_ID, settings.CLIENT_SECRET)
    SESSION.headers.update({'Authorization': f"Bearer {token_response['accessToken']}",
                            'User-Agent': 'adal-sample',
                            'Accept': 'application/json',
                            'Content-Type': 'application/json',
                            'SdkVersion': 'sample-python-adal',
                            'return-client-request-id': 'true'})
    return redirect('/graphcall')

def graphcall(request):
    """Confirm user authentication by calling Graph and displaying some data."""
    endpoint = settings.RESOURCE + settings.API_VERSION + '/me'
    http_headers = {'client-request-id': str(uuid.uuid4())}
    graphdata = SESSION.get(endpoint, headers=http_headers, stream=False).json()
    return render(request, 'html/graphcall.html',
                                 { 'graphdata': graphdata,
                                 'endpoint':endpoint,
                                 'sample':'django'})