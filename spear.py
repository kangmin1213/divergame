from PIL import ImageDraw

class Spear:
    def __init__(self, disp, cat_width):
        self.disp = disp
        self.spear_active = False  # 작살 발사 여부
        self.spear_direction = None  # 작살 방향
        self.spear_progress = 0  # 작살 진행 상태
        self.spear_speed = 0.15  # 작살 이동 속도 (속도를 빠르게 조정)
        self.spear_length = int(self.disp.width / 3)  # 작살 최대 길이
        self.cat_width = cat_width  # 고양이 이미지의 너비 (작살 시작점 계산에 필요)

    def fire(self, flipped):
        """작살 발사 시작"""
        if not self.spear_active:
            self.spear_active = True
            # 방향을 반대로 설정 (좌우 반전)
            self.spear_direction = "right" if flipped else "left"
            self.spear_progress = 0

    def update(self):
        """작살의 상태를 업데이트합니다."""
        if self.spear_active:
            if self.spear_progress < 1:  # 작살이 나가는 중
                self.spear_progress += self.spear_speed
            elif self.spear_progress >= 1 and self.spear_progress < 2:  # 작살이 되돌아오는 중
                self.spear_progress += self.spear_speed
            else:  # 작살 동작 종료
                self.spear_active = False
                self.spear_progress = 0

    def draw(self, screen, cat_x, cat_y, flipped):
        """작살을 화면에 그립니다."""
        if self.spear_active:
            progress = self.spear_progress if self.spear_progress <= 1 else 2 - self.spear_progress
            spear_x = cat_x + self.cat_width // 2
            spear_y = cat_y + self.cat_width // 2

            if self.spear_direction == "left":
                start = (spear_x, spear_y)
                end = (spear_x - int(self.spear_length * progress), spear_y)
            elif self.spear_direction == "right":
                start = (spear_x, spear_y)
                end = (spear_x + int(self.spear_length * progress), spear_y)

            draw = ImageDraw.Draw(screen)
            draw.line([start, end], fill="black", width=3)
