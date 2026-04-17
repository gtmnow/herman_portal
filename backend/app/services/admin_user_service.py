class AdminUserService:
    def planned_actions(self) -> list[str]:
        return [
            "create_user",
            "update_user",
            "deactivate_user",
            "delete_user",
            "reset_user_password",
            "remap_user_id_hash",
        ]
