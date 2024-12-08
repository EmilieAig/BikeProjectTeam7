# Website File Description:

The Website folder contains all the code that creates the website.

Basically, to launch the website on your machine, simply go to the index.qmd file and click on the first icon in the top right-hand corner, or use the ‘quarto render’ command in your terminal.

### _quarto.yml

This file contains the basis for the creation of our site. Inside you can find the sections of our navigation bar and the pages they contain. This file is used overall to organise the different pages of the site and gives the links to these different pages.

### index.qmd

This file corresponds to the home page of our site, where we present the context, analyses and data we have used.

### styles.css

This file contains the personalisation parameters for the various parts of our site (titles, text, images, etc.). You can change the site's appearance settings here.

### footer.qmd

In this file, we can find what is in the footer, with the various associated pages.

### analyses

##### map.qmd

This file contains the interactive maps we made using the Python codes in Code/Scripts, as well as the detailed analysis and interpretation of these maps.

##### statistics.qmd

This file contains the statistical analyses we carried out using the Python code in Code/Scripts, as well as the detailed analysis and interpretation of these results to answer our question.

##### video.qmd

This file contains the video we made using the Python codes in Code/Scripts, as well as a detailed analysis and interpretation of the video.

### documentation

##### classes.qmd

This file contains the documentation for the classes we used in our Python code in Code/Scripts.

##### functions.qmd

This file contains the documentation for the functions we used in our Python code in Code/Scripts.

##### packages.qmd

This file contains the documentation for the packages we used in our Python code in Code/Scripts.

### sources

##### sources.qmd

This file contains all the sources on which we have based this project. You can find articles, links and documentation that we have used ourselves.

### footer 

##### about_us.qmd

This file introduces the members of our team and gives a brief overview of our project.

##### MIT_licenses.qmd

This file contains the licence we have used to publish this project in total security.

##### privacy_policy.qmd

This file contains our privacy policy as well as the terms and conditions for the use of personal data that we have for this site.

### docs

This file is the output file for our website. In other words, when you run a script with Quarto, it will automatically transform the Quarto code into html code. The files converted into html are stored in the docs folder.