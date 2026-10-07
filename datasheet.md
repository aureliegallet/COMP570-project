# Project Datasheet 

Based on Gebru et al. "Datasheets for Datasets" (2021) [https://arxiv.org/abs/1803.09010].

---------------

## Motivation

### For what purpose was the dataset created? 
**Was there a specific task in mind? Was there a specific gap that needed to be filled? Please provide a description.**

The dataset was created to help an organization understand which neighbourhoods are best for newcomers to Montreal to move into. Specifically, this dataset aims to help optimize for rent affordability, low crime rates, number/quality of schools, peacefulness/quietness of neighbourhood and number of parks.

<!--  SPACING -->

### Who created the dataset (e.g., which team, research group) and on behalf of which entity (e.g., company, institution, organization)?

This dataset was created by a group composed of 4 COMP570 students (Aurélie Gallet, Harry Hu, Andrew Saffar and Arash Tavangar) at McGill University.

<!--  SPACING -->

### Who funded the creation of the dataset? 
**If there is an associated grant, please provide the name of the grantor and the grant name and number.**

There was no funding for the creation of this dataset.

<!--  SPACING -->

### Any other comments?
None.

-------------

## Composition

###  What do the instances that comprise the dataset represent (e.g., documents, photos, people, countries)? 
**Are there multiple types of instances (e.g., movies, users, and ratings; people and interactions between them; nodes and edges)? Please provide a description.**

The instances are aggregated statistics about each borough, describing multiple aspects (rent, crime, education, quietness and green space). Each statistic is normalised so that they can be used together and weighted according to stakeholder directives to create a proxy for borough livability.

<!--  SPACING -->

### How many instances are there in total (of each type, if appropriate)?
In our final merged dataset, we have 19 instances (1 per borough).

<!--  SPACING -->

### Does the dataset contain all possible instances or is it a sample (not necessarily random) of instances from a larger set? 
**If the dataset is a sample, then what is the larger set? Is the sample representative of the larger set (e.g., geographic coverage)? If so, please describe how this representativeness was validated/verified. If it is not representative of the larger set, please describe why not (e.g., to cover a more diverse range of instances, because instances were withheld or unavailable).**

This dataset contains all possible instances (all 19 boroughs are represented by an instance).

<!--  SPACING -->

###  What data does each instance consist of? 
**“Raw” data (e.g., unprocessed text or images) or features? In either case, please provide a description.**

The data from the source datasets were varied:
- schools with location and level of education
- parks with location, administrative handler and area
- crime records with type of crime, date and location
- 311 complaints with nature of complaint, date and location
- renting information with housing costs, cost burden, household income, costs per number of bedrooms and renter household counts.

Number of instances for each source dataset:
- Schools: 355 instances
- Parks: 1646 instances
- Crimes: 22545 instances
- 311 requests: 332341 instances
- Renting information: 100 instances <!-- @Arash please confirm --> 

Each source dataset contains all instances that were complete and provided by the city of Montreal or the province of Quebec.

<!--  SPACING -->

### Is there a label or target associated with each instance? 
**If so, please provide a description.**

There is currently no label associated with each instance.

<!--  SPACING -->

### Is any information missing from individual instances? 
**If so, please provide a description, explaining why this information is missing (e.g., because it was unavailable). 
This does not include intentionally removed information, but might include, e.g., redacted text.**

Everything is included. No data is missing.

<!--  SPACING -->

### Are relationships between individual instances made explicit (e.g., users’ movie ratings, social network links)? 
**If so, please describe how these relationships are made explicit.**

No relationships between instances.

<!--  SPACING -->

### Are there recommended data splits (e.g., training, development/validation, testing)? 
**If so, please provide a description of these splits, explaining the rationale behind them.**

No recommended data splits.

<!--  SPACING -->

### Are there any errors, sources of noise, or redundancies in the dataset? 
**If so, please provide a description.**

To our knowledge, there are no errors in the dataset.

<!--  SPACING -->

### Is the dataset self-contained, or does it link to or otherwise rely on external resources (e.g., websites, tweets, other datasets)? 
**If it links to or relies on external resources, a) are there guarantees that they will exist, and remain constant, over time; b) are there official archival versions of the complete dataset (i.e., including the external resources as they existed at the time the dataset was created); c) are there any restrictions (e.g., licenses, fees) associated with any of the external resources that
might apply to a dataset consumer? Please provide descriptions of all external resources and any restrictions associated with them, as well as links or other access points, as appropriate.**

The dataset is self-contained.

<!--  SPACING -->

### Does the dataset contain data that might be considered confidential (e.g., data that is protected by legal privilege or by doctor–patient confidentiality, data that includes the content of individuals’ non-public communications)? 
**If so, please provide a description.**

The data sources are all publicly available through government sites, so they cannot be considered confidential.

<!--  SPACING -->

### Does the dataset contain data that, if viewed directly, might be offensive, insulting, threatening, or might otherwise cause anxiety?
**If so, please describe why.**

The dataset does not contain data that could be seen as offensive.


<!--  SPACING -->

### Does the dataset identify any subpopulations (e.g., by age, gender)? 
**If so, please describe how these subpopulations are identified and provide a description of their respective distributions within the dataset.**

No.

<!--  SPACING -->

### Is it possible to identify individuals (i.e., one or more natural persons), either directly or indirectly (i.e., in combination with other data) from the dataset? 
**If so, please describe how.**

No.

<!--  SPACING -->

### Does the dataset contain data that might be considered sensitive in any way (e.g., data that reveals race or ethnic origins, sexual orientations, religious beliefs, political opinions or union memberships, or locations; financial or health data; biometric or genetic data; forms of government identification, such as social security numbers; criminal history)? 
**If so, please provide a description.**

No.

<!--  SPACING -->

### Any other comments?

None.

-------------

## Collection Process

### How was the data associated with each instance acquired? 
**Was the data directly observable (e.g., raw text, movie ratings), reported by subjects (e.g., survey responses), or indirectly inferred/derived from other data (e.g., part-of-speech tags, model-based guesses for age or language)? 
If the data was reported by subjects or indirectly inferred/derived from other data, was the data validated/verified? 
If so, please describe how.**

The data was taken from government (Quebec and Montreal) official datasets. It was then cleaned (removing rows with missing/incoherent values), and aggregate statistics were computed.

<!--  SPACING -->

### What mechanisms or procedures were used to collect the data (e.g., hardware apparatuses or sensors, manual human curation, software programs, software APIs)? 
**How were these mechanisms or procedures validated?**

The data was collected through software APIs and HTML scraping.

<!--  SPACING -->

### If the dataset is a sample from a larger set, what was the sampling strategy (e.g., deterministic, probabilistic with specific sampling probabilities)?
The data did not require any sampling

<!--  SPACING -->

### Who was involved in the data collection process (e.g., students, crowdworkers, contractors) and how were they compensated (e.g., how much were crowdworkers paid)?
The data was collected from the government sources by the students in the group. There is no compensation.

<!--  SPACING -->

### Over what timeframe was the data collected? 
**Does this timeframe match the creation timeframe of the data associated with the instances (e.g., recent crawl of old news articles)? 
If not, please describe the timeframe in which the data associated with the instances was created.**

The data was collected between 26/09/2026 and 07/10/2026. The data collected regarding crime statistics and 311 complaints were filtered for the year 2021. This year was chosen because it aligns with the latest available census data for Montreal so that the data is the most up to date as possible.

The crime data is modified daily and was last collected on 7/10/2026.
The 311 data was reportedly last modified on 4/10/2026 and was last collected on 7/10/2026.
The parks data was reportedly last modified before our collection on 28/08/2026 and was last collected on 7/10/2026.
The schools data was reportedly last modified before our collection on 22/09/2026 and was last collected on 7/10/2026.
The rent data was reportedly last modified 9 months before our collection, with the metadata being last modified on 21/01/2026. We downloaded this data on 28/10/2026. <!-- @Arash please confirm>

<!--  SPACING -->

### Were any ethical review processes conducted (e.g., by an institutional review board)? 
**If so, please provide a description of these review processes, including the outcomes, as well as a link or other access point to any supporting documentation.**

No ethical review was conducted by our team. It is unknown if there were reviews conducted for the source datasets.

<!--  SPACING -->

### Did you collect the data from the individuals in question directly, or obtain it via third parties or other sources (e.g., websites)?

As described above, the data was collected from government datasets published on the [Montréal](donnees.montreal.ca) or [Québec](https://www.donneesquebec.ca/) data portals.

<!--  SPACING -->

### Were the individuals in question notified about the data collection? 
**If so, please describe (or show with screenshots or other information) how notice was provided, and provide a link or other access point to, or otherwise reproduce, the exact language of the notification itself.**

No, the people who created all mentioned datasets were not contacted, nor were the people who may have may have been involved in the crime or citizen requests reported on.

<!--  SPACING -->

### Did the individuals in question consent to the collection and use of their data? 
**If so, please describe (or show with screenshots or other information) how consent was requested and provided, and provide a link or other access point to, or otherwise reproduce, the exact language to which the individuals consented.**

No explicit consent was asked for the use of the data in our project. However, we hope that the measures taken by the dataset publishers to obtain consent and obfuscate personal information were enough.

<!--  SPACING -->

### If consent was obtained, were the consenting individuals provided with a mechanism to revoke their consent in the future or for certain uses? 
**If so, please provide a description, as well as a link or other access point to the mechanism (if appropriate).**

N/A.

<!--  SPACING -->

### Has an analysis of the potential impact of the dataset and its use on data subjects (e.g., a data protection impact analysis) been conducted? 
**If so, please provide a description of this analysis, including the outcomes, as well as a link or other access point to any supporting documentation.**

N/A.

<!--  SPACING -->

### Any other comments?

None.

-------------

## Preprocessing/cleaning/labeling

### Was any preprocessing/cleaning/labeling of the data done (e.g., discretization or bucketing, tokenization, part-of-speech tagging, SIFT feature extraction, removal of instances, processing of missing values)? 
**If so, please provide a description. If not, you may skip the remaining questions in this section.**

The source data that we ingested was cleaned and filtered to get rid of rows with missing data or unwanted data (e.g. private parks or schools that are not in any of the 19 boroughs).
The resulting aggregate statistics in our final dataset were normalized to values between 0 and 1.

<!--  SPACING -->

### Was the “raw” data saved in addition to the preprocessed/cleaned/labeled data (e.g., to support unanticipated future uses)? 
**If so, please provide a link or other access point to the “raw” data.**

The raw data for the crime, parks and schools data can be found under [data/raw/*.csv](https://github.com/aureliegallet/COMP570-project/tree/main/data/raw) in the GitHub linked in the following question. The raw data for the 311 requests was not saved due to size concerns.

<!--  SPACING -->

### Is the software that was used to preprocess/clean/label the data available? 
**If so, please provide a link or other access point.**

Yes, all code used for these purposes is available at [https://github.com/aureliegallet/COMP570-project](https://github.com/aureliegallet/COMP570-project).

<!--  SPACING -->

### Any other comments?

None.

-------------

## Uses
### Has the dataset been used for any tasks already? 
**If so, please provide a description.**

The dataset has not been used for any tasks yet.

<!--  SPACING -->

### Is there a repository that links to any or all papers or systems that use the dataset? 
**If so, please provide a link or other access point.**

No papers or systems currently use the dataset.

<!--  SPACING -->

### What (other) tasks could the dataset be used for?

The dataset will be used in a future COMP570 project.

<!--  SPACING -->

### Is there anything about the composition of the dataset or the way it was collected and preprocessed/cleaned/labeled that might impact future uses? 
**For example, is there anything that a dataset consumer might need to know to avoid uses that could result in unfair treatment of individuals or groups (e.g., stereotyping, quality of service issues) or other risks or harms (e.g., legal risks, financial harms)? If so, please provide a
description. Is there anything a dataset consumer could do to mitigate these risks or harms?**

There is minimal risk of harm, as the data was already publicly available through government websites. However, it is important to note that the results in this dataset cannot objectively determine the best borough for everyone.

<!--  SPACING -->

### Are there tasks for which the dataset should not be used? 
**If so, please provide a description.**

The dataset is solely intended for the purpose of providing information that might help to choose which neighbourhood to live in given the specific criteria described above. It should not be used as a basis for discrimination against a neighborhood or neighborhoods.

<!--  SPACING -->

### Any other comments?

None.

-------------

## Distribution
### Will the dataset be distributed to third parties outside of the entity (e.g., company, institution, organization) on behalf of which the dataset was created? 
**If so, please provide a description.**

The dataset will be submitted for grading to the COMP570 teaching staff.

<!--  SPACING -->

### How will the dataset will be distributed (e.g., tarball on website, API, GitHub)? 
**Does the dataset have a digital object identifier (DOI)?**

The dataset will be available on GitHub.

<!--  SPACING -->

### When will the dataset be distributed?

The dataset will be submitted on October 7th 2026.

<!--  SPACING -->

### Will the dataset be distributed under a copyright or other intellectual property (IP) license, and/or under applicable terms of use (ToU)? 
**If so, please describe this license and/or ToU, and provide a link or other access point to, or otherwise reproduce, any relevant licensing terms or ToU, as well as any fees associated with these restrictions.**

The data does not belong to the group or its students in any way and as such will not be distributed under a copyright.

<!--  SPACING -->

### Have any third parties imposed IP-based or other restrictions on the data associated with the instances? 
**If so, please describe these restrictions, and provide a link or other access point to, or otherwise reproduce, any relevant licensing terms, as well as any fees associated with these restrictions.**

No.

<!--  SPACING -->

### Do any export controls or other regulatory restrictions apply to the dataset or to individual instances? 
**If so, please describe these restrictions, and provide a link or other access point to, or otherwise reproduce, any supporting documentation.**

No.

<!--  SPACING -->

### Any other comments?

None.

-------------

## Maintenance
### Who will be supporting/hosting/maintaining the dataset?

The students in this COMP 570 team will maintain the dataset for the duration of the project.

<!--  SPACING -->

### How can the owner/curator/manager of the dataset be contacted (e.g., email address)?

The students can be contacted at:
- aurelie.gallet@mail.mcgill.ca
- harry.hu@mail.mcgill.ca
- andrew.saffar@mail.mcgill.ca
- arash.tavangar@mail.mcgill.ca

<!--  SPACING -->


### Is there an erratum? 
**If so, please provide a link or other access point.**

No.

<!--  SPACING -->

### Will the dataset be updated (e.g., to correct labeling errors, add new instances, delete instances)? 
**If so, please describe how often, by whom, and how updates will be communicated to dataset consumers (e.g., mailing list, GitHub)?**

The dataset may be updated in accordance with future project tasks as necessary.

<!--  SPACING -->

### If the dataset relates to people, are there applicable limits on the retention of the data associated with the instances (e.g., were the individuals in question told that their data would be retained for a fixed period of time and then deleted)? 
**If so, please describe these limits and explain how they will be enforced.**

N/A.

<!--  SPACING -->

### Will older versions of the dataset continue to be supported/hosted/maintained?
**If so, please describe how. If not, please describe how its obsolescence will be communicated to dataset consumers.**

N/A.

<!--  SPACING -->

### If others want to extend/augment/build on/contribute to the dataset, is there a mechanism for them to do so? 
**If so, please provide a description. Will these contributions be validated/verified? If so, please describe how. If not, why not? Is there a process for communicating/distributing these contributions to dataset consumers? If so, please provide a description.**

If the COMP570 teaching staff have any feedback or contributions they would like to make, we welcome it either via the direct project feedback or via email. 

<!--  SPACING -->

### Any other comments
None.
