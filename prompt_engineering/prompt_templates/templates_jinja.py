"""
Production prompt templates with Jinja2 — supports conditionals, loops, and inheritance.
Run: python templates_jinja.py
"""
from jinja2 import Template

from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# Template with conditionals and loops
ANALYSIS_TEMPLATE = Template("""You are a {{ role }} analyst.

Analyze the following {{ data_type }}:

{% for item in items %}
- {{ item.name }}: {{ item.value }}
{% endfor %}

{% if include_recommendations %}
Provide exactly 3 actionable recommendations with expected impact.
{% endif %}

{% if output_format == "json" %}
Output as JSON with keys: summary, findings (list), risk_level (low/medium/high)
{% else %}
Output as bullet points with headers.
{% endif %}
""")

# Render with different parameters
prompt = ANALYSIS_TEMPLATE.render(
    role="financial",
    data_type="quarterly metrics",
    items=[
        {"name": "Revenue", "value": "$2.3M (+15%)"},
        {"name": "Churn", "value": "4.2% (+0.8%)"},
        {"name": "NPS", "value": "72 (-3)"},
    ],
    include_recommendations=True,
    output_format="json",
)

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.3,
)
print(response.choices[0].message.content)