from app.database import SessionLocal, engine
from app import models

def seed():
    # Ensure tables are created
    models.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # Check if we already have employees
    if db.query(models.Employee).count() > 0:
        print("Database already seeded.")
        return

    employees = [
        models.Employee(
            name="Alice Johnson",
            resume_text="Senior Frontend Developer with 8 years of experience in React, Next.js, and TypeScript. Expert in building accessible and performant web applications.",
            is_on_bench=True
        ),
        models.Employee(
            name="Bob Smith",
            resume_text="Backend Engineer specializing in Python and FastAPI. Experience with PostgreSQL, Redis, and building scalable microservices. Familiar with Docker and Kubernetes.",
            is_on_bench=True
        ),
        models.Employee(
            name="Charlie Davis",
            resume_text="Fullstack Developer proficient in Node.js, Express, and Vue.js. Strong understanding of MongoDB and SQL. Passionate about clean code and unit testing.",
            is_on_bench=True
        ),
        models.Employee(
            name="Diana Prince",
            resume_text="UI/UX Designer with a background in graphic design. Expert in Figma, Adobe XD, and building design systems. Focuses on user-centric design principles.",
            is_on_bench=True
        )
    ]
    
    db.add_all(employees)
    db.commit()
    print("Successfully seeded the bench with 4 employees.")

if __name__ == "__main__":
    seed()
