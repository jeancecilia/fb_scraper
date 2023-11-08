from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from datetime import datetime, timedelta
import pandas as pd
from selenium.webdriver.edge.options import Options
import json
import os


# FACEBOOK GROUP SCRAPER

class FGS:

    def __init__(self, username, password, input_data):

        # Headless browser configurations
        browser_options = Options()
        browser_options.add_argument("--headless")


        self.driver = webdriver.Edge(options=browser_options) # Initializing Microsoft's Edge Webdriver

        self.secondary_driver = webdriver.Edge(options=browser_options)

        self.fb_group_base_url = "https://www.facebook.com/groups/"
        

        self.data = {
            "Group Url": [],
            "Post Url": [],
            "Post Author": [],
            "Post Content": [],
            "Post Images": [],
            "Author Profile": [],
            "Line ID": []
        }

        self.is_logged_in = False

        self.username = username

        self.password = password

        self.use_profile_rule = input_data[0]

        self.use_author_posts_rule = input_data[1]

        self.post_inclusion_keywords = input_data[2]

        self.post_exclusion_keywords = input_data[3]

        self.profile_keywords = ["agent", "real estate", "property", "realtor", "estate","ตัวแทน","อสังหาริมทรัพย์","คุณสมบัติ","นายหน้า","อสังหาริมทรัพย์"]

        # Login to facebook for both drivers

        self.login(self.driver)

        time.sleep(10)

        self.login(self.secondary_driver)
    
    """
    Check whether the post time is within in specified days.
    """
    def post_time_check(self, post_time, check_days):

        # post time analysis
        # post time within a week -> 4 s (seconds), 4 m (minutes), 4 h (hours), 4 d (days)
        # post time after week -> 07 October at 21:00
        # post time after month -> 07 October
        # post time after year -> 07 October 2022
        
        check_datetime = datetime.now() - timedelta(check_days)
        
        post_date_time_obj = None
        
        post_time = post_time.strip()
        try:
            if 'at' in post_time:
                # Post time is after week but within 30 days
                post_time_parts = post_time.split('at')
                post_date = post_time_parts[0] + str(datetime.now().year)
                post_date_time_obj = datetime.strptime(post_date, '%d %B %Y')
            else:
                # Post time can be within week or after 30 days or after year
                post_time_parts = post_time.split(" ")
                if len(post_time_parts) == 2:
                    # Post time within week or after 30 days
                    if len(post_time_parts[1]) == 1:
                        # Post time within week
                        if post_time_parts[1] == 'd':
                            post_date_time_obj = datetime.now() - timedelta(int(post_time_parts[0]))
                        else:
                            post_date_time_obj = datetime.now()
                    
                    else:
                        # Post time after 30 days
                        post_time += " " + str(datetime.now().year)
                        post_date_time_obj = datetime.strptime(post_time, '%d %B %Y')
                else:
                    # Post time after year
                    post_date_time_obj = datetime.strptime(post_time, '%d %B %Y')

            # Checking whether the posttime is within specified time or not
            if post_date_time_obj.date() >= check_datetime.date():
                return True
            else:
                return False
            
        except Exception as e:

            self.log("Error in Post Time Check Function: " + str(e))

            return None


    """
    Check whether the author have posted more than once in group within sepecified days
    """
    def author_posts_check(self, agp_url, check_days):

        try:

            if not self.use_author_posts_rule:
                return False

            within_time_posts_counter = 1

            self.secondary_driver.get(agp_url)

            time.sleep(5)

            # click the active element to make elements of webpage clickable
            self.secondary_driver.switch_to.active_element.send_keys(Keys.ENTER)

            posts = list(self.secondary_driver.find_elements(By.XPATH, "//div[@class='x78zum5 xdt5ytf']"))

            print("AUTHOR GROUP POSTS:", len(posts))

            last_post = posts[-1]

            for post in posts:
                try:

                    post_parts = post.text.lower().split("\n")

                    if len(post_parts) > 1:
                        post_time = post_parts[1]
                        if post_parts[0].strip() == 'active':
                            post_time = post_parts[2]
                    else:
                        continue

                    is_post_within_time = self.post_time_check(post_time, check_days)

                    if is_post_within_time != None and not is_post_within_time:
                        break # stop scraping posts if post time is earlier than specified time

                    self.secondary_driver.execute_script("arguments[0].scrollIntoView();", post) # Navigate to post so that next posts can load in the browser
                    
                    if within_time_posts_counter > 1:

                        return True # Author have post more than once within specified time

                    if post == last_post:
                        # Finding new posts
                        all_posts = list(self.secondary_driver.find_elements(By.XPATH, "//div[@class='x78zum5 xdt5ytf']"))
                        new_post_elements = [p for p in all_posts if p not in posts]
                        
                        # Updating posts list with new posts
                        posts.extend(new_post_elements)

                        last_post = post[-1]
                    
                    time.sleep(2)

                    within_time_posts_counter += 1
                except Exception as e:
                    self.log("Error in Author Posts Check Function: " + str(e))
            
            return False # Author have not posted more than once within specified time

        except Exception as e:

            self.log("Error in Author Posts Check Function: " + str(e))

            return False

    def get_post_images(self, post_link):

                images = list()

                try:

                    self.secondary_driver.get(post_link)

                    time.sleep(5)

                    # click the active element to make elements of webpage clickable
                    self.secondary_driver.switch_to.active_element.send_keys(Keys.ENTER)
                    
                    post_links = self.secondary_driver.find_elements(By.XPATH, '//a[@role="link"]')

                    for lnk_element in post_links:

                        lnk = lnk_element.get_attribute('href')

                        print("Link:", lnk)

                        if "/commerce/listing/" in lnk:

                            lnk_element.click()

                            time.sleep(5)

                            break

                    listing_div = self.secondary_driver.find_element(By.XPATH, '//div[@class="x1a0syf3 x1ja2u2z"]')
                    
                    images_elements = list(listing_div.find_elements(By.TAG_NAME, 'img'))
                    
                    images = [img.get_attribute('src') for img in images_elements]
                
                except Exception as e:

                    self.log("Error in Images Function:" + str(e))


                return images

    """
    Retrieve LINE ID from author's post
    """
    def get_contact_details(self, data_parts):

        contact_details = ""

        try:
            for part in data_parts:
                part = part.lower().strip()
                if ":" in part:
                    if 'line' in part or 'เส้น' in part:
                        contact_details += part.split(":")[1].strip()
                        break
        except Exception as e:
            self.log("Error in contact details Function:" + str(e))

        return contact_details

    """
    Check whether the post contains the given keywords or not for post inclusion. If true we will not skip the post, otherwise skip post
    """
    def post_inclusion_check(self, post_content):

        try:
            
            if len(self.post_inclusion_keywords) == 0:
                
                # checking for some common property related keywords to ensure that the post is about property
                # filterout any irrelevant post which is not about property
                local_keywords = ['room', 'ห้อง', 'property', 'คุณสมบัติ','house', 'บ้าน', 'floor', 'พื้น']
                is_local_keyword_present = False
                for lk in local_keywords:
                    if lk in post_content:
                        is_local_keyword_present = True # post is about property
                        break
                
                if is_local_keyword_present: # to avoid completely irrelevant posts
                    return True
                    
            else:

                for kw in self.post_inclusion_keywords:
                    if kw in post_content:
                        return True # keyword found in the post
                    
            return False
            
        except Exception as e:
            self.log("Error in Post Check Function: " + str(e))
            return False



    """
    Check whether the post contains the given keywords or not for post exclusion. If true, skip the post otherwise not.
    """
    def post_exclusion_check(self, post_content):
        
        try:
            
            if len(self.post_exclusion_keywords) == 0:
                return False # No keyword given by the user

            for kw in self.post_exclusion_keywords:
                if kw in post_content:
                    return True # keyword found in the post
            
            return False
        except Exception as e:
            self.log("Error in Post Check Function: " + str(e))
            return False

    """
    Check whether the profile of author contains the given keywords or not.
    """
    def profile_check(self, author_profile_url):

        try:

            if not self.use_profile_rule:
                return False

            self.secondary_driver.get(author_profile_url)

            time.sleep(5)

            profile_section = self.secondary_driver.find_element(By.XPATH, "//div[@class='xieb3on']")

            self.profile_intro = profile_section.text.lower()

            print("###################################")
            print("Profile Intro:",self.profile_intro)
            print("################################")

            if len(self.profile_intro) > 1:

                for p_keyword in self.profile_keywords:

                    if p_keyword in self.profile_intro:

                        return True


            return False
        
        except Exception as e:

            self.log("Error in Profile Filter Function: " + author_profile_url + str(e))
            return False


    """
    Function to execute the scraping for all given facebook group urls
    """
    def execute(self):
        
        try:

            if not self.is_logged_in:
                return False # If user not logged in, do not proceed scraping process
            
            groups_urls = self.getGroupsUrls()

            if groups_urls == None: # No group url found
                self.log("No group url found")
                return

            # Scrape every group nne by one
            for url in groups_urls:

                try:

                    self.scrape(url)

                    time.sleep(5)

                except Exception as e:

                    print(f"Error occurred while scraping group: {e}")

            return True # execution successful


        except Exception as e:

            self.log("Error in executing the FGS: " + str(e))  
            return False

    def update_posts_list(self, post, group_posts, last_post):
                
                
                
        
                # Navigating to the end of the post in order to generate next posts in the webpage
                try:

                    post_footer = post.find_element(By.XPATH, ".//div[@class='xq8finb x16n37ib']") # Locate post footer

                    self.driver.execute_script("arguments[0].scrollIntoView();", post_footer) # navigate to post footer

                except:

                    comment_section = post.find_element(By.XPATH, ".//div[@class='xzueoph']") # Locate comment section
                    
                    self.driver.execute_script("arguments[0].scrollIntoView();", comment_section) # navigate to comment section
                

                time.sleep(5)
                # Update posts list with new posts
                # New posts are generated in the webpage when browser scrolled to last post
                if post == last_post:
                    # find unique posts
                    
                    all_posts = list(self.driver.find_elements(By.XPATH, "//div[@class='x1n2onr6 x1ja2u2z']")) # It contains both visited and new posts
                    new_posts = [p for p in all_posts if p not in group_posts] # Extract new posts by filtering out the old posts
                    group_posts.extend(list(new_posts))
                    print("Updated Group Posts:", len(group_posts))
                    last_post = group_posts[-1] # Last Post Updated 
                
                print("###############################")
                return group_posts,last_post

    """
    Function to scrape the posts of joined group according to given criteria
    Criteria:
                1. Only scrape posts published within last 72 Hours
                2. Scrape url, images, content and author details of post
    """
    def scrape(self, group_link):

        CHRONOLOGICAL_POSTS_URL = group_link + "?sorting_setting=CHRONOLOGICAL" # Chronological order means sorting posts w.r.t time (in ascending order)

        self.driver.get(CHRONOLOGICAL_POSTS_URL) # Load group webpage

        # click the active element to make elements of webpage clickable
        self.driver.switch_to.active_element.send_keys(Keys.ENTER)

        # locating posts
        group_posts = list(self.driver.find_elements(By.XPATH, "//div[@class='x1n2onr6 x1ja2u2z']"))

        # last post
        if len(group_posts) != 0:
            last_post = group_posts[-1]
        else:
            print("No Group Post Found")

        print("POSTS:", len(group_posts))

        for post in group_posts:

            print("#####################################")
            
            try:

                # If post contains "See more" button, click it to get all content of post
                divs = post.find_elements(By.TAG_NAME, 'div')
                
                for d in divs:
                        try:
                            if "See more" == d.text.strip():
                                d.click()
                                break     
                        except:
                            pass

                
                # Post content
                
                print("Post Content:", post.text)
                
                # time.sleep(1000)
                raw_post_content_list = post.text.lower().split("\n")
                
                if len(raw_post_content_list) <= 1:
                    continue

                
                post_time = raw_post_content_list[1]
                
                if raw_post_content_list[0].strip() == "active":
                    post_time = raw_post_content_list[2]

                # Author Details
                author_group_profile_url = post.find_element(By.TAG_NAME, 'a').get_attribute('href') # this is url of group profile

                if "/reel/" in author_group_profile_url: # author profile url is url of reel
                    continue

                author_profile_url = "https://www.facebook.com/profile.php?id=" + author_group_profile_url.split("/user/")[1].split("/")[0] # original profile
                
                
                print("Author Group Profile:", author_group_profile_url)

                # Author Name
                author_name = raw_post_content_list[0]
                print("###################################")
                print("Post Time:",post_time)
                print("################################")

                if not self.post_time_check(post_time, 30):
                    
                    group_posts, last_post = self.update_posts_list(post, group_posts, last_post)
                    time.sleep(5)
                    continue

                
                if "4 d" in post_time or "5 d" in post_time or "6 d" in post_time or len(post_time.split(" ")) > 2:
                    break # stop scraping if the current post is published on 4th day

                post_start_index = 3
                try:
                    post_end_index = raw_post_content_list.index("all reactions:")
                except:
                    post_end_index = raw_post_content_list.index("like") # Incase, if there is no reaction on post

                
                post_content = "\n".join(raw_post_content_list[post_start_index:post_end_index]) # Combine all post's content together

                post_content = post_content.replace("See translation","") # If post's content contains 'See translation', replace it with empty string


            
                # Post Filtration
                if not self.post_inclusion_check(post_content) or self.post_exclusion_check(post_content) or self.profile_check(author_profile_url) or self.author_posts_check(author_group_profile_url, 14):
                    group_posts, last_post = self.update_posts_list(post, group_posts, last_post)
                    continue # skip the post


                # # Post Url
                post_url = list(post.find_elements(By.TAG_NAME, 'span'))[6].find_element(By.TAG_NAME, 'a').get_attribute('href')
                print("Post url:", post_url)
                print("#####################################")
                
                # Post's Images
                post_images = self.get_post_images(post_url)

                # contact details
                contact_details = self.get_contact_details(raw_post_content_list)

                if len(contact_details) == 0 and self.use_profile_rule:

                    contact_details = self.get_contact_details(self.profile_intro.split("\n"))
                

                # Update data
                self.data["Group Url"].append(group_link)
                self.data["Post Url"].append(post_url)
                self.data["Post Author"].append(author_name)
                self.data["Post Content"].append(post_content)
                self.data["Post Images"].append(post_images)
                self.data["Author Profile"].append(author_profile_url)
                self.data["Line ID"].append(contact_details)

                # store data in excel file
                self.store()

                group_posts, last_post = self.update_posts_list(post, group_posts, last_post)

                time.sleep(2)

            except Exception as e:

                self.log("Error Scrape Function: " + str(e))

    """
    Function to store scraped data in excel file
    """
    def store(self):
        try:
            df = pd.DataFrame(self.data)
            writer = pd.ExcelWriter('data.xlsx', engine='xlsxwriter')
            df.to_excel(writer, sheet_name='Sheet1', index=False)
            writer._save()
        except Exception as e:
            self.log("Error in Store Function: " + str(e))

    """
    Function to check whether welcome text is present or not. It will be used to check whether there was successful login or not
    """
    def is_welcome(self, driver):

        try:
            # Find welcome element
            welcome_element = driver.find_element(By.TAG_NAME, "body")
            print("#########################")
            print("Welcome Element:", welcome_element.text)
            print("##########################")
            # If welcome element found and it contains the given text, then it means user is already logged in
            if "Welcome to Facebook," in welcome_element.text:
                return True
            else:
                return False
        except Exception as e:

            self.log("Welcome element not found. It means login unsuccessful due to invalid credentials or account is suspended")

            return False

    """
    Function to use cookies if bot already logged in
    """
    def isLoggedIn(self, driver):

        try:
            
            cookies = self.read_cookies()

            if len(cookies) == 0 or self.username not in cookies.keys():
                return False
            
            cookies = cookies[self.username]

            driver.get("https://www.facebook.com")

            # add cookies to browser
            for cookie in cookies:
                driver.add_cookie(cookie)

            # reload home page after adding the cookies to browser
            driver.get("https://www.facebook.com/?sk=welcome")

            time.sleep(5)

            if self.is_welcome(driver):
                return True
            else:
                return False
            
        except Exception as e:

            self.log("Error isLoggedIn Function: " + str(e))

            return False
        
    """
    Function to read cookies
    """
    def read_cookies(self):

        cookies = ""

        if not os.path.exists('cookies.json'):
            return cookies 

        with open("cookies.json") as c_f:

            cookies = json.loads(c_f.read())
        
        return cookies

    """
    Function to write cookies
    """
    def write_cookies(self, cookies):

        # store cookies locally
        with open("cookies.json", "w") as c:
        
            c.write(json.dumps(cookies))
        

    """
    Function to login the bot on facebook.com
    """
    def login(self, driver):

        try:

            
            if not self.isLoggedIn(driver):

                driver.get("https://www.facebook.com/") # Load Login page
                time.sleep(5)
                driver.find_element(By.ID, 'email').send_keys(self.username) # Enter email in email input
                driver.find_element(By.ID, "pass").send_keys(self.password) # Enter password in password input
                driver.find_element(By.NAME, "login").click() # Click login button to login 

                time.sleep(5) # Wait for 5 seconds to complete the login 

                # switch to default content
                self.driver.switch_to.active_element.send_keys(Keys.ENTER)

                
                if self.is_welcome(driver):
                    self.is_logged_in = True

                    cookies = self.read_cookies()

                    if len(cookies) != 0:

                        cookies[self.username] = driver.get_cookies()
                    
                    else:

                        cookies = {self.username: driver.get_cookies()}

                    self.write_cookies(cookies)
                        
                    print("Login Successful")
                else:
                    print("Login Failed [Invalid Credentials / Suspended Account]")
            
            else:
                self.is_logged_in = True
                print("Login Successful")

        except Exception as e:

            print("Login Failed [Invalid Credentials / Suspended Account]")
            self.log("Error Login Function: " + str(e))

    """
    Function to read input file which will contains urls of public facebook groups
    """
    def getGroupsUrls(self):

        try:

            with open("input.txt", "r") as input_file:
                urls = input_file.read() # read groups urls from input file
            
            urls_list = urls.split("\n") # extract individual urls on the basis of new line separator, and storing them in list

            urls_list = [url for url in urls_list if "/groups/" in url]

            if len(urls_list) == 0:
                return None

            return urls_list
            
        except Exception as e:

            self.log("Error in reading input groups urls: " + str(e))

            return None  
    
    """
    Function for monitoring the performance of bot by saving the relevant data in log.txt file
    """
    def log(self, data):

        with open("log.txt", "a") as log_file:
            log_file.write("[ "+ str(datetime.now()) + " ] " + data + "\n")