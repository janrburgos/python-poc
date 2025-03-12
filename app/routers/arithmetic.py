from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/")
def read_root():
    """
    Root endpoint that returns a welcome message.

    Returns:
        dict: A dictionary containing a welcome message.
    """
    return {"message": "Welcome to the Arithmetic API"}


@router.get("/add/{a}/{b}")
def add(a: float, b: float):
    """
    Adds two numbers.

    Args:
        a (float): The first number.
        b (float): The second number.

    Returns:
        dict: A dictionary containing the operation type and the result.
    """
    return {"operation": "addition", "result": a + b}


@router.get("/subtract/{a}/{b}")
def subtract(a: float, b: float):
    """
    Subtracts the second number from the first number.

    Args:
        a (float): The first number.
        b (float): The second number.

    Returns:
        dict: A dictionary containing the operation type and the result.
    """
    return {"operation": "subtraction", "result": a - b}


@router.get("/multiply/{a}/{b}")
def multiply(a: float, b: float):
    """
    Multiplies two numbers.

    Args:
        a (float): The first number.
        b (float): The second number.

    Returns:
        dict: A dictionary containing the operation type and the result.
    """
    return {"operation": "multiplication", "result": a * b}


@router.get("/divide/{a}/{b}")
def divide(a: float, b: float):
    """
    Divides the first number by the second number.

    Args:
        a (float): The numerator.
        b (float): The denominator.

    Raises:
        HTTPException: If the denominator is zero.

    Returns:
        dict: A dictionary containing the operation type and the result.
    """
    if b == 0:
        raise HTTPException(status_code=400, detail="Cannot divide by zero")
    return {"operation": "division", "result": a / b}
