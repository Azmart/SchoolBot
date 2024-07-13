import streamlit_authenticator as stauth
from streamlit_authenticator.utilities.hasher import Hasher

# Define your plain text passwords
plain_passwords = ['IamAzmart01', 'IamAzmart08']

# Hash the passwords
hashed_passwords = Hasher(plain_passwords).generate()

# Print the hashed passwords
print(hashed_passwords)
