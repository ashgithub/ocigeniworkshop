import oci, os, json 

# sdk:  https://github.com/oracle/oci-python-sdk/blob/22fd62c8dbbd1aaed6b75754ec1ba8a3c16a4e5a/src/oci/ai_language/ai_service_language_client.py#L584
# documentation: https://docs.oracle.com/en-us/iaas/language/using/home.htm
# #oci_ai_lang_service_users or #igiu-innovation-lab slack channels
# Small language models can be a good choice for simple tasks. 

# if you have errors running sample code reach out for help in #igiu-ai-learning

#####
#make sure your sandbox.json file is setup for your environment. You might have to specify the full path depending on  your `cwd` 
#####
SANDBOX_CONFIG_FILE = "sandbox.json"

test_string = "Oracle Cloud Infrastructure is built for enterprises seeking higher performance, lower costs, and easier cloud migration for their applications. Customers choose Oracle Cloud Infrastructure over AWS for several reasons: First, they can consume cloud services in the public cloud or within their own data center with Oracle Dedicated Region Cloud@Customer. Second, they can migrate and run any workload as is on Oracle Cloud, including Oracle databases and applications, VMware, or bare metal servers. Third, customers can easily implement security controls and automation to prevent misconfiguration errors and implement security best practices. Fourth, they have lower risks with Oracle’s end-to-end SLAs covering performance, availability, and manageability of services. Finally, their workloads achieve better performance at a significantly lower cost with Oracle Cloud Infrastructure than AWS. Take a look at what makes Oracle Cloud Infrastructure a better cloud platform than AWS."
compartmentId = None

def load_config(config_path):
    """Load configuration from a JSON file."""
    try:
        with open(config_path, 'r') as f:
                return json.load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in configuration file '{config_path}': {e}")
        return None
    
def createLanguageClient(config_path, profile ="default"):
    config = oci.config.from_file(
        config_path, profile)
    return oci.ai_language.AIServiceLanguageClient(config)


def createTextDocument(key_, data, language_code_="en"):
    return oci.ai_language.models.TextDocument(
        key=key_,
        text=data,
        language_code=language_code_
    )


def SentimentAnalysis(AI_client, text_document):

    try:
        # Run sentiment analysis on text_document
        detect_language_sentiments_response = AI_client.batch_detect_language_sentiments(
            batch_detect_language_sentiments_details=oci.ai_language.models.BatchDetectLanguageSentimentsDetails(documents=[text_document],compartment_id = compartmentId )
        )
        return detect_language_sentiments_response.data

    # Print service error for debugging
    except Exception as e:
        print(e)
    return


def KeyPhraseExtraction(AI_client, text_document):
    try:
        keyphrase_extraction = AI_client.batch_detect_language_key_phrases(
            batch_detect_language_key_phrases_details=oci.ai_language.models.BatchDetectLanguageKeyPhrasesDetails(documents=[text_document],compartment_id = compartmentId)
        )
        return keyphrase_extraction.data
    except Exception as e:
        print(e)

#https://docs.oracle.com/en-us/iaas/language/using/ner.htm
def NamedEntityExtraction(AI_client, text_document):
    try:
        language_entities = AI_client.batch_detect_language_entities(
            batch_detect_language_entities_details=oci.ai_language.models.BatchDetectLanguageEntitiesDetails(documents=[text_document],compartment_id = compartmentId)
        )

        return language_entities.data

    # Print service error for debugging
    except Exception as e:
        print(e)
    return


def TextClassification(AI_client, text_document):
    try:
        # Run text classification on text_document
        text_classification = AI_client.batch_detect_language_text_classification(
            batch_detect_language_text_classification_details=oci.ai_language.models.BatchDetectLanguageTextClassificationDetails(
                documents=[text_document],compartment_id = compartmentId
            )
        )
        # return the data
        return text_classification.data

    # Print any API errors
    except Exception as e:
        print(e)
    return


def printWelcomeMessage():
    print("Welcome to OCI AI Language example.")


def printDivider():
    # Helper function to print a divider between analysis'
    for i in range(50):
        print("-", end=""),
    print("\n")


def printAllResponses(sentiment_response, key_phrase_response, named_entity_response, text_classification_response):
    print("Sentiment Analysis on text:")
    for i in range(0, len(sentiment_response.documents)):
        for j in range(0, len(sentiment_response.documents[i].aspects)):
            print("\tText: ", sentiment_response.documents[i].aspects[j].text)
            print("\tOverall sentiment: ", sentiment_response.documents[i].aspects[j].sentiment)
            print("\tLength: ", sentiment_response.documents[i].aspects[j].length)
            print("\tOffset: ", sentiment_response.documents[i].aspects[j].offset)

    printDivider()
    print("Key phrase extraction on text:")

    for i in range(len(key_phrase_response.documents)):
        for j in range(len(key_phrase_response.documents[i].key_phrases)):
            print("\tphrase: ", key_phrase_response.documents[i].key_phrases[j].text)
            print("\tscore: ", key_phrase_response.documents[i].key_phrases[j].score)

    printDivider()
    print("Named entity extraction on text:")

    for i in range(len(named_entity_response.documents)):
        for j in range(len(named_entity_response.documents[i].entities)):
            print("\tText: ", named_entity_response.documents[i].entities[j].text)
            print("\tType: ", named_entity_response.documents[i].entities[j].type)
            print("\tSub_Type: ", named_entity_response.documents[i].entities[j].sub_type)
            print("\tLength: ", named_entity_response.documents[i].entities[j].length)
            print("\tOffset: ", named_entity_response.documents[i].entities[j].offset)

    printDivider()
    print("Text classification analysis on text:")
    for i in range(len(text_classification_response.documents)):
        for j in range(len(text_classification_response.documents[i].text_classification)):
            print("\tLabel: ", text_classification_response.documents[i].text_classification[j].label)
            print("\tScore: ", text_classification_response.documents[i].text_classification[j].score)


def runModel(data, config_path, text_model_key, language_code):

    global compartmentId
 
    # readthe sandbox config 
    scfg = load_config(config_path)
    compartmentId = scfg["oci"]["compartment"]

    # Create language client and text document to be analyzed, up to 100 can be analyzed at the same time.
    language_client = createLanguageClient(os.path.expanduser(scfg["oci"]["configFile"]),scfg["oci"]["profile"])
    text_document = createTextDocument(key_=text_model_key, language_code_= language_code, data=data)

    # Grab all responses by the AI client
    sentiment_response = SentimentAnalysis(language_client, text_document)
    key_phrase_response = KeyPhraseExtraction(language_client, text_document)
    named_entity_response = NamedEntityExtraction(language_client, text_document)
    text_classification_response = TextClassification(language_client, text_document)

    printWelcomeMessage()

    printAllResponses(sentiment_response, key_phrase_response, named_entity_response, text_classification_response)


# Run example model
runModel(test_string, SANDBOX_CONFIG_FILE, text_model_key="example", language_code="en")
