import json
from thesaurus import Word, exceptions
from flask import Flask, render_template, request, session, jsonify, redirect
from flask_session import Session
from helpers import RelatedWords, Relations

app = Flask(__name__)

app.run(host="127.0.0.1", port=5000, threaded=True) # Help it runs super fast

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

app.secret_key = 'whateverYouLike'

# To store list of words in word path
wordPath_list = []

@app.route("/")
def index():
    wordPath_list.clear()
    return render_template("index.html")

@app.route("/synonyms")
def synonyms():
    """QUERY"""
    word = request.args.get("word")

    if word not in wordPath_list:
        wordPath_list.append(word) # To create word path
    original_word = wordPath_list[0]

    """GET SYNONYMS"""
    # Get result
    try:
        results = Word(word)
    except exceptions.MisspellingError as msplt:
        session.clear()
        # return render_template("errorRedirect.html", error=msplt)
        session['mspltError'] = str(msplt)
        return redirect(f'/related?word={word}')
    except exceptions.WordNotFoundError as wnf:
        session.clear()
        session['wnf'] = str(wnf)
        return redirect(f'/related?word={word}')

    results = Word(word)
    resultData = results.data
    # session['word'] = word # To reuse in "/result"
    # Constructing parameters: part of speech and definitions
    numberOfOptions = len(results)
    partsOfSpeech = [item['partOfSpeech'].strip('.') for item in resultData] #.strip because for example, in html, div id = "adj.1" will not function. it is supposed to be adj1
    definitions = [item['meaning'] for item in resultData]
    
    # Constructing parameters: synonyms for each part of speech and definitions
    synList = results.synonyms('all')
    flat_synList = [item for sublist in synList for item in sublist] # Nothing to do with this part. This is for the next part GET RELATED WORDS!

    """GET RELATED WORDS"""
    # Result from helpers
    Related_words_data = RelatedWords(word)

    # Filter results: No overlapping with Synonyms, restricted to 10 words, with score rounded
    Related_words_data = [item for item in Related_words_data if item['word'] not in flat_synList] # Avoid overlap with Synonyms
    Related_words_data = Related_words_data[:10] # Trimming to avoid irrelevant results

    # Rounding the 'score' values in the above dict results Related_words_data
    for item in Related_words_data:
        item['score'] = round(item['score'], 2)

    """GET RELATIONS"""
    concepts = Relations("_".join(word.split())) # For example, "eat    mice  " becomes "eat_mice"
    
    # Process data: Get the lists of relations id and relations label
    relations_list_id = []
    for item in concepts:
        if item['rel']['@id'] not in relations_list_id:
            relations_list_id.append(item['rel']['@id'])

    relations_list_label = []
    for item in concepts:
        if item['rel']['label'] not in relations_list_label:
            relations_list_label.append(item['rel']['label'])

    # Rounding the 'weight' values to display better in html
    for item in concepts:
        item['weight'] = round(item['weight'], 2)

    # Change the labels to normal (eg. RelatedTo to "is related to") for easier printing out in html
    label_dict = {
        'RelatedTo': 'is related to',
        'ExternalURL': 'can be linked to other sites',
        'FormOf': 'is a form of',
        'IsA': 'is a',
        'PartOf': 'is a part of',
        'HasA': 'has',
        'UsedFor': 'is used for',
        'CapableOf': 'is capable of',
        'AtLocation': 'can be found in',
        'Causes': 'can lead to',
        'HasSubevent': 'is followed by',
        'HasFirstSubevent': 'starts with',
        'HasLastSubevent': 'ends with',
        'HasPrerequisite': 'requires',
        'HasProperty': 'has property or can be described as',
        'MotivatedByGoal': 'in order to',
        'ObstructedBy': 'is prevented by',
        'Desires': 'typically wants',
        'CreatedBy': 'is created by',
        'Synonym': 'has similar meaning with',
        'Antonym': 'has opposite meaning with',
        'DistinctFrom': 'is distinct from',
        'SymbolOf': 'is a symbol of',
        'DefinedAs': 'can be defined or explained as',
        'Entails': 'entails',
        'MannerOf': 'is a way of',
        'LocatedNear': 'can be found near',
        'HasContext': 'is often used in',
        'SimilarTo': 'is similar to',
        'EtymologicallyRelatedTo': 'has common origin with',
        'EtymologicallyDerivedFrom': 'is derived from',
        'CausesDesire': 'makes someone want',
        'MadeOf': 'is made of',
        'ReceivesAction': 'can be',
        'InstanceOf': 'is an example of',
        'NotDesires': 'typically not want',
        'DerivedFrom': 'is derived from'
    } # Build a dictionary and use it to look up relation labels

    # Create a new list as a copy of label lists to store real relation list labels, eg 'RelatedTo' to 'is related to'
    real_relations_list_label_names = relations_list_label.copy()
    for i in range(len(relations_list_label)): # Populate the list of real relation names
        if relations_list_label[i] in label_dict.keys():
            real_relations_list_label_names[i] = label_dict[relations_list_label[i]]

    # List of start node
    start_node_list = []
    for item in concepts:
        if item['start']['label'] not in start_node_list:
            start_node_list.append(item['start']['label'])

    # List for each relation
    concept_network = {}
    
    for item in relations_list_label:
        concept_network[item] = [] # Initiate a list as value for each key/relation

    for item in relations_list_label:
        for edge in concepts:
            if item == edge['rel']['label']:
                obj_to_append = dict((i, edge[i]) for i in ('start', 'end', 'rel', 'weight')) # Only take the important stuff
                concept_network[item].append(obj_to_append)

    # Problem: sometimes the word queried is 'start', other times it is 'end'
    word_start_or_end = {}

    for i in range(len(relations_list_label)):
        for j in range(len(concept_network[relations_list_label[i]])):
            if word in concept_network[relations_list_label[i]][j]['end']['label']:
                word_start_or_end[relations_list_label[i]] = 'end'
            else:
                word_start_or_end[relations_list_label[i]] = 'start'

    # Return
    return render_template("results.html", partsOfSpeech=partsOfSpeech, definitions=definitions, synList=synList, numberOfOptions=numberOfOptions, \
        resultData=resultData, Related_words_data=Related_words_data, relations_list_label=relations_list_label, concept_network=concept_network, \
            real_relations_list_label_names=real_relations_list_label_names, word_start_or_end=word_start_or_end, original_word=original_word, word=word, wordPath_list=wordPath_list)

@app.route("/related")
def related():
    """In case misspelling error of the queried word, which return no synonyms"""
    # Clear word path because it doesn't mean anything now

    """QUERY"""
    word = request.args.get("word")

    if word not in wordPath_list:
        wordPath_list.append(word) # To create word path
    original_word = wordPath_list[0]
    
    """GET SYNONYMS"""
    for key in session:
        if key == 'mspltError':
            word_suggest = session['mspltError'].split("mean '")[1].split("'?")[0]
        else:
            word_suggest = ''

    # This is the old way, when we didn't have Word not found error exception        
    """ if session['mspltError'] != '':
        word_suggest = session['mspltError'].split("mean '")[1].split("'?")[0] # Get the word suggested after the error is shown
    else:
        word_suggest = '' """

    """GET RELATED WORDS"""
    # Result from helpers
    Related_words_data = RelatedWords(word)

    # Filter results: No overlapping with Synonyms, restricted to 10 words, with score rounded
    Related_words_data = [item for item in Related_words_data] # Avoid overlap with Synonyms
    Related_words_data = Related_words_data[:10] # Trimming to avoid irrelevant results

    # Rounding the 'score' values in the above dict results Related_words_data
    for item in Related_words_data:
        item['score'] = round(item['score'], 2)

    """GET RELATIONS"""
    concepts = Relations("_".join(word.split()))
    
    # Process data: Get the lists of relations id and relations label
    relations_list_id = []
    for item in concepts:
        if item['rel']['@id'] not in relations_list_id:
            relations_list_id.append(item['rel']['@id'])

    relations_list_label = []
    for item in concepts:
        if item['rel']['label'] not in relations_list_label:
            relations_list_label.append(item['rel']['label'])

    # Rounding the 'weight' values to display better in html
    for item in concepts:
        item['weight'] = round(item['weight'], 2)

    # Change the labels to normal (eg. RelatedTo to "is related to") for easier printing out in html
    label_dict = {
        'RelatedTo': 'is related to',
        'ExternalURL': 'can be linked to other sites',
        'FormOf': 'is a form of',
        'IsA': 'is a',
        'PartOf': 'is a part of',
        'HasA': 'has',
        'UsedFor': 'is used for',
        'CapableOf': 'is capable of',
        'NotCapableOf': 'is not capable of',
        'AtLocation': 'can be found in',
        'Causes': 'can lead to',
        'HasSubevent': 'is followed by',
        'HasFirstSubevent': 'starts with',
        'HasLastSubevent': 'ends with',
        'HasPrerequisite': 'requires',
        'HasProperty': 'has property or can be described as',
        'MotivatedByGoal': 'in order to',
        'ObstructedBy': 'is prevented by',
        'Desires': 'typically wants',
        'CreatedBy': 'is created by',
        'Synonym': 'has similar meaning with',
        'Antonym': 'has opposite meaning with',
        'DistinctFrom': 'is distinct from',
        'SymbolOf': 'is a symbol of',
        'DefinedAs': 'can be defined or explained as',
        'Entails': 'entails',
        'MannerOf': 'is a way of',
        'LocatedNear': 'can be found near',
        'HasContext': 'is often used in',
        'SimilarTo': 'is similar to',
        'EtymologicallyRelatedTo': 'has common origin with',
        'EtymologicallyDerivedFrom': 'is derived from',
        'CausesDesire': 'makes someone want',
        'MadeOf': 'is made of',
        'ReceivesAction': 'can be',
        'InstanceOf': 'is an example of',
        'NotDesires': 'typically not want',
        'DerivedFrom': 'is derived from'
    } # Build a dictionary and use it to look up relation labels

    # Create a new list as a copy of label lists to store real relation list labels, eg 'RelatedTo' to 'is related to'
    real_relations_list_label_names = relations_list_label.copy()
    for i in range(len(relations_list_label)): # Populate the list of real relation names
        if relations_list_label[i] in label_dict.keys():
            real_relations_list_label_names[i] = label_dict[relations_list_label[i]]

    # List of start node
    start_node_list = []
    for item in concepts:
        if item['start']['label'] not in start_node_list:
            start_node_list.append(item['start']['label'])

    # List for each relation
    concept_network = {}
    
    for item in relations_list_label:
        concept_network[item] = [] # Initiate a list as value for each key/relation

    for item in relations_list_label:
        for edge in concepts:
            if item == edge['rel']['label']:
                obj_to_append = dict((i, edge[i]) for i in ('start', 'end', 'rel', 'weight')) # Only take the important stuff
                concept_network[item].append(obj_to_append)

    # Problem: sometimes the word queried is 'start', other times it is 'end'
    word_start_or_end = {}

    for i in range(len(relations_list_label)):
        for j in range(len(concept_network[relations_list_label[i]])):
            if word in concept_network[relations_list_label[i]][j]['end']['label']:
                word_start_or_end[relations_list_label[i]] = 'end'
            else:
                word_start_or_end[relations_list_label[i]] = 'start'

    # Return
    return render_template("related.html", word_suggest=word_suggest, Related_words_data=Related_words_data, relations_list_label=relations_list_label, concept_network=concept_network, \
            real_relations_list_label_names=real_relations_list_label_names, word_start_or_end=word_start_or_end, original_word=original_word, word=word, wordPath_list=wordPath_list)

@app.route("/aboutUs")
def aboutUs():
    return "abc"

@app.route("/interpret")
def interpret():
    return "Interpret"

@app.route("/navbarSearch")
def navbarSearch():
    wordPath_list.clear()
    navbar_word = request.args.get("word")
    return redirect(f"/synonyms?word={navbar_word}")

if __name__ == "__main__":
    app.run()