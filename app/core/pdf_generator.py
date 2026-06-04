from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import getSampleStyleSheet


def generate_resume_pdf(
    filename,
    name,
    email,
    phone,
    linkedin,
    content
):
    doc = SimpleDocTemplate(filename)

    styles = getSampleStyleSheet()

    story = []

    story.append(
        Paragraph(
            f"<b>{name}</b>",
            styles["Title"]
        )
    )

    story.append(
        Paragraph(
            f"{email} | {phone}",
            styles["Normal"]
        )
    )

    story.append(
        Paragraph(
            linkedin,
            styles["Normal"]
        )
    )

    story.append(
        Spacer(1, 20)
    )

    story.append(
        Paragraph(
            content.replace("\n", "<br/>"),
            styles["BodyText"]
        )
    )

    doc.build(story)

    return filename