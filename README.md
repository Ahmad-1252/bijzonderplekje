# Bijzonderplekje Hotel Data Extractor

A Python script that extracts hotel-related data (such as hotel name, category, referral link, rent per night, and address) from hotel websites. The script dynamically navigates JavaScript-oriented websites, handles infinite scrolling, and saves the extracted data into an Excel file for further analysis.

---

## Features
- **Dynamic Web Scraping**: Extracts data from JavaScript-heavy websites using Selenium.
- **Infinite Scrolling Handling**: Automatically handles infinite scrolling to collect all available data.
- **Asynchronous Translation**: Translates extracted text (e.g., from Dutch to English) using the `googletrans` library.
- **Data Export**: Saves the extracted data to an Excel file (`Bijzonderplekje_data.xlsx`).
- **Retry Mechanism**: Handles transient errors (e.g., timeouts, element not found) with a retry decorator.
- **Headless Mode**: Supports running the browser in headless mode for efficiency.

---

## Prerequisites

Before running the script, ensure you have the following installed:

1. **Python 3.8 or higher**
2. **Chrome Browser** (or any browser supported by Selenium)
3. **Required Python Libraries**:
   - Install the required libraries using the following command:
     ```bash
     pip install -r requirements.txt
     ```

---

## Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/bijzonderplekje.git
   cd bijzonderplekje
Install Dependencies:

pip install -r requirements.txt
Run the Script:
python hotel_data_extractor.py


How It Works
WebDriver Initialization:

The script initializes a Chrome WebDriver using webdriver-manager to handle the browser automation.

Data Collection:

The script navigates to the target website (https://bijzonderplekje.nl/overnachten/) and collects all hotel page URLs by scrolling and clicking the "Load More" button (if available).

Data Extraction:

For each hotel page, the script extracts the following details:

Hotel Name

Hotel Category

Referral Link

Rent Per Night

Address

Translation:

The extracted text (e.g., category and address) is translated from Dutch to English using the googletrans library.

Data Export:

The extracted and translated data is saved to an Excel file (Bijzonderplekje_data.xlsx).

Configuration
Headless Mode: To run the browser in headless mode (without a GUI), set headless=True in the get_chromedriver function.

Retry Mechanism: Adjust the number of retries and delay in the retries decorator if needed.

Target Website: Modify the driver.get URL in the main function to scrape a different website.

Output
The script generates an Excel file (Bijzonderplekje_data.xlsx) with the following columns:

Column Name	Description
name	Hotel Name
category	Hotel Category (translated)
referal_link	Referral Link
rent per night	Rent Per Night
address	Hotel Address (translated)
Limitations
Dynamic Websites: The script is designed for websites with a specific structure. Changes in the website's HTML may break the script.

Translation Accuracy: The googletrans library relies on Google Translate, which may not always provide accurate translations.

Legal Considerations: Ensure compliance with the target website's terms of service before scraping.

Contributing
Contributions are welcome! If you find any issues or have suggestions for improvement, please open an issue or submit a pull request.

License
This project is licensed under the MIT License. See the LICENSE file for details.

Acknowledgments
Selenium for web automation.

googletrans for text translation.

Pandas for data handling and Excel export.

### Key Points in the README:
1. **Overview**: Briefly describes the script's purpose and functionality.
2. **Features**: Highlights the key features of the script, including dynamic web scraping and infinite scrolling handling.
3. **Prerequisites**: Lists the required software and libraries.
4. **Setup**: Provides step-by-step instructions to set up and run the script.
5. **How It Works**: Explains the script's workflow.
6. **Configuration**: Describes how to customize the script.
7. **Output**: Details the output format and file.
8. **Limitations**: Mentions potential issues and constraints.
9. **Contributing**: Encourages contributions and collaboration.
10. **License**: Specifies the license for the project.

