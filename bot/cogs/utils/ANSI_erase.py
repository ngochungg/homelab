import re

class ANSI_erase:
    @staticmethod
    def erase_ansi(text: str) -> str:

        if not text:
            return ""
        
        ansi_escape = re.compile(r'\x1b\[[0-9;]*[a-zA-Z]')
        text = ansi_escape.sub('', text)
        
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', ' ', text)
        
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()