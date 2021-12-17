# README.md
## [ADA project] Exploring the biases and interest of Americans
*Rocketship Squad : Ruben Burdin, Fabrizio Forte, Julia Majkowska, Nico Sperry* 


[**Datastory link**](https://datastudio.google.com/embed/reporting/2da04b94-0570-4e83-a00d-41f7752bcd02/page/p_uygeukgbqc)

### Abstract
News publications are a reflection of the current state of the world. Based on the content of the articles we can learn not only about events and social issues. We want to use the Quotebank to extract in what contexts are US speakers talking about other countries. We annotate quotes with topics using LDA and add sentiment annotation using BigQuery library funtions. We look at spikes in distribution of quotes per coutnry to identify meaningful events and characterize them by lemmas from related quotes.   

### Research questions
 - Which countries attract the most interest of American speakers? 
     - Are those just rich countries? 
     - Are those just populous countries? 
 - Are the most interesting countries constant in time? 
- Which countries are mention in a positive context and which in negative? 
- In what topics are the countries mentioned? 
- Is the distribution of categories the same for all countries? 
- What events can spike the interest of US speakers? 

### Additional datasets
- [**Gazeteer**](http://download.geonames.org/export/dump/) - a dataset containing a mapping of geographical names to their coordinates and countries.  
- [**World Bank GDP per Capita dataset**](https://data.worldbank.org/indicator/NY.GDP.PCAP.CD?view=chart) - a dataset containing country names and population data will be used to decide ties if we have multiple country annotations.
- [**Wikidata**](https://drive.google.com/drive/folders/1VAFHacZFh0oxSxilgNByb1nlNsqznUf0)-we plan to explore a relationship between the quote author's nationality and gender and how likely they are to address a current hotword. 

### Methods
#### Dataset storage
We uploaded the datasets into the cloud database server Google BigQuery (BQ). For analysis and visualization, BQ offers many tools to quickly filter and access the data such as the built-in SQL query interface and DataStudio for visualizations.
#### Quote processing
For every quote we will have to extract geographical names, tokenize, lemmatize and remove stopwords from the text of the quote. All this is done using spacy tokenization, lemmatization and named entity recognition features. For efficiency, we process the quotes in parallel. 
To determine the geographical location associated with the hotword we gather all geographical names and assign them to a country using the Gazeteer dataset. We annotate only country names, names which can be matched unambiguously to a country and names of geographical entities with a population of over 1000 000. This gives us fairly high quality annotations, thought we observed some false annotations Michael Jordan's last name causing the quote to be matched to country Jordan, or annotating Gaza as a region of Mozambique rather then the Gaza strip.  

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

### Individual contribuitons

#### Milestone 3
- Julia : Create an efficient data preprocessing pipeline. Created a README. Performed spike analysis to find meaningful events.Create the outline of datastory.  
- Ruben : Pipe the data into Big Query and clean it. Sentiment analysis. Visualization. 
- Nico : Visualizations, and analysis of topic country distributions. 
- Fabrizio : Topic assignment with LDA, analysis of topic distribution by continent and quote distribution by coutry's GDP and population 

