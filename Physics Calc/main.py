import pygame
import sys
import math

pygame.init()
WIDTH, HEIGHT = 600, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Robotics Calculator")

WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)
BLUE = (100, 100, 255)

font = pygame.font.SysFont(None, 28)
big_font = pygame.font.SysFont(None, 36)

def draw_text(text, x, y, font, color=WHITE):
    label = font.render(text, True, color)
    screen.blit(label, (x, y))

class InputBox:
    def __init__(self, x, y, w, h, text=''):
       self.rect = pygame.Rect(x, y, w, h)
       self.color = GRAY
       self.text = text
       self.txt_surface = font.render(text, True, DARK_GRAY)
       self.active = False
    
    def handle_event(self, event):
        self.active = self.rect.collidepoint(event.pos)
        self.color = BLUE if self.active else GRAY
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    pass
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
            self.txt_surface = font.render(self.text, True, DARK_GRAY)
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, 2)
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))

    def get_value(self):
        try:
            return float(self.text)
        except:
            return 0.0

# Physics Formulas
def calculate_torque(force, radius):
    return force * radius

def calculate_force(mass, acceleration):
    return mass * acceleration

def calculate_angular_velocity(rpm):
    return (2 * math.pi * rpm) / 60

# Mode options
mode = "menu"
result = ""
inputs = []

#UI loop
running = True
while running:
    screen.fill((30, 30, 30))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    if mode == "menu":
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if 50 < mx < 550:
                if 100 < my < 140:
                    mode = "torque"
                    inputs = [InputBox(250, 100, 100, 30), InputBox(250, 150, 100, 30)]
                    result = ""

                elif 160 < my < 200:
                    mode = "force"
                    inputs = [InputBox(250, 100, 100, 30), InputBox(250, 150, 100, 30)]
                    result = ""
            
                elif 220 < my < 260:
                    mode = "angular_velocity"
                    inputs = [InputBox(250, 100, 100, 30)]
                    result = ""
            
            elif mode in ["torque", "force", "angular_velocity"]:
                for box in inputs:
                    box.handle_event(event)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    if mode == "torque":
                        f = inputs[0].get_value()
                        r = inputs[1].get_value()
                        result = f"Torque = {calculate_torque(f, r):.2f} Nm"
                    elif mode == "force":
                        m = inputs[0].get_value()
                        a = inputs[1].get_value()
                        result = f"Force = {calculate_force(m, a):.2f} N"
                    elif mode == "angular_velocity":
                        rpm = inputs[0].get_value()
                        w = calculate_angular_velocity(rpm)
                        result = f"w = {w:.2f} rad/s"
        # Drawing UI
        if mode == "menu":
            draw_text("Robotics Physics Calculator", 150, 30, big_font)
            pygame.draw.rect(screen, GRAY, (50, 100, 500, 40))
            draw_text("1. Torque (t = F x r)", 60, 110, font, DARK_GRAY)

            pygame.draw.rect(screen, GRAY, (50, 160, 500, 40))
            draw_text("2. Force (F = m x a)", 60, 170, font, DARK_GRAY)

            pygame.draw.rect(screen, GRAY, (50, 220, 500, 40))
            draw_text("3. Angular Velocity (w = 2pi x RPM / 60)", 60, 230, font, DARK_GRAY)

    elif mode in ["torque", "force", "angular_velocity"]:
        draw_text("Press Enter to Calculate | Press Esc to return", 100, 30, font, DARK_GRAY)
        for box in inputs:
            box.draw(screen)
            
            #Labels
            if mode == "torque":
                draw_text("Force (N):", 150, 105, font)
                draw_text("Radius (m):", 150, 155, font)
            elif mode == "force":
                draw_text("Mass (kg):", 150, 105, font)
                draw_text("Acceleration (m/s^2)", 150, 155, font)
            elif mode == "angular_velocity":
                draw_text("RPM:", 150, 105, font)
            
            draw_text(result, 150, 250, big_font)

            #ESC to go back
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                mode = "menu"
    pygame.display.flip()
    pygame.time.Clock().tick(30)

pygame.quit()
