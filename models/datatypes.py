from pydantic import BaseModel

class Chunk(BaseModel):
    id: int
    lines: str  # e.g., "1-15"
    content: str

class EvalMetric(BaseModel):
    rating: int
    justification: str

class CodeEval(BaseModel):
    readability: EvalMetric
    modularity: EvalMetric
    simplicity: EvalMetric
    documentation: EvalMetric
    style_consistency: EvalMetric

class Issue(BaseModel):
    """Represents an issue found in the code."""
    category_name: str
    short_description: str
    long_description: str
    severity_impact_level: str
    