"""
pip install email-validator

The email-validator library handles all
  of these complex edge cases automatically
  and can even perform a fast DNS check to ensure
  the domain actually exists.

2. Local-Only Syntax Validation (Fast)
If you need instant feedback—such as
  a real-time form field validator on
  a website—you can turn off the network-based
  domain check. This keeps the function
  incredibly fast because it does not have to wait for a DNS lookup.

Alternative:

Framework AlternativesIf you are already utilizing
  specific frameworks, you may not need to call
  email-validator directly:FastAPI / Pydantic:
  Pydantic natively provides an EmailStr type.
  It utilizes email-validator under the hood to
  automatically reject poorly formatted emails
  at your API boundary with a 422 Unprocessable Entity error.
"""
from email_validator import validate_email, EmailNotValidError



def check_email(email_address):
  try:
    # Validates syntax and delivers a DNS check for the domain
    email_info = validate_email(email_address, check_deliverability=True)

    # Returns the cleanly normalized version of the email (e.g., lowercase domain)
    return f"Valid! Normalized email: {email_info.normalized}"

  except EmailNotValidError as e:
    # Returns a friendly, human-readable error message
    return f"Invalid email: {str(e)}"


# Example Usage
email_address = "test@gmail.com"
print(check_email(email_address))  # Valid
print(check_email("bad_email@not-a-real-domainxyz.com"))  # Invalid (Domain does not exist)
print(check_email("plainaddress"))  # Invalid (Syntax error)


# Purely local validation without hitting the network
email_info = validate_email(email_address, check_deliverability=False)
