def test_scenario_analysis_endpoint(client):
    payload = {
        "raw_query": "A police officer stopped me at the market and detained me without giving any reason or warrant.",
        "language": "en"
    }
    response = client.post("/api/v1/scenario/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "extracted_facts" in data
    assert len(data["extracted_facts"]["actors"]) >= 1
    assert "Criminal Procedure & Police Powers" in data["identified_domains"]
    assert data["risk_level"] == "URGENT"
    assert data["urgency_advisory"] is not None


def test_explainable_recommendation_pipeline(client):
    payload = {
        "raw_query": "The police station refused to register my First Information Report after my phone was stolen.",
        "language": "en"
    }
    response = client.post("/api/v1/recommendations/explain", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert len(data["recommendations"]) > 0
    assert "plain_language_explanation" in data
    assert "disclaimer" in data
    # Verify provenance reference is present
    top_rec = data["recommendations"][0]
    assert "provenance_reference" in top_rec
    assert "why_recommended" in top_rec
    assert top_rec["relevance_score"] >= 0.0


def test_whatif_comparison_pipeline(client):
    original_facts = {
        "actors": ["Police Officer", "Citizen"],
        "key_events": ["Detained without warrant"],
        "location": "Delhi",
        "legal_issue": "Unlawful arrest and custody",
        "action_type": "Criminal & Procedural / Police Inquiry"
    }
    modified_facts = {
        "actors": ["Shopkeeper", "Customer"],
        "key_events": ["Defective electronics sold with no refund"],
        "location": "Delhi",
        "legal_issue": "Consumer product deficiency",
        "action_type": "Consumer Dispute / Civil Redressal"
    }
    payload = {
        "original_facts": original_facts,
        "modified_facts": modified_facts
    }
    response = client.post("/api/v1/whatif/compare", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "diff_summary" in data
    assert len(data["changes_detected"]) >= 1


def test_constitution_search(client):
    response = client.get("/api/v1/constitution/articles?query=Article%2021")
    assert response.status_code == 200
    articles = response.json()
    assert len(articles) >= 1
    assert any("Article 21" in a["identifier"] for a in articles)


def test_quiz_questions_and_submission(client):
    # Test getting questions
    response = client.get("/api/v1/quiz/questions")
    assert response.status_code == 200
    questions = response.json()
    assert len(questions) >= 1
    q1 = questions[0]
    assert "question" in q1
    assert "options" in q1

    # Test submitting answer
    submit_payload = {
        "question_id": q1["id"],
        "selected_option_index": q1["correct_index"]
    }
    submit_resp = client.post("/api/v1/quiz/submit", json=submit_payload)
    assert submit_resp.status_code == 200
    result = submit_resp.json()
    assert result["is_correct"] is True
    assert "explanation" in result


