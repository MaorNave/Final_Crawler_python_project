import pandas as pd
from Main import *
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from tqdm import tqdm
import yaml
import os
import pickle
import urllib.request
import re
from PIL import Image
import keyboard
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import numpy as np
import time
from genderize import Genderize
from datetime import datetime
from selenium.webdriver.common.by import By
global data_config

# General Core functions

# Function that calls relevant functions, retries with sleep for max retries
def call_function_with_retry(function, max_retries, article_path=False):
    retries = 0
    while retries < max_retries:
        try:
            driver.window_handles
        except:
            if retries > 0:
                driver.close()
                driver.quit()
                time.sleep(0.5)
            call_driver()
        if len(driver.window_handles) != 0:
            driver.switch_to.window(driver.window_handles[0])
        if article_path == False:
            res = function()
        else:
            res = function(article_path)

        if res:
            break
        else:
            print(f"Retrying with function: {function}...")
            retries += 1

# Initialize the Selenium Chrome driver
def call_driver():
    global driver
    global wait
    global genderize
    chrome_service = Service(af.data_config['chrome_service_path'])
    driver = webdriver.Chrome(service=chrome_service)
    driver.maximize_window()
    wait = WebDriverWait(driver, 45)
    genderize = Genderize()

# Press a keyboard key to prevent screen lock
def press_key():
    keyboard.press('up')
    time.sleep(0.5)
    keyboard.release('up')
    time.sleep(5)

# Check if a folder exists, and create if not
def folder_exists(folder_name):
    if os.path.isdir(folder_name) == False:
        os.mkdir(folder_name)
        print(f'Created a directory: {folder_name}')
    else:
        print(f'Directory {folder_name} already exists')
        pass

# Load config file
def yaml_loader(path):
    with open(path, "r") as yaml_file:
        data = yaml.safe_load(yaml_file)
    yaml_file.close()
    return data

# Dump data into a YAML file
def yaml_dumper(path, data):
    with open(path, "w") as yaml_file:
        yaml.dump(data, yaml_file)
    yaml_file.close()

# Load data from a pickled file
def pickle_loader(path):
    with open(path, 'rb') as file:
        loaded_object = pickle.load(file)
    file.close()
    return loaded_object

# Dump data into a pickled file
def pickel_dumper(path, data):
    with open(path, 'wb') as file:
        pickle.dump(data, file)
    file.close()

# Find element by method and path, then click
def find_element_click(method, path):
    element = wait.until(EC.presence_of_element_located((method, path)))
    element.click()

# Find element by XPath and clear its content
def find_element_xpath_clear(path):
    element = wait.until(EC.presence_of_element_located((By.XPATH, path)))
    element.clear()
    return element

def full_articles_links_list_creator(rev_articles_links_paths_list):
    """
    Create a list of full article links from paths to individual article lists.

    Args:
        rev_articles_links_paths_list (list): List of paths to article lists.

    Returns:
        list: List of unique article links.
    """
    full_articels_links_list = []
    for articel_list_path in rev_articles_links_paths_list:
        articel_data_list = yaml_loader(articel_list_path)
        for article_link in articel_data_list:
            if article_link not in full_articels_links_list:
                full_articels_links_list.append(article_link)
            else:
                continue

    return full_articels_links_list


def full_names_checker(rev_authors_list):
    """
    Check if the first and last author names in the list are different.

    Args:
        rev_authors_list (list): List of author elements.

    Returns:
        bool: True if first and last names are different, False otherwise.
    """
    result = True
    first_full_name = rev_authors_list[0].text.split('\n')[0]
    last_full_name = rev_authors_list[-1].text.split('\n')[0]
    if first_full_name == last_full_name:
        result = False

    return result


def text_cleaner(text):
    """
    Clean the input text by removing specified characters and extra spaces.

    Args:
        text (str): Input text to be cleaned.

    Returns:
        str: Cleaned text.
    """
    chars_to_remove = ['$', '^', '*', '/', '@', '#', '_', '\\', '{', '}', '"']
    for char in chars_to_remove:
        text = text.replace(char, '')
    sentence = text.replace('\n', ' ')
    sentence = re.sub(r'‘|’', "'", sentence)
    sentence = re.sub("'", "", sentence)
    sentence = re.sub(r'\s+', ' ', sentence)
    return sentence


def articels_list_checker(year):
    """
    Check if an articles list file exists for the given year.

    Args:
        year (str): Year to check for.

    Returns:
        bool: True if an articles list file exists for the given year, False otherwise.
    """
    year_text = year.text
    all_files = os.listdir(data_config['articels_list_by_year_folder_name'])
    prefix = "articles_list_up_to_"
    matching_files = [file for file in all_files if file.startswith(prefix)]
    year_file_exist = False
    for file_year_name in matching_files:
        if year_text in file_year_name:
            year_file_exist = True
            return year_file_exist

    return year_file_exist


def jpg_writer(image_url, output_path):
    """
    Write an image from a URL to a specified output path, resizing it to a standard size.

    Args:
        image_url (str): URL of the image to download.
        output_path (str): Path to save the downloaded and resized image.
    """
    target_width = 800
    target_height = 600
    urllib.request.urlretrieve(image_url, output_path)
    image = Image.open(output_path)
    if image.mode != 'RGB':
        image = image.convert('RGB')
    resized_image = image.resize((target_width, target_height))
    resized_image.save(output_path, 'JPEG')
    print('Image saved successfully.')

# Semi-Core functions
def fill_full_article_data_dict(input_df, general_dict, authors_dict, figures_dict, tables_dict):
    """
    Create a dictionary containing all the information for a full article record.

    Args:
        input_df (DataFrame): DataFrame containing article data.
        general_dict (dict): Dictionary containing general article information.
        authors_dict (dict): Dictionary containing author information.
        figures_dict (dict): Dictionary containing figure information.
        tables_dict (dict): Dictionary containing table information.

    Returns:
        dict: Dictionary containing complete article data.
    """
    full_data_article_dict = dict.fromkeys(input_df.columns)
    for i in range(1, 11):
        full_data_article_dict['Figure ' + str(i) + ' Link'] = figures_dict['figures_data']['figure_' + str(i)]['figure_link']
        full_data_article_dict['Figure ' + str(i) + ' caption'] = figures_dict['figures_data']['figure_' + str(i)]['figure_text']
        full_data_article_dict['Table ' + str(i) + ' caption'] = tables_dict['tables_data']['table' + str(i)]['table_text']

    full_data_article_dict['Affiliation of the first author'] = authors_dict['first_author']['affiliation']
    full_data_article_dict['Affiliation of the last author'] = authors_dict['last_author']['affiliation']
    full_data_article_dict['First author gender probability'] = authors_dict['first_author']['gender_probability']
    full_data_article_dict['Gender of the first author'] = authors_dict['first_author']['gender']
    full_data_article_dict['Gender of the last author'] = authors_dict['last_author']['gender']
    full_data_article_dict['Last author gender probability'] = authors_dict['last_author']['gender_probability']
    full_data_article_dict['Name of the first author'] = authors_dict['first_author']['name']
    full_data_article_dict['Name of the last author'] = authors_dict['last_author']['name']
    full_data_article_dict['Number of Figures'] = figures_dict['num_figuers']
    full_data_article_dict['Number of Tables'] = tables_dict['num_tables']
    full_data_article_dict['Number of authors'] = authors_dict['num_authors']
    full_data_article_dict['Paper title'] = general_dict['article_name']
    full_data_article_dict['Publication Date'] = general_dict['publication_date']
    full_data_article_dict['paper DOI'] = general_dict['doi']

    return full_data_article_dict


def get_gender(name):
    """
    Get gender information for a given name.

    Args:
        name (str): Name to determine gender for.

    Returns:
        str, float: Gender and probability of the determined gender.
    """
    names_list = name.split(' ')
    rev_api_names_list = []
    rev_dict_names_list = []
    if 'names_dict.pickel' in os.listdir(data_config['names_dict_path'].split('\\')[0]):
        names_dict = pickle_loader(data_config['names_dict_path'])
    else:
        pickel_dumper(data_config['names_dict_path'], dict())
        names_dict = pickle_loader(data_config['names_dict_path'])
    res_dict = dict.fromkeys(['gender', 'probability', 'count'])

    for name in names_list:
        if name in names_dict.keys():
            rev_dict_names_list.append(name)
        else:
            rev_api_names_list.append(name)
    if len(rev_api_names_list) != 0:
        try:
            gender_predictions_list = genderize.get(rev_api_names_list)
        except:
            print('Problem with API access. Will try again in 24 Hours.')
            time.sleep(88200)
            print('Back after 24 hours.')
            press_key()
            gender_predictions_list = genderize.get(rev_api_names_list)
    else:
        gender_predictions_list = []

    for name_key in rev_dict_names_list:
        if res_dict['probability'] == 0 or res_dict['probability'] is None:
            res_dict['gender'] = names_dict[name_key]['gender']
            res_dict['probability'] = names_dict[name_key]['probability']
            res_dict['count'] = names_dict[name_key]['count']
        elif names_dict[name_key]['probability'] > res_dict['probability'] and names_dict[name_key]['count'] > res_dict['count']:
            res_dict['gender'] = names_dict[name_key]['gender']
            res_dict['probability'] = names_dict[name_key]['probability']
            res_dict['count'] = names_dict[name_key]['count']

    for prediction in gender_predictions_list:
        names_dict[prediction['name']] = dict.fromkeys(['gender', 'probability', 'count'])
        names_dict[prediction['name']]['gender'] = prediction['gender']
        names_dict[prediction['name']]['probability'] = prediction['probability']
        names_dict[prediction['name']]['count'] = prediction['count']
        pickel_dumper(data_config['names_dict_path'], names_dict)

        if res_dict['probability'] == 0 or res_dict['probability'] is None:
            res_dict['gender'] = prediction['gender']
            res_dict['probability'] = prediction['probability']
            res_dict['count'] = prediction['count']
        elif prediction['probability'] >= res_dict['probability'] and prediction['count'] > res_dict['count']:
            res_dict['gender'] = prediction['gender']
            res_dict['probability'] = prediction['probability']
            res_dict['count'] = prediction['count']

    if res_dict['gender'] is None:
        res_dict['gender'] = 'Not Available'
        res_dict['probability'] = 0
    gender = res_dict['gender']
    probability = res_dict['probability']
    return gender, probability



def none_figuers_dict_extractor():
    """
    Creates a dictionary with placeholder information for figures.

    Returns:
    dict: A dictionary containing placeholder information for figures.
    """
    figuers_dict = dict.fromkeys(['num_figuers', 'figures_data'])
    figuers_dict['num_figuers'] = 0
    figuers_dict['figures_data'] = dict()
    for i in range(1, 11):
        figure_key = 'figure_' + str(i)
        figuers_dict['figures_data'].update(
            {figure_key: {'figure_text': 'Not Available', 'figure_link': 'Not Available'}})
    return figuers_dict


def figuers_data_extractor(figures_bar_div, data_year, paper_name):
    """
    Extract figure data from the figures bar div.

    Args:
        figures_bar_div (WebElement): WebElement containing the figures bar div.
        data_year (str): Year of the article data.
        paper_name (str): Name of the article.

    Returns:
        dict: Dictionary containing figure data.
    """
    if figures_bar_div is None:
        return none_figuers_dict_extractor()

    folder_exists(data_config['article_figuers_main_folder_name'])
    folder_exists(os.path.join(data_config['article_figuers_main_folder_name'], data_year))
    rev_paper_name_list = [char for char in paper_name if char.isalpha() or char == ' ']
    rev_paper_name = ''.join(rev_paper_name_list).replace(' ', '_')
    if len(rev_paper_name) > 80:
        rev_paper_name = rev_paper_name[:80]
    folder_exists(os.path.join(data_config['article_figuers_main_folder_name'], data_year, rev_paper_name))
    figuers_dict = dict.fromkeys(['num_figuers', 'figures_data'])
    figuers_dict['figures_data'] = dict()
    for i in range(1, 11):
        figure_key = 'figure_' + str(i)
        figuers_dict['figures_data'].update(
            {figure_key: {'figure_text': 'Not Available', 'figure_link': 'Not Available'}})

    wait.until(EC.presence_of_element_located((By.TAG_NAME, 'i')))
    figures_click_sign = figures_bar_div.find_element(By.TAG_NAME, 'i')
    figures_click_sign.click()
    time.sleep(2)

    figuers_data_div_data_result = False
    while not figuers_data_div_data_result:
        figuers_data_div = figures_bar_div.find_elements(By.CLASS_NAME, 'stats-figures-carousel-container')
        if len(figuers_data_div) == 0:
            figuers_data_div_data_result = False
            sign_in_problem_div_list = figures_bar_div.find_elements(By.CLASS_NAME, 'stats-figures-signInToView')
            if data_config['figuers_problem_check_string'] in figures_bar_div.text:
                print('no figuers')
                os.remove(os.path.join(data_config['article_figuers_main_folder_name'], data_year, rev_paper_name))
                return none_figuers_dict_extractor()
            if len(sign_in_problem_div_list) == 1:
                print('Sign in div continue')
                sign_in_problem_div_list[0].click()
                find_element_click(By.CLASS_NAME,
                                   'stats-Doc_Details_sign_in_seamlessaccess_access_through_institution_name_btn')
                print('Break on sign in problem')
        elif len(figuers_data_div) != 1:
            print('Figures problem - length of full figures div')
        else:
            figuers_data_div_data_result = True

    figuers_full_data_div_list = figuers_data_div[0].find_elements(By.CLASS_NAME, 'hide-mobile')
    rev_figuers_data_div_list = [element for element in figuers_full_data_div_list if
                                 element.find_element(By.CLASS_NAME, 'figure-name').text != '']
    figuers_dict['num_figuers'] = len(rev_figuers_data_div_list)
    figuers_data_div_list = rev_figuers_data_div_list[:10]

    for ind, figure_data_div in enumerate(figuers_data_div_list):
        key_num = str(ind + 1)
        key = 'figure_' + key_num
        figuers_dict['figures_data'][key]['figure_link'] = os.path.join(data_config['article_figuers_main_folder_name'],
                                                                        data_year, rev_paper_name, key + '.jpg')
        figuers_elements_data_load = False
        while not figuers_elements_data_load:
            try:
                figuers_dict['figures_data'][key]['figure_text'] = text_cleaner(
                    figure_data_div.find_element(By.TAG_NAME, 'p').text)
                figure_web_link = figure_data_div.find_element(By.TAG_NAME, 'img').get_attribute('src')
                figuers_elements_data_load = True
            except:
                figuers_elements_data_load = False

        jpg_writer(figure_web_link, figuers_dict['figures_data'][key]['figure_link'])

    time.sleep(0.5)
    figures_click_sign.click()
    return figuers_dict


def tabels_data_extractor(full_text_section_div):
    """
    Extract table data from the full text section div.

    Args:
        full_text_section_div (WebElement): WebElement containing the full text section div.

    Returns:
        dict: Dictionary containing table data.
    """
    tables_data_dict = dict.fromkeys(['num_tables', 'tables_data'])
    tables_data_dict['tables_data'] = dict()

    for i in range(1, 1000000):
        table_id_name = 'table' + str(i)
        try:
            tables_data_dict['tables_data'].update({table_id_name: {'table_text': None}})
            tables_data_dict['tables_data'][table_id_name]['table_text'] = text_cleaner(full_text_section_div.find_element(By.ID, table_id_name).text)
        except:
            del tables_data_dict['tables_data'][table_id_name]
            tables_data_dict['num_tables'] = i - 1
            for j in range(i, 11):
                new_table_id_name = 'table' + str(j)
                tables_data_dict['tables_data'].update({new_table_id_name: {'table_text': 'Not Available'}})
            break
    time.sleep(1)
    return tables_data_dict


def authors_data_extractor(authors_bar_div):
    """
    Extract author data from the authors bar div.

    Args:
        authors_bar_div (WebElement): WebElement containing the authors bar div.

    Returns:
        dict: Dictionary containing author data.
    """
    if authors_bar_div is None:
        authors_dict = dict.fromkeys(['first_author', 'last_author', 'num_authors'])
        authors_dict['num_authors'] = 'Not Available'
        for author_key in ['first_author', 'last_author']:
            authors_dict[author_key] = {
                "name": 'Not Available',
                "gender": 'Not Available',
                "gender_probability": 'Not Available',
                "affiliation": 'Not Available'
            }
        return authors_dict

    authors_dict = dict.fromkeys(['first_author', 'last_author', 'num_authors'])
    wait.until(EC.presence_of_element_located((By.TAG_NAME, 'i')))
    authors_click_sign = authors_bar_div.find_element(By.TAG_NAME, 'i')
    authors_click_sign.click()
    wait.until(EC.presence_of_element_located((By.ID, 'authors')))

    authors_div_list = authors_bar_div.find_elements(By.ID, 'authors')
    authors_div = authors_div_list[1]
    author_data_list = authors_div.find_elements(By.CLASS_NAME, 'col-14-24')
    if len(author_data_list) == 0:
        author_data_list = authors_div.find_elements(By.CLASS_NAME, 'col-24-24')
    authors_dict['num_authors'] = len(author_data_list)
    rev_authors_list = [author_data_list[0], author_data_list[-1]]
    check_name = full_names_checker(rev_authors_list)

    for ind, author in enumerate(rev_authors_list):
        author_data_list = author.text.split('\n')
        if len(author_data_list) != 1:
            author_name = author_data_list[0]
            author_affi = author_data_list[1].lower()
        else:
            author_name = author_data_list[0]
            author_affi = 'Not Available'

        if ind != 0:
            if check_name:
                author_gender, author_probability = get_gender(author_name)
            else:
                pass
        else:
            author_gender, author_probability = get_gender(author_name)

        if ind == 0:
            author_key = 'first_author'
        else:
            author_key = 'last_author'

        authors_dict[author_key] = {
            "name": author_name,
            "gender": author_gender,
            "gender_probability": author_probability,
            "affiliation": text_cleaner(author_affi)
        }
    time.sleep(0.5)
    authors_click_sign.click()
    return authors_dict


def publication_doi_div_exctractor():
    """
    Extract DOI and publication date data from the document page.

    Returns:
        tuple: Tuple containing the DOI data div and publication data div.
    """
    data_found = False
    while not data_found:
        try:
            all_data_divs = driver.find_elements(By.TAG_NAME, 'div')
            doi_data_div = [element for element in all_data_divs if
                            element.get_attribute('class') == 'u-pb-1 stats-document-abstract-doi']
            publication_data_div = [element for element in all_data_divs if
                                    element.get_attribute('class') == 'u-pb-1 doc-abstract-pubdate']
            data_found = True
        except:
            data_found = False
    return doi_data_div, publication_data_div


def cover_articles_deletor(article_link, full_articles_links_list, general_article_data_dict):
    """
    Delete cover articles from the list of full articles links.

    Args:
        article_link (str): Link of the article to be deleted.
        full_articles_links_list (list): List of full articles links.
        general_article_data_dict (dict): Dictionary containing general article data.

    Returns:
        None
    """
    print('exception_cover')
    if 'cover_list.yml' in os.listdir(data_config['cover_list_path'].split('/')[0]):
        is_cover_problem_list = yaml_loader(data_config['cover_list_path'])
    else:
        yaml_dumper(data_config['cover_list_path'], [])
        is_cover_problem_list = yaml_loader(data_config['cover_list_path'])

    if article_link in is_cover_problem_list:
        full_articles_links_list = full_articles_links_list.tolist()
        full_articles_links_list.remove(article_link)
        yaml_dumper(data_config['full_articels_links_list_no_cover_path'], full_articles_links_list)
    else:
        is_cover_problem_list.append(article_link)
        yaml_dumper(data_config['cover_list_path'], np.array(is_cover_problem_list).tolist())
        print(f"deleted {general_article_data_dict['article_name'].lower()} on link : {article_link}")
        full_articles_links_list = full_articles_links_list.tolist()
        full_articles_links_list.remove(article_link)
        yaml_dumper(data_config['full_articels_links_list_no_cover_path'], full_articles_links_list)


# Full-Core functions:
# Function to concat_all_yaml_lists_to_One_df
def build_full_data_df(rev_articles_data_paths_list):
    """
    Build a full data DataFrame from the list of article data paths.

    Args:
        rev_articles_data_paths_list (list): List of article data paths.

    Returns:
        None
    """
    full_df = pd.DataFrame()
    bad_paths = []
    for data_path in tqdm(rev_articles_data_paths_list):
        data_list = yaml_loader(data_path)
        for data_dict in data_list:
            for key, value in data_dict.items():
                if type(value) == str:
                    if 'link' in key.lower():
                        if os.path.exists(value):
                            continue
                        else:
                            if value != 'Not Available':
                                bad_paths.append(value)
                                continue
                            else:
                                continue
        df = pd.DataFrame(data_list)
        full_df = pd.concat([full_df, df])

    full_df_name = 'output.xlsx'
    full_df.to_excel(os.path.join(data_config['full_output_folder'], full_df_name), index=False)
    print(bad_paths)


def extract_article_info(article_path):
    """
    Extracts information from an article and saves it to the appropriate data structures.

    Args:
        article_path (str): Path to the article.

    Returns:
        list: A list containing success status and action (if needed).
    """
    try:
        cover_suspected = False
        general_article_data_dict = dict.fromkeys(['article_name', 'doi', 'publication_date'])
        folder_exists(data_config['articels_data_by_year_folder_name'])
        dict_list = os.listdir(data_config['articels_data_by_year_folder_name'])
        articels_start_index = len(dict_list) * 10 + 1
        if 'full_articels_links_list_no_cover.yml' in os.listdir(
                data_config['full_articels_links_list_no_cover_path'].split('/')[0]):
            full_articles_links_list = np.sort(yaml_loader(data_config['full_articels_links_list_no_cover_path']))
            articles_links_list = full_articles_links_list[articels_start_index:]
        else:
            if articels_start_index == 1:
                articles_links_list = np.sort(article_path)[articels_start_index - 1:]
            else:
                articles_links_list = np.sort(article_path)[articels_start_index:]
        press_key()
        full_article_data_dict_list = []
        input_df = pd.read_excel(data_config['input_df_path'])
        for ind, article_link in enumerate(articles_links_list):
            ind += articels_start_index
            driver.get(article_link)
            try:
                find_element_click(By.XPATH, data_config['url_xpath_dict']['cookies'])
            except:
                pass
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # time.sleep(0.5)
            driver.execute_script("window.scrollTo(0, 0);")
            general_article_data_dict['article_name'] = text_cleaner(wait.until(
                EC.presence_of_element_located((By.XPATH, data_config['url_xpath_dict']['article_title']))).text)
            time.sleep(0.5)
            doi_data_div, publication_data_div = publication_doi_div_exctractor()
            general_article_data_dict['doi'] = doi_data_div[0].find_element(By.TAG_NAME, 'a').get_attribute('href')

            publication_date_str = publication_data_div[0].text.split(":")[1].lstrip()
            general_article_data_dict['publication_date'] = datetime.strptime(publication_date_str, "%d %B %Y")
            data_year = general_article_data_dict['publication_date'].strftime("%Y")

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight*0.975);")
            article_data_div = wait.until(
                EC.presence_of_element_located((By.XPATH, data_config['url_xpath_dict']['article_data_div'])))
            article_data_div_list = article_data_div.find_elements(By.TAG_NAME, 'div')
            full_relevent_article_data_divs = [article_data_innerdiv for article_data_innerdiv in article_data_div_list
                                               if article_data_innerdiv.get_attribute('class') == "accordion-item"]
            relevent_article_data_divs = [element_div for element_div in full_relevent_article_data_divs if
                                          element_div.text.lower() == 'authors' or element_div.text.lower() == 'figures']
            if len(relevent_article_data_divs) == 1:
                data_div_name = relevent_article_data_divs[0].text.lower()
                if data_div_name == 'figures':
                    figures_bar_div = relevent_article_data_divs[0]
                    authors_bar_div = None
                elif data_div_name == 'authors':
                    authors_bar_div = relevent_article_data_divs[0]
                    figures_bar_div = None
            elif len(relevent_article_data_divs) == 0:
                cover_suspected = True
                wait.until(EC.presence_of_element_located((By.ID, 'article')))
                wait.until(EC.presence_of_element_located((By.ID, 'full-text-section')))
                cover_suspected = False
            else:
                if relevent_article_data_divs[0].text.lower() == 'authors':
                    authors_bar_div = relevent_article_data_divs[0]
                    figures_bar_div = relevent_article_data_divs[1]
                else:
                    authors_bar_div = relevent_article_data_divs[1]
                    figures_bar_div = relevent_article_data_divs[0]

            authors_data_dict = authors_data_extractor(authors_bar_div)
            figures_data_dict = figuers_data_extractor(figures_bar_div, data_year,
                                                       general_article_data_dict['article_name'])
            full_text_section_div = wait.until(EC.presence_of_element_located((By.ID, 'full-text-section')))
            tables_data_dict = tabels_data_extractor(full_text_section_div)
            full_article_data_dict = fill_full_article_data_dict(input_df, general_article_data_dict, authors_data_dict,
                                                                 figures_data_dict, tables_data_dict)
            full_article_data_dict_list.append(full_article_data_dict)

            if ind % 10 == 0 and ind != 0:
                file_name = 'output' + '_' + str(ind + 1) + '.yml'
                yaml_dumper(os.path.join(data_config['articels_data_by_year_folder_name'], file_name),
                            full_article_data_dict_list)
                full_article_data_dict_list = []

        print("extract_article_info Function executed successfully!")
        return True

    except Exception as e:
        if cover_suspected:
            cover_articles_deletor(article_link, full_articles_links_list, general_article_data_dict)
        elif not cover_suspected:
            print('exception on not suspected cover papers')
        print(f"extract_article_info Function failed: {e}")
        return False


def crawl_login():
    """
    Performs the login process to the journal website using institutional credentials.

    Returns:
        bool: True if login is successful, False otherwise.
    """
    try:
        activation_stay_key = data_config['activation_stay_key']
        press_key()
        driver.get(data_config['journal_url'])
        # click on browser
        find_element_click(By.XPATH, data_config['url_xpath_dict']['sign_in_button'])
        find_element_click(By.XPATH, data_config['url_xpath_dict']['institution_button'])
        # calls function that clear the input box element inside the browser
        input_element = find_element_xpath_clear(data_config['url_xpath_dict']['institution_input_element'])
        # Type a string into the input element --> same institution for everyone
        input_element.send_keys(data_config['institution_name'])
        press_key()
        # sign in via institution
        find_element_click(By.XPATH, data_config['url_xpath_dict']['institution_selection_first_item'])
        find_element_click(By.XPATH, data_config['url_xpath_dict']['students_button'])
        # puts email add and passwd info
        email_input = find_element_xpath_clear(data_config['url_xpath_dict']['institution_email_input'])
        email_input.send_keys(data_config['login_email_add'])
        email_input.send_keys(Keys.ENTER)
        press_key()
        email_passwd_input = find_element_xpath_clear(data_config['url_xpath_dict']['institution_email_passwd_input'])
        email_passwd_input.send_keys(data_config['login_passwd'])
        email_passwd_input.send_keys(Keys.ENTER)

        # waits to identification from microsoft authenticator
        if activation_stay_key == False:
            find_element_click(By.XPATH, data_config['url_xpath_dict']['sign_in_activation'])
        else:
            find_element_click(By.XPATH, data_config['url_xpath_dict']['sign_in_activation_1'])

        print("crawl_login Function executed successfully!")
        return True
    except  Exception as e:
        print(f"crawl_login Function failed: {e}")
        return False


def crawl_journal():
    """
    Crawls through journal pages, extracting article information and saving article links.

    Returns:
        bool: True if crawling is successful, False otherwise.
    """
    try:
        articles_list = []
        folder_exists(data_config['articels_list_by_year_folder_name'])
        #gets to the relevent browser link
        driver.get(data_config['journal_url'])
        # work by decades
        find_element_click(By.XPATH, data_config['url_xpath_dict']['all_issues_botton'])
        decades_elements_div = wait.until(EC.presence_of_element_located((By.XPATH, data_config['url_xpath_dict']['decades_div'])))
        decades_li_ele = decades_elements_div.find_elements(By.TAG_NAME, "li")
        for decedes_ind, decades_ele in tqdm(enumerate(decades_li_ele[:2])):
            press_key()
            #for a case that there is no cookies pop up
            try:
                find_element_click(By.XPATH, data_config['url_xpath_dict']['cookies'])
            except:
                pass
            decades_ele.click()
            years_elements_div = driver.find_element(By.XPATH, data_config['url_xpath_dict']['years_div'])
            years_li_ele = years_elements_div.find_elements(By.TAG_NAME, "li")
            if decedes_ind == 1:
                years_li_ele = years_li_ele[:5]
            # work on issues by years
            for year in years_li_ele:
                press_key()
                # for a case of that data already outputted for year
                if articels_list_checker(year):
                    continue
                # select relevat year
                year_string = year.text
                print(year_string)
                year.click()
                # gets the isuses volume div
                volume_elements_div = wait.until(EC.presence_of_element_located((By.XPATH, data_config['url_xpath_dict']['volume_div'])))
                volume_li_ele = volume_elements_div.find_elements(By.TAG_NAME, "div")
                for issue_div in volume_li_ele:
                    press_key()
                    # gets element issue from every div
                    try:
                        issue_ele = issue_div.find_element(By.TAG_NAME, "a")
                    except:
                        continue

                    href_issue_link = issue_ele.get_attribute("href")
                    driver.execute_script("window.open()")
                    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                    driver.switch_to.window(driver.window_handles[1])
                    driver.get(href_issue_link)
                    # open all papers on same window
                    find_element_click(By.XPATH,data_config['url_xpath_dict']['items_per_page'])
                    items_ele = wait.until(
                        EC.presence_of_element_located((By.XPATH, data_config['url_xpath_dict']['items_per_page_list'])))
                    relevent_number_items = items_ele.find_elements(By.TAG_NAME, "button")
                    #clicking on the last element for open all issue papers on the same page
                    relevent_number_items[-1].click()
                    # opens papers div on window
                    papers_div = wait.until(EC.presence_of_element_located((By.XPATH, data_config['url_xpath_dict']['papers_div'])))
                    papers_divs_list = papers_div.find_elements(By.TAG_NAME, "div")
                    relevent_papers_divs = [paperdiv for paperdiv in papers_divs_list if paperdiv.get_attribute("class")=="List-results-items"]
                    press_key()
                    for paper_div in tqdm(relevent_papers_divs):
                        # by searching with a tag we are clear from Cover papers which are located in
                        # span tags on List-results-items class divs on the results page
                        # check for cover papers -- only a tags
                        paper_title = paper_div.find_element(By.TAG_NAME, "h2")
                        # for cover articles case
                        try:
                            title_link = paper_title.find_element(By.TAG_NAME, "a").get_attribute("href")
                        except:
                            continue
                        articles_list.append(title_link)

                    #close the session with the new window that opened
                    driver.close()
                    #switch to original window
                    driver.switch_to.window(driver.window_handles[0])
                    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

                articles_list_name = 'articles_list_up_to_'+year_string+'.yml'
                yaml_dumper(os.path.join(data_config['articels_list_by_year_folder_name'], articles_list_name), articles_list)

        print("crawl_journal Function executed successfully!")
        return True

    except Exception as e:
        print(f"crawl_journal Function failed: {e}")
        return False



