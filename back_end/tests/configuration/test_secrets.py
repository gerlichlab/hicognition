"""Tests that the app refuses to start without the secrets that sign tokens and links."""

import unittest
from unittest.mock import patch

from app import create_app
from app.config.app_config import DevelopmentConfig, ProductionConfig

OWN_SECRETS = {"SECRET_KEY": "0123456789abcdef", "SECRET_SALT": "fedcba9876543210"}


def secrets(config_class, **values):
    """Sets the secrets of a config class for the duration of a test."""
    return patch.multiple(config_class, **{**OWN_SECRETS, **values})


class TestSecrets(unittest.TestCase):
    def test_production_starts_with_own_secrets(self):
        with secrets(ProductionConfig):
            self.assertEqual(
                create_app("production").config["SECRET_KEY"], "0123456789abcdef"
            )

    def test_missing_secret_stops_production_and_development(self):
        for name in ("SECRET_KEY", "SECRET_SALT"):
            for config_name, config_class in [
                ("production", ProductionConfig),
                ("development", DevelopmentConfig),
            ]:
                for missing in (None, ""):
                    with self.subTest(name=name, config=config_name, value=missing):
                        with secrets(config_class, **{name: missing}):
                            with self.assertRaisesRegex(
                                RuntimeError, f"{name} is not set"
                            ):
                                create_app(config_name)

    def test_example_secrets_stop_production(self):
        for name, value in [("SECRET_KEY", "eieieiei"), ("SECRET_SALT", "blblblbl")]:
            with self.subTest(name=name):
                with secrets(ProductionConfig, **{name: value}):
                    with self.assertRaisesRegex(RuntimeError, "example .env"):
                        create_app("production")

    def test_example_secrets_are_fine_for_development(self):
        """docker_dev.yml runs with the example .env."""
        with secrets(DevelopmentConfig, SECRET_KEY="eieieiei", SECRET_SALT="blblblbl"):
            self.assertEqual(
                create_app("development").config["SECRET_SALT"], "blblblbl"
            )

    def test_testing_needs_no_secrets_from_the_environment(self):
        self.assertEqual(
            create_app("testing").config["SECRET_KEY"], "hicognition-tests"
        )


if __name__ == "__main__":
    unittest.main()
