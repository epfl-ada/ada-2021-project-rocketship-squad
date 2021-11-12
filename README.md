# README.md
## [ADA project] Hotwords around the world
*Rocketship Squad : Ruben Burdin, Fabrizio Forte, Julia Majkowska, Nico Sperry*

### Abstract
News publications are a reflection of the current state of the world. Based on the content of the articles we can learn not only about events and social issues. We want to use the Quotebank to extract this information. Using quotes we can extract words and phrases which suddenly gain large popularity within the corpus to identify the most important subjects within time intervals. We will couple that with any geographical information that can also be found within a quote to create a mapping between the hotword and location. Additionally, we will create a model to assign words from the corpus to a subject (topicality analysis). 

### Research questions
 - What are the most pressing social issues for particular time frames? 
- Having identified the hotwords for a particular interval, which news outlets and authors of which gender or nationality are more likely to address these issues? 
- Is the co-occurrence of mentions of events and their geographical locations constant in time? (People start referring to the “Fukushima nuclear disaster” simply as the “nuclear disaster” over time.) 
- Which subjects and hotwords are most commonly addressed in which countries?
### Additional datasets
- [**GeoNames**](https://geonames.nga.mil/gns/html/namefiles.html) - a dataset containing a mapping of geographical names to their coordinates and countries.  
- [**World Bank GDP per Capita dataset**](https://data.worldbank.org/indicator/NY.GDP.PCAP.CD?view=chart) - a dataset containing country names and population data will be used to decide ties if we have multiple country annotations.
- [**GeoJson files for countries**](https://datahub.io/core/geo-countries) - used for visualizing countries on a map in data studio 
- [**Wikidata**](https://drive.google.com/drive/folders/1VAFHacZFh0oxSxilgNByb1nlNsqznUf0)-we plan to explore a relationship between the quote author's nationality and gender and how likely they are to address a current hotword. 

### Methods
#### Dataset storage
We uploaded the datasets into the cloud database server Google BigQuery (BQ). For analysis and visualization, BQ offers many tools to quickly filter and access the data such as the built-in SQL query interface and DataStudio for visualizations.
#### Quote processing
For every quote we will have to extract geographical names, tokenize, lemmatize and remove stopwords from the text of the quote. All this is done using spacy tokenization, lemmatization and named entity recognition features. For efficiency, we process the quotes in parallel. 
To determine the geographical location associated with the hotword we gather all geographical names, look them up by country and choose with a majority vote then disambiguate based on the country's GDP in case of ties. If time and data permits we will narrow down the location further to a city/region. 

####  Finding hotwords

First, we gather unigram statistics per quotes and aggregate them by day. From a preliminary, analysis we can see that the number of quotes drops significantly during weekends. We need to take this into account for our analysis.
Furthermore, compute bigrams statistics to determine which of them can be considered as a single hotword. 
The correlation between words can be computed following the formula ([source](https://www.tidytextmining.com/ngrams.html)): 
$\phi = \frac{c_{w_1, w_2}(C - c_{w_1}-c_{w_2} + c_{w_1, w_2}) - c_{w_1}c_{w_2}}{c_{w_1}c_{w_2}(C-c_{w_1})(C-c_{w_1})}$, where $C = |corpus|$ 
and $C_S$ are number of quotes containing words in $S$.
The statistics are mostly computed with BQ queries for performance. 
To determine hotwords we will look at data aggregated by day and by week, calculate the mean and standard deviation and consider tokens/phrases which have a period when they occur over $k \times {StandardDeviation}$ times, where k will be adjusted for performance. 

#### Topic finding
We use LDA, an unsupervised learning algorithm that associates to each quote a mixture of topics.
[Latent Dirichlet Allocation (LDA)](https://en.wikipedia.org/wiki/Latent_Dirichlet_allocation) -  [implementation used]( https://radimrehurek.com/gensim/models/ldamulticore.html ).

##### Creating a classifier
We train LDA on a small portion of the dataset (e.g. one month) and use the model to classify topics on the rest of the data, under the assumpion that a quote belongs to only one topic. 
We will fine-tune the number of topics (which is an input parameter of the LDA). We assess how good a topic model is using [Coherence](https://radimrehurek.com/gensim/models/coherencemodel.html ). 
##### Identifying subject
Once trained, LDA model will take a quote as input and will output a list of length *#topics*, containing the probability that the quote belongs to each of them. 
For each topic we take the quotes that belong to the group with probability $p > p_0$, with $p_0$ to be determined.

##### Preliminary results:
Sport |Politics | Businness|
:-----:|:-----:|:-----:|
| ![](https://i.imgur.com/Upb2gva.png)  |  ![](https://i.imgur.com/lnjjc0n.png) | ![](https://i.imgur.com/ojzeK0j.png)

From a preliminary analysis on data from first week of 2019 we find that the best number of topics parameter is 9.
Some of the topics found are: 
- sport,
- politics, 
- economics & business
- ...

For reference, see the picture above for the cloud of word representation of the topics mentioned.

Other topics are less neat, and tend to collect all the “garbage quotes” (typos, foreign language quotes, ...).

Topic finding can thus be used iteratively to find more specific topics and/or to filter the data.

#### Visualisation
To make the visualizations interactive we will connect our Google DataStudio dashboard directly to the database.

- World map with hotword and their respective locations marked. This can be done in Google Data Studio [example](https://datastudio.google.com/reporting/4617cbac-3514-4c8d-a999-a3cb6683e579)
- Map with connections between country of speaker/source and country mentioned in the content
- Word cloud visualizations for common hotwords in selected countries (by speaker and by domain name of source)
- Timeline (a horizontal slider) which will let the user select the time interval and render a list of hotwords and trending topics

### Proposed timeline and individual Milestones

#### Milestone 2
- Julia : Create an efficient data preprocessing pipeline. Create a README.
- Ruben : Pipe the data into Big Query and clean it. Analyse the data for quality and observations to be excluded from further processing for project Milestone 3.
- Nico : Create unigram and bigram statistics gathering pipelines. Conduct initial analysis on hotword determination methods. 
- Fabrizio : Create topic determination model training pipeline and pipeline for downstream topic recognition in the whole dataset. Conduct initial analysis on quality and computational feasibility of proposed methods. 

#### Until November 26
Running the preprocessing and gathering statistics pipelines for assigned years of the dataset.
- Julia : 2020, 2016
- Fabrizio : 2019, 2015
- Nico : 2018
- Ruben : 2017
Building all NLP models and sketch of the dashboard. Conduct first analysis on quote topicality.

#### Milestone 3
- Julia : For determined hotword candidates determine Geographical locations and combine it with GeoJson files for visualizations. 
- Nico : Determine time intervals when hotwords are hot
- Fabrizio : Train and run topic evaluation on the corpus. 
- Ruben : Prepare visualizations with prepared data from BQ. Preprocess the wikidata and load in BQ.

