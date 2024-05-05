import os

if 'TOKEN_NETBOX' in os.environ:
    TOKEN_NETBOX = os.environ['TOKEN_NETBOX']
else:
    TOKEN_NETBOX = 'your_token'
