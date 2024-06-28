def get_email_username(email):
    """
    Extracts the username from an email address.
    
    Parameters:
    email (str): The email address to process.
    
    Returns:
    str: The username part of the email address.
    """
    if not isinstance(email, str):
        raise ValueError("Input must be a string")
    
    if '@' not in email:
        raise ValueError("Invalid email address, missing '@' symbol")
    
    return email.split('@')[0]