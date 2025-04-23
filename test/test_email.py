import os
import sys
import traceback
from pathlib import Path
from dotenv import load_dotenv

# Properly add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now we can import modules using absolute imports
from src.utils.get_email_code import EmailVerificationHandler

# Define a function to find the .env file since we can't import it yet
def get_env_directory():
    """
    Get the directory where the .env file is located.
    Returns the directory path if .env exists, otherwise returns the current directory.
    """
    # Check common locations for .env file
    possible_env_paths = [
        ".env",  # Current directory
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"),  # Project root
        os.path.join(os.path.dirname(sys.executable), ".env"),  # Next to executable
    ]
    
    for env_path in possible_env_paths:
        if os.path.exists(env_path):
            return os.path.dirname(os.path.abspath(env_path))
    
    # If .env is not found, return current directory
    return os.path.abspath(".")


def test_icloud_imap():
    """Test the iCloud IMAP email verification functionality"""
    print("\n=== Testing iCloud IMAP Mode ===")
    icloud_user = os.getenv('ICLOUD_USER', '')
    icloud_pass = os.getenv('ICLOUD_APP_PASSWORD', '')
    
    if not icloud_user or not icloud_pass:
        print("Error: iCloud credentials not configured in .env file")
        return False
        
    print(f"iCloud user: {icloud_user}")
    
    try:
        handler = EmailVerificationHandler(icloud_user)
        code = handler.get_verification_code()
        if code:
            print(f"Successfully obtained verification code: {code}")
            return code
        else:
            print("Failed to get verification code")
            return False
    except Exception as e:
        print(f"Error during verification: {str(e)}")
        traceback.print_exc()
        return False


def print_config():
    """Print the current configuration"""
    print("\n=== Current Environment Configuration ===")
    
    # Check if .env is loaded
    env_dir = get_env_directory()
    env_path = os.path.join(env_dir, ".env")
    print(f"Using .env file: {env_path}")
    
    # Check if iCloud IMAP is configured
    icloud_user = os.getenv('ICLOUD_USER')
    icloud_pass = os.getenv('ICLOUD_APP_PASSWORD')
    
    print(f"ICLOUD_USER: {icloud_user or 'Not configured'}")
    print(f"ICLOUD_APP_PASSWORD: {'[Configured]' if icloud_pass else '[Not configured]'}")
    print(f"ICLOUD_FOLDER: {os.getenv('ICLOUD_FOLDER', 'INBOX')}")
    
    # Check if emails.txt and accounts.csv are in the right place
    emails_path = os.path.join(env_dir, "emails.txt")
    accounts_path = os.path.join(env_dir, "accounts.csv")
    
    print(f"\nData files:")
    print(f"emails.txt: {'Exists' if os.path.exists(emails_path) else 'Not found'} at {emails_path}")
    print(f"accounts.csv: {'Exists' if os.path.exists(accounts_path) else 'Not found'} at {accounts_path}")


def main():
    # Load environment variables
    load_dotenv()
    
    # Print initial configuration
    print_config()
    
    try:
        # Check if iCloud IMAP is configured
        icloud_user = os.getenv('ICLOUD_USER')
        icloud_pass = os.getenv('ICLOUD_APP_PASSWORD')
        
        if icloud_user and icloud_pass:
            result = test_icloud_imap()
            print(f"Test result: {'Successful' if result else 'Failed'}")
        else:
            print("iCloud IMAP is not configured. Please set ICLOUD_USER and ICLOUD_APP_PASSWORD in your .env file.")
    except Exception as e:
        print(f"Error during testing: {str(e)}")
        traceback.print_exc()


if __name__ == "__main__":
    main() 