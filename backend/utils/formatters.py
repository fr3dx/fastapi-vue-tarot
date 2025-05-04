import os

# Helper function to generate a human-readable card name from a given filename.
def format_card_name(filename: str) -> str:
    """
    Converts a filename into a formatted card name.
    
    Example:
        Input:  'major-arcana_the-fool.png'
        Output: 'The Fool'
    """
    # Extract the base name without the file extension.
    name_part: str = os.path.splitext(filename)[0]
    
    # Remove the category prefix by splitting on the first underscore.
    name: str = name_part.split("_", 1)[-1]
    
    # Replace hyphens and underscores with spaces, apply title casing, and prepend "The ".
    return "The " + name.replace("-", " ").replace("_", " ").title()
