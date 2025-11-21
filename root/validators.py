def validate_production_settings(debug, secret_key, allowed_hosts, token_salt):
    if not debug:
        required_vars = [
            ("DJANGO_SECRET_KEY", secret_key),
            ("DJANGO_ALLOWED_HOSTS", allowed_hosts),
            ("TOKEN_SALT", token_salt),
        ]

        missing = []
        for var_name, var_value in required_vars:
            if not var_value:
                missing.append(var_name)

        if missing:
            raise ValueError(
                f"Missing required environment variables in production: {', '.join(missing)}"
            )
