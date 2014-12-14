import re
import time

class Formater:
    @staticmethod
    def format_html_content(content):
            tokens = re.findall(r'(https?://[^\s]+)', content)
            remove_tokens = re.sub(r'(https?://[^\s]+)', '====', content)
            remainders = remove_tokens.split('====')
            html_tags = []
            if len(tokens) > 0:
                for token in tokens:
                    if token.endswith('.jpg') or token.endswith('.jpeg') or token.endswith('.png') or token.endswith('.gif'):
                        html_tags.append('<img src=\"%s\">' % (token))
                    else:
                        html_tags.append('<a href=\"%s\">%s</a>' % (token, token))
                result = remainders.pop(0)
                for tag in html_tags:
                    if len(remainders) > 0:
                        result = result + tag + remainders.pop(0)
                    else:
                        result = result + tag
                return result
            else:
                return content
