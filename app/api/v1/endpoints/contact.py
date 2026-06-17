from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.contact import Contact
from app.schemas.contact import ContactCreate

router = APIRouter()


@router.post("/")
def contact_us(
    data: ContactCreate,
    db: Session = Depends(get_db)
):

    contact = Contact(
        full_name=data.full_name,
        email=data.email,
        subject=data.subject,
        message=data.message
    )

    db.add(contact)

    db.commit()

    db.refresh(contact)

    return {
        "message": "Your query has been submitted successfully.",
        "contact_id": contact.id
    }


@router.get("/")
def get_all_contacts(
    db: Session = Depends(get_db)
):

    contacts = db.query(Contact).all()

    return contacts


@router.get("/{contact_id}")
def get_contact(
    contact_id: int,
    db: Session = Depends(get_db)
):

    contact = db.query(Contact).filter(
        Contact.id == contact_id
    ).first()

    if not contact:
        raise HTTPException(
            status_code=404,
            detail="Contact not found"
        )

    return contact


@router.delete("/{contact_id}")
def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db)
):

    contact = db.query(Contact).filter(
        Contact.id == contact_id
    ).first()

    if not contact:
        raise HTTPException(
            status_code=404,
            detail="Contact not found"
        )

    db.delete(contact)

    db.commit()

    return {
        "message": "Contact deleted successfully"
    }