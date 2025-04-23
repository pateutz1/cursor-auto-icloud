from DrissionPage import ChromiumOptions, Chromium
import sys
import os
import logging
from dotenv import load_dotenv

load_dotenv()


class BrowserManager:
    def __init__(self):
        self.browser = None

    def init_browser(self, user_agent=None):
        """Initialize browser"""
        co = self._get_browser_options(user_agent)
        self.browser = Chromium(co)
        return self.browser

    def _get_browser_options(self, user_agent=None):
        """Get browser configuration options"""
        co = ChromiumOptions()
        try:
            extension_path = self._get_extension_path("turnstilePatch")
            co.add_extension(extension_path)
        except FileNotFoundError as e:
            logging.warning(f"Warning: {e}")

        browser_path = os.getenv("BROWSER_PATH")
        if browser_path:
            co.set_paths(browser_path=browser_path)

        co.set_pref("credentials_enable_service", False)
        co.set_argument("--hide-crash-restore-bubble")
        proxy = os.getenv("BROWSER_PROXY")
        if proxy:
            co.set_proxy(proxy)

        co.auto_port()
        if user_agent:
            co.set_user_agent(user_agent)

        co.headless(
            os.getenv("BROWSER_HEADLESS", "True").lower() == "true"
        )  # Use headless mode in production environment

        # Special handling for Mac systems
        if sys.platform == "darwin":
            co.set_argument("--no-sandbox")
            co.set_argument("--disable-gpu")

        return co

    def _get_extension_path(self, exname='turnstilePatch'):
        """
        Get extension path
        
        Args:
            exname (str): Extension name, defaults to 'turnstilePatch'
            
        Returns:
            str: Path to the extension
            
        Raises:
            FileNotFoundError: If extension directory doesn't exist
        """
        # First try to locate the extension in the src folder
        root_dir = os.getcwd()
        extension_path = os.path.join(root_dir, "src", exname)
        
        # If not found in src, try the root directory
        if not os.path.exists(extension_path):
            extension_path = os.path.join(root_dir, exname)

        # For PyInstaller bundles
        if hasattr(sys, "_MEIPASS"):
            extension_path = os.path.join(sys._MEIPASS, "src", exname)
            if not os.path.exists(extension_path):
                extension_path = os.path.join(sys._MEIPASS, exname)

        if not os.path.exists(extension_path):
            raise FileNotFoundError(f"Extension not found: {extension_path}")

        return extension_path

    def quit(self):
        """Close browser"""
        if self.browser:
            try:
                self.browser.quit()
            except:
                pass
