"""
Instructor + Pydantic = type-safe, validated AI outputs.
The gold standard for production structured output.
Run: python structured_pydantic.py
"""
import instructor
from pydantic import BaseModel, Field
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# Patch the OpenAI client with Instructor
client = instructor.from_openai(OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
))

# Define your output schema with Pydantic
class MovieReview(BaseModel):
    """Structured movie review extraction."""
    title: str = Field(description="Movie title")
    year: int = Field(description="Release year")
    rating: float = Field(ge=0, le=10, description="Rating out of 10")
    genres: list[str] = Field(description="List of genres")
    pros: list[str] = Field(min_length=1, max_length=5, description="Positive aspects")
    cons: list[str] = Field(min_length=1, max_length=3, description="Negative aspects")
    recommended: bool = Field(description="Whether to recommend this movie")
    one_line_summary: str = Field(max_length=100, description="One sentence summary")

# Guaranteed to return a valid MovieReview object — or raise an error
review = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    response_model=MovieReview,  # This is the magic
    messages=[{"role": "user", "content": "Review the movie Inception (2010) by Christopher Nolan"}],
)

# Type-safe access — IDE autocomplete works!
print(f"🎬 {review.title} ({review.year})")
print(f"⭐ {review.rating}/10")
print(f"📂 {', '.join(review.genres)}")
print(f"👍 Pros: {review.pros}")
print(f"👎 Cons: {review.cons}")
print(f"{'✅ Recommended' if review.recommended else '❌ Not recommended'}")
print(f"📝 {review.one_line_summary}")