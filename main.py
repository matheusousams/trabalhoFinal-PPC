import numpy as np
from random import choice, randint
from threading import Condition, Thread
from time import sleep, time

NUMERO_DE_PESSOAS = 180
NUMERO_DE_BOXES = 3
util_time = 0
generos = ['M', 'F', 'Q']
contadorDeGeneros = [0, 0, 0]
fila = []
tempoDeEsperaHomens = []
tempoDeEsperaMulheres = []
tempoDeEsperaQueers = []


class Temporizador(Thread):
    def __init__(self, cv):
        Thread.__init__(self)
        self.condition = cv
        self.time = 0

    def run(self):
        print('**********START**********')
        while(True):
            with(self.condition):
                while(banheiro.is_empty and quantidadeDePessoas < NUMERO_DE_PESSOAS):
                    self.condition.wait()

            tempo_inicial = time()
            with(self.condition):
                while((not banheiro.is_empty) and quantidadeDePessoas < NUMERO_DE_PESSOAS):
                    self.condition.wait()

            dif = time() - tempo_inicial
            self.time += dif
            if(quantidadeDePessoas == NUMERO_DE_PESSOAS):
                global util_time
                print('**********END**********\n\n')
                util_time = self.time
                break

class Pessoa(Thread):
    def __init__(self, cv, genero, i):
        Thread.__init__(self)
        self.genero = genero
        self.condition = cv
        self.i = i

    def __str__(self):
        return 'Pessoa {} ({})'.format(self.id, self.genero)

    def run(self):
        global quantidadeDePessoas
        s = 'Pessoa {} de gênero ({}) chega\n'.format(self.i, self.genero)
        print(s)
        IniciarTempoDeEspera = time()
        fila.append(self)
        self.entrarNoBanheiro()
        if(self.genero == 'M'):
            tempoDeEsperaHomens.append(time() - IniciarTempoDeEspera)
        elif(self.genero == 'F'):
            tempoDeEsperaMulheres.append(time() - IniciarTempoDeEspera)
        else:
            tempoDeEsperaQueers.append(time() - IniciarTempoDeEspera)
        print('Pessoa {} está utilizando o banheiro\n'.format(self.i))
        sleep(5)
        self.sairDoBanheiro()
        print('Pessoa {} acaba de sair do banheiro\n'.format(self.i))
        quantidadeDePessoas += 1

    def entrarNoBanheiro(self):
        with(self.condition):
            while(True):
                if(fila.index(self) > 0):
                    printar = 'Pessoa {} não entrou porque não era a primeira da fila\n'.format(self.i)
                    print(printar)
                    self.condition.wait()
                    continue
                if(banheiro.is_full):
                    printar = 'Pessoa {} não entrou porque o banheiro estava cheio\n'.format(self.i)
                    print(printar)
                    self.condition.wait()
                    continue
                if(banheiro.is_empty):
                    break
                if(banheiro.genero != self.genero):
                    printar = 'Pessoa {} não entrou porque havia outro gênero no banheiro\n'.format(self.i)
                    print(printar)
                    self.condition.wait()
                    continue
                break

        fila.remove(self)
        banheiro.append(self)
        with(self.condition):
            self.condition.notify_all()

    def sairDoBanheiro(self):
        with(self.condition):
            banheiro.remove(self)
            self.condition.notify_all()


class Bathroom:
    def __init__(self, num_boxes):
        self.pessoas = []
        self.boxes = num_boxes

    @property
    def genero(self):
        try:
            return self.pessoas[0].genero
        except IndexError:
            return None

    def append(self, p):
        self.pessoas.append(p)

    def remove(self, p):
        self.pessoas.remove(p)

    @property
    def is_full(self):
        return len(self.pessoas) == self.boxes

    @property
    def is_empty(self):
        return len(self.pessoas) == 0


banheiro = Bathroom(num_boxes=NUMERO_DE_BOXES)
quantidadeDePessoas = 0


def main():
    cv = Condition()
    contTempo = Temporizador(cv)
    contTempo.start()
    forThreads = time()
    for i in range(NUMERO_DE_PESSOAS):
        flag = False
        while(not flag):
            genero = choice(generos)
            if(contadorDeGeneros[generos.index(genero)] < (NUMERO_DE_PESSOAS / 3)):
                flag = True
                contadorDeGeneros[generos.index(genero)] += 1
        p = Pessoa(cv, genero, i + 1)
        p.start()
        sleep(randint(2, 6))

    while(quantidadeDePessoas < NUMERO_DE_PESSOAS):
        pass

    with(cv):
        cv.notify_all()

    contTempo.join()
    tempoTotal = time() - forThreads
    usage_rate = 100 * (util_time / tempoTotal)
    print('Quantidade de pessoas de cada gênero:')
    print('Homens   -> {}'.format(contadorDeGeneros[0]))
    print('Mulheres -> {}'.format(contadorDeGeneros[1]))
    print('Queers   -> {}'.format(contadorDeGeneros[2]))
    print('********************************************** ')
    print('Tempo médio de espera para usar o banheiro para cada gênero:')
    print('Homens   -> {0:.2f}s'.format(np.mean(tempoDeEsperaHomens)))
    print('Mulheres -> {0:.2f}s'.format(np.mean(tempoDeEsperaMulheres)))
    print('Queers   -> {0:.2f}s'.format(np.mean(tempoDeEsperaQueers)))
    print('***********************************************')
    print('Tempo total: {0:.2f}s'.format(tempoTotal))
    print('Taxa de ocupação: {0:.2f}%'.format(usage_rate))


if(__name__ == '__main__'):
    main()
