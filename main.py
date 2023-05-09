import sys
import pygame
import string
import queue

#######################################################
############### CHARGEMENT DES IMAGES #################
#######################################################
mur= pygame.image.load("images/mur.png")
fond= pygame.image.load("images/fond.png")
caisse= pygame.image.load("images/caisse.png")
ouvrier= pygame.image.load("images/ouvrier.png")
ouvrier_Sur_Objectif= pygame.image.load("images/ouvrier_sur_objectif.png")
caisse_Sur_Objectif= pygame.image.load("images/caisse_sur_objectif.png")
objectif= pygame.image.load("images/objectif.png")
# eau= pygame.image.load("images/eau.png")

background = 255, 226, 191

#######################################################
############### CHARGEMENT DES SONS ###################
#######################################################
# son_mur = pygame.mixer.Sound("sons/mur.wav")
# son_caisse = pygame.mixer.Sound("sons/caisse.wav")
# son_dock = pygame.mixer.Sound("sons/dock.wav")
# son_gagne = pygame.mixer.Sound("sons/gagne.wav")



#######################################################
################### CLASSE GAME #######################
#######################################################
class game:

    def carractere_Valid(self,caractere):
        if ( caractere == ' ' or #fond
            caractere == '#' or #mur
            caractere == '@' or #ouvrier
            caractere == '.' or #objectif
            caractere == '*' or #caisse sur objectif
            caractere == '$' or #caisse
            caractere == '+' or #ouvrier sur objectif
            caractere == '~'):  #eau
            return True
        else:
            return False

    def __init__(self,filename,level):
        # crée une file d'attente LIFO (Last In, First Out) à l'aide de la classe LifoQueue de la bibliothèque queue
        # LIFO signifie que le dernier élément ajouté à la file d'attente est le premier élément à être retiré
        self.queue = queue.LifoQueue()
        self.map = []

        if int(level) < 1:
            print ("ERROR: Level "+str(level)+" n'existe pas")
            sys.exit(1)
        else:
            file = open(filename,'r')
            level_found = False
            for line in file:
                row = []
                if not level_found:
                    if  "Level "+str(level) == line.strip():
                        level_found = True
                else:
                    if line.strip() != "":
                        row = []
                        for c in line:
                            if c != '\n' and self.carractere_Valid(c):
                                row.append(c)
                            elif c == '\n': #jump to next row when newline
                                continue
                            else:
                                print ("ERROR: Level "+str(level)+" est invalide "+c)
                                sys.exit(1)
                        self.map.append(row)
                    else:
                        break
            if not level_found:
                print ("ERROR: Level "+str(level)+" not found")
                sys.exit(1)


    def size(self):
        x = 0
        y = len(self.map)
        for row in self.map:
            if len(row) > x:
                x = len(row)
        return (x * 32, y * 32)

    def get_map(self):
        return self.map

    def print_map(self):
        for row in self.map:
            for char in row:
                sys.stdout.write(char)
                sys.stdout.flush()
            sys.stdout.write('\n')

    def get_content(self,x,y):
        return self.map[y][x]

    def set_content(self,x,y,content):
        if self.carractere_Valid(content):
            self.map[y][x] = content
        else:
            print ("ERROR: Value '"+content+"' n'est pas valide")

    def worker(self):
        x = 0
        y = 0
        for row in self.map:
            for pos in row:
                if pos == '@' or pos == '+':
                    return (x, y, pos)
                else:
                    x = x + 1
            y = y + 1
            x = 0

    def can_move(self,x,y):
        return self.get_content(self.worker()[0]+x,self.worker()[1]+y) not in ['#','*','$']

    def next(self,x,y):
        return self.get_content(self.worker()[0]+x,self.worker()[1]+y)

    def can_push(self,x,y):
        return (self.next(x,y) in ['*','$'] and self.next(x+x,y+y) in [' ','.'])

    def is_completed(self):
        for row in self.map:
            for cell in row:
                if cell == '$':
                    return False
        return True

    def move_box(self,x,y,a,b):
#        (x,y) -> move to do
#        (a,b) -> box to move
        current_box = self.get_content(x,y)
        future_box = self.get_content(x+a,y+b)
        if current_box == '$' and future_box == ' ':
            self.set_content(x+a,y+b,'$')
            self.set_content(x,y,' ')
        elif current_box == '$' and future_box == '.':
            self.set_content(x+a,y+b,'*')
            self.set_content(x,y,' ')
        elif current_box == '*' and future_box == ' ':
            self.set_content(x+a,y+b,'$')
            self.set_content(x,y,'.')
        elif current_box == '*' and future_box == '.':
            self.set_content(x+a,y+b,'*')
            self.set_content(x,y,'.')

    def unmove(self):
        if not self.queue.empty():
            movement = self.queue.get()
            if movement[2]:
                current = self.worker()
                self.move(movement[0] * -1,movement[1] * -1, False)
                self.move_box(current[0]+movement[0],current[1]+movement[1],movement[0] * -1,movement[1] * -1)
            else:
                self.move(movement[0] * -1,movement[1] * -1, False)

    def move(self,x,y,save):
        if self.can_move(x,y):
            current = self.worker()
            future = self.next(x,y)
            if current[2] == '@' and future == ' ':
                self.set_content(current[0]+x,current[1]+y,'@')
                self.set_content(current[0],current[1],' ')
                if save: self.queue.put((x,y,False))

            elif current[2] == '@' and future == '.':
                self.set_content(current[0]+x,current[1]+y,'+')
                self.set_content(current[0],current[1],' ')
                if save: self.queue.put((x,y,False))

            elif current[2] == '+' and future == ' ':
                self.set_content(current[0]+x,current[1]+y,'@')
                self.set_content(current[0],current[1],'.')
                if save: self.queue.put((x,y,False))

            elif current[2] == '+' and future == '.':
                self.set_content(current[0]+x,current[1]+y,'+')
                self.set_content(current[0],current[1],'.')
                if save: self.queue.put((x,y,False))

        elif self.can_push(x,y):
            current = self.worker()
            future = self.next(x,y)
            future_box = self.next(x+x,y+y)

            if current[2] == '@' and future == '$' and future_box == ' ':
                self.move_box(current[0]+x,current[1]+y,x,y)
                self.set_content(current[0],current[1],' ')
                self.set_content(current[0]+x,current[1]+y,'@')
                if save: self.queue.put((x,y,True))

            elif current[2] == '@' and future == '$' and future_box == '.':
                self.move_box(current[0]+x,current[1]+y,x,y)
                self.set_content(current[0],current[1],' ')
                self.set_content(current[0]+x,current[1]+y,'@')
                if save: self.queue.put((x,y,True))

            elif current[2] == '@' and future == '*' and future_box == ' ':
                self.move_box(current[0]+x,current[1]+y,x,y)
                self.set_content(current[0],current[1],' ')
                self.set_content(current[0]+x,current[1]+y,'+')
                if save: self.queue.put((x,y,True))

            elif current[2] == '@' and future == '*' and future_box == '.':
                self.move_box(current[0]+x,current[1]+y,x,y)
                self.set_content(current[0],current[1],' ')
                self.set_content(current[0]+x,current[1]+y,'+')
                if save: self.queue.put((x,y,True))

            if current[2] == '+' and future == '$' and future_box == ' ':
                self.move_box(current[0]+x,current[1]+y,x,y)
                self.set_content(current[0],current[1],'.')
                self.set_content(current[0]+x,current[1]+y,'@')
                if save: self.queue.put((x,y,True))

            elif current[2] == '+' and future == '$' and future_box == '.':
                self.move_box(current[0]+x,current[1]+y,x,y)
                self.set_content(current[0],current[1],'.')
                self.set_content(current[0]+x,current[1]+y,'+')
                if save: self.queue.put((x,y,True))

            elif current[2] == '+' and future == '*' and future_box == ' ':
                self.move_box(current[0]+x,current[1]+y,x,y)
                self.set_content(current[0],current[1],'.')
                self.set_content(current[0]+x,current[1]+y,'+')
                if save: self.queue.put((x,y,True))
                
            elif current[2] == '+' and future == '*' and future_box == '.':
                self.move_box(current[0]+x,current[1]+y,x,y)
                self.set_content(current[0],current[1],'.')
                self.set_content(current[0]+x,current[1]+y,'+')
                if save: self.queue.put((x,y,True))

def print_game(map,screen):
    screen.fill(background)
    x = 0
    y = 0
    for row in map:
        for char in row:
            if char == ' ': #floor
                screen.blit(fond,(x,y))
            elif char == '#': #wall
                screen.blit(mur,(x,y))
            elif char == '@': #worker on floor
                screen.blit(ouvrier,(x,y))
            elif char == '.': #dock
                screen.blit(objectif,(x,y))
            elif char == '*': #box on dock
                screen.blit(caisse_Sur_Objectif,(x,y))
            elif char == '$': #box
                screen.blit(caisse,(x,y))
            elif char == '+': #worker on dock
                screen.blit(ouvrier_Sur_Objectif,(x,y))
            x = x + 32
        x = 0
        y = y + 32


def get_key():
  while 1:
    event = pygame.event.poll()
    if event.type == pygame.KEYDOWN:
      return event.key
    else:
      pass

def display_box(screen, message):
  "Print a message in a box in the middle of the screen"
  fontobject = pygame.font.Font(None,18)
  pygame.draw.rect(screen, (0,0,0),
                   ((screen.get_width() / 2) - 100,
                    (screen.get_height() / 2) - 10,
                    200,20), 0)
  pygame.draw.rect(screen, (255,255,255),
                   ((screen.get_width() / 2) - 102,
                    (screen.get_height() / 2) - 12,
                    204,24), 1)
  if len(message) != 0:
    screen.blit(fontobject.render(message, 1, (255,255,255)),
                ((screen.get_width() / 2) - 100, (screen.get_height() / 2) - 10))
  pygame.display.flip()

def display_end(screen):
    message = "Level Completed"
    fontobject = pygame.font.Font(None,18)
    pygame.draw.rect(screen, (0,0,0),
                   ((screen.get_width() / 2) - 100,
                    (screen.get_height() / 2) - 10,
                    200,20), 0)
    pygame.draw.rect(screen, (255,255,255),
                   ((screen.get_width() / 2) - 102,
                    (screen.get_height() / 2) - 12,
                    204,24), 1)
    screen.blit(fontobject.render(message, 1, (255,255,255)),
                ((screen.get_width() / 2) - 100, (screen.get_height() / 2) - 10))
    pygame.display.flip()


def ask(screen, question):
  "ask(screen, question) -> answer"
  pygame.font.init()
  current_string = []
  display_box(screen, question + ": " + "".join(current_string))
  while 1:
    inkey = get_key()
    if inkey == pygame.K_BACKSPACE:
      current_string = current_string[0:-1]
    elif inkey == pygame.K_RETURN:
      break
    elif inkey == pygame.K_MINUS:
      current_string.append("_")
    elif inkey <= 127:
      current_string.append(chr(inkey))
    display_box(screen, question + ": " + "".join(current_string))
  return "".join(current_string)

def start_game():
    start = pygame.display.set_mode((320,240))
    level = ask(start,"Select Level")
    if int(level) > 0:
        return level
    else:
        print ("ERROR: Invalid Level: "+str(level))
        sys.exit(2)


#######################################################
################# LANCEMENT DU JEU ####################
#######################################################

pygame.init()

level = start_game()
game = game('levels',level)
size = game.size()
screen = pygame.display.set_mode(size)
while 1:
    if game.is_completed(): display_end(screen)
    print_game(game.get_map(),screen)
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit(0)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP: game.move(0,-1, True)
            elif event.key == pygame.K_DOWN: game.move(0,1, True)
            elif event.key == pygame.K_LEFT: game.move(-1,0, True)
            elif event.key == pygame.K_RIGHT: game.move(1,0, True)
            elif event.key == pygame.K_q: sys.exit(0)
            elif event.key == pygame.K_d: game.unmove()
    pygame.display.update()
