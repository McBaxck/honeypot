import fingerprint_pro_server_api_sdk
from fingerprint_pro_server_api_sdk import EventResponse
from fingerprint_pro_server_api_sdk import Response
from fingerprint_pro_server_api_sdk.rest import ApiException


VISITOR_ID: str = ""
SECRET_API_KEY: str = "FW3B5VLqNFNdKJsgKUTZ"
PUBLIC_API_KEY: str = "mgqYOLFg5Asxl7Nh8M4o"
REGION: str = "eu"

configuration = fingerprint_pro_server_api_sdk.Configuration(
  api_key=SECRET_API_KEY,
  region=REGION
)
api_instance = fingerprint_pro_server_api_sdk.FingerprintApi(configuration)

# Get visit history of a specific visitor
try:
    visits: Response = api_instance.get_visits("4RSsCXbrOxgLfpIo8w6o", limit=10)
    print(visits)
except ApiException as e:
    print("Exception when getting visits: %s\n" % e)

# Get a specific identification event
try:
    event: EventResponse = api_instance.get_event("<requestId>")
    print(event)
except ApiException as e:
    print("Exception when getting an event: %s\n" % e)