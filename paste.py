import requests
import misc


def paste(code, name='unnamed', paste_format='text',
          expire_date='1H', private='0'):
    options = {
        'api_paste_name': name,
        'api_paste_format': paste_format,
        'api_paste_expire_date': expire_date,
        'api_paste_private': private,
        'api_option': 'paste',
        'api_user_key': '',
        'api_dev_key': misc.PBTOKEN,
        'api_paste_code': code
    }
    
    response = requests.post('https://pastebin.com/api/api_post.php',
                             data=options)
    return response.text
