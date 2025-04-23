from dotenv import load_dotenv
import os
import sys
import json

# Add parent directory to path to import language module
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

try:
    from src.utils.logger import logging
    from src.utils.language import getTranslation, _
except ImportError:
    from utils.logger import logging
    try:
        from utils.language import getTranslation, _
    except ImportError:
        # Fallback if language module is not available
        def getTranslation(key, *args):
            if args:
                return key.format(*args)
            return key


class Config:
    def __init__(self):
        # Get the application's root directory path
        if getattr(sys, "frozen", False):
            # If running as a packaged executable
            application_path = os.path.dirname(sys.executable)
        else:
            # If running in development environment
            # Look for .env in the project root, not in src/utils
            application_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        # Specify the path to the .env file
        dotenv_path = os.path.join(application_path, ".env")

        if not os.path.exists(dotenv_path):
            raise FileNotFoundError(getTranslation("env_file_not_exist").format(dotenv_path))

        # Load the .env file
        load_dotenv(dotenv_path)

        self.icloud_user = os.getenv('ICLOUD_USER', '').strip()
        if '@icloud.com' in self.icloud_user:
            self.icloud_user = self.icloud_user.replace('@icloud.com', '')
        self.icloud_pass = os.getenv('ICLOUD_APP_PASSWORD', '').strip()

        # Check configuration
        self.check_config()


    def get_icloud_imap(self):
        """Get iCloud IMAP configuration
        
        Returns:
            dict or False: iCloud IMAP configuration information, returns False if not configured
        """
        # Check if required iCloud IMAP configuration exists
        icloud_user = os.getenv('ICLOUD_USER', '').strip()

        if '@icloud.com' in icloud_user:
            icloud_user = icloud_user.replace('@icloud.com', '')

        icloud_pass = os.getenv('ICLOUD_APP_PASSWORD', '').strip()
        
        if not icloud_user or not icloud_pass:
            return False
        
        return {
            "imap_server": "imap.mail.me.com",  # Fixed server for iCloud Mail
            "imap_port": 993,                    # Fixed port for iCloud Mail
            "imap_user": icloud_user,            # Username is typically the email prefix
            "imap_pass": icloud_pass,            # App-specific password
            "imap_dir": os.getenv('ICLOUD_FOLDER', 'INBOX').strip(),
        }

    def check_config(self):
        """Check if configuration items are valid

        Validation rules:
        1. Validate if icloud user and pass is not null
        """

        required_configs = {
            "icloud_user": getTranslation("icloud_email"),
            "icloud_pass": getTranslation("icloud_app_password"),
        }

        # Check basic configuration
        for key, name in required_configs.items():
            if not self.check_is_valid(getattr(self, key)):
                raise ValueError(getTranslation("config_not_set").format(name=name, key=key.upper()))


    def check_is_valid(self, value):
        """Check if a configuration item is valid

        Args:
            value: Value of the configuration item

        Returns:
            bool: Whether the configuration item is valid
        """
        return isinstance(value, str) and len(str(value).strip()) > 0

    def print_config(self):
        logging.info(getTranslation("icloud_email_info").format(self.icloud_user))
        logging.info(getTranslation("icloud_password_info").format(self.icloud_pass))


# Usage example
if __name__ == "__main__":
    try:
        config = Config()
        print(getTranslation("env_loaded_success"))
        config.print_config()
    except ValueError as e:
        print(getTranslation("error_message").format(str(e)))
