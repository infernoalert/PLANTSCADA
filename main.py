# ==========================================
# main.py — Router (traffic cop)
# ==========================================
# Entry point: builds the View and delegates UI events to controllers.

from __future__ import annotations

from controllers import (
    clean_controller,
    equip_create_controller,
    navigation_controller,
    search_variable_controller,
    tab_viewr_controller,
    update_location_controller,
)
from services.paths import ensure_runtime_dirs
from ui import AppView


def main() -> None:
    ensure_runtime_dirs()
    view = AppView()
    view.set_on_clean(lambda: clean_controller.handle(view.get_search_string(), view))
    view.set_on_readme_click(lambda: navigation_controller.handle_readme(view))
    view.set_on_tabviewr(lambda: tab_viewr_controller.handle(view.get_tabviewr_search_string(), view))
    view.set_on_tabviewr_readme_click(lambda: navigation_controller.handle_tabviewr_readme(view))
    view.set_on_update_location(
        lambda: update_location_controller.handle(view.get_update_location_search_string(), view)
    )
    view.set_on_update_location_readme_click(
        lambda: navigation_controller.handle_update_location_readme(view)
    )
    view.set_on_equip_create(
        lambda: equip_create_controller.handle(view.get_equip_create_search_string(), view)
    )
    view.set_on_equip_create_readme_click(
        lambda: navigation_controller.handle_equip_create_readme(view)
    )
    view.set_on_search_variable(
        lambda: search_variable_controller.handle(view.get_search_variable_group_string(), view)
    )
    view.set_on_search_variable_readme_click(
        lambda: navigation_controller.handle_search_variable_readme(view)
    )
    view.run()


if __name__ == "__main__":
    main()
