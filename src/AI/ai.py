import nltk
import string
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

f = open("src/AI/Bee Movie Script.txt", "r", errors="ignore")

raw_doc = f.read()
raw_doc = raw_doc.lower()
nltk.download("punkt")
nltk.download("wordnet")
sentence_tokens = nltk.sent_tokenize(raw_doc)
word_tokens = nltk.word_tokenize(raw_doc)
Stemmer = nltk.stem.WordNetLemmatizer()

def LemTokens(tokens):
  return [Stemmer.lemmatize(token) for token in tokens]


remove_punctuation_dict = dict(
    (ord(punct), None) for punct in string.punctuation)


def LemNormalize(text):
  return LemTokens(
      nltk.word_tokenize(text.lower().translate(remove_punctuation_dict)))


Greet_Inputs = ("hello", "hi", "greetings", "sup", "what's up", "hey")
Greet_Responses = [
    "hi", "hey", "*nods*", "hi there", "hello",
    "I am glad! You are talking to me"
]


def greet(sentence):

  for word in sentence.split():
    if word.lower() in Greet_Inputs:
      return random.choice(Greet_Responses)


def response(user_response):
  robo1_response = ''
  TfidfVec = TfidfVectorizer(tokenizer=LemNormalize, stop_words='english')
  tfidf = TfidfVec.fit_transform(sentence_tokens)
  vals = cosine_similarity(tfidf[-1], tfidf)
  idx = vals.argsort()[0][-2]
  flat = vals.flatten()
  flat.sort()
  req_tfidf = flat[-2]
  if (req_tfidf == 0):
    robo1_response = robo1_response + "I am sorry! I don't understand you"
    return robo1_response
  else:
    robo1_response = robo1_response + sentence_tokens[idx]
    return robo1_response

def get_reponse(input:str):
  global word_tokens
  global sentence_tokens

  user_input = input
  user_input = user_input.lower()

  if (greet(user_input) != None):
    bot_response = greet(user_input)
  else:
    sentence_tokens.append(user_input)
    word_tokens = word_tokens + nltk.word_tokenize(user_input)
    bot_response = response(user_input)
    sentence_tokens.remove(user_input)

  return bot_response
