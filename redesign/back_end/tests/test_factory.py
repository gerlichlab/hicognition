from app import create_app

def test_config(app):
    assert app.testing
    assert 1 == 1
    
    
def test_fill_db(app, fill_db):
    
    assert 1 == 1

