from app.models import User, Space, Testimonial, Widget


def test_landing_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"TestiFlow" in response.data


def test_pricing_page(client):
    response = client.get("/pricing")
    assert response.status_code == 200
    assert b"$19" in response.data
    assert b"$49" in response.data
    assert b"$99" in response.data


def test_signup_page(client):
    response = client.get("/auth/signup")
    assert response.status_code == 200
    assert b"Create your account" in response.data


def test_login_page(client):
    response = client.get("/auth/login")
    assert response.status_code == 200
    assert b"Welcome back" in response.data


def test_signup_flow(client, db):
    response = client.post("/auth/signup", data={
        "name": "Test User",
        "email": "test@example.com",
        "password": "password123",
        "password_confirm": "password123",
    }, follow_redirects=True)
    assert response.status_code == 200

    user = User.query.filter_by(email="test@example.com").first()
    assert user is not None
    assert user.name == "Test User"
    assert user.plan == "free"


def test_signup_validation(client):
    # Short password
    response = client.post("/auth/signup", data={
        "name": "Test",
        "email": "test@example.com",
        "password": "short",
        "password_confirm": "short",
    }, follow_redirects=True)
    assert b"at least 8 characters" in response.data

    # Password mismatch
    response = client.post("/auth/signup", data={
        "name": "Test",
        "email": "test@example.com",
        "password": "password123",
        "password_confirm": "different123",
    }, follow_redirects=True)
    assert b"do not match" in response.data


def test_login_flow(client, db):
    # Create user first
    user = User(name="Test", email="test@example.com")
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()

    response = client.post("/auth/login", data={
        "email": "test@example.com",
        "password": "password123",
    }, follow_redirects=True)
    assert response.status_code == 200


def test_login_invalid_credentials(client, db):
    user = User(name="Test", email="test@example.com")
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()

    response = client.post("/auth/login", data={
        "email": "test@example.com",
        "password": "wrongpassword",
    }, follow_redirects=True)
    assert b"Invalid email or password" in response.data


def test_dashboard_requires_login(client):
    response = client.get("/dashboard/", follow_redirects=False)
    assert response.status_code == 302


def test_create_space(client, db):
    user = User(name="Test", email="test@example.com")
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()

    # Login
    client.post("/auth/login", data={
        "email": "test@example.com",
        "password": "password123",
    })

    # Create space
    response = client.post("/dashboard/spaces/new", data={
        "name": "My Product",
        "website_url": "https://example.com",
        "header_text": "Tell us what you think!",
    }, follow_redirects=True)
    assert response.status_code == 200

    space = Space.query.filter_by(name="My Product").first()
    assert space is not None
    assert space.slug == "my-product"
    assert space.user_id == user.id

    # Default widget should be created
    widget = Widget.query.filter_by(space_id=space.id).first()
    assert widget is not None
    assert widget.widget_type == "wall"


def test_free_plan_space_limit(client, db):
    user = User(name="Test", email="test@example.com", plan="free")
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()

    client.post("/auth/login", data={
        "email": "test@example.com",
        "password": "password123",
    })

    # Create first space (should succeed)
    client.post("/dashboard/spaces/new", data={
        "name": "Space 1",
    }, follow_redirects=True)

    assert Space.query.filter_by(user_id=user.id).count() == 1

    # Create second space (should be blocked for free plan)
    response = client.post("/dashboard/spaces/new", data={
        "name": "Space 2",
    }, follow_redirects=True)

    assert Space.query.filter_by(user_id=user.id).count() == 1


def test_public_collection_form(client, db):
    user = User(name="Test", email="test@example.com")
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()

    space = Space(name="Product", slug="product", user_id=user.id)
    db.session.add(space)
    db.session.commit()

    # Get collection form
    response = client.get("/t/product")
    assert response.status_code == 200
    assert b"Product" in response.data


def test_submit_testimonial(client, db):
    user = User(name="Test", email="test@example.com")
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()

    space = Space(name="Product", slug="product", user_id=user.id)
    db.session.add(space)
    db.session.commit()

    response = client.post("/t/product", data={
        "author_name": "Jane Doe",
        "author_email": "jane@example.com",
        "author_title": "CEO",
        "company": "Acme Inc",
        "rating": 5,
        "text": "This is an amazing product! Highly recommend it.",
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Thank you" in response.data

    testimonial = Testimonial.query.filter_by(space_id=space.id).first()
    assert testimonial is not None
    assert testimonial.author_name == "Jane Doe"
    assert testimonial.status == "pending"
    assert testimonial.rating == 5


def test_testimonial_validation(client, db):
    user = User(name="Test", email="test@example.com")
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()

    space = Space(name="Product", slug="product", user_id=user.id)
    db.session.add(space)
    db.session.commit()

    # Too short text
    response = client.post("/t/product", data={
        "author_name": "Jane",
        "text": "Short",
    }, follow_redirects=True)
    assert b"at least 10 characters" in response.data


def test_approve_testimonial(client, db):
    user = User(name="Test", email="test@example.com")
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()

    space = Space(name="Product", slug="product", user_id=user.id)
    db.session.add(space)
    db.session.commit()

    testimonial = Testimonial(
        space_id=space.id,
        author_name="Jane",
        text="Great product, really love it!",
        status="pending",
    )
    db.session.add(testimonial)
    db.session.commit()

    client.post("/auth/login", data={
        "email": "test@example.com",
        "password": "password123",
    })

    response = client.post(
        f"/dashboard/testimonials/{testimonial.uid}/approve",
        follow_redirects=True,
    )
    assert response.status_code == 200

    db.session.refresh(testimonial)
    assert testimonial.status == "approved"


def test_widget_data_api(client, db):
    user = User(name="Test", email="test@example.com")
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()

    space = Space(name="Product", slug="product", user_id=user.id)
    db.session.add(space)
    db.session.commit()

    widget = Widget(space_id=space.id, widget_type="wall")
    db.session.add(widget)
    db.session.commit()

    # Add approved testimonial
    testimonial = Testimonial(
        space_id=space.id,
        author_name="Jane",
        text="Amazing product!",
        rating=5,
        status="approved",
    )
    db.session.add(testimonial)
    db.session.commit()

    response = client.get(f"/widget/{widget.uid}/data")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["testimonials"]) == 1
    assert data["testimonials"][0]["author_name"] == "Jane"


def test_api_testimonials(client, db):
    user = User(name="Test", email="test@example.com")
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()

    space = Space(name="Product", slug="product", user_id=user.id)
    db.session.add(space)
    db.session.commit()

    # One approved, one pending
    db.session.add(Testimonial(space_id=space.id, author_name="Jane", text="Great!", status="approved"))
    db.session.add(Testimonial(space_id=space.id, author_name="Bob", text="Pending review", status="pending"))
    db.session.commit()

    response = client.get(f"/api/v1/spaces/{space.uid}/testimonials")
    assert response.status_code == 200
    data = response.get_json()
    assert data["count"] == 1  # Only approved ones
    assert data["testimonials"][0]["author_name"] == "Jane"


def test_user_model(db, app):
    with app.app_context():
        user = User(name="Test", email="test@example.com")
        user.set_password("mypassword123")
        db.session.add(user)
        db.session.commit()

        assert user.check_password("mypassword123")
        assert not user.check_password("wrongpassword")
        assert user.plan == "free"
        assert user.can_create_space()
        assert user.has_branding()
