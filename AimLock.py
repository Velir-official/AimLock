import pygame
import math
import random
import sys

# Инициализация Pygame
pygame.init()
pygame.mixer.init()

# Константы
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 32
        self.height = 32
        self.speed = 5
        self.health = 100
        self.max_health = 100
        self.color = BLUE
        
    def move(self, keys):
        if keys[pygame.K_w] and self.y > 0:
            self.y -= self.speed
        if keys[pygame.K_s] and self.y < SCREEN_HEIGHT - self.height:
            self.y += self.speed
        if keys[pygame.K_a] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_d] and self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed
            
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        # Рисуем направление взгляда (круг)
        pygame.draw.circle(screen, WHITE, (self.x + self.width//2, self.y + self.height//2), 5)
        
    def get_center(self):
        return (self.x + self.width//2, self.y + self.height//2)
    
    def take_damage(self, damage):
        self.health -= damage
        return self.health <= 0

class Bullet:
    def __init__(self, x, y, target_x, target_y):
        self.x = x
        self.y = y
        self.radius = 4
        self.speed = 12
        self.damage = 20
        
        # Вычисляем направление
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx**2 + dy**2)
        if distance > 0:
            self.dx = dx / distance * self.speed
            self.dy = dy / distance * self.speed
        else:
            self.dx = self.dy = 0
            
    def update(self):
        self.x += self.dx
        self.y += self.dy
        
    def draw(self, screen):
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.radius)
        
    def is_off_screen(self):
        return (self.x < -50 or self.x > SCREEN_WIDTH + 50 or 
                self.y < -50 or self.y > SCREEN_HEIGHT + 50)

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 28
        self.height = 28
        self.speed = 2
        self.health = 50
        self.max_health = 50
        self.damage = 10
        self.color = RED
        
    def move_towards(self, target_x, target_y):
        dx = target_x - (self.x + self.width//2)
        dy = target_y - (self.y + self.height//2)
        distance = math.sqrt(dx**2 + dy**2)
        if distance > 0:
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed
            
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        # Полоска здоровья
        health_ratio = self.health / self.max_health
        pygame.draw.rect(screen, RED, (self.x, self.y - 10, self.width, 5))
        pygame.draw.rect(screen, GREEN, (self.x, self.y - 10, self.width * health_ratio, 5))
        
    def take_damage(self, damage):
        self.health -= damage
        return self.health <= 0
    
    def get_center(self):
        return (self.x + self.width//2, self.y + self.height//2)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("2D Shooter")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        
        self.reset_game()
        
    def reset_game(self):
        self.player = Player(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
        self.bullets = []
        self.enemies = []
        self.score = 0
        self.game_over = False
        self.wave = 1
        self.enemies_to_spawn = 5
        self.spawn_timer = 0
        
    def spawn_enemy(self):
        side = random.randint(0, 3)  # 0: left, 1: right, 2: top, 3: bottom
        if side == 0:  # left
            x = -30
            y = random.randint(0, SCREEN_HEIGHT)
        elif side == 1:  # right
            x = SCREEN_WIDTH + 30
            y = random.randint(0, SCREEN_HEIGHT)
        elif side == 2:  # top
            x = random.randint(0, SCREEN_WIDTH)
            y = -30
        else:  # bottom
            x = random.randint(0, SCREEN_WIDTH)
            y = SCREEN_HEIGHT + 30
            
        # Увеличиваем сложность с каждой волной
        enemy = Enemy(x, y)
        enemy.speed = 2 + self.wave * 0.3
        enemy.health = 40 + self.wave * 10
        enemy.max_health = enemy.health
        return enemy
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if self.game_over and event.key == pygame.K_SPACE:
                    self.reset_game()
                    return True
            if event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                if event.button == 1:  # Левая кнопка мыши
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    player_center = self.player.get_center()
                    self.bullets.append(Bullet(player_center[0], player_center[1], mouse_x, mouse_y))
        return True
        
    def update(self):
        if self.game_over:
            return
            
        keys = pygame.key.get_pressed()
        self.player.move(keys)
        
        # Обновляем пули
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.is_off_screen():
                self.bullets.remove(bullet)
                
        # Обновляем врагов
        for enemy in self.enemies[:]:
            enemy.move_towards(self.player.x + self.player.width//2, 
                             self.player.y + self.player.height//2)
            
            # Проверка столкновения с игроком
            if (enemy.x < self.player.x + self.player.width and
                enemy.x + enemy.width > self.player.x and
                enemy.y < self.player.y + self.player.height and
                enemy.y + enemy.height > self.player.y):
                if self.player.take_damage(enemy.damage):
                    self.game_over = True
                self.enemies.remove(enemy)
                continue
                
            # Проверка столкновений пуль с врагами
            for bullet in self.bullets[:]:
                if (bullet.x + bullet.radius > enemy.x and
                    bullet.x - bullet.radius < enemy.x + enemy.width and
                    bullet.y + bullet.radius > enemy.y and
                    bullet.y - bullet.radius < enemy.y + enemy.height):
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    if enemy.take_damage(bullet.damage):
                        self.enemies.remove(enemy)
                        self.score += 10
                        break
                        
        # Спавн врагов
        if not self.game_over and len(self.enemies) < self.enemies_to_spawn:
            if self.spawn_timer <= 0:
                self.enemies.append(self.spawn_enemy())
                self.spawn_timer = 30  # Задержка между спавнами
            else:
                self.spawn_timer -= 1
                
        # Проверка завершения волны
        if len(self.enemies) == 0 and not self.game_over:
            self.wave += 1
            self.enemies_to_spawn = min(5 + self.wave, 20)
            self.player.health = min(self.player.max_health, self.player.health + 20)  # Бонус здоровья
            
    def draw_health_bar(self):
        bar_width = 300
        bar_height = 25
        x = 20
        y = 20
        health_ratio = self.player.health / self.player.max_health
        
        pygame.draw.rect(self.screen, RED, (x, y, bar_width, bar_height))
        pygame.draw.rect(self.screen, GREEN, (x, y, bar_width * health_ratio, bar_height))
        pygame.draw.rect(self.screen, WHITE, (x, y, bar_width, bar_height), 2)
        
        # Текст здоровья
        health_text = self.font.render(f"HP: {self.player.health}/{self.player.max_health}", True, WHITE)
        self.screen.blit(health_text, (x, y - 25))
        
    def draw(self):
        self.screen.fill(BLACK)
        
        # Рисуем сетку (эффект движения)
        for i in range(0, SCREEN_WIDTH, 50):
            pygame.draw.line(self.screen, (20, 20, 20), (i, 0), (i, SCREEN_HEIGHT))
        for i in range(0, SCREEN_HEIGHT, 50):
            pygame.draw.line(self.screen, (20, 20, 20), (0, i), (SCREEN_WIDTH, i))
        
        self.player.draw(self.screen)
        for bullet in self.bullets:
            bullet.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw(self.screen)
            
        # Интерфейс
        self.draw_health_bar()
        
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH - 150, 20))
        
        wave_text = self.font.render(f"Wave: {self.wave}", True, WHITE)
        self.screen.blit(wave_text, (SCREEN_WIDTH - 150, 60))
        
        # Подсказки
        controls_text = self.font.render("WASD - Move | Mouse - Aim & Shoot", True, WHITE)
        self.screen.blit(controls_text, (10, SCREEN_HEIGHT - 30))
        
        if self.game_over:
            # Затемнение экрана
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            game_over_text = self.big_font.render("GAME OVER", True, RED)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
            self.screen.blit(game_over_text, text_rect)
            
            score_text = self.big_font.render(f"Score: {self.score}", True, WHITE)
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
            self.screen.blit(score_text, score_rect)
            
            restart_text = self.font.render("Press SPACE to restart or ESC to quit", True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 100))
            self.screen.blit(restart_text, restart_rect)
            
        pygame.display.flip()
        
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()