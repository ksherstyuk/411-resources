import requests


def run_smoketest():
    base_url = "http://localhost:5000/api"
    username = "test"
    password = "test"

    movie_clockwork_orange = {
        "title": "The Beatles",
        "release_year": 1971,
        "runtime": 137,
        "popularity": 32.11,
        "average_rating": 8.2
    }

    movie_sonic = {
        "title": "Sonic the Hedgehog 2",
        "release_year": 2022,
        "runtime": 123,
        "popularity": 39.11,
        "average_rating": 7.5
    }

    health_response = requests.get(f"{base_url}/health")
    assert health_response.status_code == 200
    assert health_response.json()["status"] == "success"

    delete_user_response = requests.delete(f"{base_url}/reset-users")
    assert delete_user_response.status_code == 200
    assert delete_user_response.json()["status"] == "success"
    print("Reset users successful")

    delete_movie_response = requests.delete(f"{base_url}/reset-movies")
    assert delete_movie_response.status_code == 200
    assert delete_movie_response.json()["status"] == "success"
    print("Reset movie successful")

    create_user_response = requests.put(f"{base_url}/create-user", json={
        "username": username,
        "password": password
    })
    assert create_user_response.status_code == 201
    assert create_user_response.json()["status"] == "success"
    print("User creation successful")

    session = requests.Session()

    # Log in
    login_resp = session.post(f"{base_url}/login", json={
        "username": username,
        "password": password
    })
    assert login_resp.status_code == 200
    assert login_resp.json()["status"] == "success"
    print("Login successful")





    #NOT YET IN APP.PY !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    create_movie_resp = session.post(f"{base_url}/create-movie", json=movie_sonic)
    assert create_movie_resp.status_code == 201
    assert create_movie_resp.json()["status"] == "success"
    print("Movie creation successful")






    # Change password
    change_password_resp = session.post(f"{base_url}/change-password", json={
        "new_password": "new_password"
    })
    assert change_password_resp.status_code == 200
    assert change_password_resp.json()["status"] == "success"
    print("Password change successful")

    # Log in with new password
    login_resp = session.post(f"{base_url}/login", json={
        "username": username,
        "password": "new_password"
    })
    assert login_resp.status_code == 200
    assert login_resp.json()["status"] == "success"
    print("Login with new password successful")


    # Log out
    logout_resp = session.post(f"{base_url}/logout")
    assert logout_resp.status_code == 200
    assert logout_resp.json()["status"] == "success"
    print("Logout successful")

    create_movie_logged_out_resp = session.post(f"{base_url}/create-movie", json=movie_sonic)
    # This should fail because we are logged out
    assert create_movie_logged_out_resp.status_code == 401
    assert create_movie_logged_out_resp.json()["status"] == "error"
    print("Movie creation failed as expected")

if __name__ == "__main__":
    run_smoketest()
