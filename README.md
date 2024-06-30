# Easy Apply Bots

This repository contains two automated bots to help you apply for jobs on Indeed and LinkedIn. The Indeed Easy Apply bot and the LinkedIn Easy Apply bot will navigate through job postings and apply to them automatically using the credentials and settings provided.

## Features

- Automated job application on Indeed and LinkedIn
- Utilizes Selenium for web scraping and automation
- Configurable using environment variables and a YAML configuration file
- Supports automatic form filling using OpenAI GPT-3

## Prerequisites

- Python 3.12 or later
- Chrome browser installed
- LinkedIn and Indeed accounts

## Installation

1. Clone the repository:

    ```sh
    git clone git@github.com:big-datai/EasyApplyBot.git
    cd EasyApplyBot
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

2. Install the required packages:

    ```sh
    pip install -r requirements.txt
    ```

3. Create a `.env` file in the root directory of the project and add your environment variables:

    ```
    OPENAI_API_KEY=your_openai_api_key
    USERNAME=your_indeed_username
    PASSWORD=your_indeed_password
    ```

4. For the LinkedIn bot, create a `config.yaml` file in the root directory with the following structure:

    ```yaml
    email: your_linkedIn_email
    password: your_linkedIn_password
    positions: ["Software Engineer", "Data Scientist"]
    locations: ["Remote", "New York, NY"]
    uploads:
      resume: "path_to_your_resume"
    ```

## Usage

### Indeed Easy Apply Bot

1. Start Chrome in debug mode and log in to your Google account in the browser. Authenticate both on LinkedIn and Indeed with your Google account:

    ```sh
    /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir="/path/to/your/chrome/profile"
    ```

2. Run the Indeed Easy Apply bot:

    ```sh
    python indeed_easy_apply.py
    ```

### LinkedIn Easy Apply Bot

1. Run the LinkedIn Easy Apply bot:

    ```sh
    python linkedin_easy_apply.py
    ```

## Files

- `indeed_easy_apply.py`: Main script for Indeed Easy Apply bot.
- `linkedin_easy_apply.py`: Main script for LinkedIn Easy Apply bot.
- `config.yaml`: Configuration file for LinkedIn Easy Apply bot.
- `.env`: Environment variables for API keys and credentials.

## Troubleshooting

- Ensure Chrome is started in debug mode for the Indeed bot.
- Check the logs for detailed error messages in `errors.log`.
- Verify your `.env` and `config.yaml` files are correctly set up.

## Contributing

Contributions are welcome! Please create a pull request or open an issue for any improvements or bugs.

## License

This project is licensed under the MIT License.
