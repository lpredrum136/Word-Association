import requests, json

def RelatedWords(word):
    """Look up word"""
    response = requests.get(f"https://relatedwords.org/api/related?term={word}")
    response_in_JSON = response.json()
    for item in response_in_JSON:
        item.pop("from")
    return response_in_JSON[:20]

def Relations(word):
    obj = requests.get(f'http://api.conceptnet.io/c/en/{word}?limit=2000').json()
    obj_data = obj['edges']
    
    # Preprocess: Drop everything that is not English
    """ try:
        obj_data = [item for item in obj_data if item['end']['language'] == 'en' and word not in item['end']['label']]
    except:
        pass """ # Because sometimes results return 200 words but only 398 "language". Should be 400, but we don't wanna deal with it
    # The above try except is not good as it still return results with word IN item['end']['label'], probably because it has something to do with how try except works
    # Therefore, we propose a longer but more careful method below. Still consider the case where there is no 'language' key.

    for item in list(obj_data):
        for key in item['end']:
            if key == 'language':
                if item['end']['language'] != 'en':
                    obj_data.remove(item)
    for item in list(obj_data):
        for key in item['start']:
            if key == 'language':
                if item['start']['language'] != 'en':
                    obj_data.remove(item)
    obj_data = [item for item in obj_data if word not in item['end']['label']]

    # return
    return obj_data



    """ responseInJSON = response.json()
    for wordType, listOfThesaurus in responseInJSON.items():
        for simiType in list(listOfThesaurus):
            if simiType == "ant" or simiType == "usr":
                listOfThesaurus.pop(simiType)
    # responseInJSON.pop("noun")
    return responseInJSON """
    """ # Contact API
    try:
        response = requests.get(f"http://words.bighugelabs.com/api/2/435029d33f4616e31354636ff8970307/{word}/json")
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        quote = response.json()
        return {
            "name": quote["companyName"],
            "price": float(quote["latestPrice"]),
            "symbol": quote["symbol"]
        }
    except (KeyError, TypeError, ValueError):
        return None """