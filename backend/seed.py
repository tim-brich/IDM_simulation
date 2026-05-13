from sqlalchemy.orm import Session
from models import Level, Task

def init_db(db: Session):
    # Check if levels already exist
    level = db.query(Level).first()
    if level:
        return # Database already seeded

    # Add Demo Levels
    level1 = Level(order_index=1, title="Основы знакомства", description="Научитесь здороваться и представляться.")
    level2 = Level(order_index=2, title="В магазине", description="Как купить продукты и спросить цену.")
    db.add_all([level1, level2])
    db.commit()

    # Add Tasks for Level 1
    tasks_level1 = [
        Task(
            level_id=level1.id,
            type="choice",
            question="Как сказать 'Привет'?",
            correct_answer="Сәләм",
            metadata_json={"options": ["Сәләм", "Хуш", "Рәхмәт", "Эйе"]}
        ),
        Task(
            level_id=level1.id,
            type="translate",
            question="Меня зовут Тимур.",
            correct_answer="Минең исемем Тимур."
        ),
        Task(
            level_id=level1.id,
            type="scenario",
            question="Ты встречаешь старшего родственника на улице. Поздоровайся вежливо."
        )
    ]

    # Add Tasks for Level 2
    tasks_level2 = [
        Task(
            level_id=level2.id,
            type="choice",
            question="Как спросить 'Сколько это стоит?'",
            correct_answer="Был күпме тора?",
            metadata_json={"options": ["Был күпме тора?", "Киссерегеҙ", "Мин белмәйем", "Күпме"]}
        ),
        Task(
            level_id=level2.id,
            type="translate",
            question="Я хочу купить хлеб.",
            correct_answer="Мин икмәк һатып алырға теләйем."
        )
    ]

    db.add_all(tasks_level1)
    db.add_all(tasks_level2)
    db.commit()
    print("Database seeded successfully with demo data.")
