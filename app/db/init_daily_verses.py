from sqlalchemy.orm import Session
from app.models.daily_verse import DailyVerse


def init_daily_verses(db: Session) -> None:
    """초기 말씀 데이터 생성"""

    initial_verses = [
        {
            "verse": '"여호와는 나의 목자시니 내게 부족함이 없으리로다"',
            "reference": "시편 23:1",
        },
        {
            "verse": '"내가 산을 향하여 눈을 들리리라 나의 도움이 어디서 올까"',
            "reference": "시편 121:1",
        },
        {
            "verse": '"수고하고 무거운 짐 진 자들아 다 내게로 오라 내가 너희를 쉬게 하리라"',
            "reference": "마태복음 11:28",
        },
        {
            "verse": '"하늘이 하나님의 영광을 선포하고 궁창이 그의 손으로 하신 일을 나타내는도다"',
            "reference": "시편 19:1",
        },
        {
            "verse": '"그러나 여호와를 의뢰하는 자는 새 힘을 얻으리니 독수리의 날개치며 올라감 같을 것이요"',
            "reference": "이사야 40:31",
        },
        {
            "verse": '"너는 마음을 다하여 여호와를 의뢰하고 네 명철을 의지하지 말라"',
            "reference": "잠언 3:5",
        },
        {
            "verse": '"너희는 먼저 그의 나라와 그의 의를 구하라 그리하면 이 모든 것을 너희에게 더하시리라"',
            "reference": "마태복음 6:33",
        },
        {
            "verse": '"내가 강하고 담대하라 명령한 것이 아니냐 두려워하지 말며 놀라지 말라 네가 어디로 가든지 네 하나님 여호와가 너와 함께 하느니라"',
            "reference": "여호수아 1:9",
        },
        {
            "verse": '"하나님이 세상을 이처럼 사랑하사 독생자를 주셨으니 이는 그를 믿는 자마다 멸망하지 않고 영생을 얻게 하려 하심이라"',
            "reference": "요한복음 3:16",
        },
        {
            "verse": '"여호와의 말씀이니라 내가 너희를 향한 생각을 아나니 평안이요 재앙이 아니니라 너희에게 미래와 희망을 주는 것이니라"',
            "reference": "예레미야 29:11",
        },
        {
            "verse": '"너희 염려를 다 주께 맡기라 이는 그가 너희를 돌보심이라"',
            "reference": "베드로전서 5:7",
        },
        {
            "verse": '"내게 능력 주시는 자 안에서 내가 모든 것을 할 수 있느니라"',
            "reference": "빌립보서 4:13",
        },
        {
            "verse": '"주 예수를 믿으라 그리하면 너와 네 집이 구원을 받으리라"',
            "reference": "사도행전 16:31",
        },
        {
            "verse": '"만군의 여호와가 말하노라 이는 힘으로 되지 아니하며 능력으로 되지 아니하고 오직 나의 영으로 되느니라"',
            "reference": "스가랴 4:6",
        },
        {
            "verse": '"감사함으로 그의 문에 들어가며 찬송함으로 그의 궁정에 들어가서 그에게 감사하며 그의 이름을 송축할지어다"',
            "reference": "시편 100:4",
        },
        {"verse": '"모든 일을 원망과 시비가 없이 하라"', "reference": "빌립보서 2:14"},
        {
            "verse": '"항상 기뻐하라 쉬지 말고 기도하라 범사에 감사하라 이것이 그리스도 예수 안에서 너희를 향하신 하나님의 뜻이니라"',
            "reference": "데살로니가전서 5:16-18",
        },
        {
            "verse": '"사랑하는 자들아 우리가 서로 사랑하자 사랑은 하나님께 속한 것이니 사랑하는 자마다 하나님으로부터 나서 하나님을 안다"',
            "reference": "요한일서 4:7",
        },
        {
            "verse": '"그런즉 믿음, 소망, 사랑 이 세 가지는 항상 있을 것인데 그 중의 제일은 사랑이라"',
            "reference": "고린도전서 13:13",
        },
        {
            "verse": '"평안을 너희에게 끼치노니 곧 나의 평안을 너희에게 주노라 내가 너희에게 주는 것은 세상이 주는 것과 같지 아니하니라"',
            "reference": "요한복음 14:27",
        },
    ]

    # 기존 데이터가 있는지 확인
    existing_count = db.query(DailyVerse).count()
    if existing_count > 0:
        print(f"이미 {existing_count}개의 말씀이 있습니다.")
        return

    # 초기 데이터 생성
    for verse_data in initial_verses:
        verse = DailyVerse(
            verse=verse_data["verse"], reference=verse_data["reference"], is_active=True
        )
        db.add(verse)

    db.commit()
    print(f"{len(initial_verses)}개의 말씀을 생성했습니다.")


if __name__ == "__main__":
    from app.db.session import SessionLocal

    db = SessionLocal()
    try:
        init_daily_verses(db)
    finally:
        db.close()
