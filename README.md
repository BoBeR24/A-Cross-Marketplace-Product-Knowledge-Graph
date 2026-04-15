# A-Cross-Marketplace-Product-Knowledge-Graph
## Building A Cross-Marketplace Product Knowledge Graph. Project made in affiliation with Maastricht University as a part of Building And Mining Knowledge Graphs course.

The project is separated in sections:
- [`data_processing`](./data_processing) contains Jupyter Notebooks for cleaning both used datasets
- [`building_the_graph`](./building_the_graph) contains the Jupyter Notebook which creates and enriches the graph,
  Notebook for visualization and gathering statistics.
- [`data`](./data) contains all datasets used in this project(if `data` is missing, refer to `data_processing` jupyter files)
- [`graphs`](./graphs) contains `.ttl` files with all the graphs, including SHACL shapes.
- [`vector_store_1000`](./vector_store_1000) contains vector store files for the `graph_1000.ttl`

---

If you want to try information retrieval tool, you can use [retrieval_system.py](./retrieval_system.py).
1. For that first ensure that you have all the dependencies installed:  
       For pip:  
       ```
         pip install -r requirements.txt
       ```  
       For conda(this will create environment from `.yml`):  
       ```
       conda env create -f environment.yml
       ```

2. To launch the tool use(don't forget to activate conda environment if you have one):  
       ```
         python ./retrieval_system.py
       ```
3. Using the tool you can either create new vector store, or use the existing one(only for the `graph_1000`). It is recommended to use
smaller graph for tests, `graph_20000` can take tens of minutes to create vector store from(for a fast test 
[vector_store_test](./vector_store_test) is available). 
  There is also an example SPARQL query in `./query.txt`, you can try it using `retrieval_system.py`, it will produce 
something like this(may take up to a few minutes):

```
'product: http://products-kg.org/product/83'
('label: Swan 4 Holes 8 Tones Mini Harmonica Metal Chain '
 'Necklace Style Mouth Organ Excellent and Useful and '
 'Attractive')
'offer: http://products-kg.org/offer/83'
'price: 2.58'
'currency: USD'
----------------------------------------------------------------------------------------------------
'product: http://products-kg.org/product/167'
('label: Shredneck Tuner Tips - Tuning Post Covers - '
 'Protectors - Model: TT1 - Package of 12 tips')
'offer: http://products-kg.org/offer/167'
'price: 4.49'
'currency: USD'
----------------------------------------------------------------------------------------------------
'product: http://products-kg.org/product/151'
('label: Mini 8 Key Kalimba Thumb Piano Gifts for Kids '
 'Beginners Music Lovers Players, Cute Instrument Pendant '
 'Keychain Accessories, Wood Finger Thumb piano, Musical '
 'good accessory Pendant Gift')
'offer: http://products-kg.org/offer/151'
'price: 4.99'
'currency: USD'
----------------------------------------------------------------------------------------------------
'product: http://products-kg.org/product/67'
('label: Removable Piano Keyboard Note Labels, Piano '
 'Keyboard Stickers for Beginners, 88 Key Full Size '
 'Silicone Piano Notes Guide')
'offer: http://products-kg.org/offer/67'
'price: 5.88'
'currency: USD'
----------------------------------------------------------------------------------------------------
'product: http://products-kg.org/product/374'
('label: Microphone Cover Thick Mic Cover Colorful Foam '
 'Microphone Windscreen Reusable Microphone Covers '
 'Suitable for Karaoke DJ, Conference Room, Stage '
 'Performance(5PCS)')
'offer: http://products-kg.org/offer/374'
'price: 5.95'
'currency: USD'
----------------------------------------------------------------------------------------------------
```


---
## AI Disclosure

Ai was used only for help in code generation. All analysis, report and other things were done exclusively by human