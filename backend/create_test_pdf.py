from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Create a test PDF with Dr. Ambedkar's quotes
c = canvas.Canvas("data/raw/test_ambedkar.pdf", pagesize=letter)

# Add some content
c.setFont("Helvetica", 16)
c.drawString(50, 750, "Dr. B.R. Ambedkar - Test Document")

c.setFont("Helvetica", 12)
y_position = 700
quotes = [
    "Education is the most powerful weapon which you can use to change the world.",
    "I measure the progress of a community by the degree of progress which women have achieved.",
    "Caste is not a physical object like a wall of bricks or a line of barbed wire which prevents the Hindus from co-mingling.",
    "Freedom of mind is the real freedom.",
    "Be educated, be organized, and be agitated."
]

for quote in quotes:
    c.drawString(50, y_position, quote)
    y_position -= 30

c.save()
print("✅ Test PDF created at data/raw/test_ambedkar.pdf")
