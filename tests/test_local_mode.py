from app.services.mock_ai import generate_outline, generate_story


class Request:
    story_prompt = "A robot finds a hidden garden"
    character_name = "Arun"
    setting = "a futuristic lab"
    tone = "funny"
    art_style = "comic book"


def test_mock_outline():
    outline = generate_outline(Request())
    assert "Arun" in outline


def test_mock_story_has_five_panels():
    story = generate_story(Request(), "outline")
    assert len(story) == 5
    assert story[0]["panel_number"] == 1
    assert story[-1]["panel_number"] == 5
