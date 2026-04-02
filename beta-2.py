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
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.action = action
        self.font = pygame.font.Font(None, 48)
        
    def draw(self, screen):
        pygame.draw.rect(screen, self.current_color, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 3)
        
        text_surface = self.font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                self.current_color = self.hover_color
            else:
                self.current_color = self.color
                
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.action:
                return self.action()
        return None

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
    def __init__(self, x, y, wave):
        self.x = x
        self.y = y
        self.width = 28
        self.height = 28
        self.speed = 2 + wave * 0.3
        self.health = 40 + wave * 10
        self.max_health = self.health
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
        pygame.display.set_caption("AimLock - 2D Шутер")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        
        # Состояния игры
        self.state = "MENU"  # MENU, PLAYING, SETTINGS
        self.settings_message_alpha = 0
        self.settings_message_timer = 0
        
        self.reset_game()
        self.create_menu()
        
    def create_menu(self):
        button_width = 250
        button_height = 60
        start_x = SCREEN_WIDTH // 2 - button_width // 2
        
        self.menu_buttons = [
            Button(start_x, 300, button_width, button_height, "ИГРАТЬ", DARK_GRAY, GRAY, self.start_game),
            Button(start_x, 400, button_width, button_height, "НАСТРОЙКИ", DARK_GRAY, GRAY, self.open_settings),
            Button(start_x, 500, button_width, button_height, "ВЫХОД", DARK_GRAY, GRAY, self.quit_game)
        ]
        
    def start_game(self):
        self.state = "PLAYING"
        self.reset_game()
        return None
        
    def open_settings(self):
        self.state = "SETTINGS"
        self.settings_message_alpha = 255
        self.settings_message_timer = 60
        return None
        
    def quit_game(self):
        pygame.quit()
        sys.exit()
        
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
        side = random.randint(0, 3)
        if side == 0:
            x = -30
            y = random.randint(0, SCREEN_HEIGHT)
        elif side == 1:
            x = SCREEN_WIDTH + 30
            y = random.randint(0, SCREEN_HEIGHT)
        elif side == 2:
            x = random.randint(0, SCREEN_WIDTH)
            y = -30
        else:
            x = random.randint(0, SCREEN_WIDTH)
            y = SCREEN_HEIGHT + 30
            
        return Enemy(x, y, self.wave)
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == "PLAYING":
                        self.state = "MENU"
                        return True
                    elif self.state == "SETTINGS":
                        self.state = "MENU"
                        return True
                    else:
                        return False
                        
                if self.state == "PLAYING" and self.game_over and event.key == pygame.K_SPACE:
                    self.reset_game()
                    return True
                    
            # Обработка кнопок только в меню
            if self.state == "MENU":
                for button in self.menu_buttons:
                    result = button.handle_event(event)
                    if result is not None:
                        return result
                        
            # Стрельба в игре
            if self.state == "PLAYING" and not self.game_over and event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    player_center = self.player.get_center()
                    self.bullets.append(Bullet(player_center[0], player_center[1], mouse_x, mouse_y))
                    
        return True
        
    def update(self):
        if self.state == "PLAYING" and not self.game_over:
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
            if len(self.enemies) < self.enemies_to_spawn:
                if self.spawn_timer <= 0:
                    self.enemies.append(self.spawn_enemy())
                    self.spawn_timer = 30
                else:
                    self.spawn_timer -= 1
                    
            # Проверка завершения волны
            if len(self.enemies) == 0:
                self.wave += 1
                self.enemies_to_spawn = min(5 + self.wave, 20)
                self.player.health = min(self.player.max_health, self.player.health + 20)
                
        # Обновление сообщения "СКОРО" в настройках
        if self.state == "SETTINGS":
            if self.settings_message_timer > 0:
                self.settings_message_timer -= 1
                self.settings_message_alpha = min(255, self.settings_message_alpha + 5)
            else:
                self.settings_message_alpha -= 5
                if self.settings_message_alpha <= 0:
                    self.state = "MENU"
                    
    def draw_health_bar(self):
        bar_width = 300
        bar_height = 25
        x = 20
        y = 20
        health_ratio = self.player.health / self.player.max_health
        
        pygame.draw.rect(self.screen, RED, (x, y, bar_width, bar_height))
        pygame.draw.rect(self.screen, GREEN, (x, y, bar_width * health_ratio, bar_height))
        pygame.draw.rect(self.screen, WHITE, (x, y, bar_width, bar_height), 2)
        
        health_text = self.font.render(f"Здоровье: {self.player.health}/{self.player.max_health}", True, WHITE)
        self.screen.blit(health_text, (x, y - 25))
        
    def draw_menu(self):
        # Фоновый эффект
        for i in range(0, SCREEN_WIDTH, 50):
            pygame.draw.line(self.screen, DARK_GRAY, (i, 0), (i, SCREEN_HEIGHT))
        for i in range(0, SCREEN_HEIGHT, 50):
            pygame.draw.line(self.screen, DARK_GRAY, (0, i), (SCREEN_WIDTH, i))
            
        # Заголовок
        title_text = self.big_font.render("AIMLOCK", True, YELLOW)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 150))
        self.screen.blit(title_text, title_rect)
        
        subtitle_text = self.font.render("2D ШУТЕР", True, WHITE)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH//2, 210))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Кнопки
        for button in self.menu_buttons:
            button.draw(self.screen)
            
        # Управление
        controls_text = self.font.render("WASD - Движение | Мышь - Прицел | ЛКМ - Стрельба | ESC - Меню", True, GRAY)
        controls_rect = controls_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 50))
        self.screen.blit(controls_text, controls_rect)
        
    def draw_settings(self):
        # Затемнение экрана
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Текст "СКОРО" с анимацией
        if self.settings_message_alpha > 0:
            soon_text = self.big_font.render("СКОРО", True, YELLOW)
            soon_text.set_alpha(self.settings_message_alpha)
            text_rect = soon_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(soon_text, text_rect)
            
            info_text = self.font.render("Функция в разработке...", True, WHITE)
            info_text.set_alpha(self.settings_message_alpha)
            info_rect = info_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60))
            self.screen.blit(info_text, info_rect)
            
    def draw_game(self):
        self.screen.fill(BLACK)
        
        # Сетка
        for i in range(0, SCREEN_WIDTH, 50):
            pygame.draw.line(self.screen, (20, 20, 20), (i, 0), (i, SCREEN_HEIGHT))
        for i in range(0, SCREEN_HEIGHT, 50):
            pygame.draw.line(self.screen, (20, 20, 20), (0, i), (SCREEN_WIDTH, i))
        
        self.player.draw(self.screen)
        for bullet in self.bullets:
            bullet.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw(self.screen)
            
        self.draw_health_bar()
        
        score_text = self.font.render(f"Очки: {self.score}", True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH - 150, 20))
        
        wave_text = self.font.render(f"Волна: {self.wave}", True, WHITE)
        self.screen.blit(wave_text, (SCREEN_WIDTH - 150, 60))
        
        # ESC для выхода в меню
        menu_hint = self.font.render("ESC - Главное меню", True, GRAY)
        self.screen.blit(menu_hint, (SCREEN_WIDTH - 150, SCREEN_HEIGHT - 30))
        
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            game_over_text = self.big_font.render("ИГРА ОКОНЧЕНА", True, RED)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
            self.screen.blit(game_over_text, text_rect)
            
            score_text = self.big_font.render(f"Счёт: {self.score}", True, WHITE)
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
            self.screen.blit(score_text, score_rect)
            
            restart_text = self.font.render("Нажмите ПРОБЕЛ чтобы начать заново или ESC для выхода в меню", True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 100))
            self.screen.blit(restart_text, restart_rect)
            
    def draw(self):
        if self.state == "MENU":
            self.draw_menu()
        elif self.state == "SETTINGS":
            self.draw_settings()
        elif self.state == "PLAYING":
            self.draw_game()
            
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