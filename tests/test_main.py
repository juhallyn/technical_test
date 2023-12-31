import unittest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app
from sqlalchemy.orm import Session
from models import CalculationResult
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config.database import DatabaseConfig
from sqlalchemy_utils import create_database, database_exists

from alembic.config import Config
from alembic import command

Base = declarative_base()


def apply_migrations(engine_url):
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", engine_url)
    command.upgrade(alembic_cfg, "head")


def override_get_db():
    test_database_url = DatabaseConfig.DATABASE_URL + "_test"
    engine = create_engine(test_database_url)
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = testing_session_local()

    try:
        if not database_exists(engine.url):
            create_database(engine.url)
            apply_migrations(test_database_url)

        session.bind = engine
        return session

    except Exception as e:
        session.close()
        raise e


class TestApp(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.db = override_get_db()
        self.db.query(CalculationResult).delete()
        self.db.commit()

    def tearDown(self):
        self.db.query(CalculationResult).delete()
        self.db.commit()

    @patch("config.database.SessionLocal", side_effect=override_get_db)
    def test_eval_rpn(self, mock_get_db):
        expr = "2 2.2 + 3 * 1 / 3 / 45 -"

        response = self.client.post(
            "/eval_rpn/",
            json={"expr": expr},
        )

        self.assertEqual(response.status_code, 200)
        result = response.json()

        self.assertIn("result", result)
        self.assertEqual(result["result"], -40.8)

        data_db = (
            self.db.query(CalculationResult)
            .filter(CalculationResult.expression == expr)
            .all()
        )
        self.assertEqual(len(data_db), 1)

        self.assertEqual(data_db[0].expression, expr)
        self.assertEqual(data_db[0].result, -40.8)

    # @patch("main.get_db", side_effect=override_get_db)
    # def test_eval_rpn_division_by_zero(self, mock_get_db):
    #     expr = "4 0 /"

    #     response = self.client.post("/eval_rpn/", json={"expr": expr})

    #     self.assertEqual(response.status_code, 400)
    #     error_result = response.json()
    #     self.assertIn("detail", error_result)
    #     self.assertEqual(
    #         error_result["detail"], "Error: Division by zero is not allowed."
    #     )

    @patch("config.database.SessionLocal", side_effect=override_get_db)
    def test_eval_rpn_division_by_zero(self, mock_get_db):
        expr = "4 0 /"

        response = self.client.post("/eval_rpn/", json={"expr": expr})

        self.assertEqual(response.status_code, 400)
        error_result = response.json()
        self.assertIn("detail", error_result)
        self.assertEqual(
            error_result["detail"], "Error: Division by zero is not allowed."
        )

        data_db = self.db.query(CalculationResult).all()
        self.assertEqual(len(data_db), 0)

    @patch("config.database.SessionLocal", side_effect=override_get_db)
    def test_eval_rpn_addition(self, mock_get_db):
        expr = "2 2 +"

        response = self.client.post("/eval_rpn/", json={"expr": expr})

        self.assertEqual(response.status_code, 200)
        result = response.json()

        self.assertIn("result", result)
        self.assertEqual(result["result"], 4)

        data_db = (
            self.db.query(CalculationResult)
            .filter(CalculationResult.expression == expr)
            .all()
        )
        self.assertEqual(len(data_db), 1)
        self.assertEqual(data_db[0].expression, expr)
        self.assertEqual(data_db[0].result, 4)

    @patch("config.database.SessionLocal", side_effect=override_get_db)
    def test_eval_rpn_subtraction(self, mock_get_db):
        expr = "5 3 -"

        response = self.client.post("/eval_rpn/", json={"expr": expr})

        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertIn("result", result)
        self.assertEqual(result["result"], 2)

        data_db = (
            self.db.query(CalculationResult)
            .filter(CalculationResult.expression == expr)
            .all()
        )
        self.assertEqual(len(data_db), 1)
        self.assertEqual(data_db[0].expression, expr)
        self.assertEqual(data_db[0].result, 2)

    @patch("config.database.SessionLocal", side_effect=override_get_db)
    @patch("sqlalchemy.sql.functions.now")
    def test_export_csv_with_data(
        self, mock_sqlalchemy_now, mock_get_db
    ):
        mock_sqlalchemy_now.return_value = datetime(2023, 1, 1, 12, 0, 0)

        data_to_add = [
            {"expr": "2 2 +", "result": 4},
            {"expr": "5 3 -", "result": 2},
            {"expr": "6 2 /", "result": 3},
        ]

        for data in data_to_add:
            response = self.client.post("/eval_rpn/", json=data)
            self.assertEqual(response.status_code, 200)

        response_export_csv = self.client.get("/export_csv/")
        self.assertEqual(response_export_csv.status_code, 200)

        # Additional assertions specific to this test, if needed

        # Verify that CalculationResult records for the added data exist in the database
        expected_data_db = [
            {"expr": "2 2 +", "result": 4},
            {"expr": "5 3 -", "result": 2},
            {"expr": "6 2 /", "result": 3},
        ]

        data_db = (
            self.db.query(CalculationResult)
            .filter(
                CalculationResult.expression.in_([data["expr"] for data in expected_data_db]),
                CalculationResult.result.in_([data["result"] for data in expected_data_db]),
            )
            .all()
        )

        self.assertEqual(len(data_db), len(expected_data_db))