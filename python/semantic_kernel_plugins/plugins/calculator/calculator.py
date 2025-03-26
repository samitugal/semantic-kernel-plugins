import math
from typing import Optional

from semantic_kernel.functions import kernel_function

class CalculatorPlugin:
    def __init__(self):
        self.name = "calculator"
        self.description = "A plugin for performing calculations"

    @kernel_function(
        description="Add two numbers",
        name="add",
    )
    def add(self, a: float, b: float) -> float:
        """
        Add two numbers together.

        Args:
            a: The first number to add.
            b: The second number to add.    

        Returns:
            The sum of the two numbers.
        """
        return a + b
    
    @kernel_function(
        description="Subtract two numbers",
        name="subtract",
    )
    def subtract(self, a: float, b: float) -> float:
        """
        Subtract one number from another.

        Args:
            a: The number to subtract from.
            b: The number to subtract.

        Returns:
            The result of the subtraction.
        """
        return a - b
    
    @kernel_function(
        description="Multiply two numbers",
        name="multiply",
    )
    def multiply(self, a: float, b: float) -> float:
        """
        Multiply two numbers together.

        Args:
            a: The first number to multiply.
            b: The second number to multiply.

        Returns:
            The product of the two numbers.
        """
        return a * b
    
    @kernel_function(
        description="Divide two numbers",
        name="divide",
    )
    def divide(self, a: float, b: float) -> float:
        """
        Divide one number by another.   

        Args:
            a: The number to divide.
            b: The number to divide by.

        Returns:
            The result of the division.
        """

        if b == 0:
            return "Error: Division by zero"
        return a / b
    
    @kernel_function(
        description="Calculate the square of a number",
        name="square",
    )
    def square(self, a: float) -> float:
        """
        Calculate the square of a number.

        Args:
            a: The number to square.

        Returns:    
            The square of the number.
        """
        return a * a
    
    @kernel_function(
        description="Calculate the square root of a number",
        name="square_root",
    )
    def square_root(self, a: float) -> float:
        """
        Calculate the square root of a number.

        Args:
            a: The number to calculate the square root of.

        Returns:
            The square root of the number.
        """
        if a < 0:
            return "Error: Cannot calculate square root of negative number"
        return math.sqrt(a)
    
    @kernel_function(
        description="Calculate the cube of a number",
        name="cube",
    )
    def cube(self, a: float) -> float:
        """
        Calculate the cube of a number.

        Args:
            a: The number to calculate the cube of.

        Returns:
            The cube of the number.
        """
        return a * a * a
    
    @kernel_function(
        description="Calculate the power of a number",
        name="power",
    )
    def power(self, base: float, exponent: float) -> float:
        """
        Calculate the power of a number.

        Args:
            base: The base number.
            exponent: The exponent.

        Returns:
            The result of the power calculation.
        """
        return base ** exponent
    
    @kernel_function(
        description="Calculate the logarithm of a number",
        name="log",
    )
    def log(self, a: float, base: Optional[float] = None) -> float:
        """
        Calculate the logarithm of a number.

        Args:
            a: The number to calculate the logarithm of.
            base: The base of the logarithm.

        Returns:
            The result of the logarithm calculation.
        """
        if base is None:
            return math.log(a)
        return math.log(a, base)
    
    @kernel_function(
        description="Calculate the sine of a number",
        name="sin",
    )
    def sin(self, a: float) -> float:
        """
        Calculate the sine of a number.

        Args:
            a: The number to calculate the sine of.

        Returns:
            The sine of the number.
        """
        return math.sin(a)
    
    @kernel_function(
        description="Calculate the cosine of a number",
        name="cos",
    )
    def cos(self, a: float) -> float:
        """
        Calculate the cosine of a number.

        Args:
            a: The number to calculate the cosine of.

        Returns:
            The cosine of the number.
        """
        return math.cos(a)
    
    @kernel_function(
        description="Calculate the tangent of a number",
        name="tan",
    )
    def tan(self, a: float) -> float:
        """
        Calculate the tangent of a number.

        Args:
            a: The number to calculate the tangent of.

        Returns:
            The tangent of the number.
        """
        return math.tan(a)
    
    @kernel_function(
        description="Calculate the factorial of a number",
        name="factorial",
    )
    def factorial(self, a: int) -> int:
        """
        Calculate the factorial of a number.

        Args:
            a: The number to calculate the factorial of.

        Returns:
            The factorial of the number.
        """
        if a < 0:
            return "Error: Cannot calculate factorial of negative number"
        return math.factorial(a)
    
    @kernel_function(
        description="Calculate the absolute value of a number",
        name="abs",
    )
    def absolute_value(self, a: float) -> float:
        """
        Calculate the absolute value of a number.

        Args:
            a: The number to calculate the absolute value of.

        Returns:
            The absolute value of the number.
        """
        return abs(a)
    

