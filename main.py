from robotics import Robot

SCIENTISTS = {
    1: "Albert Einstein",
    2: "Isaac Newton",
    3: "Marie Curie",
    4: "Charles Darwin"
}


class RobotController:
    def __init__(self):
        self.robot = Robot(name="Quandrinaut")
        self.menu = {"1.": "Search for a Scientist", "2.": "Exit."}

    def activate_menu(self):
        """
        Primary controller of the robot.
        :return: None
        """
        self.__introduce()

        answer = True
        while answer:
            user_input = self.__fetch_user_input()
            if user_input == "2":
                answer = False
                self.__shutdown()
            elif user_input == "1":
                scientist_input_int = self.__scientist_menu()
                self.__crawl_wiki(scientist_input_int)
            else:
                print("Incorrect input. Please try again.")
                continue

    def __introduce(self):
        """
        Introduce the robot to the user
        :return: None
        """
        self.robot.say_hello()

    def __shutdown(self):
        """
        Shutdown the bot
        :return: None
        """
        self.robot.say_goodbye()

    def __crawl_wiki(self, scientist_id):
        """
        Commence the crawl for the robot
        :param scientist_id: ID of the scientist to lookup
        :return: None
        """
        scientist_requested = SCIENTISTS[scientist_id]
        print(f"Fetching data for {scientist_requested}...", end="\n\n")
        self.robot.execute("https://wikipedia.org/", scientist_requested)

    def __fetch_user_input(self) -> str:
        """
        Fetch choice from the user
        :return: str
        """
        print("Primary Menu.")
        for menu_number, menu_item in self.menu.items():
            print(menu_number, menu_item)
        user_input = input("Enter your choice: ")
        return user_input

    def __scientist_menu(self) -> int:
        """
        Scientist selection menu
        :return: Chosen scientist id
        """
        correct_scientist_choice = True
        while correct_scientist_choice:
            print("Scientist Choice Menu.", end="\n")
            print(f"Enter your choice of Scientist ID from,", end="\n")
            for ID, name in SCIENTISTS.items():
                print(f"{ID}. {name}")
            scientist_input = input("Waiting for input: ")

            try:
                scientist_input_int = int(scientist_input)
                if scientist_input_int not in SCIENTISTS.keys():
                    print(f"Wrong choice of Scientist. Hint: choose a number from {list(SCIENTISTS.keys())}")
                    continue
                return scientist_input_int
            except ValueError:
                print(f"Only numbers are accepted. Please enter a number from {list(SCIENTISTS.keys())}")


def main():
    RobotController().activate_menu()


if __name__ == "__main__":
    main()
