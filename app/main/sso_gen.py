from looker_sdk import init40, models40

ini = '/usr/local/google/home/hugoselbie/code_sample/py/ini/Looker_23_3.ini'
sdk = init40(config_file=ini)


def generate_looker_url(dashboard_id: str, **kwargs) -> str:
    sso_body = models40.EmbedSsoParams(
        target_url=f"https://cortexqa.cloud.looker.com/dashboards/{dashboard_id}?Year=2022%2F07%2F01+to+2023%2F03%2F31&Currency=USD&Region=&Sales+Org=&Distribution+Channel=&Division=&Product=",
        session_length=15*60,
        force_logout_login=False,
        external_user_id="3",
        first_name="Adam",
        last_name="Dell",
        permissions=["access_data",
                             "see_lookml_dashboards",
                             "see_looks",
                             "see_user_dashboards",
                             "explore",
                             "create_table_calculations",
                             "create_custom_fields",
                             "can_create_forecast",
                             "save_content",
                             "create_public_looks",
                             "download_with_limit",
                             "download_without_limit",
                             "schedule_look_emails",
                             "schedule_external_look_emails",
                             "create_alerts",
                             "follow_alerts",
                             "send_to_s3",
                             "send_to_sftp",
                             "send_outgoing_webhook",
                             "send_to_integration",
                             "see_sql",
                             "see_lookml",
                             "develop",
                             "deploy",
                             "support_access_toggle",
                             "use_sql_runner",
                             "clear_cache_refresh",
                             "see_drill_overlay",
                             "manage_spaces",
                             "manage_homepage",
                             "manage_models",
                             "create_prefetches",
                             "login_special_email",
                             "embed_browse_spaces",
                             "embed_save_shared_space",
                             "see_alerts",
                             "see_queries",
                             "see_logs",
                             "see_users",
                             "sudo",
                             "see_schedules",
                             "see_pdts",
                             "see_datagroups",
                             "update_datagroups",
                             "see_system_activity",
                            "mobile_app_access"],
        models=["All"],
        group_ids=["5"],
        external_group_id="Sapphire_Test_Space",
        user_attributes={
                    "region": "New York", "country": "USA"})
    url=sdk.create_sso_embed_url(body = sso_body)
    return url

if __name__ == '__main__':
    x=generate_looker_url()
    print(x)
