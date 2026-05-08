import flet as ft
import subprocess
import threading
from pathlib import Path

HOME = Path.home()

DEMOS = {
    "AIzunda":      HOME / "AIzunda",
    "LLaVA":        HOME / "LLaVA",
    "RealtimeDepth": HOME / "RealtimeDepth",
}

# ---- demo control ----

def stop_demo(name: str):
    directory = DEMOS[name]
    script = directory / "stop_all.sh"
    if script.exists():
        subprocess.run(["bash", "stop_all.sh"], cwd=str(directory), timeout=60)

def start_demo(name: str):
    for demo_name in DEMOS:
        if demo_name != name:
            stop_demo(demo_name)
    directory = DEMOS[name]
    script = directory / "start_all.sh"
    if script.exists():
        subprocess.Popen(["bash", "start_all.sh"], cwd=str(directory))

def stop_all_demos():
    for name in DEMOS:
        stop_demo(name)

# ---- UI ----

def main(page: ft.Page):
    page.title = "Demo Launcher"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#1a1a2e"
    page.window.width = 460
    page.window.height = 580
    page.padding = 30

    status = ft.Text(
        "待機中",
        size=13,
        color="#888888",
        text_align=ft.TextAlign.CENTER,
    )
    progress = ft.ProgressBar(visible=False, width=380, color="#4fc3f7", bgcolor="#333355")

    def set_status(msg: str, color="#888888", busy=False):
        status.value = msg
        status.color = color
        progress.visible = busy
        page.update()

    def make_start_handler(name: str):
        def handler(e):
            set_status(f"{name} を起動中 (他デモを停止してから起動)...", "#ffd54f", busy=True)
            def task():
                try:
                    start_demo(name)
                    set_status(f"{name} を起動しました", "#81c784")
                except Exception as ex:
                    set_status(f"エラー: {ex}", "#ef5350")
            threading.Thread(target=task, daemon=True).start()
        return handler

    def handle_stop_all(e):
        set_status("全デモを停止中...", "#ffb74d", busy=True)
        def task():
            try:
                stop_all_demos()
                set_status("全デモを停止しました", "#ffb74d")
            except Exception as ex:
                set_status(f"エラー: {ex}", "#ef5350")
        threading.Thread(target=task, daemon=True).start()

    def handle_shutdown(e):
        def confirm(ev):
            page.pop_dialog()
            subprocess.Popen(["sudo", "shutdown", "-h", "now"])

        def cancel(ev):
            page.pop_dialog()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("シャットダウン確認", color="#ef5350"),
            content=ft.Text("PCをシャットダウンしますか？\nこの操作は元に戻せません。"),
            actions=[
                ft.TextButton(
                    "シャットダウン",
                    on_click=confirm,
                    style=ft.ButtonStyle(color="#ef5350"),
                ),
                ft.TextButton("キャンセル", on_click=cancel),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dlg)

    def btn(label: str, handler, bg: str, icon_name: str):
        return ft.FilledButton(
            content=ft.Row(
                [
                    ft.Icon(icon_name, size=20, color="white"),
                    ft.Text(label, size=15, weight=ft.FontWeight.W_500, color="white"),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
                tight=True,
            ),
            on_click=handler,
            width=380,
            height=54,
            style=ft.ButtonStyle(
                bgcolor={
                    ft.ControlState.DEFAULT: bg,
                    ft.ControlState.HOVERED:  bg,
                    ft.ControlState.PRESSED:  bg,
                },
                shape=ft.RoundedRectangleBorder(radius=10),
                elevation={"default": 3, "hovered": 6},
            ),
        )

    page.add(
        ft.Column(
            [
                ft.Text("Demo Launcher", size=26, weight=ft.FontWeight.BOLD, color="white"),
                ft.Text("デモ起動管理ツール", size=12, color="#666688"),
                ft.Divider(color="#333355", height=24),

                btn("AIzunda を起動",       make_start_handler("AIzunda"),      "#2e7d32", ft.Icons.PLAY_ARROW_ROUNDED),
                btn("LLaVA を起動",         make_start_handler("LLaVA"),        "#1565c0", ft.Icons.PLAY_ARROW_ROUNDED),
                btn("RealtimeDepth を起動", make_start_handler("RealtimeDepth"), "#6a1b9a", ft.Icons.PLAY_ARROW_ROUNDED),

                ft.Divider(color="#333355", height=24),

                btn("全て停止",    handle_stop_all, "#e65100", ft.Icons.STOP_ROUNDED),
                btn("PC 電源オフ", handle_shutdown,  "#b71c1c", ft.Icons.POWER_SETTINGS_NEW_ROUNDED),

                ft.Divider(color="#333355", height=14),
                progress,
                status,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
        )
    )

ft.run(main)
