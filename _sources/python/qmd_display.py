"""
These are some useful display tools for returning results in quarto
output.
"""

def print_row(label, value, unit=""):
    """
    Prints a perfectly aligned row with thousands separators and decimal alignment.
    
    :param label: The text label (e.g., "Frequency:")
    :param value: The numeric value to format
    :param unit: The unit string (e.g., "Hertz")
    """
    # 1. Format number with commas and 2 decimal places
    formatted_value = f"{value:,.2f}"
    
    # 2. Print with left-aligned label (<25), right-aligned number (>15), and unit
    print(f"{label:<25} {formatted_value:>15} {unit}")
