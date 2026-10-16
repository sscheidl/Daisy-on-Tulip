"""Native Tulip app. Start with tulip.run('daisy_toy_piano')."""

def run(screen):
    from .app import PianoApp
    # Keep the app, timers and bound callbacks alive for this UIScreen.
    screen.daisy_app = PianoApp(screen)
