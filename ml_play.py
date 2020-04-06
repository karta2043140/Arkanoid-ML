import games.arkanoid.communication as com
from games.arkanoid.communication import(
    SceneInfo, GameStatus, PlatformAction
)

def ml_loop():
    #init
    ball_served = False
    ball_direction = True # Left-0 Right-1
    ball_fast = False
    ball_speed = 7
    ball_x = 90
    ball_y = 400
    platform_x = 75
    platform_y = 400

    #start
    com.ml_ready()
    while True:
        scene_info = com.get_scene_info()
        if scene_info.status != GameStatus.GAME_ALIVE:
            #reset
            ball_served = False
            ball_direction = True
            ball_fast = False
            ball_speed = 7
            #restart
            com.ml_ready()
            continue

        #predict
        if not ball_served:
            ball_x = scene_info.ball[0] + 2.5
            ball_y = scene_info.ball[1] + 5
            platform_x = scene_info.platform[0] + 20
            platform_y = scene_info.platform[1]
        ball_preX = ball_x
        ball_preY = ball_y
        platform_preX = platform_x
        ball_x = scene_info.ball[0] + 2.5
        ball_y = scene_info.ball[1] + 5
        platform_x = scene_info.platform[0] + 20
        predict_x = ball_x

        if ball_x - ball_preX < 0:
            ball_direction = False
        else:
            ball_direction = True
        if ball_x - ball_preX >= -7 and ball_x - ball_preX <= 7:
            ball_fast = False
            ball_speed = 7
        else:
            ball_fast = True
            ball_speed = 10

        #instruction
        if not ball_served:
            ball_served = True
            com.send_instruction(scene_info.frame, PlatformAction.SERVE_TO_RIGHT)
        else:
            if ball_y + 7 >= platform_y and predict_x <= platform_x + 15 and predict_x >= platform_x - 15:
                if ball_direction:
                    com.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
                else:
                    com.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
            elif ball_y + 7 * 2 >= platform_y and predict_x <= platform_x + 15 and predict_x >= platform_x - 15:
                if platform_x == 20:
                    com.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
                elif platform_x == 180:
                    com.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
            else:
                remain_frame = ball_y
                predict_x = ball_x - 2.5
                direction = ball_direction
                while remain_frame < platform_y:
                    if direction:
                        predict_x = predict_x + ball_speed
                        if predict_x > 200 - 5:
                            predict_x = 200 - 5
                            direction = False
                    else:
                        predict_x = predict_x - ball_speed
                        if predict_x < 0:
                            predict_x = 0
                            direction = True
                    remain_frame = remain_frame + 7
                predict_x = predict_x + 2.5
                if platform_x - predict_x > 0:
                    com.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
                else:
                    com.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)