import sass
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

class SCSSCompileHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('.scss'):
            print(f"Detected change in {event.src_path}, recompiling SCSS...")
            scss_input = 'static/scss/custom-bootstrap.scss'
            css_output = 'static/css/custom-bootstrap.css'
            compiled_css = sass.compile(filename=scss_input)
            with open(css_output, 'w') as f:
                f.write(compiled_css)
            print(f"SCSS compiled to {css_output}")

if __name__ == "__main__":
    path = "static/scss"
    event_handler = SCSSCompileHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()

    print(f"Watching {path} for changes... Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
