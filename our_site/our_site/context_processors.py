import json
import random
from constance import config

def random_quote(request):
    """
    Context processor to inject a random quote when QUOTES_ENABLED is True.
    Returns {'random_quote': {'text': ..., 'author': ...}} or empty dict.
    """
    if not config.QUOTES_ENABLED:
        return {}
    try:
        quotes_list = json.loads(config.QUOTES_LIST or '[]')
    except json.JSONDecodeError:
        quotes_list = []

    if quotes_list:
        quote = random.choice(quotes_list)
    else:
        quote = {'text': '', 'author': ''}
    return {'random_quote': quote}
