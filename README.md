This repo consists of a source code  which detects plagiarism in a textual document using **cosine similarity**.<br>


<b>FILES DESCRIPTION</b> <br>

1.<b>app.py:</b> The main application file that contains the core logic and routing for the project. This file initializes the application, handles user input, and manages the overall flow of the program. <br>

2.<b>requirements.txt:</b> A list of Python dependencies required to run the project. This file allows users to install all necessary packages by running <b>pip install -r requirements.txt.</b> <br>

3.<b>docs/:</b> A directory containing documentation files and resources. This includes:<br>
 a.<b>sign.txt: </b> A text file used to store user sign-up information, such as usernames and password hashes.<br>
b.<b>matokeo.txt:</b>A text file that stores the results of the plagiarism checks, including student usernames and their plagiarism percentages.This can only be viewd when you log in as an admin.<br>
c.<b>juma.txt:</b> A text file containing specific content used by the application, this is the txt file that acts as a datbase. It is compared against the uploaded file to generate the plagiarism percentage.<br>

4.<b>sample text/:</b> A directory containing txt files that you can upload to the website to check the plagiarism percentage against juma.txt. You can change the words of the txt files in this directory(fatma.txt,john.txt) and see how it will affect the plagiarism percentage. 

 









