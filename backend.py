 
import logging
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import pymongo
import uuid
import os  
from openai import AzureOpenAI  

logger = logging.getLogger()
logger.setLevel(logging.INFO)


endpoint = os.getenv("ENDPOINT_URL")
deployment = os.getenv("DEPLOYMENT_NAME")  
search_endpoint = os.getenv("SEARCH_ENDPOINT")  
search_key = os.getenv("SEARCH_KEY")  
search_index = os.getenv("SEARCH_INDEX_NAME")  
subscription_key = os.getenv("AZURE_OPENAI_API_KEY")


# Download necessary NLTK datasets if not already downloaded
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
 
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')
 
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
 
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')
 
# Initialize lemmatizer and stopwords
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))
 
# MongoDB connection details (use your actual connection string)
MONGO_URI = "mongodb://beyondhumancosmosmongodb:8igjEd0wSlV0jFCiAIcDDoQQcSu0xnGXLvP8nGqOM1ttlLH4lyucqnu88vL6lzhoWyK7VG6GSNfKACDb82ADfw==@beyondhumancosmosmongodb.mongo.cosmos.azure.com:10255/?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000&appName=@beyondhumancosmosmongodb@"  # Store this in the environment variable or hard-code for testing
DATABASE_NAME = "BeyondHuman_CosmosMongodb"
COLLECTION_NAME = "cosmosmongodbcollection"
 
# Initialize MongoDB client
client = pymongo.MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]
def generate_unique_key_value():
    return str(uuid.uuid4())
# Define function to lemmatize a sentence
def lemmatize_sentence(sentence: str):
    """Lemmatizes words from a sentence and removes stopwords."""
    words = word_tokenize(sentence)
    return [lemmatizer.lemmatize(word.lower()) for word in words if word.lower() not in stop_words and word.isalpha()]

def chatgptcall(query):
    # Initialize Azure OpenAI client with key-based authentication
    client = AzureOpenAI(  
        azure_endpoint=endpoint,  
        api_key=subscription_key,  
        api_version="2024-05-01-preview",  
    )  
        
    # Prepare the chat prompt  
    chat_prompt = [
        {
            "role": "system",
            "content": query
        }
    ]  
    
    completion = client.chat.completions.create(
        model = deployment,
        temperature = 0.5,
        max_tokens = 1000,
        messages = chat_prompt
    )

    return completion.choices[0].message.content
 
def process_sentence(sentence: str,input_text: str):
    """Processes the sentence, checking for existing data in MongoDB or inserting new data."""
    # Lemmatize the sentence
    root_words = lemmatize_sentence(input_text)
 
    # Join the root words into a single string separated by hyphens
    root_words_str = '-'.join(root_words)
 
    # Check if the lemmatized root words exist in MongoDB
    existing_document = collection.find_one({"root_words": root_words_str})
 
    if existing_document:
        # If document exists, return the value field (assuming the value field is 'value')
        logging.info("Prompt answer was already present in DB so directly fetched from it")
        value_field = existing_document.get('value', 'No value found')
        # return f'{{"root_words": "{root_words_str}", "found_in_db": true, "value": "{value_field}"}}'
        return value_field
    else:
        # If document does not exist, insert a new document
        try:
            chatgptresponse = chatgptcall(sentence)
            unique_key_value = generate_unique_key_value()
            document = {
                "sentence": sentence,
                "root_words": root_words_str,
                "value": chatgptresponse,  # Placeholder value
                "uniqueKey": unique_key_value  # Ensure this field is included
            }
            collection.insert_one(document)  # Insert the document into MongoDB
            # logging.info(f"Document inserted: {document}")
            logging.info("Prompt answer was not present in DB so fetched from chat gpt response")

            return chatgptresponse
            # return f'{{"root_words": "{root_words_str}", "found_in_db": false}}'
        except Exception as e:
            logging.error(f"Error inserting document to MongoDB: {str(e)}")
            return '{"error": "Error inserting document to MongoDB."}'
 
# Main function to run the script
def driver_function(sentence,input_text):
    # Example sentence input (this could be taken from user input or another source)
    # sentence = input("Enter a sentence to lemmatize and process: ")
 
    if not sentence:
        print('Error: Please provide a sentence.')
        return
 
    # Process the sentence
    result = process_sentence(sentence,input_text)
 
    # Print the result
    return result