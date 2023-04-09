from pdfminer.high_level import extract_text
import nltk
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tree import Tree
import re
import requests
import spacy

# load pre-trained model
nlp = spacy.load('en_core_web_sm')

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')
nltk.download('stopwords')

data=extract_text('Abhimanyu_July22.pdf')

## to store the final json object
dict = {}

## to extract the name from the pdf
nltk_results = ne_chunk(pos_tag(word_tokenize(data)))
names=[]
for nltk_result in nltk_results:
    if type(nltk_result) == Tree:
        name = ''
        for nltk_result_leaf in nltk_result.leaves():
            name += nltk_result_leaf[0] + ' '
        # print ('Type: ', nltk_result.label(), 'Name: ', name)
        names.append(name)
    
dict['Name'] = names[0].strip()

## to extract the contact number from the pdf
PHONE_REG = re.compile(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]')
contact_number=[]
phone = re.findall(PHONE_REG, data)
if phone:
    number = ''.join(phone[0])
    if data.find(number) >= 0 and len(number) < 16:
        contact_number.append(number)

dict['Contact Number'] = contact_number

## to extract the email from the pdf
EMAIL_REG = re.compile(r'[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+')
email = re.findall(EMAIL_REG, data)

dict['Email'] = email

## to extract skills from resume
def skill_exists(skill):
    url = f'https://api.apilayer.com/skills?q={skill}'
    headers = {'apikey': 'QqgCEru1OQYvNJnn71oz8yd1YxHhbhmy'}
    response = requests.request('GET', url, headers=headers)
    result = response.json()
 
    if response.status_code == 200:
        return len(result) > 0 and result[0].lower() == skill.lower()
    raise Exception(result.get('message'))
 
 
def extract_skills(input_text):
    stop_words = set(nltk.corpus.stopwords.words('english'))
    word_tokens = nltk.tokenize.word_tokenize(input_text)
 
    # remove the stop words
    filtered_tokens = [w for w in word_tokens if w not in stop_words]
 
    # remove the punctuation
    filtered_tokens = [w for w in word_tokens if w.isalpha()]
 
    # generate bigrams and trigrams (such as artificial intelligence)
    bigrams_trigrams = list(map(' '.join, nltk.everygrams(filtered_tokens, 2, 3)))
 
    # we create a set to keep the results in.
    found_skills = set()
 
    # we search for each token in our skills database
    for token in filtered_tokens:
        if skill_exists(token.lower()):
            found_skills.add(token)
 
    # we search for each bigram and trigram in our skills database
    for ngram in bigrams_trigrams:
        if skill_exists(ngram.lower()):
            found_skills.add(ngram)
 
    return found_skills

skills=extract_skills(data)

dict['Skills'] = skills

## to extract education details from resume

organizations = []

# first get all the organization names using nltk
nlp_text = nlp(data)
organizations = [sent.text.strip() for sent in nlp_text.sents]

education = set()
edu_flag=False
sections = ['skills', 'education', 'experience', 'project', 'achievements']
sections.remove('education')
for org in organizations:
    if not edu_flag and org.lower().find("education") >= 0:
        education.add(org[org.lower().find('education'):])
        edu_flag=True
    elif edu_flag:
        break_flag = False
        for val in sections:
            if org.lower().find(val) >= 0:
                break_flag=True
                break
        if break_flag:
            break
        education.add(org)

dict['Education'] = education

## to extract experience details from resume
experience = set()
exp_flag=False
sections = ['skills', 'education', 'experience', 'project', 'achievements']
sections.remove('experience')
for org in organizations:
    if not exp_flag and ( org.lower().find("experience")>=0):
        experience.add(org[org.lower().find('experience'):])
        exp_flag=True
    elif exp_flag:
        break_flag = False
        for val in sections:
            if org.lower().find(val) >= 0:
                break_flag=True
                break
        if break_flag:
            break
        experience.add(org)

dict['Experience'] = experience

##to extract projects from resume
projects = set()
project_flag=False
sections = ['skills', 'education', 'experience', 'project', 'achievements']
sections.remove('project')
for org in organizations:
    if not project_flag and org.lower().find("projects")>=0:
        projects.add(org[org.lower().find("projects"):])
        project_flag=True
    elif project_flag:
        break_flag = False
        for val in sections:
            if org.lower().find(val) >= 0:
                break_flag=True
                break
        if break_flag:
            break
        projects.add(org)

dict['Projects'] = projects

##to extract achievements and awards from resume
achievements = set()
achievements_flag=False
sections = ['skills', 'education', 'experience', 'project', 'achievements']
sections.remove('achievements')
for org in organizations:
    if not achievements_flag and org.lower().find("achievements")>=0:
        achievements.add(org[org.lower().find("achievements"):])
        achievements_flag=True
    elif achievements_flag:
        break_flag = False
        for val in sections:
            if org.lower().find(val) >= 0:
                break_flag=True
                break
        if break_flag:
            break
        achievements.add(org)

dict['Achievements'] = achievements
print(dict)