# Database Structure and Organization

The database used in this project was divided into **8 separate parts**.  
The reason for this decision is related to the way the data was collected from the Wiki API. When making large numbers of requests, it is necessary to respect the API’s rate limits and introduce delays between queries. Without these delays, the API would reject or throttle the requests, making the data collection process unreliable or even blocked.  

If the entire dataset were to be downloaded in a single run from one machine, the process would take an extremely long time because every request would have to be slowed down with pauses in order to comply with the API restrictions. Splitting the dataset into 8 parts allowed the collection to be spread across multiple runs or systems, which reduced the effective waiting time and made the whole process more manageable.  

This partitioning was purely a matter of timing and API rate limitations, not a hardware issue. Each of the 8 parts represents a portion of the same dataset and can be used independently during development and testing. However, for convenience and completeness, the **entire dataset has also been stored in the folder `full_set/`**. That directory contains all the collected data combined into a single, unpartitioned form.  

