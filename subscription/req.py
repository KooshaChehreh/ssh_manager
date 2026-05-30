import requests
url = "https://setar.shrewdgamer.sbs:8000/sub/bmltYXphaGVkLDE3Nzk0NjQ5NzkBPdqHoTiNC"

try:
    response = requests.get(url)
        
        # بررسی موفقیت‌آمیز بودن درخواست (کد وضعیت 200)
    response.raise_for_status() 
        
        # چاپ محتوای پاسخ
    print(response.text)
        
except requests.exceptions.RequestException as e:
    print(e)