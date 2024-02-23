# 1 - インポート
import random
import sys
import math

import pygame
from pygame import mixer
from pygame.locals import *

# 2 - ゲームの設定

# 2.1 - ゲームの初期化
pygame.init()
mixer.init()
WIDTH = 400
HEIGHT = 800
(p_x, p_y) = (200, 400)
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# 2.2 player に関する設定
p_v = 3

# 2.3 player の laser に関する設定
p_lasers = []
p_laser_v = 10

# 2.4 enemy に関する設定
e_v = 1
enemies = []
enemies_max_len = 10
enemy_frequency = 20
enemy_timer = enemy_frequency

# 2.5 enemy の laser に関する設定
e_laser_v = 2
e_lasers = []
e_laser_frequency = 80
e_laser_timer = e_laser_frequency

# 2.6 castle に関する設定
castle_size = (64, 64)
positions = [(0, 700), (100, 700), (200, 700), (300, 700)]
castle_hp_init = 5
castle_hp_list = [castle_hp_init] * 4
castles_rect = [pygame.Rect(positions[i], castle_size) for i in range(4)]

# 2.7 文字に関する設定
font_top = pygame.font.Font(None, 40)
font_hp = pygame.font.Font(None, 55)
font_clock = pygame.font.Font(None, 100)
font_counter = pygame.font.Font(None, 45)
font_score = pygame.font.Font(None, 50)

# 2.8 タイマーに関する設定
GAME_TIME = 30000
start_time = 0
timer_height = 70

# 2.9 画面遷移に関する設定
# 0 -> 「TOP」, 1 -> 「PLAY」, 2 -> 「SCORE」
scene = 0

# 2.10 - 画像の読み込み
player = pygame.image.load("resources/images/myplayer2.jpeg")
player = pygame.transform.scale(player, (64, 64))
castle = pygame.image.load("resources/images/castle.png")
p_laser_surface = pygame.image.load("resources/images/p_laser.jpeg")
p_laser_surface = pygame.transform.scale(p_laser_surface, (40, 40))
enemy_surface = pygame.image.load("resources/images/e_player.jpeg")
enemy_surface = pygame.transform.scale(enemy_surface, (64,64))
e_laser_surface = pygame.image.load("resources/images/e_laser.jpeg")
e_laser_surface = pygame.transform.scale(e_laser_surface, (40, 40))

# 2.11 - 画像のサイズ
p_width = player.get_width()
p_height = player.get_height()

p_laser_width = p_laser_surface.get_width()
p_laser_height = p_laser_surface.get_height()

e_width = enemy_surface.get_width()
e_height = enemy_surface.get_height()

e_laser_width = e_laser_surface.get_width()
e_laser_height = e_laser_surface.get_height()

# 2.12 - 各種カウンター
p_laser_counter = 0
p_hit_enemy_counter = 0
fight_time_counter = 0

# 2.13 - 音声の読み込み
p_laser_sound = mixer.Sound("./resources/se/mylaser2.mp3")
p_laser_hit_sound = mixer.Sound("./resources/se/mylaser.mp3")
e_laser_sound = mixer.Sound("./resources/se/e_laser.mp3")
e_laser_castle_hit_sound = mixer.Sound("./resources/se/e_laser_castle_hit.mp3")


# 2.14 - bgm の再生
mixer.music.load("./resources/bgm/bgm01.mp3")
mixer.music.play(-1)

# 3 - スコアを計算する関数
def calc_score(result, hit_rate, result_hp, fight_time_counter):

    score = 0
    score += result * 100
    score += hit_rate * 100
    score += result_hp * 10
    score += fight_time_counter * 5

    return math.floor(score)


# 4 - ループの実行
while True:

    # 5 - 画面を一度消す
    screen.fill(0)

    # 6 - 「TOP」画面
    if scene == 0:
        text = font_top.render("Start Game with ENTER", False, (255, 255, 255))
        screen.blit(text, (20, HEIGHT / 2))

    # 7 - 「PLAY」画面
    if scene == 1:

        # 7.1 - 画面に player を描画
        screen.blit(player, (p_x, p_y))

        # 7.2 player の レーザーを描画
        for p_laser_i, p_laser in enumerate(p_lasers):
            p_laser[1] -= p_laser_v
            if p_laser[1] < -p_laser_height:
                p_lasers.pop(p_laser_i)

            screen.blit(p_laser_surface, p_laser)

        # 7.3 画面に enemy を描画
        enemy_timer -= 1
        if enemy_timer <= 0 and len(enemies) < enemies_max_len:
            enemies.append(
                [random.randint(0, WIDTH - e_width), -e_height + timer_height]
            )
            enemy_timer = enemy_frequency

        for enemy_i, enemy in enumerate(enemies):
            enemy[1] += e_v
            if enemy[1] > HEIGHT:
                enemies.pop(enemy_i)
            screen.blit(enemy_surface, enemy)

            # 7.3.1 - enemy のレーザーの発射
            e_laser_timer -= 1
            if e_laser_timer <= 0:
                e_lasers.append(
                    [
                        enemy[0] + e_width / 2 - e_laser_width / 2,
                        enemy[1] + e_laser_height,
                    ]
                )
                e_laser_timer = e_laser_frequency
                e_laser_sound.play()

            # 7.3.2 - player の攻撃によって敵を削除
            enemy_rect = pygame.Rect(enemy_surface.get_rect())
            enemy_rect.left, enemy_rect.top = enemy

            for p_laser_i, p_laser in enumerate(p_lasers):
                p_laser_rect = pygame.Rect(p_laser_surface.get_rect())
                p_laser_rect.left, p_laser_rect.top = p_laser
                if enemy_rect.colliderect(p_laser_rect):
                    enemies.pop(enemy_i)
                    p_lasers.pop(p_laser_i)
                    p_hit_enemy_counter += 1
                    p_laser_hit_sound.play()

        # 7.4 - enemy のレーザー描画
        for e_laser_i, e_laser in enumerate(e_lasers):
            e_laser[1] += e_laser_v
            if e_laser[1] > HEIGHT:
                e_lasers.pop(e_laser_i)
            screen.blit(e_laser_surface, e_laser)

            # 7.4.1 - enemy のレーザーと城の当たり判定
            e_laser_rect = pygame.Rect(e_laser_surface.get_rect())
            e_laser_rect.left, e_laser_rect.top = e_laser

            for castle_rect_i, castle_rect in enumerate(castles_rect):
                if castle_rect.colliderect(e_laser_rect):
                    if castle_hp_list[castle_rect_i] > 0:
                        e_lasers.pop(e_laser_i)
                        castle_hp_list[castle_rect_i] -= 1
                        e_laser_castle_hit_sound.play()

        # 7.5 castle を描画
        for castle_i, castle_hp in enumerate(castle_hp_list):
            if castle_hp >= 1:
                screen.blit(castle, positions[castle_i])

            # 7.5.1 HP を表示
            hp = castle_hp_list[castle_i]
            hp_text = "*" * hp
            text = font_hp.render(hp_text, False, (255, 255, 255))
            hp_position = [
                positions[castle_i][0],
                positions[castle_i][1] + castle_size[1],
            ]
            screen.blit(text, hp_position)

        # 7.6 ゲームタイマーを表示
        pygame.draw.rect(screen, (40, 40, 40), Rect(0, 0, WIDTH, timer_height))
        now_time = pygame.time.get_ticks() - start_time
        fight_time_counter = now_time / 1000
        left_time = (GAME_TIME - now_time) // 1000 if (GAME_TIME - now_time) >= 0 else 0
        time_text = font_clock.render(str(left_time), False, (0, 0, 255))
        screen.blit(time_text, (0, 0))

        lasers_text = font_counter.render(
            "lasers : " + str(p_laser_counter), False, (255, 255, 255)
        )
        screen.blit(lasers_text, (100, 20))
        hit_text = font_counter.render(
            "hit : " + str(p_hit_enemy_counter), False, (255, 255, 255)
        )
        screen.blit(hit_text, (270, 20))

        # 7.7 - スコア画面への遷移
        if sum(castle_hp_list) <= 0 or left_time <= 0:
            scene = 2

    # 8 - 「SCORE」画面
    if scene == 2:

        # 8.1 - 勝敗を表示
        result = 1 if sum(castle_hp_list) > 0 else 0
        result_char = "Win" if result else "Lose"
        result_text = font_score.render(result_char, False, (0, 0, 255))
        screen.blit(result_text, (20, 20))

        # 8.2 - 命中率を表示
        hit_rate = p_hit_enemy_counter / p_laser_counter
        hit_percent = "{:.0%}".format(p_hit_enemy_counter / p_laser_counter)
        hit_rate_text = font_score.render(
            "Hit Rate : " + hit_percent, False, (255, 255, 255)
        )
        screen.blit(hit_rate_text, (20, 100))

        # 8.3 - 城の残りの HP を表示
        result_hp = sum(castle_hp_list)
        result_hp_text = font_score.render(
            "Remaining HP : " + str(result_hp), False, (255, 255, 255)
        )
        screen.blit(result_hp_text, (20, 200))

        # 8.4 - プレイ時間を表示
        result_time_text = font_score.render(
            "Fight Time : " + str(fight_time_counter), False, (255, 255, 255)
        )
        screen.blit(result_time_text, (20, 300))

        # 8.5 - スコアを表示
        score = calc_score(result, hit_rate, result_hp, fight_time_counter)
        score_text = font_score.render("Score : " + str(score), False, (255, 217, 0))
        screen.blit(score_text, (20, 400))

        # 8.6 - ガイド文章を表示
        guid_text = font_score.render("TOP [t] , REPLAY [r]", False, (255, 255, 255))
        screen.blit(guid_text, (20, 600))

    # 9 - 画面を更新する
    pygame.display.flip()
    pygame.time.wait(20)

    # 10 - イベントを確認
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit(0)

        if event.type == pygame.KEYDOWN:
            if event.key == K_RETURN and scene == 0:
                start_time = pygame.time.get_ticks()
                scene = 1

            # 10.1 - ゲーム中にスペースキーを押したらレーザーを発射する
            if event.key == K_SPACE and scene == 1:
                p_lasers.append(
                    [p_x + p_width / 2 - p_laser_width / 2, p_y - p_laser_height]
                )
                p_laser_counter += 1
                p_laser_sound.play()
            # 10.2 - Score 画面で t を押したらスタート画面へ戻る
            if event.key == K_t and scene == 2:
                castle_hp_list = [castle_hp_init] * 4
                p_laser_counter = 0
                p_hit_enemy_counter = 0
                p_lasers = []
                enemies = []
                e_lasers = []
                scene = 0

            # 10.3 - Score 画面で r を押したらゲームを始める
            if event.key == K_r and scene == 2:
                start_time = pygame.time.get_ticks()
                castle_hp_list = [castle_hp_init] * 4
                p_laser_counter = 0
                p_hit_enemy_counter = 0
                p_lasers = []
                enemies = []
                e_lasers = []
                scene = 1

    # 11 - player の動作
    pressed_key = pygame.key.get_pressed()
    if pressed_key[K_LEFT]:
        if p_x > 0:
            p_x -= p_v
    if pressed_key[K_RIGHT]:
        if p_x < WIDTH - p_width:
            p_x += p_v 
    if pressed_key[K_UP]:
        if p_y > 0 + timer_height:
            p_y -= p_v
    if pressed_key[K_DOWN]:
        if p_y < HEIGHT - p_height * 2.5:
            p_y += p_v