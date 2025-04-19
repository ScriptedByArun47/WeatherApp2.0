from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line
from kivy.animation import Animation
from kivy.metrics import dp
from kivy.clock import Clock
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivy.uix.image import Image
import math


class SunTrackerBar(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(100)
        self.padding = [dp(10), dp(10)]
        self.spacing = dp(10)

        # Outer frosted card
        self.card = MDCard(
            size_hint=(1, None),
            height=dp(80),
            padding=dp(10),
            radius=[dp(12)],
            md_bg_color=(1, 1, 1, 0.2),
            elevation=2
        )
        # Inner layout
        self.inner_layout = BoxLayout(
            orientation='horizontal',
            spacing=dp(10)
        )

        self.sunrise_label = MDLabel(
            text="6:00 AM",
            size_hint=(None, 1),
            width=dp(60),
            halign="left",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 0.9)
        )

        self.sunset_label = MDLabel(
            text="6:00 PM",
            size_hint=(None, 1),
            width=dp(60),
            halign="right",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 0.9)
        )

        # Sun track
        self.track_canvas = Widget()
        with self.track_canvas.canvas:
            Color(1, 1, 1, 0.2)
            self.track_line = Line(points=[], width=dp(3), cap='round')

        # Sun + Glow
        self.sun_widget = Widget(size_hint=(None, None), size=(dp(24), dp(24)))

        # Glow (halo)
        with self.sun_widget.canvas:
            self.glow_color = Color(1, 0.94, 0.75, 0.35)
            self.sun_glow = Ellipse(pos=self.sun_widget.pos, size=(dp(50), dp(50)))

        # Add Sun Icon
        self.sun_icon = Image(source="assets/icons/sun.png", size=self.sun_widget.size, size_hint=(None, None))
        self.sun_widget.add_widget(self.sun_icon)

        # Add Moon Icon (initially hidden)
        self.moon_icon = Image(source="assets/icons/moon.png", size=self.sun_widget.size, size_hint=(None, None))
        self.sun_widget.add_widget(self.moon_icon)
        self.moon_icon.opacity = 0  # Hide the moon icon initially

        # Assemble UI
        self.inner_layout.add_widget(self.sunrise_label)
        self.inner_layout.add_widget(self.track_canvas)
        self.inner_layout.add_widget(self.sun_widget)
        self.inner_layout.add_widget(self.sunset_label)
        self.card.add_widget(self.inner_layout)
        self.add_widget(self.card)

        self.bind(size=self.update_graphics, pos=self.update_graphics)
        Clock.schedule_once(lambda dt: self.animate_glow_loop(), 0.5)

    def update_graphics(self, *args):
        start_x = self.sunrise_label.width + dp(10)
        end_x = self.width - self.sunset_label.width - dp(10)
        y = self.y + self.card.height / 2
        self.track_line.points = [start_x, y, end_x, y]
        self.update_sun_visual(start_x, y)

    def update_sun_visual(self, x, y):
        self.sun_widget.pos = (x - self.sun_widget.width / 2, y - self.sun_widget.height / 2)
        self.sun_icon.pos = self.sun_widget.pos
        self.moon_icon.pos = self.sun_widget.pos  # Move the moon icon along with the sun

        self.sun_glow.pos = (
            self.sun_widget.center_x - self.sun_glow.size[0] / 2,
            self.sun_widget.center_y - self.sun_glow.size[1] / 2
        )

    def update_sun_position(self, sunrise_ts, sunset_ts, current_ts):
        try:
            start_x = self.sunrise_label.width + dp(10)
            end_x = self.width - self.sunset_label.width - dp(10)
            y = self.y + self.card.height / 2

        # Determine if it's daytime or nighttime
            if sunrise_ts <= current_ts <= sunset_ts:
            # Daytime logic — track the sun
                total = sunset_ts - sunrise_ts
                elapsed = current_ts - sunrise_ts
                percentage = max(0, min(1, elapsed / total))
                is_day = True
            else:
            # Nighttime logic — track the moon
                if current_ts < sunrise_ts:
                # Before today's sunrise → night started yesterday
                    night_start = sunset_ts - 86400  # yesterday's sunset
                    night_end = sunrise_ts
                else:
                # After today's sunset → night ends tomorrow
                    night_start = sunset_ts
                    night_end = sunrise_ts + 86400  # tomorrow's sunrise

                total = night_end - night_start
                elapsed = current_ts - night_start
                percentage = max(0, min(1, elapsed / total))
                is_day = False

        # Calculate new x position for icon (sun or moon)
            new_x = start_x + (end_x - start_x) * percentage

        # Animate movement
            anim = Animation(
            x=new_x - self.sun_widget.width / 2,
            y=y - self.sun_widget.height / 2,
            duration=1,
            t="out_quad"
        )
            anim.bind(on_progress=self.animate_sun_growth)
            anim.start(self.sun_widget)

        # Toggle visibility
            self.sun_icon.opacity = 1 if is_day else 0
            self.moon_icon.opacity = 0 if is_day else 1

        except Exception as e:
            print("Sun/Moon animation error:", e)


    def animate_sun_growth(self, anim, widget, progress):
        scale = 0.95 + 0.15 * math.sin(progress * math.pi)
        new_size = dp(24) * scale
        widget.size = (new_size, new_size)
        self.sun_icon.size = widget.size  # Update sun icon size
        self.sun_icon.pos = widget.pos
        self.moon_icon.size = widget.size  # Update moon icon size
        self.moon_icon.pos = widget.pos
        self.sun_glow.size = (widget.size[0] * 2.0, widget.size[1] * 2.0)
        self.sun_glow.pos = (
            widget.center_x - self.sun_glow.size[0] / 2,
            widget.center_y - self.sun_glow.size[1] / 2
        )

    def animate_glow_loop(self):
        # Smooth pulsating glow
        anim = Animation(a=0.6, duration=1.5, t='in_out_sine') + Animation(a=0.3, duration=1.5, t='in_out_sine')
        anim.bind(on_progress=self.update_glow_alpha)
        anim.repeat = True
        anim.start(self.glow_color)

    def update_glow_alpha(self, anim, color_instruction, progress):
        pass  # Alpha already animated by Kivy; nothing extra needed here
