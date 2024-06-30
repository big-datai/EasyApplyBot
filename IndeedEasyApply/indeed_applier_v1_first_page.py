import os
import time
import random
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import openai
from dotenv import load_dotenv
import docx

# Load environment variables from the .env file
load_dotenv()
# Start browser first in debug mode and login
# /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir="/Users/admin1/Library/Application Support/Google/Chrome/Default"
# Access the environment variables
openai.api_key = os.getenv('OPENAI_API_KEY')

class IndeedApplier:
    def __init__(self, username, password, keyword, location, cv_file_path):
        self.username = username
        self.password = password
        self.keyword = keyword
        self.location = location
        self.driver = self.start_driver()
        self.cv = self.load_cv(cv_file_path)
        self.jobs_status = []

    def start_driver(self):
        options = webdriver.ChromeOptions()
        options.add_experimental_option("debuggerAddress", "localhost:9222")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        return driver

    def load_cv(self, cv_file_path):
        doc = docx.Document(cv_file_path)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return '\n'.join(full_text)

    def login(self):
        self.driver.get("https://secure.indeed.com/account/login")
        time.sleep(random.randint(30, 40))
        # Add login logic if needed

    def apply_to_jobs(self):
        self.driver.get(f"https://www.indeed.com/jobs?q={self.keyword}&l={self.location}")
        time.sleep(random.randint(5, 10))

        jobs = self.driver.find_elements(By.CLASS_NAME, 'job_seen_beacon')

        file_exists = os.path.isfile('links.csv')

        with open('links.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["Job Title", "Company", "Location", "Link", "Status"])

            for job in jobs:
                try:
                    try:
                        job_title_element = job.find_element(By.CLASS_NAME, 'jobTitle')
                        job_title_element.click()
                        time.sleep(random.randint(5, 10))
                        self.driver.switch_to.window(self.driver.window_handles[-1])
                        job_title = job_title_element.text
                    except Exception as e:
                        self.log_error(job.get_attribute('outerHTML'))
                        pass

                    try:
                        company = self.driver.find_element(By.CSS_SELECTOR, 'a[class*="css-1ioi40n"]').text
                    except:
                        company = self.driver.find_element(By.CSS_SELECTOR, 'div[data-company-name]').text

                    try:
                        location = self.driver.find_element(By.CSS_SELECTOR, 'div[data-testid="inlineHeader-companyLocation"] div').text
                    except:
                        location = self.driver.find_element(By.CSS_SELECTOR, 'div[data-location]').text

                    link = self.driver.current_url

                    try:
                        apply_button = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'Apply now')]"))
                        )
                        apply_link = apply_button.get_attribute('href')

                        if not apply_link:
                            apply_link = self.driver.find_element(By.XPATH, "//form[contains(@action, 'indeedapply')]").get_attribute('action')

                        if not apply_link:
                            apply_button_wrapper = self.driver.find_element(By.CSS_SELECTOR, 'div.jobsearch-IndeedApplyButton-buttonWrapper button')
                            apply_link = apply_button_wrapper.get_attribute('href')

                        if not apply_link:
                            apply_button_wrapper = self.driver.find_element(By.CSS_SELECTOR, 'div.ia-IndeedApplyButton button')
                            apply_link = apply_button_wrapper.get_attribute('href')

                        if not apply_link:
                            apply_button_wrapper = self.driver.find_element(By.XPATH, "//div[contains(@class, 'jobsearch-ButtonContainer-inlineBlock')]//div[contains(@class, 'jobsearch-IndeedApplyButton')]//div[contains(@class, 'ia-IndeedApplyButton')]//button")
                            apply_link = apply_button_wrapper.get_attribute('href')

                    except Exception as e:
                        print(f"Error retrieving apply link: {e}")
                        apply_link = None
                        pass

                    if apply_link and len(apply_link) < 300:
                        try:
                            print(f"Applying for job: {job_title} at {company} in {apply_link}")
                            apply_button.click()
                            time.sleep(random.randint(5, 10))
                            self.fill_form()
                            self.jobs_status.append({'job_title': job_title, 'company': company, 'location': location, 'link': apply_link, 'status': 'applied'})
                            self.write_job_status_to_csv()
                        except Exception as e:
                            self.log_error(f"Failed to apply for job: {e}")
                            pass
                    else:
                        print(f"Saving external job: {job_title} at {company} in {apply_link}")
                        self.jobs_status.append({'job_title': job_title, 'company': company, 'location': location, 'link': apply_link or link, 'status': 'external'})
                        self.write_job_status_to_csv()

                    time.sleep(random.randint(5, 10))

                except Exception as e:
                    self.log_error(f"Error with job : {e}")
                    self.driver.switch_to.window(self.driver.window_handles[0])
                    pass

    def fill_form(self):
        for i in range(5):  # Assuming there are 5 pages in the application
            try:
                questions = self.driver.find_elements(By.CSS_SELECTOR, 'div[class*="form-question"]')
                for question in questions:
                    label = question.find_element(By.CSS_SELECTOR, 'label').text
                    input_field = question.find_element(By.CSS_SELECTOR, 'input, textarea')
                    response = self.get_response_from_chatgpt(label)
                    input_field.send_keys(response)
                next_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="Next"]'))
                )
                next_button.click()
                time.sleep(random.randint(5, 10))
            except Exception as e:
                self.log_error(f"Error while filling form: {e}")
                break

    def get_response_from_chatgpt(self, question):
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Using the following CV to provide suitable responses for a job application form. CV: {self.cv} \n\nQuestion: {question}",
            max_tokens=150
        )
        return response.choices[0].text.strip()

    def log_error(self, message):
        with open('errors.log', 'a') as f:
            f.write(message + '\n')

    def write_job_status_to_csv(self):
        with open('links.csv', mode='a', newline='') as csvfile:
            fieldnames = ['job_title', 'company', 'location', 'link', 'status']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if csvfile.tell() == 0:
                writer.writeheader()
            for job in self.jobs_status:
                writer.writerow(job)
            self.jobs_status.clear()  # Clear the list after writing to file

    def quit(self):
        self.driver.quit()

if __name__ == "__main__":
    keyword = "director software engineer"
    location = "remote"
    username = os.getenv('USERNAME')
    password = os.getenv('PASSWORD')
    cv_file_path = 'DavePavlovDistinguishedEngineerAIMLv1.docx'

    applier = IndeedApplier(username, password, keyword, location, cv_file_path)
    applier.apply_to_jobs()
    applier.quit()
