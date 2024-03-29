import openai
from openai.error import RateLimitError, InvalidRequestError
from requests.exceptions import ReadTimeout

MAX_LENGTH_ERR_MSG = "Максимальная длина контекста составляет около 3000 слов, ответ превысил длину контекста. Пожалуйста, повторите вопрос, либо перефразируйте его."

RATE_LIMIT_ERR_MSG = "ChatGPT в данный момент перегружен запросами, пожалуйста повторите свой запрос чуть позже."


def make_request(messages, api_key, model):
    try:
        completion = openai.ChatCompletion.create(
            model=model,
            messages=messages
        )
        answer = completion.choices[0]['message']['content']
        if answer:
            return answer
        else:
            make_request(messages, api_key, model)
    except RateLimitError:
        return RATE_LIMIT_ERR_MSG

    except ReadTimeout:
        return RATE_LIMIT_ERR_MSG

    except InvalidRequestError:
        return MAX_LENGTH_ERR_MSG
