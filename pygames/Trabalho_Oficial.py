import pygame ,sys ,random

pygame.init()#Inicia os módulos do pygame
#Fazendo algumas definições iniciais
TELA_LARGURA = 750
TELA_ALTURA = 700
CINZA = (29,29,27)
AMARELO = (243, 216, 63)
VERMELHO = (255,0,0)
#Preparando alguns dos textos que irão aparecer
nome_jogo = pygame.font.Font('monogram.ttf', 100)
instrucoes = pygame.font.Font('monogram.ttf', 35)
font = pygame.font.Font('monogram.ttf', 40)
level_surface = font.render("LEVEL 01", False, AMARELO)
game_over_surface = font.render("GAME OVER", False, AMARELO)
gameover_surface = font.render("Pressione P para recomecar", False , AMARELO)
gameover_surface_2 = font.render("Pressione ESC para voltar ao menu", False , AMARELO)
score_text_surface = font.render("SCORE", False, AMARELO)

#Preparando a tela
tela = pygame.display.set_mode((TELA_LARGURA,TELA_ALTURA + 100))#dimensões da janela
pygame.display.set_caption("Python space invaders")#Título da janela

relogio = pygame.time.Clock()

#Criando Laser
class Laser(pygame.sprite.Sprite):
    def __init__(self, posicao, velocidade, tela_altura):
        super().__init__()
        self.image = pygame.Surface((4,15))
        self.image.fill((243,216,63))
        self.rect = self.image.get_rect(center = posicao)
        self.velocidade = velocidade
        self.tela_altura = tela_altura
    def update(self):
        self.rect.y -= self.velocidade
        if self.rect.y > self.tela_altura + 15 or self.rect.y < 0:
            self.kill()

#Criando aliens
class Alien(pygame.sprite.Sprite):
    def __init__(self, x ,y):
        super().__init__()
        self.image = pygame.image.load("alien_1.png")
        self.rect = self.image.get_rect(topleft = (x, y))

    def update(self , direcao):
        self.rect.x += direcao

#Criando Nave Diferente e Misteriosa
class MysteryShip(pygame.sprite.Sprite):
    def __init__(self, tela_largura):
        super().__init__()
        self.tela_largura = tela_largura
        self.image = pygame.image.load("mystery.png")

        x = random.choice([0, self.tela_largura - self.image.get_width() ])
        if x == 0:
            self.velocidade = 3
        else:
            self.velocidade = -3
        self.rect = self.image.get_rect(topleft = (x, 40))
    
    def update(self):
        self.rect.x += self.velocidade
        if self.rect.right > self.tela_largura:
            self.kill()
        elif self.rect.left < 0:
            self.kill()


#Criando Jogador Principal
class Nave(pygame.sprite.Sprite):
    def __init__(self, tela_largura, tela_altura):
        super().__init__()
        self.tela_largura = tela_largura
        self.tela_altura = tela_altura
        self.image = pygame.image.load("spaceship.png")
        self.rect = self.image.get_rect(midbottom = (self.tela_largura/2, self.tela_altura))
        self.velocidade = 6 
        self.lasers_group = pygame.sprite.Group()
        self.laser_pronto = True 
        self.laser_time = 0 
        self.laser_delay = 300

    def comandos_do_jogador(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]: #Ir para a direita
            self.rect.x += self.velocidade
        if keys[pygame.K_LEFT]: #Ir para a esquerda
            self.rect.x -= self.velocidade 
        if keys[pygame.K_SPACE] and self.laser_pronto: #Atirar
            self.laser_pronto = False
            laser = Laser(self.rect.center, 5, self.tela_altura)
            self.lasers_group.add(laser)
            self.laser_time = pygame.time.get_ticks()

    def limitar_movimento(self):
        if self.rect.right > self.tela_largura:
            self.rect.right = self.tela_largura
        if self.rect.left < 0:
            self.rect.left = 0
        
    def recarregar_laser(self):
        if not self.laser_pronto:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_time >= self.laser_delay:
                self.laser_pronto = True 

    def reset(self):
        self.rect = self.image.get_rect(midbottom = (self.tela_largura/2 , self.tela_altura))
        self.lasers_group.empty()

    def update(self):
        self.comandos_do_jogador()
        self.limitar_movimento()
        self.lasers_group.update()
        self.recarregar_laser()





class Jogo:
    def __init__(self, tela_largura, tela_altura):
        self.tela_largura = tela_largura 
        self.tela_altura = tela_altura 
        self.nave_group = pygame.sprite.GroupSingle()
        self.nave_group.add(Nave(self.tela_largura, self.tela_altura))
        self.aliens_group = pygame.sprite.Group()
        self.criar_aliens()
        self.aliens_direcao = 1
        self.alien_laser_group = pygame.sprite.Group()
        self.mystery_ship_group = pygame.sprite.GroupSingle()
        self.vidas = 3 
        self.run = True
        self.score = 0




    def criar_aliens(self):
        for linha in range(5):
            for coluna in range(11):
                x = 75 + coluna * 55
                y = 110 + linha * 55
                alien = Alien(x, y)
                self.aliens_group.add(alien)

    def mover_aliens(self):
        self.aliens_group.update(self.aliens_direcao)

        aliens_sprites = self.aliens_group.sprites()
        for alien in aliens_sprites:
            if alien.rect.right >= self.tela_largura:
                self.aliens_direcao = -1
                self.alien_move_baixo(2)
            elif alien.rect.left <= 0:
                self.aliens_direcao = 1
                self.alien_move_baixo(2)

    def alien_move_baixo(self, distancia):
        if self.aliens_group:
            for alien in self.aliens_group.sprites():
                alien.rect.y += distancia
    
    def alien_atira_laser(self):
        if self.aliens_group.sprites():
            random_alien = random.choice(self.aliens_group.sprites())
            laser_sprite = Laser(random_alien.rect.center, -6, self.tela_altura)
            self.alien_laser_group.add(laser_sprite)

    def criar_mystery_ship(self):
        self.mystery_ship_group.add(MysteryShip(self.tela_largura))

    def checkando_colisoes(self):
        #Nave
        if self.nave_group.sprite.lasers_group:
            for laser_sprite in self.nave_group.sprite.lasers_group:
                aliens_leva_hit =  pygame.sprite.spritecollide(laser_sprite, self.aliens_group, True)
                if aliens_leva_hit:
                    self.score += 100
                    laser_sprite.kill() 
                if pygame.sprite.spritecollide(laser_sprite, self.mystery_ship_group, True):
                   self.score += 500
                   laser_sprite.kill() 

        #Alien Lasers
        if self.alien_laser_group:
            for laser_sprite in self.alien_laser_group:
                if pygame.sprite.spritecollide(laser_sprite, self.nave_group, False):
                    laser_sprite.kill()
                    self.vidas -= 1
                    if self.vidas == 0:
                        self.game_over()


        if self.aliens_group:
            for alien in self.aliens_group:
                if pygame.sprite.spritecollide(alien, self.nave_group, False):
                    self.game_over()
                
    
    def checkando_aliens(self):
        if len(self.aliens_group) + len(self.mystery_ship_group) == 0 :
             self.game_over()


    def game_over(self):
        self.run = False

    def reset(self):
        self.run = True 
        self.vidas = 3 
        self.nave_group.sprite.reset()
        self.aliens_group.empty()
        self.alien_laser_group.empty()
        self.criar_aliens()
        self.mystery_ship_group.empty()
        self.score = 0
        


jogo = Jogo(TELA_LARGURA, TELA_ALTURA)

ATIRAR_LASER = pygame.USEREVENT
pygame.time.set_timer(ATIRAR_LASER, 300)

MYSTERYSHIP = pygame.USEREVENT + 1 
pygame.time.set_timer(MYSTERYSHIP, random.randint(4000,8000))

cena ="menu"

while True:
    #checkando eventos
    if cena =="jogo":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == ATIRAR_LASER and jogo.run:
                jogo.alien_atira_laser()
            if event.type == MYSTERYSHIP and jogo.run:
                jogo.criar_mystery_ship()
                pygame.time.set_timer(MYSTERYSHIP, random.randint(4000,8000))
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    cena = "menu"
            


            keys = pygame.key.get_pressed()
            if keys[pygame.K_p] and jogo.run == False:
                jogo.reset()


        #Updating
        if jogo.run:
            jogo.nave_group.update()
            jogo.mover_aliens()
            jogo.alien_laser_group.update()
            jogo.mystery_ship_group.update()
            jogo.checkando_colisoes()
            jogo.checkando_aliens()


        #desenhando
        tela.fill(CINZA)


        pygame.draw.line(tela, AMARELO,(0, 730), (775, 730), 3)
        if jogo.run:
            tela.blit(level_surface, (580,750,50,5))
        else:
            tela.blit(gameover_surface, (200,500,50,5))
            tela.blit(game_over_surface, (580,750,50,5))
            tela.blit(gameover_surface_2, (150,550,50,5) )
            
        
        x = 50
        for live in range(jogo.vidas):
            tela.blit(jogo.nave_group.sprite.image, (x,745))
            x += 50
        tela.blit(score_text_surface,(50,15,50,50))
        score_surface = font.render(str(jogo.score),False,AMARELO)
        tela.blit(score_surface, (50,40,50,50))

        jogo.nave_group.draw(tela)
        jogo.nave_group.sprite.lasers_group.draw(tela)
        jogo.aliens_group.draw(tela)
        jogo.alien_laser_group.draw(tela)
        jogo.mystery_ship_group.draw(tela)



        pygame.display.update()
        relogio.tick(60)
    
    

    elif cena == "menu":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    cena = "jogo"
        
        tela.fill(CINZA)
        text = nome_jogo.render("Aliens Invaders", True, AMARELO)
        text_comandos = instrucoes.render("Use as 'setinhas' para se mover,e 'espaco' para atirar",True, AMARELO)
        text_comecar = instrucoes.render("Pressione ENTER para iniciar", True, AMARELO)
        tela.blit(text, (120, 150))
        tela.blit(text_comandos, (30,500))
        tela.blit(text_comecar, (175,600))
        pygame.display.update()
