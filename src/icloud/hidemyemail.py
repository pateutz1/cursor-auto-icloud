import asyncio
import aiohttp
import ssl
import certifi
import os
import sys

# Add parent directory to path to import language module
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

try:
    from src.utils.logger import logging
    from src.utils.language import getTranslation, _
except ImportError:
    from utils.logger import logging
    from utils.language import getTranslation, _


class HideMyEmail:
    base_url_v1 = "https://p68-maildomainws.icloud.com/v1/hme"
    base_url_v2 = "https://p68-maildomainws.icloud.com/v2/hme"
    params = {
        "clientBuildNumber": "2413Project28",
        "clientMasteringNumber": "2413B20",
        "clientId": "",
        "dsid": "", # Directory Services Identifier (DSID) is a method of identifying AppleID accounts
    }

    def __init__(self, label: str = "Cursor-Auto-iCloud", cookies: str = ""):
        """Initializes the HideMyEmail class.

        Args:
            label (str)     Label that will be set for all emails generated, defaults to `Cursor-Auto-iCloud`
            cookies (str)   Cookie string to be used with requests. Required for authorization.
        """
        self.label = label

        # Cookie string to be used with requests. Required for authorization.
        self.cookies = cookies

    async def __aenter__(self):
        connector = aiohttp.TCPConnector(ssl_context=ssl.create_default_context(cafile=certifi.where())) 
        self.s = aiohttp.ClientSession(
            headers={
                "Connection": "keep-alive",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
                "Content-Type": "text/plain",
                "Accept": "*/*",
                "Sec-GPC": "1",
                "Origin": "https://www.icloud.com",
                "Sec-Fetch-Site": "same-site",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Dest": "empty",
                "Referer": "https://www.icloud.com/",
                "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8,cs;q=0.7",
                "Cookie": self.__cookies.strip(),
            },
            timeout=aiohttp.ClientTimeout(total=10),
            connector=connector,
        )

        return self

    async def __aexit__(self, exc_t, exc_v, exc_tb):
        await self.s.close()

    @property
    def cookies(self) -> str:
        return self.__cookies

    @cookies.setter
    def cookies(self, cookies: str):
        # remove new lines/whitespace for security reasons
        self.__cookies = cookies.strip()

    async def generate_email(self) -> dict:
        """Generates an email"""
        try:
            logging.debug(getTranslation("generating_icloud_hidden_email"))
            async with self.s.post(
                f"{self.base_url_v1}/generate", params=self.params, json={"langCode": "en-us"}
            ) as resp:
                res = await resp.json()
                return res
        except asyncio.TimeoutError:
            logging.error(getTranslation("generate_email_timeout"))
            return {"error": 1, "reason": getTranslation("request_timeout")}
        except Exception as e:
            logging.error(getTranslation("generate_email_failed").format(str(e)))
            return {"error": 1, "reason": str(e)}

    async def reserve_email(self, email: str) -> dict:
        """Reserves an email and registers it for forwarding"""
        try:
            logging.debug(getTranslation("reserving_email").format(email))
            payload = {
                "hme": email,
                "label": self.label,
                "note": "Cursor-Auto-iCloud",
            }
            async with self.s.post(
                f"{self.base_url_v1}/reserve", params=self.params, json=payload
            ) as resp:
                res = await resp.json()
            return res
        except asyncio.TimeoutError:
            logging.error(getTranslation("reserve_email_timeout"))
            return {"error": 1, "reason": getTranslation("request_timeout")}
        except Exception as e:
            logging.error(getTranslation("reserve_email_failed").format(str(e)))
            return {"error": 1, "reason": str(e)}

    async def list_email(self) -> dict:
        """List all HME"""
        logging.info(getTranslation("getting_email_list"))
        try:
            async with self.s.get(f"{self.base_url_v2}/list", params=self.params) as resp:
                res = await resp.json()
                return res
        except asyncio.TimeoutError:
            logging.error(getTranslation("list_email_timeout"))
            return {"error": 1, "reason": getTranslation("request_timeout")}
        except Exception as e:
            logging.error(getTranslation("list_email_failed").format(str(e)))
            return {"error": 1, "reason": str(e)}

    async def deactivate_email(self, anonymous_id: str) -> dict:
        """Deactivates an email using its anonymousId"""
        logging.info(getTranslation("deactivating_email").format(anonymous_id))
        try: 
            async with self.s.post(f"{self.base_url_v1}/deactivate", params=self.params, json={"anonymousId": anonymous_id}) as resp:
                res = await resp.json()
                return res
        except asyncio.TimeoutError:
            logging.error(getTranslation("deactivate_email_timeout"))
            return {"error": 1, "reason": getTranslation("request_timeout")}
        except Exception as e:
            logging.error(getTranslation("deactivate_email_failed").format(str(e)))
            return {"error": 1, "reason": str(e)}

    async def delete_email(self, anonymous_id: str, email: str = None) -> dict:
        """Deletes an email using its anonymousId
        
        Args:
            anonymous_id: The anonymousId of the email to delete
            email: Optional email address (for logging purposes only)
        """
        log_identifier = email if email else anonymous_id
        logging.info(getTranslation("deleting_email").format(log_identifier))
        try: 
            payload = {"anonymousId": anonymous_id}
            async with self.s.post(f"{self.base_url_v1}/delete", params=self.params, json=payload) as resp:
                res = await resp.json()
                print(res)
                return res
        except asyncio.TimeoutError:
            logging.error(getTranslation("delete_email_timeout"))
            return {"error": 1, "reason": getTranslation("request_timeout")}
        except Exception as e:
            print(e)
            logging.error(getTranslation("delete_email_failed").format(str(e)))
            return {"error": 1, "reason": str(e)}
        