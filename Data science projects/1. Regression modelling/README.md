# Project overview

## Description 

The housing crisis is affecting towns and cities worldwide, with high demand and short supply resulting in a lack of affordable housing for the average buyer or renter. This crisis is particularly acute in tourist hotspots where the rise of short-term rentals is taking more properties off the market, away from long-term dwellers.

Airbnb is an online platform that launched in 2008, allowing travellers to book more authentic and affordable short-term stays compared to a prefabricated and pricier hotel experience. Increasingly, property investors looking to expand their portfolios have seen how lucrative Airbnb rentals are. Coupled with poor regulation of Airbnb rentals that outstay their terms, this has only added fuel to the fire. According to <a href='https://www.wired.co.uk/article/airbnb-london-short-term-rentals'>Wired</a>, 56% of London Airbnb listings comprised of entire homes by 2019, and the number of listings in the city's more suburban quarters had increased fifteen-fold compared to four years prior.

This project presents a potential solution to this problem - using machine learning to accurately predict the price of an Airbnb listing. If we can accurately predict the price, then we know what factors and variables influence pricing the most. This information can support current research and, once escalated, could be used as part of lobbying tactics to protect certain areas and types of housing from Airbnb investment based on these factors.

Since price is a continuous variable and data labelled with this known target is needed to make predictions, I will be using supervised regression models to solve this problem. RMSE (root mean squared error) is the metric of choice used to measure the performance of each model used in this project.

Please follow this project in the given order of files:

<ol>
    <li>ETL pipeline</li>
    <li>Exploratory data analysis</li>
</ol>

## Prerequisites

For this project, you will need to download the two datasets available in the Data folder and an IDE (integrated learning environment) that runs on Python such as <a href='https://noteable.io/jupyter-notebook/install-jupyter-notebook/'>Jupyter Notebook</a>. Google Colab is an option you can use without having to install Python manually, however, you might have to install some of the packages used in this project. A guide of how to do this can be found <a href='https://saturncloud.io/blog/how-to-install-python-packages-in-googles-colab/#:~:text=With%20Colab%2C%20you%20can%20run,how%20to%20install%20Python%20packages.'>here</a>.
