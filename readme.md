# Haikusaare - Tammsaare haiku generator

N-gram Markov Model haiku generator (syllabification from estnltk) and corresponding web application. Usable with any Estonian text corpus but the text processing code is built for the specific A. H. Tammsaare corpus bundled in the repository. All bundled books are freely available from [digiraamat.ee](https://www.digiraamat.ee/) and [wikisource.org](https://et.wikisource.org/wiki/Esileht). 
 
Requires the ```estnltk 1.6.5beta``` and ```flask``` packages for python. To run locally, run ```server.py```. To run in a server, set up ```wsgi``` and ```nginx```. 

Some great examples can be found in ```pearls.txt```.
