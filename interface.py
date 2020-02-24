# Haikusaare command line interface

from haikusaare import Haikusaare
from faulthandler import enable, disable # for profiler

def run():
    enable() # crashes possible from EstNLTK C/C++ code

    print('Haikusaare valmistub...')
    generator = Haikusaare()

    #while True: # temp comment
    for insp in ['perenaine', 'mees', 'mets', 'talu', 'vankrid', 'Eesti', 'jumal', 'onu', 'quit']: #temp

        print()
        print('Anna haiku jaoks ühe sõnaga inspiratsiooni (või kirjuta "quit" et lahkuda):')
        #insp = input('> ') # temp comment
        print('> '+insp) # temp

        if insp.strip() == 'quit':
            break

        print()
        print('haikusaare:')
        print(generator.generate_haiku(insp))

    print('\nJää hüvasti!')
    disable()

if __name__ == '__main__':
    run()
