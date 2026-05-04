"""
Create a 'fake scanned' PDF by rendering text onto images, then bundling
into a PDF. This simulates what a real scanned document looks like to
our document processor.
"""
from PIL import Image, ImageDraw, ImageFont

# Create two pages of text rendered as images
pages_text = [
    [
        "ACME FINTECH",
        "BIAS TESTING METHODOLOGY",
        "Version 1.0 - February 2026",
        "",
        "1. PURPOSE",
        "This document defines the methodology for testing the Loan AI",
        "system for bias and disparate impact across protected attributes.",
        "",
        "2. SCOPE",
        "Testing covers the following protected attributes:",
        "- Gender (binary classification: Male, Female)",
        "- Age (categorized: 18-25, 26-45, 46-65, 66+)",
        "- Ethnicity (where data is collected with consent)",
    ],
    [
        "3. METRICS",
        "We use the following fairness metrics:",
        "- Disparate Impact Ratio (target >= 0.80)",
        "- Demographic Parity Difference (target <= 0.05)",
        "- Equalized Odds (target <= 0.05)",
        "",
        "4. CADENCE",
        "Testing is performed quarterly on production data.",
        "",
        "5. REMEDIATION",
        "When a metric falls below threshold, the AI Governance",
        "Committee reviews and decides on remediation action.",
        "",
        "Approved by: [signed]",
        "Date: 15-Feb-2026",
    ],
]

images = []
for page_text in pages_text:
    img = Image.new("RGB", (1240, 1754), color="white")
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("/Library/Fonts/Arial.ttf", 36)
    except IOError:
        font = ImageFont.load_default()
    
    y = 100
    for line in page_text:
        draw.text((100, y), line, fill="black", font=font)
        y += 60
    
    images.append(img)

# Save as multi-page PDF
images[0].save(
    "sample_scanned_methodology.pdf",
    save_all=True,
    append_images=images[1:],
    resolution=200.0,
)
print("Created sample_scanned_methodology.pdf (a fake-scanned 2-page PDF)")