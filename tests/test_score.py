from datetime import date

from score import is_valid, score, score_leads

TODAY = date(2026, 11, 26)


def lead(signal_date="2026-11-26", industry="media", country="India", website="https://example.com"):
    return {
        "company": "Example",
        "country": country,
        "industry": industry,
        "signal_date": signal_date,
        "website": website,
    }


def test_all_rules_match():
    assert score(lead(industry="fintech", country="UAE"), TODAY) == 100


def test_date_boundaries():
    assert score(lead("2026-11-26"), TODAY) == 40  # today
    assert score(lead("2026-10-27"), TODAY) == 40  # 30 days
    assert score(lead("2026-10-26"), TODAY) == 20  # 31 days
    assert score(lead("2026-08-28"), TODAY) == 20  # 90 days
    assert score(lead("2026-08-27"), TODAY) == 0  # 91 days


def test_industry_and_country_ignore_case_and_whitespace():
    row = lead("2026-01-01", industry=" Real_Estate ", country=" saudi arabia")
    assert score(row, TODAY) == 60


def test_filter_drops_bad_rows():
    assert not is_valid(lead(website="   "), TODAY)
    assert not is_valid(lead("2026-11-27"), TODAY)
    assert not is_valid(lead("not-a-date"), TODAY)
    assert is_valid(lead(), TODAY)


def test_score_leads_sorts_highest_first():
    rows = [lead("2026-01-01"), lead(industry="luxury", country="UK"), lead(website="")]
    assert [row["score"] for row in score_leads(rows, TODAY)] == [100, 0]
