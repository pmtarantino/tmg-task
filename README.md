# Task for TMG interview

The approach was to split the task into two clear steps: scrapping and clustering.

The scrapping was approached as a stand-alone script, while the clustering was done using Jupyter Notebook, with comments and explanations between the different steps.

To replicate and run all of this, create a new Python virtual enviroment and install the libraries using PIP (requirements file included).

## Scrapping

The scrapping can be replicated running

```python scrapper.py --file site_list.txt```

although the file can be changed for any other file (where the websites are one per line). The script will create a new directory and will save the texts for each file inside that directory, one file per website. I choose using text files instead of a database because I found it a simpler solution for this usecase. 

The scrapper will go one by one for the websites on the list and it will retrieve its content. It will also retrieve all the links inside and filter the ones pointing to external websites, or files that are not HTML (like images, PDF, or javascript links). It will then keep only 20 of these links and retrieve them using _threading_ to do it in parallel. Why only 20? Some websites had several hundreds of internal links, and adding more texts for our analysis was not necessary. Twenty internal pages plus the original landing was enough for the analysis.

Three websites from the original list (100 websites) failed - one of them returned error 400 and other two had an error on the SSL handshake. However, although the script was able to identify these errors, it didnt stop or stall. The parsing continued succesfully, and it was notified at the end that the scrapping was not complete (it was done by a simple _assert_ condition, it can be improved).

## Clustering

The clustering algorithm, its technique and explanation can be found on the _clustering.ipynb_ Jupyter notebook.