# LOCM
An implementation of Learning Object-Centric Models (LOCM).  
It takes valid action sequences and generated a domain model (in PDDL).  


locm1.py is our implementation directly according to the paper.  
While locm2.py is a modified from Shivam Miglani's work reducing the interactive components in order to reduce user interaction.

## How to run

- Install dependencies in requirements.txt
- Go to the root folder
- Save your action sequences in Training sequence folder using the length of the sequence as a file name. Example if the length of 
the sequence = 10, save it as 10.txt.
- Run run_locm.bash with an input argument 1 to run locm1 and 2 for locm2.  For example to run locm2:
```
$ ./run_locm.bash 2
```
### Features
- requires only action sequences as an input (no need to specify intermediate states)
- provides action schima both in graphical and xml format
### To do
- Learn static predicates

## Sources
- LOCM is based on the paper "Acquiring planning domain models using LOCM"     https://www.researchgate.net/publication/259432709 .
- https://icaps20subpages.icaps-conference.org/wp-content/uploads/2020/10/KEPS-2020_paper_16.pdf


