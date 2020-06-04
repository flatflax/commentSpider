# commentSpider

Scrap information like comments from socail media websites.(mainly focus on tmall & jd).

## jdSpider

The comments scraping part store the result into `*.txt` files. It would be loaded into mongoDB and take a part in the development of the machine learning model built for sentimental analytic.(Python + Selenium webdriver)

The reclike product part store the result into `*.csv` files. And it would be loaded into the graph database Neo4j. But the follow-up development has not be decided.(Python Requests)

* comments scraping
	* jdComment.py 
	* jdLink.py
	* jdTest.py (realize multithreading)
* reclike product
	* guessulike.py
	* dataclear.py

## tmallSpider

The comments scraping part is likely to that in jdSpider. And it has not been update for a long time. (Python + Selenium webdriver)

So do the same product scraping part. The result of these two parts are stored into `*.txt` file and would be loaded into mongoDB. (Python + Selenium webdriver)

* comments scraping
	* tmLink.py
	* tmComment.py
* same product scraping
	* similarProduct.py