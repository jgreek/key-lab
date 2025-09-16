from pathlib import Path


class DisplayManager:
    def __init__(self, config_manager, csv_logger):
        self.config_manager = config_manager
        self.csv_logger = csv_logger

    def get_action_comment(self, key_combo):
        comment = ""

        apps = self.config_manager.get_apps()
        if key_combo in apps:
            app_path = apps[key_combo]
            app_name = Path(app_path).stem
            comment = f"Open {app_name}"

        commands = self.config_manager.get_commands()
        if key_combo in commands:
            cmd_list = commands[key_combo]
            if cmd_list and len(cmd_list) > 0:
                first_cmd = cmd_list[0]
                if 'comment' in first_cmd:
                    comment = first_cmd['comment']
                elif 'command' in first_cmd:
                    comment = f"Run: {first_cmd['command']}"
                elif 'file_command' in first_cmd:
                    comment = f"File: {first_cmd['file_command']}"
                else:
                    comment = f"{len(cmd_list)} commands"

        return comment

    def print_cheatsheet(self):
        print("\n" + "=" * 50)
        print("MacKeyListener Cheatsheet".center(50))
        print("=" * 50)

        backspace_combo = self.config_manager.get_setting("backspace_custom_combo", True)
        combo_timeout = self.config_manager.get_setting("combo_timeout_seconds", 5.0)

        print("\nSettings:")
        print(f"  Backspace Custom Combo: {'Yes' if backspace_combo else 'No'}")
        print(f"  Combo Timeout: {combo_timeout} seconds")

        print("\nConfigured App Shortcuts:")
        for key, app in self.config_manager.get_apps().items():
            count = self.csv_logger.get_action_count(key)
            print(f"  {key:<10} : {Path(app).stem} ({count})")

        print("\nShortcuts:")
        for key, commands in self.config_manager.get_commands().items():
            count = self.csv_logger.get_action_count(key)
            if commands and len(commands) > 0:
                first_cmd = commands[0]
                if 'comment' in first_cmd:
                    print(f"  {key:<10} : {first_cmd['comment']} ({count})")
                elif 'command' in first_cmd:
                    print(f"  {key:<10} : {first_cmd['command']} ({count})")
                else:
                    print(f"  {key:<10} : {len(commands)} commands ({count})")

        print("=" * 50)

    def print_csv_stats(self):
        print("\n" + "=" * 60)
        print("Action Usage Statistics".center(60))
        print("=" * 60)

        actions = self.csv_logger.get_stats()

        if not actions:
            print("No usage data available yet.")
            return

        print(f"{'Code':<12} {'Count':<8} {'Last Used':<20} {'Comment'}")
        print("-" * 60)

        for action in actions[:10]:  # Show top 10
            if action['code']:
                print(f"{action['code']:<12} {action['count']:<8} {action['last_action']:<20} {action['comment'][:25]}")

        total_actions = sum(int(action['count']) for action in actions if action['code'])
        print(f"\nTotal actions logged: {total_actions}")
        print(f"Unique shortcuts used: {len([a for a in actions if a['code']])}")

    def print_least_used_commands(self):
        print("\n" + "=" * 60)
        print("Least Used Commands".center(60))
        print("=" * 60)

        # Get all configured commands and apps
        all_commands = set(self.config_manager.get_commands().keys())
        all_apps = set(self.config_manager.get_apps().keys())
        all_actions = all_commands.union(all_apps)

        # Get usage statistics
        actions = self.csv_logger.get_stats()
        action_dict = {a['code']: a for a in actions if a['code']}

        # Find commands with zero usage by comparing with logged actions
        logged_codes = {a['code'] for a in actions if a['code']}
        unused_actions = all_actions - logged_codes

        # Create entries for unused actions
        zero_count_entries = []
        for code in unused_actions:
            comment = self.get_action_comment(code)
            zero_count_entries.append({
                'code': code,
                'count': '0',
                'last_action': 'Never',
                'comment': comment
            })

        # Combine with existing stats and sort by count (ascending)
        all_entries = actions + zero_count_entries
        all_entries.sort(key=lambda x: self.csv_logger.safe_int(x.get('count')))

        # Display header
        print(f"{'Code':<12} {'Count':<8} {'Last Used':<20} {'Comment'}")
        print("-" * 60)

        # Show the 8 least used commands
        for action in all_entries[:8]:
            if action['code']:
                print(f"{action['code']:<12} {action['count']:<8} {action['last_action']:<20} {action['comment'][:25]}")

        print("=" * 60)

    def print_recent_commands(self):
        print("\n" + "=" * 60)
        print("10 Most Recent Commands".center(60))
        print("=" * 60)

        actions = self.csv_logger.get_recent_actions()

        if not actions:
            print("No usage data available yet.")
            return

        print(f"{'Code':<12} {'Count':<8} {'Last Used':<20} {'Comment'}")
        print("-" * 60)

        for action in actions[:10]:  # Show top 10 most recent
            if action['code']:
                print(f"{action['code']:<12} {action['count']:<8} {action['last_action']:<20} {action['comment'][:25]}")

        print("=" * 60)
