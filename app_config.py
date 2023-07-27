import os

OPENAI_KEY = "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" #OpenAI API key

ELEVENLABS_API_KEY = "283236cbabf8d3b1b5c508ac729b735c" #ElevenLabs API key

CLIENT_ID = "e00963f2-823f-4827-9033-ddefc0109d86" # Application (client) ID of app registration

CLIENT_SECRET = "XuD8Q~ZwVvmXCO0kg6oVvXUSGXkJXl7P-nRq2dr9" # Placeholder - for use ONLY during testing.
# In a production app, we recommend you use a more secure method of storing your secret,
# like Azure Key Vault. Or, use an environment variable as described in Flask's documentation:
# https://flask.palletsprojects.com/en/1.1.x/config/#configuring-from-environment-variables
# CLIENT_SECRET = os.getenv("CLIENT_SECRET")
# if not CLIENT_SECRET:
#     raise ValueError("Need to define CLIENT_SECRET environment variable")

AUTHORITY = "https://login.microsoftonline.com/30b7d94e-3354-4950-93fe-5ac3feb98e78"  # For multi-tenant app
# AUTHORITY = "https://login.microsoftonline.com/Enter_the_Tenant_Name_Here"

REDIRECT_PATH = "/getAToken"  # Used for forming an absolute URL to your redirect URI.
                              # The absolute URL must match the redirect URI you set
                              # in the app's registration in the Azure portal.

# You can find more Microsoft Graph API endpoints from Graph Explorer
# https://developer.microsoft.com/en-us/graph/graph-explorer
ENDPOINT = 'https://graph.microsoft.com/v1.0/users'  # This resource requires no admin consent

# You can find the proper permission names from this document
# https://docs.microsoft.com/en-us/graph/permissions-reference
SCOPE = ["User.ReadBasic.All"]

SESSION_TYPE = "filesystem"  # Specifies the token cache should be stored in server-side session

API_KEY = "bXJlZGRpYm9pbmFAZ21haWwuY29t:yPYpJrAXDVKxFT4K-KYHB" #Please change this to your own API key
API_URL = "https://api.d-id.com"

aws_access_key_id='AKIAQHA26W4T6P4OEAWH'
aws_secret_access_key='tQ23TIQr5lSO9PrJ2KZD7ovknn3QJIvVRRU0DUi6'