"""
constants.py

Store any constants related to the TitanAuth REST API.
"""

# Base URI for any authentication requests.
BASE_URI = "https://titanda.sh"
# Base Token's URI.
TOKENS_URI = BASE_URI + "/tokens/"

# Date format used by Token expiration dates.
DATE_FMT = "%Y-%m-%d"

BASIC = "basic"
PREMIUM = "premium"
DEVELOPMENT = "development"
