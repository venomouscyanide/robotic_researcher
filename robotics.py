import time
from datetime import datetime
from typing import Tuple

from RPA.Browser.Selenium import Selenium
from bs4 import BeautifulSoup, Tag

import dateparser


class Robot:
    def __init__(self, name: str):
        """
        Helps robot initialize selenium driver for crawling
        :param name: name of the robot
        """
        self.name = name
        self.driver: Selenium = Selenium(auto_close=True)

    def __init_browser(self, webpage: str) -> None:
        """
        Initializes and open an available browser for initiating the crawl
        :param webpage: string containing the website used for crawling scientists' data
        :return: None
        """
        self.driver.open_available_browser(url=webpage, headless=True, maximized=True)

    def say_hello(self) -> None:
        """
        Introduce the robot to the user
        :return: None
        """
        print(f"Hi, I am {self.name}.", end='\n')
        print("I can help you find out the age of famous scientists and present you with a short intro to their lives.",
              end="\n")

    def say_goodbye(self) -> None:
        """
        Conclude conversation with the user
        :return: None
        """
        print("Goodbye!", end="\n")
        print("I hope you had fun learning about famous scientists.", end="\n")

    def __go_to_scientist_page(self, scientist_name: str):
        """
        Helps the robot navigate to the scientist's wiki entry page
        :param scientist_name: Name of the scientist for whom the info is to be crawled for
        :return: None
        """
        self.driver.input_text("id:searchInput", scientist_name)
        self.driver.submit_form("id:search-form")

    def __parse_wiki_entry(self) -> BeautifulSoup:
        """
        Parse the wiki entry source page to extract age and first para
        :return: BeautifulSoup parsed object
        """
        time.sleep(2)
        page_source = self.driver.get_source()
        soup_parsed = BeautifulSoup(page_source, features="html.parser")
        return soup_parsed

    def execute(self, webpage: str, scientist_name: str):
        """
        Heart of the robot
        :param webpage: wikipedia site used to crawl
        :param scientist_name: name of scientist that the user chose
        :return: None
        """
        self.__init_browser(webpage)
        self.__go_to_scientist_page(scientist_name)
        soup_parsed_object = self.__parse_wiki_entry()
        age = self.__parse_scientist_age(soup_parsed_object)
        first_para = self.__get_first_para(soup_parsed_object)
        self.__print_gathered_data(age, first_para, scientist_name)
        self.driver.close_browser()

    def __parse_scientist_age(self, soup_parsed_object: BeautifulSoup):
        """
        Helps calculate the age of the scientist
        :param soup_parsed_object: BS4 object for the wiki entry
        :return: calculate age of the scientist
        """
        # table parsing adapted from https://stackoverflow.com/a/23377804
        div_for_info_table = soup_parsed_object.find('table', attrs={'class': "infobox biography vcard"})
        table_body = div_for_info_table.find('tbody')
        rows = table_body.find_all('tr')
        age = self.__get_age_helper(rows)
        return age

    def __get_age_helper(self, rows: 'ResultSet') -> float:
        """
        Helper method to get the age of the scientist
        :param rows: rows parsed from BS4
        :return: age of the scientist
        """
        age = 0
        birth_date = None
        for row in rows:
            col_title_elements = row.find_all('th')
            col_title = [ele.text.strip() for ele in col_title_elements]
            col_title_str = "_".join(col_title)

            if col_title_str.startswith("Born"):
                birth_date, _ = self.__date_parse_helper(row)

            if col_title_str.startswith("Died"):
                date_of_demise, col_value_str = self.__date_parse_helper(row)
                age = self.__calculate_age(birth_date, date_of_demise, col_value_str)
                break
        return age

    def __date_parse_helper(self, row: Tag) -> Tuple[datetime, str]:
        """
        Parse the birth/death date into a datetime object
        :param row: Row object from BS4
        :return: data and column value associated with the row (optionally consumed)
        """
        col_value_elements = row.find_all('td')
        col_value = [ele.text.strip() for ele in col_value_elements]
        col_value_str = " ".join(col_value)
        date = col_value_str[col_value_str.find("(") + 1:col_value_str.find(")")]
        date = dateparser.parse(date)
        return date, col_value_str

    def __get_first_para(self, soup_parsed_object: BeautifulSoup) -> str:
        """
        Fetch intro para of the scientist
        :param soup_parsed_object: BS4 object
        :return: first non-emtpy para for the scientist
        """
        first_para = "First Paragraph not found!"
        for para_element in soup_parsed_object.find_all('p'):
            cleaned_para_text = para_element.text.strip()
            if cleaned_para_text:
                first_para = cleaned_para_text
                break
        return first_para

    def __print_gathered_data(self, age: int, first_para: str, scientist_name: str) -> None:
        """
        Present the crawled data to the user
        :param age: Calculate age of the scientist
        :param first_para: First para of the scientist
        :param scientist_name: Name of the scientist
        :return:
        """
        print(f"I have finished gathering the age and introduction for {scientist_name}.", end="\n\n")
        print(f"{scientist_name} was {int(age)} years old.", end="\n\n")
        print(f"Here's a short intro into who {scientist_name} was,", end="\n\n")
        print(first_para, end="\n\n\n")

    def __calculate_age(self, birth_date: datetime, date_of_demise: datetime, col_value_str: str) -> float:
        """
        Helps calculate the age in years from birth and death dates
        :param birth_date: Birthdate of the scientist
        :param date_of_demise: Date of death of the scientist
        :param col_value_str: raw column value from which death date was parsed
        :return: calculated age of the scientist
        """
        age_truth = int(col_value_str.split("(aged")[1].split(")")[0])
        age = (date_of_demise - birth_date).days / 365
        # sanity check
        assert int(age) == age_truth, "Age calculated does not match what's present on wiki."
        return age
