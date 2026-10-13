"""Entry point for the built .exe.

When you package the app, this is what runs. It simply opens the desktop
window. Running from source you can still use organizer.py or gui.py directly.
"""

from gui import main

if __name__ == "__main__":
    main()
