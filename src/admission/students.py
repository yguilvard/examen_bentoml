# Python Imports
from dataclasses import dataclass, fields
from pydantic import BaseModel

from admission.errors import ScoreTooHighError, ScoreTooLowError

# Constants
MAX_SCORES = {
    'gre_score':    340.0,
    'toefl_score':  120.0,
    'rating':       5.0,
    'sop':          5.0,
    'lor':          5.0,
    'cgpa':         1.0,
    'research_xp':  1.0,
    'chances':      1.0
}

@dataclass(frozen=True, slots=True)
class Student(BaseModel):
    # GRE Score: Score obtenu au test GRE (noté sur 340)
    gre_score: float 
    #TOEFL Score: Score obtenu au test TOEFL (noté sur 120)
    toefl_score: float 
    # University Rating: Note de l'université (notée sur 5)
    rating: float 
    # SOP: Statement of Purpose (noté sur 5)
    sop: float 
    #LOR: Letter of Recommendation (noté sur 5)
    lor: float 
    # CGPA: Cumulative Grade Point Average (noté sur 10)
    cgpa: float 
    # Research: Expérience de recherche (0 ou 1)
    research_xp: float
    # Chance of Admit: Chance d'admission (notée sur 1)
    chances: float 

    def __post_init__(self)-> None:
        # Checks the values for each fields is in a valid range
        for field in fields(self):
            if field.name in MAX_SCORES:
                value = getattr(self, field.name)
                if value < 0:
                    raise ScoreTooLowError(field.name, value)

                max_value = MAX_SCORES.get(field.name)
                if max_value is None:
                    raise ValueError(f"Missing max value for field {field.name}")
                if value > max_value:
                    raise ScoreTooHighError(field.name, value, max_value)

