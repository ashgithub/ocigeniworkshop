"""
What this file does:
Demonstrates OCI Language service capabilities for natural language processing tasks including sentiment analysis, key phrase extraction, named entity recognition, text classification, and PII masking. Shows how to analyze text documents using various AI-powered language understanding features.

Documentation to reference:
- OCI Language: https://docs.oracle.com/en-us/iaas/language/using/home.htm
- Sentiment Analysis: hhttps://docs.oracle.com/en-us/iaas/Content/language/using/sentment.htm
- Key Phrases: https://docs.oracle.com/en-us/iaas/Content/language/using/key_ref.htm
- Named Entities: https://docs.oracle.com/en-us/iaas/Content/language/using/ner.htm
- Text Classification: https://docs.oracle.com/en-us/iaas/Content/language/using/text-class.htm
- PII Detection: https://docs.oracle.com/en-us/iaas/Content/language/using/pii.htm
- OCI Python SDK: https://github.com/oracle/oci-python-sdk/tree/master/src/oci/ai_language

Relevant slack channels:
- #oci_ai_lang_service_users: for questions on OCI Language service
- #igiu-innovation-lab: general discussions on your project
- #igiu-ai-learning: help with sandbox environment or help with running this code

Env setup:
- sandbox.yaml: Contains OCI config, compartment, and other details.
- .env: Load environment variables (e.g., API keys if needed).

How to run the file:
uv run llm/oci_language.py

Comments to important sections of file:
- Step 1: Load configuration and initialize client.
- Step 2: Prepare text document for analysis.
- Step 3: Perform sentiment analysis.
- Step 4: Extract key phrases.
- Step 5: Perform named entity recognition.
- Step 6: Classify text content.
- Step 7: Apply PII masking.
- Step 8: Display all analysis results.
"""

import oci
import os
import json

from dotenv import load_dotenv
from envyaml import EnvYAML

# Step 1: Load configuration and initialize client
SANDBOX_CONFIG_FILE = "sandbox.yaml"
load_dotenv()

# Sample text for NLP analysis (contains various entities and sentiments)
SAMPLE_TEXT = """Oracle Cloud Infrastructure is built for enterprises seeking higher performance, lower costs, and easier cloud migration for their applications. Customers choose Oracle Cloud Infrastructure over AWS for several reasons: First, they can consume cloud services in the public cloud or within their own data center with Oracle Dedicated Region Cloud@Customer. Second, they can migrate and run any workload as is on Oracle Cloud, including Oracle databases and applications, VMware, or bare metal servers. Third, customers can easily implement security controls and automation to prevent misconfiguration errors and implement security best practices. Fourth, they have lower risks with Oracle's end-to-end SLAs covering performance, availability, and manageability of services. Finally, their workloads achieve better performance at a significantly lower cost with Oracle Cloud Infrastructure than AWS. Take a look at what makes Oracle Cloud Infrastructure a better cloud platform than AWS. Contact Oracle at 1-800.555.1234 or at 123, oracle way, redwood shores, ca-94065"""

# Global compartment ID (set during execution)
compartment_id = None

def load_config(config_path):
    """Load configuration from a YAML file."""
    try:
        with open(config_path, 'r') as f:
                return EnvYAML(config_path)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
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


def perform_sentiment_analysis(language_client, text_document):
    """Step 3: Perform sentiment analysis on the text document."""
    try:
        sentiment_response = language_client.batch_detect_language_sentiments(
            batch_detect_language_sentiments_details=oci.ai_language.models.BatchDetectLanguageSentimentsDetails(
                documents=[text_document],
                compartment_id=compartment_id
            )
        )
        return sentiment_response.data
    except Exception as e:
        print(f"Error in sentiment analysis: {e}")
        return None


def perform_key_phrase_extraction(language_client, text_document):
    """Step 4: Extract key phrases from the text document."""
    try:
        key_phrase_response = language_client.batch_detect_language_key_phrases(
            batch_detect_language_key_phrases_details=oci.ai_language.models.BatchDetectLanguageKeyPhrasesDetails(
                documents=[text_document],
                compartment_id=compartment_id
            )
        )
        return key_phrase_response.data
    except Exception as e:
        print(f"Error in key phrase extraction: {e}")
        return None


def perform_named_entity_recognition(language_client, text_document):
    """Step 5: Perform named entity recognition (NER) on the text document."""
    try:
        ner_response = language_client.batch_detect_language_entities(
            batch_detect_language_entities_details=oci.ai_language.models.BatchDetectLanguageEntitiesDetails(
                documents=[text_document],
                compartment_id=compartment_id
            )
        )
        return ner_response.data
    except Exception as e:
        print(f"Error in named entity recognition: {e}")
        return None


def perform_text_classification(language_client, text_document):
    """Step 6: Classify the text content into categories."""
    try:
        classification_response = language_client.batch_detect_language_text_classification(
            batch_detect_language_text_classification_details=oci.ai_language.models.BatchDetectLanguageTextClassificationDetails(
                documents=[text_document],
                compartment_id=compartment_id
            )
        )
        return classification_response.data
    except Exception as e:
        print(f"Error in text classification: {e}")
        return None


def perform_pii_masking(language_client, text_document, masking_config):
    """Step 7: Apply PII masking to protect sensitive information."""
    try:
        pii_response = language_client.batch_detect_language_pii_entities(
            batch_detect_language_pii_entities_details=oci.ai_language.models.BatchDetectLanguagePiiEntitiesDetails(
                documents=[text_document],
                compartment_id=compartment_id,
                masking=masking_config
            )
        )
        return pii_response.data
    except Exception as e:
        print(f"Error in PII masking: {e}")
        return None
    

def printWelcomeMessage():
    print("Welcome to OCI AI Language example.")


def printDivider():
    # Helper function to print a divider between analysis'
    for i in range(50):
        print("-", end=""),
    print("\n")


def printAllResponses(sentiment_response, key_phrase_response, named_entity_response, text_classification_response, pii_masking_response):
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


    printDivider()
    print("PII masking on text:")
    for i in range(len(pii_masking_response.documents)):
        for j in range(len(pii_masking_response.documents[i].entities)):
            print("\tScore: ", pii_masking_response.documents[i].entities[j])

def display_analysis_results(sentiment_response, key_phrase_response, ner_response, classification_response, pii_response):
    """Step 8: Display all analysis results in a formatted way."""
    print("Welcome to OCI Language Service NLP Analysis Demo")
    print("=" * 60)

    # Sentiment Analysis Results
    print("\n📊 SENTIMENT ANALYSIS:")
    print("-" * 30)
    if sentiment_response and sentiment_response.documents:
        for doc in sentiment_response.documents:
            for aspect in doc.aspects:
                print(f"  Text: '{aspect.text}'")
                print(f"  Sentiment: {aspect.sentiment}")
                print(f"  Length: {aspect.length}, Offset: {aspect.offset}")
    else:
        print("  No sentiment data available")

    # Key Phrase Extraction Results
    print("\n🔑 KEY PHRASE EXTRACTION:")
    print("-" * 30)
    if key_phrase_response and key_phrase_response.documents:
        for doc in key_phrase_response.documents:
            for phrase in doc.key_phrases:
                print(f"  Phrase: '{phrase.text}' (Score: {phrase.score:.3f})")
    else:
        print("  No key phrases found")

    # Named Entity Recognition Results
    print("\n🏷️  NAMED ENTITY RECOGNITION:")
    print("-" * 30)
    if ner_response and ner_response.documents:
        for doc in ner_response.documents:
            for entity in doc.entities:
                print(f"  Text: '{entity.text}'")
                print(f"  Type: {entity.type}, Sub-type: {entity.sub_type}")
                print(f"  Length: {entity.length}, Offset: {entity.offset}")
    else:
        print("  No named entities found")

    # Text Classification Results
    print("\n📂 TEXT CLASSIFICATION:")
    print("-" * 30)
    if classification_response and classification_response.documents:
        for doc in classification_response.documents:
            for classification in doc.text_classification:
                print(f"  Label: {classification.label} (Score: {classification.score:.3f})")
    else:
        print("  No classification results")

    # PII Masking Results
    print("\n🔒 PII MASKING:")
    print("-" * 30)
    if pii_response and pii_response.documents:
        for doc in pii_response.documents:
            print(f"  Masked entities found: {len(doc.entities)}")
            # Note: PII response structure may vary, adjust display as needed
    else:
        print("  No PII entities detected")

    print("\n" + "=" * 60)


def run_nlp_analysis(text_content, config_path, document_key="sample_doc", language="en"):
    """Main function to run complete NLP analysis pipeline."""
    global compartment_id

    # Load configuration
    config_data = load_config(config_path)
    if not config_data:
        print("Failed to load configuration")
        return

    compartment_id = config_data["oci"]["compartment"]

    # Step 2: Prepare text document for analysis
    language_client = createLanguageClient(
        os.path.expanduser(config_data["oci"]["configFile"]),
        config_data["oci"]["profile"]
    )
    text_document = createTextDocument(
        key_=document_key,
        data=text_content,
        language_code_=language
    )

    # Perform all NLP analyses
    sentiment_response = perform_sentiment_analysis(language_client, text_document)
    key_phrase_response = perform_key_phrase_extraction(language_client, text_document)
    ner_response = perform_named_entity_recognition(language_client, text_document)
    classification_response = perform_text_classification(language_client, text_document)

    # Configure PII masking (mask all detected PII entities)
    pii_masking_config = {
        "ALL": oci.ai_language.models.PiiEntityMask(
            mode="MASK",
            masking_character="*",
            leave_characters_unmasked=4,
            is_unmasked_from_end=True
        )
    }
    pii_response = perform_pii_masking(language_client, text_document, pii_masking_config)

    # Display results
    display_analysis_results(
        sentiment_response,
        key_phrase_response,
        ner_response,
        classification_response,
        pii_response
    )


# Main execution
if __name__ == "__main__":
    print("🔍 Starting OCI Language Service NLP Analysis...")
    run_nlp_analysis(SAMPLE_TEXT, SANDBOX_CONFIG_FILE)

    # Additional experimentation ideas:
    # - Try different texts with various sentiments, entities, and PII
    # - Experiment with different languages (supported: en, es, pt, etc.)
    # - Test batch processing with multiple documents
    # - Customize PII masking rules for different entity types
    # - Use the results for downstream processing or data enrichment
