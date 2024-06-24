import os
import time
import random
import csv
import logging
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
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def start_driver(self):
        options = webdriver.ChromeOptions()
        options.add_experimental_option("debuggerAddress", "localhost:9222")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        return driver

    def load_cv(self, cv_file_path):
        doc = docx.Document(cv_file_path)
        full_text = [para.text for para in doc.paragraphs]
        return '\n'.join(full_text)

    def login(self):
        self.driver.get("https://secure.indeed.com/account/login")
        time.sleep(random.randint(30, 40))
        # Add login logic if needed

    def apply_to_jobs(self):
        current_page = 0
        while True:
            self.driver.get(f"https://www.indeed.com/jobs?q={self.keyword}&l={self.location}&start={current_page*10}")
            time.sleep(random.randint(5, 10))

            jobs = self.driver.find_elements(By.CLASS_NAME, 'job_seen_beacon')

            if not jobs:
                break

            file_exists = os.path.isfile('links.csv')
            with open('links.csv', mode='a', newline='') as file:
                writer = csv.writer(file)
                if not file_exists:
                    writer.writerow(["Job Title", "Company", "Location", "Link", "Status"])

                for job in jobs:
                    self.process_job(job, writer)

            if not self.click_next_page():
                break
            current_page += 1

    def process_job(self, job, writer):
        try:
            job_title_element = job.find_element(By.CLASS_NAME, 'jobTitle')
            job_title_element.click()
            time.sleep(random.randint(5, 10))
            self.driver.switch_to.window(self.driver.window_handles[-1])
            job_title = job_title_element.text

            company = self.get_company()
            location = self.get_location()
            link = self.driver.current_url
            apply_button, apply_link = self.get_apply_link()

            if apply_link and len(apply_link) < 300:
                self.apply_to_job(job_title, company, location, apply_link, apply_button, writer)
            else:
                self.save_external_job(job_title, company, location, link, apply_link, writer)

            time.sleep(random.randint(5, 10))
        except Exception as e:
            self.log_error(f"Error with job: {e}")
            self.driver.switch_to.window(self.driver.window_handles[0])

    def get_company(self):
        try:
            return self.driver.find_element(By.CSS_SELECTOR, 'a[class*="css-1ioi40n"]').text
        except:
            return self.driver.find_element(By.CSS_SELECTOR, 'div[data-company-name]').text

    def get_location(self):
        try:
            return self.driver.find_element(By.CSS_SELECTOR, 'div[data-testid="inlineHeader-companyLocation"] div').text
        except:
            return self.driver.find_element(By.CSS_SELECTOR, 'div[data-location]').text

    def get_apply_link(self):
        try:
            apply_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'Apply now')]"))
            )
            apply_link = apply_button.get_attribute('href') or \
                   self.driver.find_element(By.XPATH, "//form[contains(@action, 'indeedapply')]").get_attribute('action')
            return apply_button, apply_link
        except Exception as e:
            self.log_error(f"Error retrieving apply link: {e}")
            return None, None

    def apply_to_job(self, job_title, company, location, apply_link, apply_button, writer):
        try:
            print(f"Applying for job: {job_title} at {company} in {apply_link}")
            apply_button.click()
            time.sleep(random.randint(5, 10))
            self.fill_form()
            self.jobs_status.append({'job_title': job_title, 'company': company, 'location': location, 'link': apply_link, 'status': 'applied'})
            self.write_job_status_to_csv(writer)
        except Exception as e:
            self.log_error(f"Failed to apply for job: {e}")

    def save_external_job(self, job_title, company, location, link, apply_link, writer):
        print(f"Saving external job: {job_title} at {company} in {apply_link}")
        self.jobs_status.append({'job_title': job_title, 'company': company, 'location': location, 'link': apply_link or link, 'status': 'external'})
        self.write_job_status_to_csv(writer)

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

    def click_next_page(self):
        try:
            next_page_button = self.driver.find_element(By.CSS_SELECTOR, 'a[data-testid="pagination-page-next"]')
            next_page_button.click()
            time.sleep(random.randint(5, 10))
            return True
        except:
            return False

    def log_error(self, message):
        logging.error(message)
        with open('errors.log', 'a') as f:
            f.write(message + '\n')

    def write_job_status_to_csv(self, writer):
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
