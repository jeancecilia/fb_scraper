class FGSIO:

    def printBanner(self):
        print("#############################################")
        print("         FACEBOOK GROUP SCRAPER")
        print("#############################################")
        print("")

    def getInput(self):

        use_post_inclusion_rule = self.prompt("Post Inclusion")

        use_post_exlusion_rule = self.prompt("Post Exlusion")

        use_author_rule = self.prompt("Author Profile")

        use_author_posts_rule = self.prompt("Author Posts Frequency")

        post_inclusion_keywords = list()

        if use_post_inclusion_rule:
            post_inclusion_keywords = self.get_post_keywords("Inclusion")

        post_exlusion_keywords = list()
        if use_post_exlusion_rule:
            post_exlusion_keywords = self.get_post_keywords("Exclusion")


        return use_author_rule, use_author_posts_rule, post_inclusion_keywords, post_exlusion_keywords

    def get_post_keywords(self, type):

        print("")

        print("NOTE: Separate more than one keywords with comma ','")

        post_keyword_input = input(f"Enter Keywords for Post {type}: ")

        keywords = post_keyword_input.split(",") # separating the keywords

        keywords = [kw.strip().lower() for kw in keywords if len(kw.strip()) > 0] # making every keyword lowercase and filtering out any empty string

        return keywords
    
    def prompt(self, rule):

        user_input = ""

        while user_input != "yes" and user_input != "no" and user_input != 'y' and user_input != 'n':
            print("")
            print(f"Do you want to use the '{rule}' rule?")
            user_input = input("Enter YES/yes/Y/y or NO/no/N/n: ").lower()

        if user_input == "yes" or user_input == 'y':
            return True
        else:
            return False