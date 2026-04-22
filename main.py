# ==========================================
# main.py — Router (traffic cop)
# ==========================================
# Entry point: builds the View and delegates UI events to controllers.

from __future__ import annotations

from controllers import clean_controller, navigation_controller, tab_viewr_controller
from ui import AppView


def main() -> None:
    view = AppView()
    view.set_on_clean(lambda: clean_controller.handle(view.get_search_string(), view))
    view.set_on_readme_click(lambda: navigation_controller.handle_readme(view))
    view.set_on_tabviewr(lambda: tab_viewr_controller.handle(view.get_tabviewr_search_string(), view))
    view.set_on_tabviewr_readme_click(lambda: navigation_controller.handle_tabviewr_readme(view))
    view.run()


if __name__ == "__main__":
    main()
