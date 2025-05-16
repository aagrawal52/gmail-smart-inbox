import base64
from bs4 import BeautifulSoup
from typing import Dict, Any

class EmailParser:
    @staticmethod
    def base64url_decode(data: str) -> bytes:
        """Decode base64url-encoded data."""
        data = data.encode('utf-8')
        data += b'=' * (4 - (len(data) % 4))
        return base64.urlsafe_b64decode(data)

    @staticmethod
    def is_html_text(text: str) -> bool:
        """Check if text contains HTML."""
        try:
            soup = BeautifulSoup(text, 'html.parser')
            return len(soup.find_all()) > 0
        except:
            return False

    @classmethod
    def find_text_part(cls, parts: list) -> str:
        """Extract text from message parts."""
        res_string = ""
        for part in parts:
            mimeType = part.get('mimeType')
            if mimeType == 'text/plain':
                data = part.get('body', {}).get('data')
                if data:
                    text = cls.base64url_decode(data).decode('utf-8')
                    if cls.is_html_text(text):
                        soup = BeautifulSoup(text, 'html.parser')
                        res_string = res_string + " " + soup.get_text(separator=' ')
                    else:
                        res_string = res_string + " " + text           
            elif mimeType == 'text/html':
                data = part.get('body', {}).get('data')
                if data:
                    html = cls.base64url_decode(data).decode('utf-8')
                    soup = BeautifulSoup(html, 'html.parser')
                    res_string = res_string + " " + soup.get_text(separator=' ')
            elif mimeType in ['multipart/alternative', 'multipart/related']:
                res_string = res_string + " " + cls.find_text_part(part.get('parts', []))
        return res_string

    @classmethod
    def parse_email_body(cls, payload: Dict[str, Any]) -> str:
        """Parse email body from payload."""
        if payload['mimeType'] == 'text/plain':
            data = payload.get('body', {}).get('data')
            if data:
                return cls.base64url_decode(data).decode('utf-8')
        elif payload['mimeType'] == 'text/html':
            data = payload.get('body', {}).get('data')
            if data:
                html = cls.base64url_decode(data).decode('utf-8')
                soup = BeautifulSoup(html, 'html.parser')
                return soup.get_text(separator=' ')
        elif payload['mimeType'].startswith('multipart/'):
            parts = payload.get('parts', [])
            text = cls.find_text_part(parts)
            if text:
                return text
        return ""

    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text."""
        y = ''.join([i if ord(i) < 128 else ' ' for i in text])
        return ' '.join(y.strip().split())

    @classmethod
    def parse_with_error_handling(cls, payload: Dict[str, Any]) -> str:
        """Safely parse email body with error handling."""
        try:
            text = cls.parse_email_body(payload)
            return cls.clean_text(text)
        except:
            return "Unable to Parse" 