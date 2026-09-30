import pygame
import random
from .audio_feedback import AudioFeedback
from .target import Target

# Game Engine

WHITE = (255, 255, 255)
RED = (220, 60, 60)

DIFFICULTIES = {
    "Easy": {"base_radius": 48, "min_radius": 18, "lifespan_frames": 120},
    "Medium": {"base_radius": 40, "min_radius": 12, "lifespan_frames": 90},
    "Hard": {"base_radius": 32, "min_radius": 8, "lifespan_frames": 60},
}

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.margin = 60
        self.hud_height = 60
        self.round_seconds = 30
        self.difficulty = "Medium"
        self.audio = AudioFeedback()
        self.target = self._spawn_target()

        self.time_left_frames = self.round_seconds * 60

        self.hits = 0
        self.misses = 0
        self.score = 0
        self.font = pygame.font.SysFont("Arial", 26)
        self.game_over_font = pygame.font.SysFont("Arial", 54, bold=True)
        self.game_over = False
        self.should_quit = False

    def _spawn_target(self):
        x = random.randint(self.margin, self.width - self.margin)
        y = random.randint(self.margin + self.hud_height, self.height - self.margin)
        return Target(x, y, **DIFFICULTIES[self.difficulty])

    def start_new_game(self, difficulty):
        if difficulty not in DIFFICULTIES:
            raise ValueError(f"Unknown difficulty: {difficulty}")

        self.difficulty = difficulty
        self.hits = 0
        self.misses = 0
        self.score = 0
        self.time_left_frames = self.round_seconds * 60
        self.target = self._spawn_target()
        self.game_over = False
        self.should_quit = False

    def handle_event(self, event):
        if self.game_over:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    self.start_new_game("Easy")
                elif event.key == pygame.K_m:
                    self.start_new_game("Medium")
                elif event.key == pygame.K_h:
                    self.start_new_game("Hard")
                elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                    self.should_quit = True
            return
        if event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_click(event.pos)

    def _handle_click(self, pos):
        x, y = pos
        if self.target.contains_point(x, y):
            self.hits += 1
            self.score += 1
            self.audio.play_hit_sound()
            self.target = self._spawn_target()
        else:
            self.misses += 1
            self.audio.play_miss_sound()

    def handle_input(self):
        # Reserved for continuously-held-key input; this game is
        # entirely mouse-driven, so there's nothing to poll here.
        pass

    def update(self):
        if self.game_over:
            return

        self.time_left_frames -= 1
        if self.time_left_frames <= 0:
            self.game_over = True
            self.audio.play_game_over_sound()
            return

        self.target.update()
        if self.target.expired():
            self.misses += 1  # letting a target time out counts as a miss too
            self.audio.play_miss_sound()
            self.target = self._spawn_target()

    def accuracy(self):
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return round(100 * self.hits / total, 1)

    def render(self, screen):
        if self.game_over:
            title = self.game_over_font.render("GAME OVER", True, WHITE)
            score_text = self.font.render(f"Final score: {self.score}", True, WHITE)
            accuracy_text = self.font.render(
                f"Accuracy: {self.accuracy()}%", True, WHITE
            )

            screen.blit(title, title.get_rect(center=(self.width // 2, self.height // 2 - 70)))
            screen.blit(
                score_text,
                score_text.get_rect(center=(self.width // 2, self.height // 2)),
            )
            screen.blit(
                accuracy_text,
                accuracy_text.get_rect(center=(self.width // 2, self.height // 2 + 45)),
            )
            replay_text = self.font.render(
                "E: Easy    M: Medium    H: Hard", True, WHITE
            )
            exit_text = self.font.render("Esc or Q: Exit", True, WHITE)
            screen.blit(
                replay_text,
                replay_text.get_rect(center=(self.width // 2, self.height // 2 + 105)),
            )
            screen.blit(
                exit_text,
                exit_text.get_rect(center=(self.width // 2, self.height // 2 + 145)),
            )
            return

        r = int(self.target.visual_radius())
        pygame.draw.circle(screen, RED, (self.target.x, self.target.y), r)
        pygame.draw.circle(screen, WHITE, (self.target.x, self.target.y), r, 2)

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        seconds_left = max(0, self.time_left_frames // 60)
        timer_text = self.font.render(f"Time: {seconds_left}s", True, WHITE)
        screen.blit(timer_text, (self.width - 140, 10))

        acc_text = self.font.render(f"Accuracy: {self.accuracy()}%", True, WHITE)
        screen.blit(acc_text, (self.width // 2 - 90, 10))

