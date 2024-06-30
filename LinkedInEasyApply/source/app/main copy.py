import yaml
import time  # Import time module for sleep function
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from validate_email import validate_email
from webdriver_manager.chrome import ChromeDriverManager
from linkedineasyapply import LinkedinEasyApply


def init_browser():
    browser_options = Options()
    options = [
        '--disable-blink-features',
        '--no-sandbox',
        '--start-maximized',
        '--disable-extensions',
        '--ignore-certificate-errors',
        '--disable-blink-features=AutomationControlled',
        '--remote-debugging-port=9222'
    ]

    for option in options:
        browser_options.add_argument(option)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=browser_options)
    driver.implicitly_wait(1)  # wait time in seconds to allow loading of elements
    driver.set_window_position(0, 0)
    driver.maximize_window()
    return driver


def validate_yaml():
    with open("/Users/admin1/EasyApplyBot/LinkedInEasyApply/source/config.yaml", 'r') as stream:
        try:
            parameters = yaml.safe_load(stream)
            print(parameters)
        except yaml.YAMLError as exc:
            raise exc

    mandatory_params = ['email', 'password', 'disableAntiLock', 'remote', 'lessthanTenApplicants',
                        'experienceLevel', 'jobTypes', 'date', 'positions', 'locations', 'residentStatus',
                        'distance', 'outputFileDirectory', 'checkboxes', 'universityGpa', 'languages',
                        'experience', 'personalInfo', 'eeo', 'uploads']

    for param in mandatory_params:
        if param not in parameters:
            raise ValueError(f"Parameter '{param}' is missing in config.yaml")

    assert validate_email(parameters['email'])
    assert parameters['password']
    assert isinstance(parameters['disableAntiLock'], bool)
    assert isinstance(parameters['remote'], bool)
    assert isinstance(parameters['lessthanTenApplicants'], bool)
    assert isinstance(parameters['residentStatus'], bool)
    assert parameters['experienceLevel']
    assert any(parameters['experienceLevel'].values())
    assert parameters['jobTypes']
    assert any(parameters['jobTypes'].values())
    assert parameters['date']
    assert any(parameters['date'].values())
    assert parameters['distance'] in {0, 5, 10, 25, 50, 100}
    assert parameters['positions']
    assert parameters['locations']
    assert 'resume' in parameters['uploads']
    assert parameters['checkboxes']
    assert isinstance(parameters['checkboxes']['driversLicence'], bool)
    assert isinstance(parameters['checkboxes']['requireVisa'], bool)
    assert isinstance(parameters['checkboxes']['legallyAuthorized'], bool)
    assert isinstance(parameters['checkboxes']['certifiedProfessional'], bool)
    assert isinstance(parameters['checkboxes']['urgentFill'], bool)
    assert isinstance(parameters['checkboxes']['commute'], bool)
    assert isinstance(parameters['checkboxes']['backgroundCheck'], bool)
    assert isinstance(parameters['checkboxes']['securityClearance'], bool)
    assert 'degreeCompleted' in parameters['checkboxes']
    assert isinstance(parameters['universityGpa'], (int, float))

    # Validate languages
    languages = parameters.get('languages', {})
    valid_language_types = {'none', 'conversational', 'professional', 'native or bilingual'}

    for lang_key, lang_value in languages.items():
        assert lang_value.lower() in valid_language_types, f"Invalid language type '{lang_value}' for '{lang_key}'"

    # Validate experience levels, personal info, eeo, and other parameters as before

    return parameters


def handle_linkedIn_verification(driver):
    # Check if verification message appears
    try:
        verify_message = driver.find_element_by_xpath("//h1[contains(text(), 'Check your LinkedIn app')]")
        if verify_message.is_displayed():
            print("Verification message found. Please verify in your LinkedIn app.")
            # Add code here to handle verification in LinkedIn app manually
            # You may need to pause the script and prompt the user to verify in the app
            # input("Press Enter after verifying in LinkedIn app...")
            time.sleep(10)  # Add a delay to allow the user to complete verification
    except:
        pass  # If verification message is not found, continue


if __name__ == '__main__':
    parameters = validate_yaml()
    browser = init_browser()

    bot = LinkedinEasyApply(parameters, browser)
    # bot.login()

    # Handle LinkedIn verification if needed
    # handle_linkedIn_verification(browser)

    # bot.security_check()
    bot.start_applying()

    # Optionally, add further steps after applying
    browser.quit()
