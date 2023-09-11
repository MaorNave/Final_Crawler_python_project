from ActivationFunctions import *
import ActivationFunctions as af


# Main function
def main():
    # Load general config for the assignment
    af.data_config = yaml_loader('Input/config.yml')
    max_retries = af.data_config['max_retries']
    print('Session initialized')

    # Calls a function that crawls to login the website:
    if af.data_config['toggel_for_login_crawler']:
        call_function_with_retry(crawl_login, max_retries)
    else:
        pass

    # Call to function that gets all articles from the specified https
    if af.data_config['toggel_for_juornal_crawler']:
        call_function_with_retry(crawl_journal, max_retries)
    else:
        pass

    # Create a full list of total links from relevant issues and years on the journal
    rev_articles_links_names_list = af.os.listdir(af.data_config['articels_list_by_year_folder_name'])
    rev_articles_links_paths_list = [af.os.path.join(af.data_config['articels_list_by_year_folder_name'], article_name)
                                     for article_name in rev_articles_links_names_list]
    full_links_articles_list = full_articles_links_list_creator(rev_articles_links_paths_list)

    # Call to function that gets all articles from the specified https
    # For each article - we save the full article data dict to a list
    if af.data_config['toggel_for_extract_article_info']:
        call_function_with_retry(extract_article_info, max_retries, full_links_articles_list)
    else:
        pass

    # Get all saved data from folder and extract one output file.
    rev_articles_data_names_list = af.os.listdir(af.data_config['articels_data_by_year_folder_name'])
    rev_articles_data_paths_list = [
        af.os.path.join(af.data_config['articels_data_by_year_folder_name'], article_data_name) for article_data_name in
        rev_articles_data_names_list]
    af.build_full_data_df(rev_articles_data_paths_list)

    af.driver.quit()  # Close the browser when done
    print("Driver closed")


if __name__ == "__main__":
    main()
