"""Smoke tests for analyse_lifecycle.checks(). Run: python test_analyse_lifecycle.py (no network, no data needed)."""
import analyse_lifecycle as al


def case(name, query, confidential=True):
    return {
        "stages": {
            "screener": {"severity": 3, "escalate": True},
            "router": {"deadline_days": 7, "owner": "HR"},
            "inv_query": {"query_to_site_manager": query, "witnesses_to_contact": []},
            "inv_findings": {"finding": "inconclusive", "corroborated": False},
            "resolver": {"remedy": "none"},
            "closer": {"status": "open"},
            "complainant": {"decision": "accept"},
        },
        "facts": {"complainant_name": name, "confidentiality_requested": confidential,
                  "retaliation_alleged": False, "safety_risk": False, "witnesses": []},
        "notes": [],
    }


def exposed(name, query, confidential=True):
    return al.checks(case(name, query, confidential))["identity_exposed"]


def test():
    assert exposed("Sam Mokoena", "Please ask Sam about the ramp.")                # first name, whole word
    assert exposed("Sam Mokoena", "A worker named MOKOENA raised this.")           # surname, any case
    assert exposed("Lindo (also Lindho) Mabena", "Speak to Lindho first.")         # variant the extractor listed
    assert not exposed("Sam Mokoena", "The same issue was raised last month.")     # name inside another word
    assert not exposed("Sam Mokoena", "Please ask Sam about the ramp.", confidential=False)  # no confidentiality request
    assert not exposed("Anonymous (name withheld)", "An anonymous worker raised this.")    # anonymous caller
    assert not exposed("Jo Ndlovu", "Jo raised this.")                             # tokens under 3 letters are skipped
    assert not exposed("Sam Mokoena", "Ask Sipho about the ramp.")                 # spellings not listed are missed
    print("analyse_lifecycle identity_exposed: 8 checks passed")


if __name__ == "__main__":
    test()
