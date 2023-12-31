import csv
import io

from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from config.database import get_db
from models import CalculationResult

app = FastAPI()


class RPN(BaseModel):
    expr: str


def eval_rpn(string: str) -> float:
    stack = []

    operators = {
        "+": lambda x, y: x + y,
        "-": lambda x, y: x - y,
        "*": lambda x, y: x * y,
        "/": lambda x, y: x / y,
    }

    elements = string.split(" ")

    for element in elements:
        try:
            float_element = float(element)
            stack.append(float_element)
        except ValueError:
            if element in operators:
                operand2 = stack.pop()
                operand1 = stack.pop()
                try:
                    result = operators[element](operand1, operand2)
                    stack.append(result)
                except ZeroDivisionError:
                    raise ValueError("Error: Division by zero is not allowed.")
            else:
                raise ValueError("Invalid element in RPN expr: {}".format(element))

    if len(stack) == 1:
        result = stack[0]
        if result.is_integer():
            result = int(result)
        return result
    else:
        raise ValueError("Malformed RPN expr")


def csv_generator(results):
    csv_data = io.StringIO()
    csv_writer = csv.writer(csv_data)

    # Write CSV header
    csv_writer.writerow(["expression", "result", "created_at"])

    for result in results:
        csv_writer.writerow([result.expression, result.result, result.created_at])

        # Yield the current content of the StringIO
        yield csv_data.getvalue()

        # Reset the StringIO for the next iteration
        csv_data.truncate(0)
        csv_data.seek(0)


def save_calculation_result(db: Session, expr: str, result: float):
    try:
        db_result = CalculationResult(expression=expr, result=result)
        db.add(db_result)
        db.commit()
        db.refresh(db_result)
    except Exception as e:
        db.rollback()
        raise e


@app.get("/export_csv/")
async def export_csv(db: Session = Depends(get_db)):
    results = db.query(CalculationResult).all()

    return StreamingResponse(
        csv_generator(results),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="results.csv"'},
    )


@app.post("/eval_rpn/")
def handle_eval_rpn_request(rpn: RPN, db: Session = Depends(get_db)):
    try:
        result = eval_rpn(rpn.expr)
        save_calculation_result(db, rpn.expr, result)
        return {"result": result}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
